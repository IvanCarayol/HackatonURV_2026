import pandas as pd
from catboost import CatBoostRegressor
import optuna
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np

print("1. Cargando datos para el Modelo de Previsión de Demanda...")
cohort = pd.read_csv("hackato_cohort.csv")
diagnostics = pd.read_csv("hackato_diagnostics.csv")
farmacs = pd.read_csv("hackato_farmacs.csv")
urgencies = pd.read_csv("hackato_visites_urgencies.csv")
visites_hospital = pd.read_csv("hackato_visites_hospital.csv")
visites_primaria = pd.read_csv("hackato_visites_primaria.csv")

# ==========================================
# FASE 1: FILTRADO DE PACIENTES (PCC y MACA)
# ==========================================
cohort_cronicos = cohort[cohort['cronic'].isin(['PCC', 'MACA'])].copy()

# ==========================================
# FASE 2: EL TARGET (Número de visitas futuras DÍA > 335)
# ==========================================
urgencies_futuro = urgencies[urgencies['data'] > 335]
conteo_futuro = urgencies_futuro.groupby('id_pacient').size().reset_index(name='TARGET_num_visitas_mes')

df_modelo2 = cohort_cronicos.merge(conteo_futuro, on='id_pacient', how='left')
df_modelo2['TARGET_num_visitas_mes'] = df_modelo2['TARGET_num_visitas_mes'].fillna(0)

urgencies_pasado = urgencies[urgencies['data'] <= 335]
conteo_urg_pasado = urgencies_pasado.groupby('id_pacient').size().reset_index(name='historial_urgencies_previes')

hospital_pasado = visites_hospital[visites_hospital['data'] <= 335]
conteo_hosp_pasado = hospital_pasado.groupby('id_pacient').size().reset_index(name='hospitalitzacions_previes')

conteo_primaria = visites_primaria.groupby('id_pacient')['visites'].sum().reset_index(name='total_visites_primaria')

# ==========================================
# FASE 3: ENSAMBLAR MATRIZ MAESTRA Y FEATURE ENGINEERING
# ==========================================
df_modelo2 = df_modelo2.merge(conteo_urg_pasado, on='id_pacient', how='left')
df_modelo2 = df_modelo2.merge(conteo_hosp_pasado, on='id_pacient', how='left')
df_modelo2 = df_modelo2.merge(conteo_primaria, on='id_pacient', how='left')
df_modelo2 = df_modelo2.merge(diagnostics, on='id_pacient', how='left')
df_modelo2 = df_modelo2.merge(farmacs, on='id_pacient', how='left')
df_modelo2 = df_modelo2.fillna(0)

for col in ['sexe', 'grup_edat', 'cronic']:
    df_modelo2[col] = df_modelo2[col].astype(str)

print("\n-> Aplicando Feature Engineering Clínico para Previsión de Demanda...")
df_modelo2['carga_asistencial_pasada'] = df_modelo2['historial_urgencies_previes'] + df_modelo2['hospitalitzacions_previes'] + df_modelo2['total_visites_primaria']
df_modelo2['ratio_ingresos_urgencias'] = df_modelo2['hospitalitzacions_previes'] / (df_modelo2['historial_urgencies_previes'] + 1)
df_modelo2['alerta_polimedicacion'] = (df_modelo2['farmacs_totals'] > 10).astype(int)
df_modelo2['infeccion_reciente_grave'] = ((df_modelo2.get('antiinfecciosos_per_a_us_sistemic', 0) > 0) & (df_modelo2['hospitalitzacions_previes'] > 0)).astype(int)

# ==========================================
# FASE 4: ENTRENAMIENTO CATBOOST (TWEEDIE) + OPTUNA
# ==========================================
print("\n2. Entrenando la red predictiva de volumen (CatBoost Tweedie nativo)...")

X = df_modelo2.drop(columns=['id_pacient', 'situacio', 'TARGET_num_visitas_mes'])
Y = df_modelo2['TARGET_num_visitas_mes']

