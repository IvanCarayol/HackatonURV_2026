import os
import pandas as pd
from catboost import CatBoostClassifier
import optuna
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import numpy as np

# Configurar rutas relativas al script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Database")

print("1. Cargando y fusionando datos de mortalidad...")
cohort = pd.read_csv(os.path.join(DATA_DIR, "hackato_cohort.csv"))
diagnostics = pd.read_csv(os.path.join(DATA_DIR, "hackato_diagnostics.csv"))
farmacs = pd.read_csv(os.path.join(DATA_DIR, "hackato_farmacs.csv"))

df_maestro = cohort.merge(diagnostics, on="id_pacient", how="left")
df_maestro = df_maestro.merge(farmacs, on="id_pacient", how="left")
df_maestro = df_maestro.fillna({'diags_totals': 0, 'farmacs_totals': 0})
for col in ['sexe', 'grup_edat', 'cronic']:
    df_maestro[col] = df_maestro[col].astype(str)

# ==========================================
# FASE 1.5: FEATURE ENGINEERING CLÍNICO
# ==========================================
print("\n-> Aplicando Feature Engineering Clínico...")
df_maestro['indice_fragilidad'] = df_maestro['diags_totals'] + df_maestro['farmacs_totals']
df_maestro['alerta_polimedicacion'] = (df_maestro['farmacs_totals'] > 10).astype(int)
df_maestro['coctel_cardio_nervioso'] = ((df_maestro.get('sistema_cardiovascular', 0) > 0) & (df_maestro.get('sistema_nervios', 0) > 0)).astype(int)

# ==========================================
# FASE 2: PREPARACIÓN DE TARGET Y PARTICIÓN
# ==========================================
df_maestro['TARGET_mortalidad'] = df_maestro['situacio'].apply(lambda x: 1 if x == 'D' else 0)

X = df_maestro.drop(columns=['id_pacient', 'situacio', 'TARGET_mortalidad'])
Y = df_maestro['TARGET_mortalidad']

cat_features = ['sexe', 'grup_edat', 'cronic']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=42, stratify=Y)
ratio_desbalanceo = len(Y_train[Y_train == 0]) / len(Y_train[Y_train == 1])

# ==========================================
# FASE 3: OPTIMIZACIÓN OPTUNA (CATBOOST NATIVO)
# ==========================================
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
    
    for train_idx, val_idx in cv.split(X_train, Y_train):
        X_train_cv, X_val_cv = X_train.iloc[train_idx], X_train.iloc[val_idx]
        Y_train_cv, Y_val_cv = Y_train.iloc[train_idx], Y_train.iloc[val_idx]
        
        model = CatBoostClassifier(**params)
        model.fit(X_train_cv, Y_train_cv)
        preds = model.predict_proba(X_val_cv)[:, 1]
        auc_scores.append(roc_auc_score(Y_val_cv, preds))
        
    return np.mean(auc_scores)

optuna.logging.set_verbosity(optuna.logging.WARNING)
study = optuna.create_study(direction='maximize')
print("Optimizando hiperparámetros de mortalidad (10 configuraciones)...")
study.optimize(objective, n_trials=10)

mejores_params = study.best_params
mejores_params['scale_pos_weight'] = ratio_desbalanceo
mejores_params['cat_features'] = cat_features
mejores_params['random_seed'] = 42
mejores_params['verbose'] = 0

print("\nReentrenando CatBoost Mortalidad definitivo...")
modelo_mortalidad = CatBoostClassifier(**mejores_params)
modelo_mortalidad.fit(X_train, Y_train)

# ==========================================
# FASE 4: EVALUACIÓN TEST PURO
# ==========================================
print("\n--- RESULTADOS DEL MODELO EN DATOS NUEVOS (TEST) ---")
predicciones = modelo_mortalidad.predict(X_test)
probabilidades = modelo_mortalidad.predict_proba(X_test)[:, 1]

print("Área bajo la curva (ROC-AUC):", round(roc_auc_score(Y_test, probabilidades), 3))

