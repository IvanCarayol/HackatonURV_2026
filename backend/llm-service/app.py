import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama import Client

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Medical LLM Service", description="Mistral-7B via Ollama for medical extraction")

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama-server:11434")
MODEL_NAME = "mistral:7b"
client = Client(host=OLLAMA_HOST)

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
async def check_ollama_connection():
    try:
        logger.info(f"Connecting to Ollama at {OLLAMA_HOST}...")
        # Check if model exists, if not pull it
        models = client.list()
        model_exists = any(m['name'].startswith(MODEL_NAME) for m in models.get('models', []))
        
        if not model_exists:
            logger.info(f"Model {MODEL_NAME} not found. Pulling it (this may take a while)...")
            client.pull(MODEL_NAME)
            logger.info(f"Model {MODEL_NAME} pulled successfully.")
        else:
            logger.info(f"Model {MODEL_NAME} already available in Ollama.")
    except Exception as e:
        logger.error(f"Failed to connect to Ollama or pull model: {str(e)}")
        # We don't raise an exception here because the server should still start, 
        # but endpoints will fail later if not fixed.

class ExtractionRequest(BaseModel):
    text: str

@app.get("/health")
async def health():
    return {"status": "ok", "ollama_host": OLLAMA_HOST, "model": MODEL_NAME}

@app.post("/extract")
async def extract_medical_data(request: ExtractionRequest):
    prompt = f"""<s>[INST] Eres un extractor de datos médicos profesional. 
    Analiza el texto y devuelve exclusivamente un objeto JSON con estos campos:
    {list(json_template.keys())}
    
    Si no conoces un valor numérico, pon 0. Si no conoces un texto, pon "No indicado".
    
    Texto a analizar: {request.text} [/INST]</s>"""
    
    try:
        response = client.generate(
            model=MODEL_NAME,
            prompt=prompt,
            options={
                "temperature": 0.1,
                "num_predict": 800,
            }
        )
        
        raw_output = response['response']
        logger.info(f"Raw output: {raw_output}")
        
        # Clean response to get only JSON
        json_start = raw_output.find('{')
        json_end = raw_output.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = raw_output[json_start:json_end]
            try:
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from output: {json_str}")
                return {"error": "Could not format JSON", "raw_output": raw_output}
        else:
            return {"error": "No JSON found in response", "raw_output": raw_output}
            
    except Exception as e:
        logger.error(f"Error during Ollama inference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
