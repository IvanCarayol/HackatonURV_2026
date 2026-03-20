from app.models import ExtractedEntities, DecisionTreeResult

class MockDecisionTree:
    """
    Mock del Árbol de Decisión. 
    Este servicio simula el comportamiento de la red neuronal/árbol del hospital 
    para poder testear la integración End-to-End de los LLMs.
    """

    def predict(self, data: ExtractedEntities) -> DecisionTreeResult:
        # Lógica de ejemplo mockeada para Subproblema 2
        # Predicción de visitas a urgencias de agudos al mes siguiente en población PCC o MACA
        if data.subproblema == 2:
            if data.cronic == "MACA" and (data.n_visites_urgencies_mes or 0) >= 2 and (data.n_farmacs or 0) >= 6:
                return DecisionTreeResult(
                    prediccio="ALTA_PROBABILITAT_URGENCIES",
                    probabilitat=0.83,
                    confianca_model="alta",
                    ruta_decisio=["cronic=MACA", "n_visites>=2", "n_farmacs>=6"],
                    recomanacio="Revisar pla terapeutic i programar visita primaria urgent"
                )
            else:
                return DecisionTreeResult(
                    prediccio="BAIXA_PROBABILITAT_URGENCIES",
                    probabilitat=0.15,
                    confianca_model="alta",
                    ruta_decisio=["cronic!=MACA", "o_risc_baix"],
                    recomanacio="Continuar control pautat segons programa actiu"
                )

        # Mock general por defecto
        return DecisionTreeResult(
            prediccio="MODERADA",
            probabilitat=0.50,
            confianca_model="media",
            ruta_decisio=["ruta_estandar"],
            recomanacio="Evaluació ordinaria"
        )

ml_model = MockDecisionTree()
