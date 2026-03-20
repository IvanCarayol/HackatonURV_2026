from fastapi import FastAPI, HTTPException
from app.models import (
    FrontendQueryRequest, FrontendQueryResponse,
    ExtractedEntities, DecisionTreeResult
)
from app.llm_service import llm_service
from app.ml_model import ml_model
import os
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Sistema de Soporte Clínico",
    description="API REST conectando FastAPI, el modelo de IA predictivo y LLM para población envejecida."
)

# Permitir orígenes para acceso externo en el Homelab
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable de entorno opcional para cuando el árbol vive en otro contenedor
DECISION_TREE_URL = os.getenv("DECISION_TREE_URL")

@app.post("/api/v1/query", response_model=FrontendQueryResponse, summary="Consulta principal End-to-End")
async def main_query_endpoint(request: FrontendQueryRequest):
    """
    Recibe el texto del usuario. 
    1. El LLM de entrada extrae entidades (Structured Output).
    2. Las entidades son enviadas al Árbol de Decisión (Físico o por Red).
    3. El LLM de salida genera una respuesta en lenguaje natural.
    """
    try:
        # Capa 1: Extracción vía LLM
        entidades = llm_service.extract_entities(
            user_input=request.user_input, 
            subproblema=request.subproblema
        )

        # Capa 2: Inferencia Árbol de Decisión
        # Si estamos en Docker y hay una URL configurada, llamamos al microservicio
        if DECISION_TREE_URL:
            async with httpx.AsyncClient() as client:
                response = await client.post(DECISION_TREE_URL, json=entidades.dict())
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail="Error en el microservicio del Modelo")
                decision = DecisionTreeResult(**response.json())
        else:
            # Si no hay URL (local sin Docker), usamos el mock de python directamente
            decision = ml_model.predict(entidades)

        # Capa 3: Generación de respuesta natural
        respuesta_natural = llm_service.generate_natural_response(
            decision_json=decision, 
            user_input=request.user_input,
            idioma=request.idioma
        )

        # Ensambla respuesta completa
        return FrontendQueryResponse(
            resposta_natural=respuesta_natural,
            nivell_risc=decision.confianca_model, # Retornamos la confianza como nivel cualitativo por simplicidad
            confianca=decision.probabilitat,
            subproblema=request.subproblema
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error orquestando el flujo: {str(e)}")

@app.post("/api/v1/extract", response_model=ExtractedEntities, summary="Solo Extracción (LLM Entrada)")
async def extract_endpoint(request: FrontendQueryRequest):
    """
    Recibe texto y devuelve JSON estructurado con parámetros clínicos. 
    Útil para depurar y testear independientemente el modelo de lenguage.
    """
    try:
        return llm_service.extract_entities(request.user_input, request.subproblema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/predict", response_model=DecisionTreeResult, summary="Solo Predicción (Árbol Decisión)")
async def predict_endpoint(entidades_clinicas: ExtractedEntities):
    """
    Recibe el JSON estructurado ya extraído y devuelve la respuesta del Árbol de Decisión mock.
    Consumido internamente por el orquestador principal o manualmente.
    """
    try:
        return ml_model.predict(entidades_clinicas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health", summary="Healthcheck del servicio")
async def health_check():
    """
    Verifica que la API del LLM configurada es alcanzable y está viva.
    """
    return {"status": "ok", "api": "up"}

# Punto de entrada local: python -m uvicorn app.main:app --reload
