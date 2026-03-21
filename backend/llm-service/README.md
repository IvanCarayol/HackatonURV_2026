# MedRisk Pro: LLM Service & Decision Trees Engine

Este servicio es el núcleo de inteligencia de MedRisk Pro. Combina el poder de **Mistral-7B (vía Ollama)** para el procesamiento de lenguaje natural médico con un motor de **Árboles de Decisión (CatBoost)** para predicciones clínicas precisas.

## 🚀 Tecnologías
- **FastAPI**: Framwork web de alto rendimiento.
- **Ollama**: Orquestador de LLMs locales (Mistral-7B).
- **CatBoost**: Motor de Gradient Boosting para los modelos de decisión.
- **CSV Storage**: Base de datos ligera para el historial de consultas y validaciones.

---

## 🛠️ API Endpoints

### 1. Sistema y Autenticación
- **`GET /health`**: Verifica el estado del servicio, la conexión con Ollama y si los modelos de IA están entrenados.
- **`POST /login`**: Autenticación de facultativos.
  - *Payload*: `{ "username": "...", "password": "...", "center": "..." }`

### 2. Análisis Inteligente (Pipeline de IA)
- **`POST /extract`**: Extrae datos clínicos estructurados (JSON) a partir de un texto libre o dictado por voz.
- **`POST /predict`**: Recibe datos clínicos estructurados y devuelve predicciones de riesgo (Mortalidad, Urgencias, Perfil PCC).
- **`POST /report`**: Genera un informe narrativo profesional basado en las predicciones encontradas.
- **`POST /analyze`**: Ejecuta el pipeline completo (Extraer -> Predecir -> Reportar) en una sola llamada. **Es el endpoint principal del frontend.**

### 3. Gestión de Historial (Persistencia)
- **`GET /patients`**: Devuelve la lista de todos los pacientes consultados anteriormente y guardados en el archivo `queried_patients.csv`.
- **`GET /patient/{id}`**: Recupera la información básica de un paciente específico por su ID.
- **`GET /predict/{id}`**: Ejecuta de nuevo los modelos de IA para un paciente ya guardado en el historial, recuperando también los valores de explicabilidad (SHAP).

### 4. Auditoría y Validación Médica
- **`POST /validate/{id}`**: Permite al facultativo aceptar o rechazar una predicción de la IA.
  - *Payload*: `{ "section": "auditor|previsor|risc", "value": 1|-1 }`
  - Esto actualiza el estado global de validación para garantizar la trazabilidad humana en la decisión médica.

---

## 📂 Estructura de Datos (CSV)
El sistema guarda los resultados en `backend/database/queried_patients.csv` con los siguientes campos adicionales de control:
- `id`: Identificador único de consulta.
- `tratado_auditor`: Estado de validación clínica.
- `tratado_previsor`: Estado de validación de volumen de urgencias.
- `tratado_risc`: Estado de validación de riesgo de mortalidad.

---

## 🛠️ Ejecución Local
Asegúrese de tener **Ollama** funcionando con el modelo `mistral:7b` cargado.
```bash
cd backend/llm-service
python app.py
```
El servicio arrancará en el puerto **8080**.
