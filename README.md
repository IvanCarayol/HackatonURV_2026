# 🏥 MedRisk Pro

### Plataforma Avanzada de Análisis de Riesgo Clínico y Soporte a la Decisión Médica Basada en IA

**MedRisk Pro** es un Sistema de Soporte a la Decisión (DSS) diseñado para entornos hospitalarios y de atención primaria. Combina el poder del Procesamiento de Lenguaje Natural (LLM) con algoritmos avanzados de Machine Learning (Árboles de Decisión) para evaluar historiales clínicos, predecir riesgos a futuro y sugerir planes de acción en tiempo real.

---

## 🎯 Objetivo del Proyecto
El objetivo principal de MedRisk Pro es dotar a los profesionales sanitarios de una herramienta predictiva que anticipe eventos adversos (hospitalización o fallecimiento) y necesidades asistenciales futuras. Al identificar precozmente a los pacientes de alto riesgo (incluidos los crónicos ocultos), el sistema permite implementar intervenciones preventivas personalizadas, optimizando la asignación de recursos y mejorando la calidad de vida del paciente.

---

## ✨ Funcionalidades Principales

1.  **🧠 Análisis Clínico de Texto Libre (NLP)**: Integración con un modelo de lenguaje de gran tamaño (**Mistral-7B vía Ollama**) capaz de leer notas médicas no estructuradas y extraer automáticamente entidades clínicas (diagnósticos, fármacos, demografía) en formato JSON estructurado.

2.  **📊 Triple Motor de Predicción (Machine Learning)**: Utiliza modelos **CatBoost** entrenados y ejecutados en paralelo para calcular:
    *   **Riesgo de Mortalidad Anual**: Clasificador que evalúa la probabilidad de defunción.
    *   **Demanda Asistencial**: Regresor que estima el número de visitas a urgencias esperadas en el próximo mes.
    *   **Detector de Crónicos Ocultos (PCC)**: Clasificador optimizado con **Optuna** para identificar pacientes que se comportan clínicamente como Pacientes Crónicos Complejos aunque no estén diagnosticados como tal.

3.  **📝 Generación de Informes Narrativos Automatizados**: Traducción de las predicciones numéricas en predicciones médicas escritas por la IA en un tono profesional.

4.  **📈 Visualización Dinámica de la IA**: Gráficos interactivos en tiempo real (`GlobalWeightsChart`) que reflejan fielmente los pesos y la lógica interna de los modelos tras cada reentrenamiento, eliminando el uso de diagramas estáticos.

5.  **🔐 Autenticación y Control de Acceso**: Sistema de inicio de sesión validado mediante hashing (**SHA-256**) con restricciones para personal autorizado (ej. Centro JoanXXIII).

6.  **💾 Histórico y Auditoría**: Guardado automático de pacientes consultados en bases de datos (CSV) con soporte para validación manual de predicciones por parte de auditores.

7.  **♿ Accesibilidad Universal e Inclusiva**: Panel de control con modo de **alto contraste**, fuente para **dislexia**, aumento de fuente y **dictado por voz**, diseñado para garantizar la equidad en el uso de la tecnología médica.

---

## 🛠️ Stack Tecnológico

### Backend & API: Python 3.11
*   **Framework Web**: FastAPI
*   **Motor de IA (LLM)**: Mistral-7B (vía Ollama)
*   **Machine Learning**: CatBoost, Scikit-learn, Optuna
*   **Base de Datos**: CSVs (Persistencia ligera y trazable)
*   **Orquestación**: Docker & Docker Compose

### Frontend: React.js (Vite)
*   Interfaz moderna con múltiples modos de entrada (Formulario Técnico y Chat NLP).
*   Diseño responsivo y adaptativo.
*   Integración de Web Speech API para accesibilidad.

---

## 🚀 Arquitectura del Sistema
El sistema sigue una arquitectura modular dividida en tres capas principales:

1.  **Capa de Ingesta (NLP)**:
    *   Recibe el texto libre del historial clínico.
    *   Utiliza Mistral-7B para extraer entidades estructuradas.
    *   Genera un JSON clínico estandarizado.

2.  **Capa de Predicción (ML)**:
    *   Procesa los datos a través del `DecisionTreesEngine`.
    *   Ejecuta predicciones en paralelo para máxima eficiencia.
    *   Calcula valores de importancia de variables (SHAP) para explicabilidad.

3.  **Capa de Presentación (Frontend)**:
    *   Interfaz web intuitiva con visualización de riesgos en formato semáforo.
    *   Generación de recomendaciones narrativas automáticas.

---

## 📂 Estructura del Proyecto

```text
HackatonURV_2026/
├── backend/
│   ├── docker-compose.yaml         # Orquestación de infraestructura
│   ├── llm-service/
│   │   ├── app.py                  # API FastAPI (Endpoints centrales)
│   │   └── auth/                   # Gestión de credenciales CSV
│   └── decision-trees/             # Motor predictivo Machine Learning
│       ├── decision_trees_engine.py# Lógica concurrente CatBoost
│       └── Database/               # Cohortes médicas de entrenamiento
├── frontend/                       # Aplicación React (Vite)
│   ├── src/
│   │   ├── App.jsx                 # Control de navegación y accesibilidad
│   │   └── components/             # Dashboard, Login, ChatInput, ResultPanel...
│   └── .env                        # Configuración de conexión con el Homelab
├── start_medrisk.bat               # Orquestador autónomo para Windows
└── start_medrisk.sh                # Orquestador autónomo para Linux
```

---

## 📋 Requisitos del Sistema

### Hardware Recomendado
*   **RAM**: 16 GB mínimo (32 GB recomendado).
*   **GPU**: NVIDIA con soporte CUDA (Requerido para el LLM y entrenamiento acelerado).
*   **Almacenamiento**: 15 GB libres.

### Software Base
*   **Docker & Docker Compose** (V2+).
*   **NVIDIA Container Toolkit**.
*   **Python 3.10+** (si se ejecuta fuera de Docker).
*   **Node.js 18+ & npm**.

---

## 🚀 Guía de Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/ivancarayol/hackatonurv_2026.git
cd HackatonURV_2026
```

### 2. Ejecución Unificada (Recomendado)
Hemos creado scripts orquestadores que preparan el entorno virtual, instalan dependencias y lanzan todo el sistema automáticamente.

*   **En Windows**: Ejecuta `start_medrisk.bat`
*   **En Linux/Homelab**:
    ```bash
    chmod +x start_medrisk.sh
    ./start_medrisk.sh
    ```

### 3. Configuración del Homelab
Si ejecutas el backend en un servidor externo, crea un archivo `frontend/.env`:
```env
VITE_API_URL=http://<IP_TU_SERVIDOR>:8080
```

---

## 💻 Uso de la Plataforma
1.  **Autenticación**: Inicio de sesión validado para el Centro JoanXXIII.
2.  **Entrada de Datos**: Pega informes médicos en el modo **Chat** o usa el **Cuestionario Técnico**.
3.  **Resultados**: Visualiza el % de riesgo y la explicabilidad clínica (SHAP).
4.  **Accesibilidad**: Usa el panel inferior izquierdo para adaptar la interfaz a tus necesidades.

---

&copy; 2026 MedRisk Pro - Sistema de Soporte Clínico Universal e Inclusivo.
