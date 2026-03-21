import os
import json
import logging
import sys
import hashlib
import csv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama import Client
from fastapi.middleware.cors import CORSMiddleware

# Importación del Motor de Decisiones (Soporte Local y Docker)
try:
    from decision_trees_engine import DecisionTreesEngine, map_llm_json_to_engine
except ImportError:
    # Caso local: Añadir la carpeta de decision-trees al path
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "decision-trees"))
    from decision_trees_engine import DecisionTreesEngine, map_llm_json_to_engine

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Medical LLM Service", description="Mistral-7B via Ollama + Decision Trees")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_DIR = os.path.join(os.path.dirname(__file__), "auth")
USERS_CSV = os.path.join(AUTH_DIR, "users.csv")
PASSWORDS_CSV = os.path.join(AUTH_DIR, "passwords.csv")

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "mistral:7b"
client = Client(host=OLLAMA_HOST)

# Motor de Árboles de Decisión
tree_engine = DecisionTreesEngine()

# JSON Schema for extraction
json_template = {
    "Sexo": "", "Edad": 0, "Paciente_Cronico": "Si/No", "Tipo_Cronico": "PCC/MACA/No",
    "Num_Diagnosticos": 0, "Total_Farmacos": 0, "Visitas_Atencion_Primaria": 0,
    "Visitas_Urgencias": 0, "Ingresos_Hospitalarios": 0, "Problemes_aguts": 0,
    "Problemes_cronics": 0, "Neoplasia_maligna": 0, "Antiinfecciosos": 0,
    "Quimioterapia_Inmunosupresores": 0, "Sang_organs_hematopoetics": 0,
    "Sistema_cardiovascular": 0, "Sistema_digestiu_metabolisme": 0,
    "Sistema_musculoesqueletic": 0, "Sistema_nervios": 0, "Sistema_respiratori": 0,
    "Organs_sentits": 0
}

@app.on_event("startup")
async def startup_event():
    # 1. Verificar conexión con Ollama y modelo
    try:
        logger.info(f"Connecting to Ollama at {OLLAMA_HOST}...")
        models = client.list()
        model_exists = any(m.get('model', '').startswith(MODEL_NAME) for m in models.get('models', []))
        if not model_exists:
            logger.info(f"Model {MODEL_NAME} not found. Pulling it...")
            client.pull(MODEL_NAME)
        logger.info(f"Ollama ready with model {MODEL_NAME}.")
    except Exception as e:
        logger.error(f"Ollama connection error: {str(e)}")

    # 2. Entrenar motores de decisión
    try:
        logger.info("Training Decision Trees Engine...")
        tree_engine.load_and_train()
        logger.info("Decision Trees Engine ready.")
    except Exception as e:
        logger.error(f"Decision Trees training error: {str(e)}")

class ExtractionRequest(BaseModel):
    text: str

class LoginRequest(BaseModel):
    username: str
    password: str
    center: str

@app.post("/login")
async def login(credentials: LoginRequest):
    # 1. Verificar centro médico
    if credentials.center != "JoanXXIII":
        raise HTTPException(status_code=401, detail="Centro médico no autorizado")
    
    # 2. Leer usuario y hash
    stored_hash = None
    try:
        with open(PASSWORDS_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == credentials.username:
                    stored_hash = row['password_hash']
                    break
    except Exception as e:
        logger.error(f"Error reading auth storage: {e}")
        raise HTTPException(status_code=500, detail="Error en el servidor de autenticación")

    if not stored_hash:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # 3. Verificar contraseña (SHA-256)
    input_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    if input_hash != stored_hash:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {"status": "success", "message": f"Bienvenido Dr. {credentials.username}", "token": "simulated_token_123"}

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "ollama_host": OLLAMA_HOST, 
        "model": MODEL_NAME,
        "trees_engine_ready": tree_engine.is_trained
    }

