import pandas as pd
from catboost import CatBoostClassifier
import optuna
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
import numpy as np

print("1. Cargando el historial clínico completo de todos los pacientes...")

cohort = pd.read_csv("hackato_cohort.csv")
diagnostics = pd.read_csv("hackato_diagnostics.csv")
farmacs = pd.read_csv("hackato_farmacs.csv")
urgencies = pd.read_csv("hackato_visites_urgencies.csv")
visites_hospital = pd.read_csv("hackato_visites_hospital.csv")
visites_primaria = pd.read_csv("hackato_visites_primaria.csv")

# ==========================================
# FASE 1: PERFIL CLÍNICO TOTAL
# ==========================================
conteo_urg = urgencies.groupby('id_pacient').size().reset_index(name='total_urgencies_any')
conteo_hosp = visites_hospital.groupby('id_pacient').size().reset_index(name='total_hospital_any')
conteo_prim = visites_primaria.groupby('id_pacient')['visites'].sum().reset_index(name='total_primaria_any')

df_perfil = cohort.merge(conteo_urg, on='id_pacient', how='left')
df_perfil = df_perfil.merge(conteo_hosp, on='id_pacient', how='left')
df_perfil = df_perfil.merge(conteo_prim, on='id_pacient', how='left')
df_perfil = df_perfil.merge(diagnostics, on='id_pacient', how='left')
df_perfil = df_perfil.merge(farmacs, on='id_pacient', how='left')
df_perfil = df_perfil.fillna({'total_urgencies_any': 0, 'total_hospital_any': 0, 'total_primaria_any': 0, 'diags_totals': 0, 'farmacs_totals': 0})
# Las categóricas que sean nan las ponemos a string para que catboost no se queje
for col in ['sexe', 'grup_edat']:
    df_perfil[col] = df_perfil[col].astype(str)

# ==========================================
# FASE 1.5: FEATURE ENGINEERING
# ==========================================
print("\n-> Creando nuevas variables clínicas avanzadas (Feature Engineering)...")

df_perfil['carga_asistencial_total'] = df_perfil['total_urgencies_any'] + df_perfil['total_hospital_any'] + df_perfil['total_primaria_any']
df_perfil['ratio_gravedad_visitas'] = (df_perfil['total_urgencies_any'] + df_perfil['total_hospital_any']) / (df_perfil['total_primaria_any'] + 1)
df_perfil['complejidad_quimica'] = df_perfil['farmacs_totals'] / (df_perfil['diags_totals'] + 1)
df_perfil['alerta_polimedicacion'] = (df_perfil['farmacs_totals'] > 10).astype(int)
df_perfil['coctel_cardio_nervioso'] = ((df_perfil.get('sistema_cardiovascular', 0) > 0) & (df_perfil.get('sistema_nervios', 0) > 0)).astype(int)

# ==========================================
# FASE 2: ENTRENAR AL "DETECTOR DE PCC" (CATBOOST NATIVO)
# ==========================================
print("\n2. Entrenando a la IA (CatBoost NATIVO) para descubrir qué define a un paciente PCC...")

df_entrenamiento = df_perfil[df_perfil['cronic'].isin(['PCC', 'NO'])].copy()
df_entrenamiento['TARGET_ES_PCC'] = df_entrenamiento['cronic'].apply(lambda x: 1 if x == 'PCC' else 0)

X = df_entrenamiento.drop(columns=['id_pacient', 'situacio', 'cronic', 'TARGET_ES_PCC'])
Y = df_entrenamiento['TARGET_ES_PCC']

# Definimos las variables categóricas nativas
cat_features = ['sexe', 'grup_edat']

ratio_desbalanceo = len(Y[Y == 0]) / len(Y[Y == 1])