cat_features = ['sexe', 'grup_edat', 'cronic']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=42)

print("\n--- INICIANDO OPTUNA CON CATBOOST (TWEEDIE REGRESSION) ---")
def objective(trial):
    params = {
        'iterations': trial.suggest_int('iterations', 100, 300),
        'depth': trial.suggest_int('depth', 3, 7),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
        'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1.0, 10.0),
        'loss_function': 'Tweedie:variance_power=1.5',
        'cat_features': cat_features,
        'verbose': 0,
        'random_seed': 42
    }
    
    cv = KFold(n_splits=3, shuffle=True, random_state=42)
    mae_scores = []
    
    for train_idx, val_idx in cv.split(X_train):
        X_train_cv, X_val_cv = X_train.iloc[train_idx], X_train.iloc[val_idx]
        Y_train_cv, Y_val_cv = Y_train.iloc[train_idx], Y_train.iloc[val_idx]
        
        model = CatBoostRegressor(**params)
        model.fit(X_train_cv, Y_train_cv)
        
        preds = model.predict(X_val_cv)
        preds = np.clip(preds, 0, None)
        mae = mean_absolute_error(Y_val_cv, preds)
        mae_scores.append(mae)
        
    return np.mean(mae_scores)

optuna.logging.set_verbosity(optuna.logging.WARNING)
study = optuna.create_study(direction='minimize')
print("Optimizando hiperparámetros de demanda (10 configuraciones)...")
study.optimize(objective, n_trials=10)

mejores_params = study.best_params
mejores_params['loss_function'] = 'Tweedie:variance_power=1.5'
mejores_params['cat_features'] = cat_features
mejores_params['random_seed'] = 42
mejores_params['verbose'] = 0

print("\nReentrenando CatBoostRegressor de demanda definitivo...")
modelo_volumen = CatBoostRegressor(**mejores_params)
modelo_volumen.fit(X_train, Y_train)

# ==========================================
# FASE 5: EVALUACIÓN Y GESTIÓN DE CAMAS
# ==========================================
print("\n--- RESULTADOS: PREVISIÓN DE DEMANDA A 1 MES ---")
predicciones_brutas = modelo_volumen.predict(X_test)
predicciones_brutas = np.clip(predicciones_brutas, 0, None)

mae = mean_absolute_error(Y_test, predicciones_brutas)
print(f"Error Absoluto Medio (MAE): {mae:.3f} visitas por paciente")

# ==========================================
# FASE 6: SIMULADOR DE PACIENTES
# ==========================================
print("\n" + "="*50)
print("INICIANDO SIMULADOR: PREVISIÓN DE VISITAS A URGENCIAS (NATIVO)")
print("="*50)

def predecir_volumen_paciente(datos_paciente_dict, desc=""):
    print(f"\n--- TEST: {desc} ---")
    
    df_nuevo = pd.DataFrame([datos_paciente_dict])
    
    h_urg = df_nuevo.get('historial_urgencies_previes', pd.Series([0]))[0]
    h_hosp = df_nuevo.get('hospitalitzacions_previes', pd.Series([0]))[0]
    h_prim = df_nuevo.get('total_visites_primaria', pd.Series([0]))[0]
    farmacs_t = df_nuevo.get('farmacs_totals', pd.Series([0]))[0]
    
    df_nuevo['carga_asistencial_pasada'] = h_urg + h_hosp + h_prim
    df_nuevo['ratio_ingresos_urgencias'] = h_hosp / (h_urg + 1)
    df_nuevo['alerta_polimedicacion'] = int(farmacs_t > 10)
    df_nuevo['infeccion_reciente_grave'] = int((df_nuevo.get('antiinfecciosos_per_a_us_sistemic', pd.Series([0]))[0] > 0) and (h_hosp > 0))

    for col in X.columns:
        if col not in df_nuevo:
            if col in cat_features:
                df_nuevo[col] = 'Desconegut'
            else:
                df_nuevo[col] = 0
                
    df_nuevo = df_nuevo[X.columns]
    
    visitas_esperadas = max(0, modelo_volumen.predict(df_nuevo)[0])
    
    print(f"Visitas esperadas en los próximos 30 días: {visitas_esperadas:.3f}")
    if visitas_esperadas >= 0.25:
        print("🚨 ALERTA ROJA: Hiperfrecuentador inminente (>25% prob). Ingreso muy probable.")
    elif visitas_esperadas >= 0.12:
        print("⚠️ ALERTA AMARILLA: Alto riesgo de descompensación (>12% prob). Llamar desde Primaria.")
    else:
        print("✅ Paciente Crónico Estable: Riesgo basal.")

