from pydantic import BaseModel, Field
from typing import Optional, List

# --- Frontend to API Payloads ---

class FrontendQueryRequest(BaseModel):
    user_input: str = Field(..., description="Texto libre introducido por el usuario o gestor sanitario")
    idioma: str = Field(default="es", description="Idioma de la petición (ej. 'es', 'ca')")
    subproblema: int = Field(..., description="El ID del subproblema (ej. 1, 2, 3)")

class FrontendQueryResponse(BaseModel):
    resposta_natural: str = Field(..., description="Respuesta en lenguaje natural generada por el LLM de salida")
    nivell_risc: str = Field(..., description="Nivel de riesgo extraído u obtenido")
    confianca: float = Field(..., description="Nivel de confianza de la predicción (0-1)")
    subproblema: int = Field(..., description="El ID del subproblema evaluado")


# --- LLM Entrada to Árbol Decisión (Extracción JSON) ---

class ExtractedEntities(BaseModel):
    # Campos que el LLM de entrada debe extraer.
    # Este esquema se adapta según el subproblema. Aquí definimos un superset con valores por defecto.
    subproblema: int = Field(default=2, description="ID del subproblema al que se ajustan los datos")
    cronic: str = Field(default="NO", description="Etiqueta de cronicidad del paciente. Valores permitidos: 'NO', 'PCC', 'MACA'")
    edad: Optional[int] = Field(default=None, description="Edad del paciente en años")
    n_visites_urgencies_mes: Optional[int] = Field(default=0, description="Número de visitas a urgencias recientes")
    n_visites_hospital: Optional[int] = Field(default=0, description="Número de ingresos hospitalarios")
    n_farmacs: Optional[int] = Field(default=0, description="Número de fármacos activos")
    dies_ultima_visita_primaria: Optional[int] = Field(default=None, description="Días relativos desde última visita a primaria")
    n_diagnostics: Optional[int] = Field(default=0, description="Número de diagnósticos activos")
    laboratori_flags: Optional[bool] = Field(default=False, description="Presencia/ausencia de analíticas relevantes")
    
    # Metadatos del LLM
    confianza_extraccion: float = Field(..., description="Medida de confianza del LLM al extraer estos datos (0.0 a 1.0)")


# --- Árbol Decisión to LLM Salida (Predicción) ---

class DecisionTreeResult(BaseModel):
    prediccio: str = Field(..., description="Etiqueta de la predicción, ej. 'ALTA_PROBABILITAT_URGENCIES'")
    probabilitat: float = Field(..., description="Probabilidad de la predicción (0.0 a 1.0)")
    confianca_model: str = Field(..., description="Confianza interna cualitativa del modelo (ej. 'alta', 'media', 'baja')")
    ruta_decisio: List[str] = Field(default_factory=list, description="Reglas del árbol activadas, ej. ['cronic=MACA', 'n_farmacs>=6']")
    recomanacio: str = Field(..., description="Recomendación cruda generada por el árbol de decisión")