print("\n--- INICIANDO OPTUNA CON CATBOOST ---")
def objective(trial):
    params = {
        'iterations': trial.suggest_int('iterations', 100, 300),
        'depth': trial.suggest_int('depth', 4, 8),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
        'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1.0, 10.0),
        'scale_pos_weight': ratio_desbalanceo,
        'cat_features': cat_features,
        'verbose': 0,
        'random_seed': 42
    }
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    auc_scores = []
    
    for train_idx, val_idx in cv.split(X, Y):
        X_train_cv, X_val_cv = X.iloc[train_idx], X.iloc[val_idx]
        Y_train_cv, Y_val_cv = Y.iloc[train_idx], Y.iloc[val_idx]
        
        model = CatBoostClassifier(**params)
        model.fit(X_train_cv, Y_train_cv)
        
        preds = model.predict_proba(X_val_cv)[:, 1]
        auc = roc_auc_score(Y_val_cv, preds)
        auc_scores.append(auc)
        
    return np.mean(auc_scores)

optuna.logging.set_verbosity(optuna.logging.WARNING)
study = optuna.create_study(direction='maximize')
print("Optimizando hiperparámetros...")
study.optimize(objective, n_trials=10)

mejores_params = study.best_params
mejores_params['scale_pos_weight'] = ratio_desbalanceo
mejores_params['cat_features'] = cat_features
mejores_params['random_seed'] = 42
mejores_params['verbose'] = 0

print("\nReentrenando el modelo final CatBoost...")
detector_pcc = CatBoostClassifier(**mejores_params)
detector_pcc.fit(X, Y)

# ==========================================
# FASE 3: LA BÚSQUEDA DE CRÓNICOS OCULTOS
# ==========================================
print("\n3. Analizando a la población 'Sana' (Etiqueta NO) en busca de anomalías...")

pacientes_no_cronicos = df_entrenamiento[df_entrenamiento['TARGET_ES_PCC'] == 0].copy()
X_no_cronicos = X[Y == 0]

probabilidades_pcc = detector_pcc.predict_proba(X_no_cronicos)[:, 1]
pacientes_no_cronicos['Probabilidad_Real_PCC'] = probabilidades_pcc * 100

candidatos_ocultos = pacientes_no_cronicos.sort_values(by='Probabilidad_Real_PCC', ascending=False)

print("\n" + "="*50)
print("¡ALERTA CLÍNICA! TOP 5 PACIENTES QUE DEBERÍAN SER PCC:")
print("="*50)
top_5 = candidatos_ocultos[['id_pacient', 'Probabilidad_Real_PCC', 'diags_totals', 'farmacs_totals', 'carga_asistencial_total', 'grup_edat']]
print(top_5.head(5).to_string(index=False))

# ==========================================
# FASE 4: ¿CUÁLES SON LOS "SÍNTOMAS" DEL PCC?
# ==========================================
importancias = detector_pcc.get_feature_importance()
df_sintomas = pd.DataFrame({'Variable': X.columns, 'Peso': importancias}).sort_values(by='Peso', ascending=False)

print("\n" + "="*50)
print("LOS 5 'SÍNTOMAS' + VARIABLES CLÍNICAS QUE DEFINEN A UN PCC SEGÚN CATBOOST:")
print("="*50)
print(df_sintomas.head(5).to_string(index=False))

# ==========================================
# FASE 5: SIMULADOR DE PACIENTES (TESTING)
# ==========================================
print("\n" + "="*50)
print("INICIANDO SIMULADOR DE PACIENTES: DETECTOR DE CRÓNICOS NATIVO")
print("="*50)

