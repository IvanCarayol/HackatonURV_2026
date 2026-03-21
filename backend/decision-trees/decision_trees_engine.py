import os
import asyncio
import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, CatBoostRegressor
from sklearn.model_selection import train_test_split

class DecisionTreesEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "Database")
        self.models = {}
        self.is_trained = False
        self.feature_columns = {} # Store columns expected by each model

    def load_and_train(self):
        print("🚀 [Engine] Iniciando entrenamiento de los 3 modelos de decisión...")
        
        # 1. Cargar Datos
        try:
            cohort = pd.read_csv(os.path.join(self.data_dir, "hackato_cohort.csv"))
            diagnostics = pd.read_csv(os.path.join(self.data_dir, "hackato_diagnostics.csv"))
            farmacs = pd.read_csv(os.path.join(self.data_dir, "hackato_farmacs.csv"))
            urgencies = pd.read_csv(os.path.join(self.data_dir, "hackato_visites_urgencies.csv"))
            visites_hospital = pd.read_csv(os.path.join(self.data_dir, "hackato_visites_hospital.csv"))
            visites_primaria = pd.read_csv(os.path.join(self.data_dir, "hackato_visites_primaria.csv"))
        except Exception as e:
            print(f"❌ Error cargando base de datos: {e}")
            return False

        # --- PREPARACIÓN COMÚN ---
        df_base = cohort.merge(diagnostics, on="id_pacient", how="left")
        df_base = df_base.merge(farmacs, on="id_pacient", how="left")
        
        # Conteo de asistencias
        conteo_urg = urgencies.groupby('id_pacient').size().reset_index(name='total_urg')
        conteo_hosp = visites_hospital.groupby('id_pacient').size().reset_index(name='total_hosp')
        conteo_prim = visites_primaria.groupby('id_pacient')['visites'].sum().reset_index(name='total_prim')
        
        df_base = df_base.merge(conteo_urg, on='id_pacient', how='left')
        df_base = df_base.merge(conteo_hosp, on='id_pacient', how='left')
        df_base = df_base.merge(conteo_prim, on='id_pacient', how='left')
        df_base = df_base.fillna(0)

        for col in ['sexe', 'grup_edat', 'cronic']:
            df_base[col] = df_base[col].astype(str)

        # ------------------------------------------
        # MODELO 1: MORTALIDAD (ARBOLEDAD)
        # ------------------------------------------
        df_mort = df_base.copy()
        df_mort['TARGET'] = df_mort['situacio'].apply(lambda x: 1 if x == 'D' else 0)
        X_m = df_mort.drop(columns=['id_pacient', 'situacio', 'TARGET', 'total_urg', 'total_hosp', 'total_prim'])
        y_m = df_mort['TARGET']
        
        # allow_writing_files=False para evitar catboost_info
        self.models['mortalidad'] = CatBoostClassifier(iterations=200, depth=6, learning_rate=0.1, verbose=0, allow_writing_files=False, cat_features=['sexe', 'grup_edat', 'cronic'])
        self.models['mortalidad'].fit(X_m, y_m)
        self.feature_columns['mortalidad'] = X_m.columns.tolist()

        # ------------------------------------------
        # MODELO 2: VISITAS / DEMANDA (ARBOLVISITA)
        # ------------------------------------------
        df_vis = df_base[df_base['cronic'].isin(['PCC', 'MACA'])].copy()
        X_v = df_vis.drop(columns=['id_pacient', 'situacio', 'total_urg'])
        y_v = df_vis['total_urg']
        
        self.models['visitas'] = CatBoostRegressor(iterations=200, depth=5, learning_rate=0.1, verbose=0, allow_writing_files=False, cat_features=['sexe', 'grup_edat', 'cronic'])
        self.models['visitas'].fit(X_v, y_v)
        self.feature_columns['visitas'] = X_v.columns.tolist()

        # ------------------------------------------
        # MODELO 3: DETECTOR PCC (DETECTARPCC)
        # ------------------------------------------
        df_pcc = df_base[df_base['cronic'].isin(['PCC', 'NO'])].copy()
        df_pcc['TARGET'] = df_pcc['cronic'].apply(lambda x: 1 if x == 'PCC' else 0)
        X_p = df_pcc.drop(columns=['id_pacient', 'situacio', 'cronic', 'TARGET'])
        y_p = df_pcc['TARGET']
        
        self.models['pcc'] = CatBoostClassifier(iterations=200, depth=6, learning_rate=0.1, verbose=0, allow_writing_files=False, cat_features=['sexe', 'grup_edat'])
        self.models['pcc'].fit(X_p, y_p)
        self.feature_columns['pcc'] = X_p.columns.tolist()

        self.is_trained = True
        print("✅ [Engine] Todos los modelos entrenados en paralelo y listos.")
        return True

    async def predict_async(self, patient_data_dict):
        """
        Ejecuta las 3 predicciones EN PARALELO usando asyncio.to_thread
        """
        if not self.is_trained:
            return {"error": "Modelos no entrenados"}

        df_input = pd.DataFrame([patient_data_dict])
        
        # Preparación previa (común)
        all_cols = set(self.feature_columns['mortalidad'] + self.feature_columns['visitas'] + self.feature_columns['pcc'])
        for col in all_cols:
            if col not in df_input.columns:
                df_input[col] = 0

        # Disparar predicciones en paralelo
        print("⚡ [Engine] Procesando predicciones en paralelo...")
        res_mortalidad, res_visitas, res_pcc = await asyncio.gather(
            asyncio.to_thread(self._predict_mortalidad, df_input),
            asyncio.to_thread(self._predict_visitas, df_input),
            asyncio.to_thread(self._predict_pcc, df_input)
        )

        return {
            "mortalidad_riesgo_anual": res_mortalidad,
            "visitas_urgencias_estimadas_mes": res_visitas,
            "probabilidad_perfil_pcc": res_pcc
        }

    # Métodos privados para ejecuciones segregadas en hilos
    def _predict_mortalidad(self, df):
        cols = self.feature_columns['mortalidad']
        return round(float(self.models['mortalidad'].predict_proba(df[cols])[0][1]) * 100, 2)

    def _predict_visitas(self, df):
        cols = self.feature_columns['visitas']
        return round(float(self.models['visitas'].predict(df[cols])[0]), 2)

    def _predict_pcc(self, df):
        cols = self.feature_columns['pcc']
        return round(float(self.models['pcc'].predict_proba(df[cols])[0][1]) * 100, 2)

