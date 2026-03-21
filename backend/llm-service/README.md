# Medical LLM Service

Este servicio proporciona una API REST para la extracción de datos médicos estructurados a partir de texto en lenguaje natural utilizando el modelo **Mistral-7B** a través de **Ollama**.

## Arquitectura

- **Motor de Inferencia**: [Ollama](https://ollama.com/) (sirviendo `mistral:7b`)
- **API Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10)
- **Contenerización**: Docker Compose con soporte para GPU NVIDIA.

## Requisitos Previos

- Docker y Docker Compose installed.
- NVIDIA Container Toolkit (opcional, para aceleración por GPU).

## Instalación y Despliegue

Desde la carpeta `backend/`, ejecuta:

```bash
docker-compose up --build
```

> **Nota:** La primera vez que se inicie, el servicio descargará automáticamente el modelo `mistral` (aprox. 4.1GB). Esto puede tardar varios minutos dependiendo de tu conexión a internet.

## Endpoints de la API

El servicio está disponible en `http://localhost:8001`.

### 1. Health Check
Verifica que la conexión con el servidor Ollama y el modelo estén activos.

- **URL:** `/health`
- **Método:** `GET`
- **Respuesta Exitosa:**
  ```json
  {
    "status": "ok",
    "ollama_host": "http://ollama-server:11434",
    "model": "mistral:7b"
  }
  ```

### 2. Extracción de Datos Médicos
Analiza un texto médico y devuelve un objeto JSON estructurado.

- **URL:** `/extract`
- **Método:** `POST`
- **Cuerpo de la Petición:**
  ```json
  {
    "text": "Paciente varón de 82 años. Es paciente crónico tipo MACA. Se le han realizado 12 diagnósticos en total."
  }
  ```
- **Respuesta Exitosa (JSON):**
  El servicio devolverá un objeto con los siguientes campos mapeados:
  - `Sexo`, `Edad`, `Paciente_Cronico`, `Tipo_Cronico`
  - `Num_Diagnosticos`, `Total_Farmacos`, `Visitas_Atencion_Primaria`
  - `Visitas_Urgencias`, `Ingresos_Hospitalarios`
  - Desglose por sistemas (Cardiovascular, Nervioso, Respiratorio, etc.)

## Ejemplo de Uso (cURL)

```bash
curl -X POST http://localhost:8001/extract \
     -H "Content-Type: application/json" \
     -d '{"text": "Paciente mujer de 45 años con diabetes crónica. Toma 3 fármacos para el sistema digestivo."}'
```

## Configuración del Entorno

Las siguientes variables de entorno se pueden configurar en el `docker-compose.yaml`:

- `OLLAMA_HOST`: Dirección del servidor Ollama (por defecto `http://ollama-server:11434`).
- `MODEL_NAME`: Nombre del modelo a utilizar (por defecto `mistral:7b`).