def evaluar_candidato_pcc(datos_paciente_dict, descripcion):
    print(f"\n--- TEST: {descripcion} ---")
    
    df_nuevo = pd.DataFrame([datos_paciente_dict])
    
    total_urg = df_nuevo.get('total_urgencies_any', pd.Series([0]))[0]
    total_hosp = df_nuevo.get('total_hospital_any', pd.Series([0]))[0]
    total_prim = df_nuevo.get('total_primaria_any', pd.Series([0]))[0]
    farmacs_t = df_nuevo.get('farmacs_totals', pd.Series([0]))[0]
    diags_t = df_nuevo.get('diags_totals', pd.Series([0]))[0]
    
    df_nuevo['carga_asistencial_total'] = total_urg + total_hosp + total_prim
    df_nuevo['ratio_gravedad_visitas'] = (total_urg + total_hosp) / (total_prim + 1)
    df_nuevo['complejidad_quimica'] = farmacs_t / (diags_t + 1)
    df_nuevo['alerta_polimedicacion'] = int(farmacs_t > 10)
    df_nuevo['coctel_cardio_nervioso'] = int((df_nuevo.get('sistema_cardiovascular', pd.Series([0]))[0] > 0) and (df_nuevo.get('sistema_nervios', pd.Series([0]))[0] > 0))
    
    # Rellenamos columnas numéricas con 0 y categóricas con "Ninguno"
    for col in X.columns:
        if col not in df_nuevo:
            if col in cat_features:
                df_nuevo[col] = 'Desconegut'
            else:
                df_nuevo[col] = 0
                
    df_nuevo = df_nuevo[X.columns]
    
    probabilidad = detector_pcc.predict_proba(df_nuevo)[0][1] * 100
    
    print(f"Probabilidad de ser PCC: {probabilidad:.2f}%")
    if probabilidad > 75:
        print("🚨 ALERTA ROJA: Perfil idéntico a un Crónico Complejo. ¡Revisar urgente!")
    elif probabilidad > 50:
        print("⚠️ ALERTA AMARILLA: Paciente sospechoso. Sugerencia de revisión en Primaria.")
    else:
        print("✅ Paciente Sano/Estable: Su perfil concuerda con la etiqueta 'NO' crónico.")