# ==========================================
# FASE 5: SIMULADOR DE PACIENTES
# ==========================================
print("\n" + "="*50)
print("INICIANDO BATERÍA DE PRUEBAS CLÍNICAS (SIMULACIÓN NATIVA)")
print("="*50)

def predecir_nuevo_paciente(datos_paciente_dict, desc=""):
    df_nuevo = pd.DataFrame([datos_paciente_dict])
    
    diags_t = df_nuevo.get('diags_totals', pd.Series([0]))[0]
    farmacs_t = df_nuevo.get('farmacs_totals', pd.Series([0]))[0]
    df_nuevo['indice_fragilidad'] = diags_t + farmacs_t
    df_nuevo['alerta_polimedicacion'] = int(farmacs_t > 10)
    df_nuevo['coctel_cardio_nervioso'] = int((df_nuevo.get('sistema_cardiovascular', pd.Series([0]))[0] > 0) and (df_nuevo.get('sistema_nervios', pd.Series([0]))[0] > 0))

    for col in X_train.columns:
        if col not in df_nuevo:
            if col in cat_features:
                df_nuevo[col] = 'Desconegut'
            else:
                df_nuevo[col] = 0
                
    df_nuevo = df_nuevo[X_train.columns]
    
    prob = modelo_mortalidad.predict_proba(df_nuevo)[0][1]
    riesgo = prob * 100
    
    print(f"\n--- {desc} ---")
    print(f"Riesgo de mortalidad a 1 año: {riesgo:.2f}%")
    if riesgo > 50:
        print("Alerta: Paciente de Alto Riesgo.")
    else:
        print("Paciente de Bajo Riesgo.")

