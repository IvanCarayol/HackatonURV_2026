from fastapi import FastAPI
from app.models import ExtractedEntities, DecisionTreeResult

app = FastAPI(title="Servicio de Inferencia Clínica")

@app.post("/predict", response_model=DecisionTreeResult)
async def predict_clinical_case(data: ExtractedEntities):
    """
    Este es el lugar donde reside el Árbol de Decisión / Red Neuronal.
    """
    # Lógica de ejemplo mockeada para Subproblema 2
    if data.subproblema == 2:
        if data.cronic == "MACA" and (data.n_visites_urgencies_mes or 0) >= 2 and (data.n_farmacs or 0) >= 6:
            return DecisionTreeResult(
                prediccio="ALTA_PROBABILITAT_URGENCIES",
                probabilitat=0.83,
                confianca_model="alta",
                ruta_decisio=["cronic=MACA", "n_visites>=2", "n_farmacs>=6"],
                recomanacio="Revisar pla terapeutic i programar visita primaria urgent"
            )

    # Inferencia por defecto
    return DecisionTreeResult(
        prediccio="RISC_BAIX",
        probabilitat=0.10,
        confianca_model="media",
        ruta_decisio=["ruta_estandar"],
        recomanacio="Continuar control ordinari"
    )