# ==========================================
# ---------------------------------------------------------
# CASOS DE PRUEBA (BATERÍA AMPLIADA: 19 PERFILES CLÍNICOS)
# ---------------------------------------------------------
pacientes_prueba = [
    # LOS ORIGINALES
    ({'sexe': 'H', 'grup_edat': '30-34', 'diags_totals': 1, 'farmacs_totals': 0, 'total_primaria_any': 2, 'total_urgencies_any': 0}, "1. El Joven Sano (Riesgo Nulo)"),
    ({'sexe': 'D', 'grup_edat': '90>', 'diags_totals': 2, 'farmacs_totals': 10, 'total_primaria_any': 0, 'total_urgencies_any': 0, 'sistema_cardiovascular': 3, 'sistema_nervios': 2}, "2. El 'Fantasma' Polimedicado (>90 años, 10 fármacos, 0 visitas)"),
    ({'sexe': 'H', 'grup_edat': '40-44', 'diags_totals': 5, 'farmacs_totals': 3, 'total_primaria_any': 20, 'total_urgencies_any': 2, 'antiinfecciosos_per_a_us_sistemic': 2}, "3. Joven Hiperfrecuentador (40 años, 20 visitas)"),
    ({'sexe': 'H', 'grup_edat': '80-84', 'diags_totals': 12, 'farmacs_totals': 6, 'total_primaria_any': 15, 'total_urgencies_any': 1, 'sistema_digestiu_i_metabolisme': 2, 'sistema_cardiovascular': 2}, "4. Abuelo Frágil en el Límite (80-84 años, 6 fármacos)"),
    
    # 15 NUEVOS CASOS
    ({'sexe': 'H', 'grup_edat': '20-24', 'diags_totals': 0, 'farmacs_totals': 0, 'total_primaria_any': 1, 'total_urgencies_any': 0}, "5. Deportista Universitario (0 meds, 0 diags)"),
    ({'sexe': 'D', 'grup_edat': '45-49', 'diags_totals': 1, 'farmacs_totals': 1, 'total_primaria_any': 1, 'total_urgencies_any': 0}, "6. Revisión Rutinaria Ginecológica (45-49 años)"),
    ({'sexe': 'D', 'grup_edat': '50-54', 'diags_totals': 2, 'farmacs_totals': 0, 'total_primaria_any': 3, 'total_urgencies_any': 0}, "7. Mujer Mediana Edad Sana (Menopausia)"),
    ({'sexe': 'H', 'grup_edat': '40-44', 'diags_totals': 3, 'farmacs_totals': 2, 'total_primaria_any': 10, 'total_urgencies_any': 1, 'sistema_nervios': 2}, "8. Hombre con Estrés/Ansiedad Laboral (10 primarias, ansiolíticos)"),
    ({'sexe': 'H', 'grup_edat': '75-79', 'diags_totals': 2, 'farmacs_totals': 1, 'total_primaria_any': 2, 'total_urgencies_any': 0}, "9. Abuelo Sano y Activo (75 años, solo pastilla tensión)"),
    ({'sexe': 'H', 'grup_edat': '30-34', 'diags_totals': 2, 'farmacs_totals': 2, 'total_primaria_any': 4, 'total_urgencies_any': 1, 'sistema_respiratori': 2}, "10. Joven Asmático Controlado (2 inhaladores)"),
    ({'sexe': 'D', 'grup_edat': '55-59', 'diags_totals': 3, 'farmacs_totals': 3, 'total_primaria_any': 4, 'total_urgencies_any': 0, 'sistema_digestiu_i_metabolisme': 2}, "11. Diabética Tipo 2 Controlada (55 años, 3 meds)"),
    ({'sexe': 'D', 'grup_edat': '65-69', 'diags_totals': 3, 'farmacs_totals': 8, 'total_primaria_any': 6, 'total_urgencies_any': 0}, "12. Polimedicada sin gravedad evidente (65a, 8 meds para 3 diags)"),
    ({'sexe': 'H', 'grup_edat': '70-74', 'diags_totals': 6, 'farmacs_totals': 6, 'total_primaria_any': 12, 'total_urgencies_any': 3, 'total_hospital_any': 1}, "13. Paciente Pre-PCC (70a, 6 meds, 6 diags, 1 ingreso)"),
    ({'sexe': 'D', 'grup_edat': '85-89', 'diags_totals': 10, 'farmacs_totals': 12, 'total_primaria_any': 25, 'total_urgencies_any': 4, 'sistema_cardiovascular': 4, 'sistema_nervios': 3}, "14. Crónica de Libro (85a, 12 meds, Cóctel Cardio-Nervioso)"),
    ({'sexe': 'H', 'grup_edat': '25-29', 'diags_totals': 1, 'farmacs_totals': 4, 'total_primaria_any': 5, 'total_urgencies_any': 4, 'total_hospital_any': 1}, "15. Joven Accidente Moto (1 diag trauma, 4 meds, 4 urgencias)"),
    ({'sexe': 'D', 'grup_edat': '90>', 'diags_totals': 5, 'farmacs_totals': 15, 'total_primaria_any': 2, 'total_urgencies_any': 1, 'sistema_nervios': 5}, "16. Anciana 90+ Muy Frágil (15 meds, altísima complejidad química)"),
    ({'sexe': 'H', 'grup_edat': '60-64', 'diags_totals': 4, 'farmacs_totals': 5, 'total_primaria_any': 8, 'total_urgencies_any': 2, 'total_hospital_any': 1, 'sistema_cardiovascular': 4}, "17. Hombre 60a Post-Infarto Agudo (1 ingreso, 5 meds cardio)"),
    ({'sexe': 'D', 'grup_edat': '50-54', 'diags_totals': 1, 'farmacs_totals': 1, 'total_primaria_any': 30, 'total_urgencies_any': 0}, "18. Falsa PCC (Hipocondría/Ansiedad: 30 visitas primaria, 1 med)"),
    ({'sexe': 'H', 'grup_edat': '35-39', 'diags_totals': 4, 'farmacs_totals': 8, 'total_primaria_any': 15, 'total_urgencies_any': 3, 'total_hospital_any': 2}, "19. Joven Oncológico Inducido (8 meds, múltiples ingresos - No es PCC geriátrico)")
]

for datos, desc in pacientes_prueba:
    evaluar_candidato_pcc(datos, desc)