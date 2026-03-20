from pydantic import BaseModel, Field
from typing import Optional, List

class ExtractedEntities(BaseModel):
    subproblema: int = Field(default=2)
    cronic: str = Field(default="NO")
    edad: Optional[int] = Field(default=None)
    n_visites_urgencies_mes: Optional[int] = Field(default=0)
    n_visites_hospital: Optional[int] = Field(default=0)
    n_farmacs: Optional[int] = Field(default=0)
    dies_ultima_visita_primaria: Optional[int] = Field(default=None)
    n_diagnostics: Optional[int] = Field(default=0)
    laboratori_flags: Optional[bool] = Field(default=False)
    confianza_extraccion: float = Field(0.0)

class DecisionTreeResult(BaseModel):
    prediccio: str
    probabilitat: float
    confianca_model: str
    ruta_decisio: List[str] = []
    recomanacio: str
