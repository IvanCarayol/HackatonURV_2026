import os
from pydantic import BaseModel
from openai import OpenAI
from app.models import ExtractedEntities, DecisionTreeResult

# --- Environment loading & variables should be done in config/main or here ---
# Using openai client to connect to local instances (like vLLM, Ollama, Llama.cpp) 
# or remote providers replacing the base_url.

# For a homelab/local model, typically:
# BASE_URL = "http://localhost:11434/v1" (Ollama)
# BASE_URL = "http://localhost:8000/v1" (vLLM)
# Default is None, which falls back to OPENAI_API_BASE environment variable.
# For Google Gemini, one would use the 'google-genai' SDK or configure an orchestrator like LiteLLM to serve an OpenAI proxy.

class LLMService:
    def __init__(self):
        # We initialize the OpenAI client which natively supports structured output
        # It picks up OPENAI_API_KEY and OPENAI_BASE_URL from the environment by default
        self.api_key = os.getenv("LLM_API_KEY", "dummy_local_key")
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")  # Default to generic local API
        self.model_name = os.getenv("LLM_MODEL_NAME", "llama3") # Example for ollama local model

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def extract_entities(self, user_input: str, subproblema: int) -> ExtractedEntities:
        """
        LLM de Entrada: Extrae entidades de variables clínicas
        usando OpenAI Structured Outputs.
        """
        system_prompt = (
            "Eres un asistente de datos clínicos del sistema de soporte a la decisión. "
            f"Extrae la información sobre pacientes al formato JSON requerido para el subproblema {subproblema}. "
            "Devuelve los datos estrictamente según el esquema y calcula una confianza_extraccion de 0.0 a 1.0 según la certeza."
        )

        try:
            # We use `beta.chat.completions.parse` to force JSON output aligning with Pydantic class ExtractedEntities
            response = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                response_format=ExtractedEntities,
            )
            # The parsed object is guaranteed to match ExtractedEntities structure
            return response.choices[0].message.parsed
        except Exception as e:
            # Fallback if parsing fails or local textgen doesn't fully support structured outputs yet
            print(f"Error extrayendo entidades con LLM: {e}")
            return ExtractedEntities(
                subproblema=subproblema,
                confianza_extraccion=0.0
            )

    def generate_natural_response(self, decision_json: DecisionTreeResult, user_input: str, idioma: str = "es") -> str:
        """
        LLM de Salida: Genera una respuesta en lenguaje natural para el gestor sanitario.
        """
        # Formulate instructions based on the documentation
        system_prompt = (
            "Eres un asistente de apoyo a la decisión clínica. Recibirás un JSON con el "
            "resultado de un modelo predictivo y debes explicarlo de forma clara y concisa "
            "a un gestor sanitario.\n"
            "Incluye: (1) el resultado principal, (2) el nivel de confianza, (3) una recomendación accionable breve.\n"
            "No uses jerga técnica de Machine Learning. Usa siempre el idioma especificado en la petición."
        )

        prompt = (
            f"El idioma de salida debe ser '{idioma}'.\n\n"
            f"Contexto original del paciente:\n{user_input}\n\n"
            f"Resultado del árbol de decisión (JSON):\n{decision_json.json()}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generando respuesta natural con LLM: {e}")
            return f"Hubo un error al procesar el caso clínico: {str(e)}"

llm_service = LLMService()