def clean_int(val):
    """
    Asegura que el valor sea un entero. Maneja casos donde el LLM devuelve 
    una lista de strings (ej: ["Insuficiencia cardíaca"]) o strings extraños.
    """
    if isinstance(val, list):
        return len(val) # Interpretamos la lista de enfermedades como recuento
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        # Intentar convertir texto numérico
        try:
            return int(float(val))
        except (ValueError, TypeError):
            # Si es un texto no numérico pero no es negativo ("No", "None"),
            # asumimos que es una descripción y cuenta como 1 ocurrencia.
            clean_val = val.strip().lower()
            if clean_val in ["no", "none", "no indicado", "no indicat", "0", "false"]:
                return 0
            return 1 # Si hay texto descriptivo, es que hay al menos 1 problema
    return 0

def map_llm_json_to_engine(llm_data):
    """
    Traduce el JSON del LLM al formato que esperan los árboles, 
    limpiando tipos de datos inesperados.
    """
    def get_grup_edat(edad_input):
        try:
            e = clean_int(edad_input)
            if e >= 90: return "90>"
            low = (e // 5) * 5
            return f"{low}-{low+4}"
        except: return "Desconegut"

    mapped = {
        "sexe": "H" if str(llm_data.get("Sexo", "")).lower() in ["varón", "hombre", "h", "varon"] else "D",
        "grup_edat": get_grup_edat(llm_data.get("Edad", 0)),
        "cronic": llm_data.get("Tipo_Cronico", "NO"),
        "diags_totals": clean_int(llm_data.get("Num_Diagnosticos", 0)),
        "farmacs_totals": clean_int(llm_data.get("Total_Farmacos", 0)),
        "problemes_salut_aguts": clean_int(llm_data.get("Problemes_aguts", 0)),
        "problemes_salut_cronics": clean_int(llm_data.get("Problemes_cronics", 0)),
        "problemes_salut_neoplasia_maligna": clean_int(llm_data.get("Neoplasia_maligna", 0)),
        "antiinfecciosos_per_a_us_sistemic": clean_int(llm_data.get("Antiinfecciosos", 0)),
        "antineoplasics_i_immunomoduladors": clean_int(llm_data.get("Quimioterapia_Inmunosupresores", 0)),
        "sang_i_organs_hematopoetics": clean_int(llm_data.get("Sang_organs_hematopoetics", 0)),
        "sistema_cardiovascular": clean_int(llm_data.get("Sistema_cardiovascular", 0)),
        "sistema_digestiu_i_metabolisme": clean_int(llm_data.get("Sistema_digestiu_metabolisme", 0)),
        "sistema_musculoesqueletic": clean_int(llm_data.get("Sistema_musculoesqueletic", 0)),
        "sistema_nervios": clean_int(llm_data.get("Sistema_nervios", 0)),
        "sistema_respiratori": clean_int(llm_data.get("Sistema_respiratori", 0)),
        "organs_dels_sentits": clean_int(llm_data.get("Organs_sentits", 0)),
        "total_prim": clean_int(llm_data.get("Visitas_Atencion_Primaria", 0)),
        "total_hosp": clean_int(llm_data.get("Ingresos_Hospitalarios", 0))
    }
    
    # Limpieza de Tipo_Cronico
    cronic_raw = str(mapped['cronic']).upper()
    if "PCC" in cronic_raw: mapped['cronic'] = 'PCC'
    elif "MACA" in cronic_raw: mapped['cronic'] = 'MACA'
    else: mapped['cronic'] = 'NO'

    return mapped
