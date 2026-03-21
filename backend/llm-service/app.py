import os
import json
import logging
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama import Client

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

# CORS Support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama-server:11434")
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
        model_exists = any(m['name'].startswith(MODEL_NAME) for m in models.get('models', []))
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

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IA Médica - Dashboard Predictivo</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4f46e5;
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text: #1e293b;
                --red: #ef4444;
                --green: #22c55e;
            }
            body { font-family: 'Outfit', sans-serif; background-color: var(--bg); color: var(--text); padding: 40px; margin: 0; }
            .container { max-width: 1000px; margin: 0 auto; }
            h1 { font-weight: 600; color: var(--primary); font-size: 2.5rem; margin-bottom: 30px; }
            .card { background: var(--card-bg); padding: 25px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 25px; }
            textarea { width: 100%; height: 120px; border: 2px solid #e2e8f0; border-radius: 12px; padding: 15px; font-size: 16px; box-sizing: border-box; font-family: inherit; }
            button { background: var(--primary); color: white; border: none; padding: 15px 30px; border-radius: 10px; cursor: pointer; font-weight: 600; float: right; margin-top: 15px; transition: transform 0.2s; }
            button:hover { transform: translateY(-2px); }
            .results { display: none; margin-top: 80px; }
            .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
            .risk-card { text-align: center; border-radius: 12px; padding: 20px; color: white; }
            .risk-value { font-size: 2rem; font-weight: 600; }
            .report-box { border-left: 5px solid var(--primary); background: #eff6ff; padding: 20px; font-style: italic; line-height: 1.6; }
            pre { background: #1e293b; color: #f8fafc; padding: 20px; border-radius: 12px; overflow-x: auto; font-size: 14px; }
            .loading { color: var(--primary); font-weight: 600; display: none; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Gestione de Pacientes IA</h1>
            <div class="card">
                <p>Describe el caso clínico del paciente para un análisis completo de riesgos 360°:</p>
                <textarea id="inputText" placeholder="Varón de 89 años, crónico tipo MACA..."></textarea>
                <button onclick="analyze()">Lanzar Análisis Predictivo</button>
                <div id="loading" class="loading">⚙️ La inteligencia artificial está pensando... (aprox. 10s)</div>
            </div>

            <div id="results" class="results">
                <h3>📊 Análisis Predictivo de Riesgos</h3>
                <div class="grid">
                    <div id="mortalityCard" class="risk-card">
                        <div>Riesgo Mortalidad</div>
                        <div id="mortalityVal" class="risk-value">0%</div>
                    </div>
                    <div id="visitasCard" class="risk-card">
                        <div>Frecuentación Urgencias</div>
                        <div id="visitasVal" class="risk-value">0</div>
                    </div>
                    <div id="pccCard" class="risk-card">
                        <div>Perfil Crónico (PCC)</div>
                        <div id="pccVal" class="risk-value">0%</div>
                    </div>
                </div>

                <h3>🩺 Informe Clínico Narrativo</h3>
                <div class="card report-box" id="reportText">Procesando...</div>

                <h3>📑 Datos Médicos Estructurados (JSON)</h3>
                <pre id="jsonResult">{}</pre>
            </div>
        </div>

        <script>
            async function analyze() {
                const text = document.getElementById('inputText').value;
                if (!text) return alert("Escribe algo por favor");
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';

                try {
                    const res = await fetch('/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: text})
                    });
                    const data = await res.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('results').style.display = 'block';
                    
                    // Actualizar Riesgos
                    updateRisk('mortality', data.predictive_analysis.mortalidad_riesgo_anual, 40);
                    updateRisk('visitas', data.predictive_analysis.visitas_urgencias_estimadas_mes, 0.5, true);
                    updateRisk('pcc', data.predictive_analysis.probabilidad_perfil_pcc, 60);
                    
                    document.getElementById('visitasVal').innerText = data.predictive_analysis.visitas_urgencias_estimadas_mes;
                    
                    // Actualizar Informe
                    document.getElementById('reportText').innerText = data.narrative_report;
                    
                    // Actualizar JSON
                    document.getElementById('jsonResult').innerText = JSON.stringify(data.extracted_medical_data, null, 2);

                } catch (e) {
                    alert("Error conectando con el servidor");
                    document.getElementById('loading').style.display = 'none';
                }
            }

            function updateRisk(id, val, threshold, isValue = false) {
                const card = document.getElementById(id + 'Card');
                const valElem = document.getElementById(id + 'Val');
                valElem.innerText = isValue ? val : val + '%';
                card.style.background = val > threshold ? '#ef4444' : '#22c55e';
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "ollama_host": OLLAMA_HOST, 
        "model": MODEL_NAME,
        "trees_engine_ready": tree_engine.is_trained
    }

async def run_extraction(text: str):
    """Lógica entera de extracción via Ollama"""
    prompt = f"""<s>[INST] Eres un extractor de datos médicos profesional. 
    Analiza el texto y devuelve exclusivamente un objeto JSON con estos campos:
    {list(json_template.keys())}
    
    Si no conoces un valor numérico, pon 0. Si no conoces un texto, pon "No indicado".
    
    Texto a analizar: {text} [/INST]</s>"""
    
    response = client.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.1, "num_predict": 800})
    raw_output = response['response']
    
    json_start = raw_output.find('{')
    json_end = raw_output.rfind('}') + 1
    
    if json_start != -1 and json_end != -1:
        json_str = raw_output[json_start:json_end]
        return json.loads(json_str)
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
        return "No se pudo generar el informe narrativo."

@app.post("/report")
async def report_only(prediction_data: dict, medical_data: dict = None):
    return {"report": await run_report_generation(prediction_data, medical_data or {})}

@app.post("/predict")
async def predict_only(medical_data: dict):
    if not tree_engine.is_trained:
        raise HTTPException(status_code=503, detail="Decision trees engine is not yet trained")
    try:
        tree_input = map_llm_json_to_engine(medical_data)
        return await tree_engine.predict_async(tree_input)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

@app.post("/analyze")
async def analyze_full_case(request: ExtractionRequest):
    extracted_data = await run_extraction(request.text)
    if not extracted_data:
        raise HTTPException(status_code=500, detail="LLM Extraction failed")

    try:
        tree_input = map_llm_json_to_engine(extracted_data)
        analysis_results = await tree_engine.predict_async(tree_input)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    narrative_report = await run_report_generation(analysis_results, extracted_data)

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
