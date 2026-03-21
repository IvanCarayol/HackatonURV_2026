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
        # El campo correcto en versiones recientes es 'model', no 'name'
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

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IA Médica - Dashboard Predictivo 360°</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4f46e5;
                --bg: #f1f5f9;
                --card-bg: #ffffff;
                --text: #0f172a;
                --accent: #6366f1;
            }
            body { font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .header { grid-column: span 2; display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
            .header h1 { color: var(--primary); margin: 0; font-size: 2rem; }
            .card { background: var(--card-bg); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            textarea { width: 100%; height: 120px; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 12px; font-family: inherit; font-size: 15px; margin-top: 10px; }
            .btn { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; margin-top: 10px; transition: 0.2s; width: 100%; }
            .btn:hover { background: var(--accent); }
            .btn-all { background: #1e293b; padding: 15px; font-size: 16px; margin-bottom: 10px; }
            .btn-step { background: #fff; color: var(--primary); border: 2px solid var(--primary); margin-top: 8px; }
            .btn-step:hover { background: #f5f3ff; }
            
            .grid-risks { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 20px; }
            .risk-card { padding: 15px; border-radius: 10px; text-align: center; color: white; transition: 0.3s; }
            .risk-val { font-size: 1.8rem; font-weight: 600; margin-top: 5px; }
            .risk-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; }

            pre { background: #1e293b; color: #f8fafc; padding: 15px; border-radius: 8px; overflow: auto; height: 300px; font-size: 12px; }
            .report-box { background: #eff6ff; border-left: 4px solid var(--primary); padding: 15px; margin-top: 20px; line-height: 1.5; font-style: italic; min-height: 60px; }
            .loading { color: var(--primary); font-weight: 600; font-size: 13px; margin: 10px 0; display: none; text-align: center; }
            
            .step-title { font-weight: 600; font-size: 14px; margin-top: 15px; display: block; color: #475569; }
            .editable-json { width: 100%; height: 350px; background: #272822; color: #f8f8f2; border: none; padding: 10px; font-family: 'Courier New', monospace; border-radius: 8px; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 AI Healthcare Dashboard</h1>
                <div id="status" style="font-size: 12px; color: #64748b;">🟢 Ollama Ready | 🟢 Engines Loaded</div>
            </div>

            <!-- Columna Izquierda: Entrada e Informe -->
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div class="card">
                    <span class="step-title">ENTRADA DE TEXTO NATURAL</span>
                    <textarea id="inputText" placeholder="Varón de 89 años, crónico tipo MACA con insuficiencia cardíaca. Toma 20 fármacos..."></textarea>
                    
                    <button class="btn btn-all" onclick="fullFlow()">🚀 Lanzar Análisis Completo (End-to-End)</button>
                    <div id="loading" class="loading">⚙️ Procesando análisis integral...</div>
                </div>

                <div class="card">
                    <span class="step-title">🩺 INFORME NARRATIVO DEL DR. IA (LLM-REPORT)</span>
                    <div id="reportText" class="report-box">A la espera de resultados...</div>
                    
                    <div class="grid-risks">
                        <div id="risk_m" class="risk-card" style="background: #94a3b8;"><div class="risk-label">Mortalidad</div><div id="val_m" class="risk-val">--%</div></div>
                        <div id="risk_v" class="risk-card" style="background: #94a3b8;"><div class="risk-label">Visitas</div><div id="val_v" class="risk-val">--</div></div>
                        <div id="risk_p" class="risk-card" style="background: #94a3b8;"><div class="risk-label">Perfil PCC</div><div id="val_p" class="risk-val">--%</div></div>
                    </div>
                </div>
            </div>

            <!-- Columna Derecha: Flujo Secuencial / JSON -->
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div class="card">
                    <span class="step-title">🧪 PANEL DE DESARROLLADOR: FLUJO POR ENDPOINTS</span>
                    
                    <button class="btn btn-step" onclick="stepExtract()">[1] Extraer JSON Médico (/extract)</button>
                    <button class="btn btn-step" onclick="stepPredict()">[2] Predecir Riesgos IA (/predict)</button>
                    <button class="btn btn-step" onclick="stepReport()">[3] Redactar Informe (/report)</button>

                    <span class="step-title">VALOR INTERMEDIO (JSON EDITABLE)</span>
                    <textarea id="jsonEdit" class="editable-json"></textarea>
                    <p style="font-size: 11px; color: #94a3b8; margin-top: 5px;">* Puedes editar el JSON arriba y luego darle a 'Predecir' para ver el impacto.</p>
                </div>
            </div>
        </div>

        <script>
            // Persistencia de datos en la UI
            let lastPredictions = {};

            async function fullFlow() {
                const text = document.getElementById('inputText').value;
                if (!text) return alert("Escribe un caso clínico");
                
                showLoading(true);
                try {
                    const res = await call('/analyze', {text: text});
                    updateUI(res.extracted_medical_data, res.predictive_analysis, res.narrative_report);
                } catch(e) { alert("Error en el servidor"); }
                showLoading(false);
            }

            async function stepExtract() {
                const text = document.getElementById('inputText').value;
                showLoading(true);
                const data = await call('/extract', {text: text});
                document.getElementById('jsonEdit').value = JSON.stringify(data, null, 2);
                showLoading(false);
            }

            async function stepPredict() {
                try {
                const medical_data = JSON.parse(document.getElementById('jsonEdit').value);
                showLoading(true);
                const predictions = await call('/predict', medical_data);
                lastPredictions = predictions;
                updateStats(predictions);
                showLoading(false);
                } catch(e) { alert("JSON inválido"); showLoading(false); }
            }

            async function stepReport() {
                const medical_data = JSON.parse(document.getElementById('jsonEdit').value);
                showLoading(true);
                const res = await call('/report', {prediction_data: lastPredictions, medical_data: medical_data});
                document.getElementById('reportText').innerText = res.report;
                showLoading(false);
            }

            // Helpers
            async function call(endpoint, body) {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body)
                });
                return await res.json();
            }

            function updateUI(medical, predict, report) {
                document.getElementById('jsonEdit').value = JSON.stringify(medical, null, 2);
                document.getElementById('reportText').innerText = report;
                lastPredictions = predict;
                updateStats(predict);
            }

            function updateStats(p) {
                setRisk('risk_m', 'val_m', p.mortalidad_riesgo_anual, 40, '%');
                setRisk('risk_v', 'val_v', p.visitas_urgencias_estimadas_mes, 0.5, '');
                setRisk('risk_p', 'val_p', p.probabilidad_perfil_pcc, 60, '%');
            }

            function setRisk(cardId, valId, val, threshold, unit) {
                document.getElementById(valId).innerText = val + unit;
                document.getElementById(cardId).style.background = val > threshold ? '#ef4444' : '#22c55e';
            }

            function showLoading(show) {
                document.getElementById('loading').style.display = show ? 'block' : 'none';
            }
        </script>
    </body>
    </html>
    """

@app.on_event("startup")
async def startup_event():
    try:
        models = client.list()
        model_exists = any(m['name'].startswith(MODEL_NAME) for m in models.get('models', []))
        if not model_exists:
            client.pull(MODEL_NAME)
    except Exception as e:
        logger.error(f"Ollama connection error: {str(e)}")

    try:
        tree_engine.load_and_train()
    except Exception as e:
        logger.error(f"Decision Trees training error: {str(e)}")

class ExtractionRequest(BaseModel):
    text: str

async def run_extraction(text: str):
    prompt = f"<s>[INST] Eres un extractor de datos médicos profesional. Devuelve exclusivamente un objeto JSON con estos campos: {list(json_template.keys())} Texto: {text} [/INST]</s>"
    response = client.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.1, "num_predict": 800})
    raw_output = response['response']
    json_start = raw_output.find('{')
    json_end = raw_output.rfind('}') + 1
    if json_start != -1 and json_end != -1:
        return json.loads(raw_output[json_start:json_end])
    return None

@app.post("/extract")
async def extract_endpoint(request: ExtractionRequest):
    return await run_extraction(request.text)

async def run_report_generation(prediction_data: dict, medical_data: dict):
    context = f"DATOS: {medical_data} | RIESGOS: {prediction_data}"
    prompt = f"<s>[INST] Eres un Doctor experto. Escribe un resumen clínico profesional breve basado en estos datos y riesgos. Sé conciso (2 frases). {context} [/INST]</s>"
    try:
        response = client.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.3})
        return response['response'].strip()
    except: return "Error generando informe."

@app.post("/report")
async def report_endpoint(data: dict):
    # data can have prediction_data and medical_data
    return {"report": await run_report_generation(data.get('prediction_data', {}), data.get('medical_data', {}))}

@app.post("/predict")
async def predict_endpoint(medical_data: dict):
    tree_input = map_llm_json_to_engine(medical_data)
    return await tree_engine.predict_async(tree_input)

@app.post("/analyze")
async def analyze_full_endpoint(request: ExtractionRequest):
    extracted_data = await run_extraction(request.text)
    if not extracted_data: raise HTTPException(status_code=500, detail="LLM failed")
    
    tree_input = map_llm_json_to_engine(extracted_data)
    analysis_results = await tree_engine.predict_async(tree_input)
    narrative_report = await run_report_generation(analysis_results, extracted_data)

    return {
        "extracted_medical_data": extracted_data,
        "predictive_analysis": analysis_results,
        "narrative_report": narrative_report
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
