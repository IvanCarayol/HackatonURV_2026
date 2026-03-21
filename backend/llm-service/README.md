# Medical LLM & Analytics Service

Este servicio proporciona una API completa para la extracción de datos médicos y análisis predictivo de pacientes crónicos complejos (PCC/MACA). Combina el poder de **Mistral-7B** con **Árboles de Decisión (CatBoost)**.

## Arquitectura

- **Motor de Inferencia LLM**: [Ollama](https://ollama.com/) (sirviendo `mistral:7b`)
- **Motor de Predicción**: 3 Árboles de Decisión entrenados en paralelo (Mortalidad, Demanda de Urgencias, Perfil PCC).
- **API Framework**: FastAPI (Python 3.10)
- **Aceleración**: Soporte para GPU NVIDIA via Docker.

## Instalación y Despliegue

```bash
cd backend
docker-compose up --build
```

Al arrancar, el sistema descargará el modelo y entrenará los árboles automáticamente. Sabrás que está listo cuando el log muestre: `✅ [Engine] Todos los modelos entrenados en paralelo y listos.`

---

## Flujos de Trabajo (API Endpoints)

El servicio está disponible en `http://localhost:8001`.

### FLUJO A: Análisis en un solo paso (`One-Shot`)

Ideal para automatización rápida.
- **Endpoint**: `POST /analyze`
- **Body**: `{"text": "..."}`
- **Respuesta**: JSON con datos extraídos, predicciones de riesgo, alertas y un **informe narrativo** generado por la IA.

### FLUJO B: Análisis Modular (Encadenado)

Ideal si quieres que un humano valide el JSON antes de predecir.

**1. Extracción (Paso 1)**
- **Endpoint**: `POST /extract`
- **Body**: `{"text": "..."}`
- **Respuesta**: JSON con variables médicas (Edad, Sexo, Medicamentos...).

**2. Predicción y Reporte (Paso 2)**
- **Endpoint**: `POST /predict`: Devuelve solo los % de riesgo.
- **Endpoint**: `POST /report`: Genera el informe escrito profesional.
- **Body**: JSON obtenido en el paso 1.

---

## Detalle de los Endpoints Principales

### 1. `POST /analyze` (Análisis Completo)
```bash
curl -X POST http://localhost:8001/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "Paciente varón de 85 años, 10 fármacos, MACA."}'
```
**Respuesta:**
- `extracted_medical_data`: Datos clínicos procesados.
- `predictive_analysis`: Mortalidad (%), Visitas (Mes), Perfil PCC (%).
- `narrative_report`: Resumen clínico redactado por el Dr. Inteligencia Artificial.
- `summary`: Flags rápidos (Riesgo Alto/Bajo).

### 2. `POST /predict` (Solo Inteligencia de Riesgo)
Recibe el JSON médico y devuelve las probabilidades calculadas por los árboles de decisión entrenados.

### 3. `POST /report` (Informe narrativo)
Envía las predicciones y diagnósticos para obtener una explicación en lenguaje natural apta para médicos y enfermería.

### 4. `GET /health`
Verifica el estado de Ollama y si los árboles de decisión están ya cargados en memoria.

---

## Configuración Técnica
- Puerto: `8001` (Interno `8000`)
- Modelos CatBoost: Ejecución en paralelo mediante `asyncio.to_thread`.
- Limpieza: Configurado para no generar basura (`catboost_info`) en el disco.