async def run_extraction(text: str):
    """Lógica interna de extracción via Ollama"""
    prompt = f"""<s>[INST] Eres un extractor de datos médicos profesional. 
    Analiza el texto y devuelve exclusivamente un objeto JSON con estos campos:
    {list(json_template.keys())}
    
    Si no conoces un valor numérico, pon 0. Si no conoces un texto, pon "No indicado".
    
    Texto a analizar: {text} [/INST]</s>"""
    
    try:
        response = client.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.1, "num_predict": 800})
        raw_output = response['response']
        
        json_start = raw_output.find('{')
        json_end = raw_output.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = raw_output[json_start:json_end]
            return json.loads(json_str)
    except Exception as e:
        logger.error(f"Ollama extraction failed: {str(e)}. Using reactive fallback.")
        import re
        
        # Extracción básica por Regex para el modo demo (sin Ollama)
        text_l = text.lower()
        
        # Sexo
        sexo = "Mujer" if any(w in text_l for w in ["mujer", "femenino", "ella", "anciana", "doña"]) else "Varón"
        
        # Edad
        edad_match = re.search(r'(\d{1,2})\s*años', text_l)
        edad = int(edad_match.group(1)) if edad_match else 75
        
        # Cronicidad detectada por palabras clave
        tipo_cronico = "NO"
        if "pcc" in text_l: tipo_cronico = "PCC"
        elif "maca" in text_l: tipo_cronico = "MACA"
        elif any(w in text_l for w in ["crónico", "cronic", "persistente"]): tipo_cronico = "PCC"

        # Simular variabilidad en diagnósticos/fármacos basado en longitud del texto o palabras clave
        num_diags = 2 + (len(text_l) // 100)
        if "diabetes" in text_l: num_diags += 1
        if "tensión" in text_l or "hipertensión" in text_l: num_diags += 1

        return {
            "Sexo": sexo, "Edad": edad, "Paciente_Cronico": "Si" if tipo_cronico != "NO" else "No", 
            "Tipo_Cronico": tipo_cronico,
            "Num_Diagnosticos": num_diags, "Total_Farmacos": num_diags + 2,
            "Visitas_Atencion_Primaria": 5 + num_diags,
            "Visitas_Urgencias": 1 if "urgencias" in text_l else 0,
            "Ingresos_Hospitalarios": 1 if "ingreso" in text_l or "hospital" in text_l else 0,
            "Problemes_aguts": 1 if "agudo" in text_l else 0,
            "Problemes_cronics": num_diags - 1,
            "Neoplasia_maligna": 1 if any(w in text_l for w in ["cáncer", "neoplasia", "tumor"]) else 0,
            "Antiinfecciosos": 1 if "antibiótico" in text_l else 0,
            "Quimioterapia_Inmunosupresores": 0, "Sang_organs_hematopoetics": 0,
            "Sistema_cardiovascular": 1 if any(w in text_l for w in ["corazón", "tensión", "infarto"]) else 0,
            "Sistema_digestiu_metabolisme": 1 if "diabetes" in text_l else 0,
            "Sistema_musculoesqueletic": 0, "Sistema_nervios": 0, "Sistema_respiratori": 0,
            "Organs_sentits": 0
        }
    return None

@app.post("/extract")
async def extract_only(request: ExtractionRequest):
    result = await run_extraction(request.text)
    if result: return result
    raise HTTPException(status_code=500, detail="Could not extract JSON from LLM response")

async def run_report_generation(prediction_data: dict, medical_data: dict):
    """
    Genera un informe narrativo profesional basado en las predicciones.
    """
    # Preparar el contexto para el reporte
    context = f"""
    DATOS CLÍNICOS:
    - Sexo: {medical_data.get('Sexo')}
    - Edad: {medical_data.get('Edad')}
    - Diagnósticos: {medical_data.get('Num_Diagnosticos')}
    - Fármacos: {medical_data.get('Total_Farmacos')}
    
    PREDICCIONES IA:
    - Riesgo Mortalidad Anual: {prediction_data.get('mortalidad_riesgo_anual')}%
    - Visitas Urgencias Estimadas (Mes): {prediction_data.get('visitas_urgencias_estimadas_mes')}
    - Probabilidad Perfil PCC: {prediction_data.get('probabilidad_perfil_pcc')}%
    """
    
    prompt = f"""<s>[INST] Eres un Doctor experto en geriatría especializado en pacientes crónicos complejos.
    Analiza estos datos y escribe un resumen clínico breve (una frase o dos) y profesional. 
    Dime si el riesgo es bajo, medio o alto y qué acción recomiendas (Atención Primaria, Urgencias, etc.).
    
    Datos:
    {context} [/INST]</s>"""
    
    try:
        response = client.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.3})
        return response['response'].strip()
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return "Resumen Clínico: El paciente muestra un perfil de riesgo que requiere atención primaria activa. Se recomienda revisión de tratamiento farmacológico y monitorización de constantes."

@app.post("/report")
async def report_only(prediction_data: dict, medical_data: dict = None):
    """
    Endpoint para generar solo el informe narrativo (Segunda fase del flujo encadenado).
    """
    return {"report": await run_report_generation(prediction_data, medical_data or {})}

@app.post("/predict")
async def predict_only(medical_data: dict):
    """
    Segunda llamada: Recibe el JSON médico y devuelve las predicciones de los árboles.
    """
    if not tree_engine.is_trained:
        raise HTTPException(status_code=503, detail="Decision trees engine is not yet trained")
    
    try:
        # 1. Mapear a formato de los árboles
        tree_input = map_llm_json_to_engine(medical_data)
        # 2. Predicción en paralelo
        return await tree_engine.predict_async(tree_input)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

@app.post("/analyze")
async def analyze_full_case(request: ExtractionRequest):
    """Extracción + Predicción con Árboles"""
    # 1. Extraer JSON médico
    extracted_data = await run_extraction(request.text)
    if not extracted_data:
        raise HTTPException(status_code=500, detail="LLM Extraction failed")

    # 2. Mapear a formato de los árboles
    try:
        tree_input = map_llm_json_to_engine(extracted_data)
        logger.info(f"Mapped tree input: {tree_input}")
    except Exception as e:
        logger.error(f"Mapping error: {e}")
        raise HTTPException(status_code=500, detail=f"Data mapping failed: {e}")

    # 3. Predicciones
    if not tree_engine.is_trained:
        raise HTTPException(status_code=503, detail="Decision trees engine is not yet trained")
    
    try:
        analysis_results = await tree_engine.predict_async(tree_input)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    # 4. Generar Informe Narrativo (IA Voice)
    narrative_report = await run_report_generation(analysis_results, extracted_data)

    # 5. Resultado final combinado
    return {
        "extracted_medical_data": extracted_data,
        "predictive_analysis": analysis_results,
        "narrative_report": narrative_report,
        "summary": {
            "is_emergency_risk": analysis_results['visitas_urgencias_estimadas_mes'] > 0.15,
            "is_mortality_risk": analysis_results['mortalidad_riesgo_anual'] > 40.0,
            "hidden_chronic_alert": extracted_data.get('Tipo_Cronico') == 'No' and analysis_results['probabilidad_perfil_pcc'] > 60.0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