# Pruebas con strings puras (19 Perfiles)
pacientes_mortalidad = [
    # LOS ORIGINALES
    ({'sexe': 'D', 'grup_edat': '30-34', 'cronic': 'NO', 'diags_totals': 1, 'problemes_salut_aguts': 1, 'farmacs_totals': 0}, "1. Joven Sana"),
    ({'sexe': 'H', 'grup_edat': '65-69', 'cronic': 'PCC', 'diags_totals': 6, 'problemes_salut_cronics': 4, 'farmacs_totals': 5, 'sistema_cardiovascular': 2, 'sistema_digestiu_i_metabolisme': 2}, "2. Crónico Complejo (PCC) Estable"),
    ({'sexe': 'D', 'grup_edat': '75-79', 'cronic': 'MACA', 'diags_totals': 15, 'problemes_salut_neoplasia_maligna': 3, 'farmacs_totals': 10, 'antineoplasics_i_immunomoduladors': 2, 'sistema_nervios': 4}, "3. Oncológica Avanzada (MACA)"),
    ({'sexe': 'H', 'grup_edat': '85-89', 'cronic': 'NO', 'diags_totals': 2, 'problemes_salut_cronics': 1, 'farmacs_totals': 1, 'organs_dels_sentits': 1}, "4. Anciano sin Cronicidad"),
    ({'sexe': 'H', 'grup_edat': '20-24', 'cronic': 'NO', 'diags_totals': 10, 'problemes_salut_aguts': 8, 'farmacs_totals': 6, 'antiinfecciosos_per_a_us_sistemic': 3}, "5. TRAMPA: Joven con Infección/Trauma Agudo"),
    ({'sexe': 'D', 'grup_edat': '50-54', 'cronic': 'NO', 'diags_totals': 2, 'problemes_salut_neoplasia_maligna': 1, 'farmacs_totals': 2, 'antineoplasics_i_immunomoduladors': 2}, "6. TRAMPA: Asesino Silencioso (Cáncer Debutante)"),
    ({'sexe': 'H', 'grup_edat': '80-84', 'cronic': 'PCC', 'diags_totals': 18, 'problemes_salut_cronics': 12, 'farmacs_totals': 14, 'sistema_cardiovascular': 4}, "7. TRAMPA: Anciano Polimedicado Estable"),
    ({'sexe': 'D', 'grup_edat': '40-44', 'cronic': 'MACA', 'diags_totals': 5, 'farmacs_totals': 6, 'sistema_nervios': 4}, "8. TRAMPA: Juventud Paliativa (MACA)"),

    # 11 NUEVOS CASOS (19 en total)
    ({'sexe': 'H', 'grup_edat': '90>', 'cronic': 'MACA', 'diags_totals': 20, 'problemes_salut_cronics': 15, 'farmacs_totals': 18, 'sistema_cardiovascular': 5, 'sistema_nervios': 4}, "9. Final de Vida Evidente (>90a, MACA, 18 meds)"),
    ({'sexe': 'H', 'grup_edat': '35-39', 'cronic': 'NO', 'diags_totals': 0, 'farmacs_totals': 0}, "10. Hombre Joven Sano Invicto (0 diags, 0 meds)"),
    ({'sexe': 'D', 'grup_edat': '60-64', 'cronic': 'NO', 'diags_totals': 5, 'problemes_salut_aguts': 5, 'farmacs_totals': 4, 'antiinfecciosos_per_a_us_sistemic': 3}, "11. Mujer 60a Neumonía Grave (Infección sistémica)"),
    ({'sexe': 'H', 'grup_edat': '55-59', 'cronic': 'PCC', 'diags_totals': 8, 'problemes_salut_cronics': 6, 'farmacs_totals': 7, 'sistema_cardiovascular': 3}, "12. Adulto 55a Infartado (PCC, Cardio meds)"),
    ({'sexe': 'D', 'grup_edat': '85-89', 'cronic': 'PCC', 'diags_totals': 12, 'problemes_salut_cronics': 8, 'farmacs_totals': 3}, "13. Abuela PCC Falsa Alarma (12 diags pero solo 3 meds)"),
    ({'sexe': 'H', 'grup_edat': '45-49', 'cronic': 'NO', 'diags_totals': 3, 'problemes_salut_neoplasia_maligna': 2, 'farmacs_totals': 0}, "14. Cáncer No Tratado (45a, Neoplasia activa, 0 meds)"),
    ({'sexe': 'D', 'grup_edat': '70-74', 'cronic': 'MACA', 'diags_totals': 10, 'problemes_salut_cronics': 8, 'farmacs_totals': 5}, "15. MACA Robusta (70a, MACA pero baja carga farmacológica)"),
    ({'sexe': 'H', 'grup_edat': '80-84', 'cronic': 'NO', 'diags_totals': 4, 'problemes_salut_cronics': 2, 'farmacs_totals': 11, 'sistema_nervios': 5}, "16. Anciano Demencia/Alzheimer (NO cronic pero Alzheimer severo meds nerviosos)"),
    ({'sexe': 'D', 'grup_edat': '25-29', 'cronic': 'MACA', 'diags_totals': 6, 'problemes_salut_neoplasia_maligna': 4, 'farmacs_totals': 8, 'antineoplasics_i_immunomoduladors': 4}, "17. Leucemia Joven (25a, MACA Oncológica Paliativa)"),
    ({'sexe': 'H', 'grup_edat': '75-79', 'cronic': 'PCC', 'diags_totals': 16, 'problemes_salut_cronics': 12, 'farmacs_totals': 20, 'sistema_digestiu_i_metabolisme': 5}, "18. PCC Extremo Metabólico (Diabético severo, 20 meds)"),
    ({'sexe': 'D', 'grup_edat': '65-69', 'cronic': 'NO', 'diags_totals': 2, 'problemes_salut_aguts': 1, 'farmacs_totals': 2}, "19. Jubilada Reciente Sana (65a, 2 meds rutina)")
]

for datos, desc in pacientes_mortalidad:
    predecir_nuevo_paciente(datos, desc)

# ==========================================
# FASE 6: EXPLICABILIDAD
# ==========================================
importancias = modelo_mortalidad.get_feature_importance()
df_importancias = pd.DataFrame({'Variable': X_train.columns, 'Importancia': importancias}).sort_values(by='Importancia', ascending=False)
print("\nRanking Clínico de la IA NATIVA:")
print(df_importancias.head(8).to_string(index=False))