# ---------------------------------------------------------
# CASOS DE PRUEBA (19 PERFILES DE DEMANDA HOSPITALARIA)
# ---------------------------------------------------------
pacientes_visitas = [
    # LOS ORIGINALES
    ({'cronic': 'MACA', 'sexe': 'H', 'grup_edat': '85-89', 'diags_totals': 22, 'farmacs_totals': 18, 'historial_urgencies_previes': 12, 'hospitalitzacions_previes': 4, 'total_visites_primaria': 45, 'antiinfecciosos_per_a_us_sistemic': 3, 'sistema_respiratori': 3}, "1. MACA Crítico (18 meds, 12 urgencias, 4 ingresos)"),
    ({'cronic': 'PCC', 'sexe': 'H', 'grup_edat': '75-79', 'diags_totals': 8, 'farmacs_totals': 6, 'historial_urgencies_previes': 0, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 4}, "2. PCC Estable (0 ingresos previos)"),
    ({'cronic': 'MACA', 'sexe': 'D', 'grup_edat': '85-89', 'diags_totals': 15, 'farmacs_totals': 12, 'historial_urgencies_previes': 5, 'hospitalitzacions_previes': 2, 'total_visites_primaria': 10}, "3. MACA Puerta Giratoria (5 urgencias, 2 ingresos)"),
    ({'cronic': 'PCC', 'sexe': 'H', 'grup_edat': '80-84', 'diags_totals': 10, 'farmacs_totals': 8, 'historial_urgencies_previes': 0, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 25}, "4. PCC Descompensado Primaria (25 visitas ambulatorio)"),
    ({'cronic': 'PCC', 'sexe': 'D', 'grup_edat': '70-74', 'diags_totals': 6, 'farmacs_totals': 5, 'antiinfecciosos_per_a_us_sistemic': 2, 'historial_urgencies_previes': 1, 'hospitalitzacions_previes': 1, 'total_visites_primaria': 5}, "5. PCC con Infección Reciente (Antibióticos e Ingreso)"),

    # 14 NUEVOS CASOS
    ({'cronic': 'PCC', 'sexe': 'H', 'grup_edat': '65-69', 'diags_totals': 5, 'farmacs_totals': 3, 'historial_urgencies_previes': 0, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 1}, "6. PCC Reciente Diagnóstico (65a, Aislado, 1 visita)"),
    ({'cronic': 'MACA', 'sexe': 'D', 'grup_edat': '90>', 'diags_totals': 12, 'farmacs_totals': 15, 'historial_urgencies_previes': 2, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 12, 'sistema_respiratori': 2}, "7. MACA EPOC Avanzado (90a, 2 urgencias asma/epoc)"),
    ({'cronic': 'PCC', 'sexe': 'H', 'grup_edat': '75-79', 'diags_totals': 9, 'farmacs_totals': 11, 'historial_urgencies_previes': 8, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 8}, "8. PCC Ansioso (Hiperfrecuentador de Urgencias leves, 8 urg sin ingreso)"),
    ({'cronic': 'MACA', 'sexe': 'H', 'grup_edat': '50-54', 'diags_totals': 7, 'farmacs_totals': 6, 'historial_urgencies_previes': 1, 'hospitalitzacions_previes': 3, 'total_visites_primaria': 2, 'antiinfecciosos_per_a_us_sistemic': 4}, "9. MACA Joven Sepsis Repetitiva (50a, 3 ingresos, 4 antibióticos)"),
    ({'cronic': 'PCC', 'sexe': 'D', 'grup_edat': '80-84', 'diags_totals': 14, 'farmacs_totals': 10, 'historial_urgencies_previes': 15, 'hospitalitzacions_previes': 5, 'total_visites_primaria': 30}, "10. PCC Tormenta Perfecta (15 urg, 5 ingresos, 30 primarias)"),
    ({'cronic': 'MACA', 'sexe': 'D', 'grup_edat': '85-89', 'diags_totals': 10, 'farmacs_totals': 7, 'historial_urgencies_previes': 0, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 0}, "11. MACA Fantasma Remoto (85a, 0 visitas totales médicas)"),
    ({'cronic': 'PCC', 'sexe': 'H', 'grup_edat': '70-74', 'diags_totals': 6, 'farmacs_totals': 4, 'historial_urgencies_previes': 2, 'hospitalitzacions_previes': 2, 'total_visites_primaria': 5}, "12. PCC Ingreso Seguro (70a, 2 urg -> 2 ingresos directos)"),
    ({'cronic': 'MACA', 'sexe': 'H', 'grup_edat': '90>', 'diags_totals': 18, 'farmacs_totals': 14, 'historial_urgencies_previes': 6, 'hospitalitzacions_previes': 1, 'total_visites_primaria': 22, 'sistema_respiratori': 4}, "13. MACA Gran Dependiente Respiratorio (90a, 6 urgencias)"),
    ({'cronic': 'PCC', 'sexe': 'D', 'grup_edat': '60-64', 'diags_totals': 8, 'farmacs_totals': 12, 'historial_urgencies_previes': 1, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 18}, "14. PCC Polimedicada Ambulatoria (60a, 12 meds, 18 primarias)"),
    ({'cronic': 'MACA', 'sexe': 'D', 'grup_edat': '75-79', 'diags_totals': 11, 'farmacs_totals': 8, 'historial_urgencies_previes': 4, 'hospitalitzacions_previes': 4, 'total_visites_primaria': 6, 'antiinfecciosos_per_a_us_sistemic': 5}, "15. MACA Infecciones Hospitalarias (4 urg = 4 ingresos, 4 antibióticos)"),
    ({'cronic': 'PCC', 'sexe': 'H', 'grup_edat': '85-89', 'diags_totals': 12, 'farmacs_totals': 9, 'historial_urgencies_previes': 10, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 2}, "16. PCC Usa Urgencias como CAP (10 urgencias leves, 0 ingresos)"),
    ({'cronic': 'MACA', 'sexe': 'H', 'grup_edat': '40-44', 'diags_totals': 6, 'farmacs_totals': 6, 'historial_urgencies_previes': 3, 'hospitalitzacions_previes': 1, 'total_visites_primaria': 15}, "17. MACA Joven Degenerativo (40a, 1 ingreso, 15 primarias)"),
    ({'cronic': 'PCC', 'sexe': 'D', 'grup_edat': '80-84', 'diags_totals': 7, 'farmacs_totals': 5, 'historial_urgencies_previes': 1, 'hospitalitzacions_previes': 0, 'total_visites_primaria': 50}, "18. PCC Extremo Primaria (80a, Miedo al hospital, 50 visitas CAP)"),
    ({'cronic': 'MACA', 'sexe': 'H', 'grup_edat': '90>', 'diags_totals': 25, 'farmacs_totals': 20, 'historial_urgencies_previes': 15, 'hospitalitzacions_previes': 8, 'total_visites_primaria': 30, 'antiinfecciosos_per_a_us_sistemic': 6, 'sistema_respiratori': 5}, "19. MACA Colapso Sistémico Multi-Órgano (20 meds, 8 ingresos, 15 urgencias)")
]

for datos, desc in pacientes_visitas:
    predecir_volumen_paciente(datos, desc)