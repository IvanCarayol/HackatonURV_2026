# Decision Trees Service (IA Analítica)

Esta carpeta contiene el motor de inteligencia artificial predictiva del sistema. Utiliza **Gradient Boosting (CatBoost)** para analizar perfiles de pacientes crónicos y detectar riesgos futuros.

## Componentes Principales

La carpeta se divide en dos tipos de archivos: el **Motor de Producción** y los **Scripts de Experimentación**.

### 1. El Motor de Producción (`decision_trees_engine.py`)
Este es el cerebro central que utiliza el servicio de LLM:
- **Carga de Datos**: Realiza un merge inteligente de 6 bases de datos clínicas (`cohort`, `diagnostics`, `farmacs`, `urgencies`, `visites_hospital`, `visites_primaria`).
- **Entrenamiento Paralelizado**: Entrena los 3 modelos simultáneamente al arrancar mediante `asyncio.to_thread`.
- **Predicción Asíncrona**: Procesa las probabilidades de riesgo en paralelo para máxima velocidad.
- **Mapeador Inteligente**: Traduce el JSON extraído por el LLM (`Edad`, `Sexo`, `Fármacos`) al formato técnico que esperan los árboles de decisión.

### 2. Scripts de Experimentación (Exploratorios)
Son scripts independientes diseñados para entrenar y simular casos específicos con **Optuna** (optimización de hiperparámetros).
- **`arboledad.py`**: Modelo especializado en **Probabilidad de Mortalidad a 1 año**.
- **`arbolvisita.py`**: Modelo de **Previsión de Demanda** (estimación de visitas a urgencias en el próximo mes).
- **`detectarPCC.py`**: "Cazador de crónicos ocultos". Analiza a pacientes marcados como "NO crónicos" en busca de patrones idénticos a los de un **PCC (Paciente Crónico Complejo)**.

## Instalación y Requisitos

Para instalar las dependencias necesarias:
```bash
pip install -r requirements.txt
```
Librerías clave: `pandas`, `catboost`, `optuna`, `scikit-learn`, `matplotlib`.

## Datos (`Database/`)

Los modelos se entrenan utilizando los archivos CSV oficiales del hackatón situados en la subcarpeta `Database/`. El motor de producción carga estos archivos automáticamente al iniciarse.

## Características Técnicas de los Modelos
- **Optimización**: Silencioso por defecto (`allow_writing_files=False`), no genera la carpeta temporal `catboost_info`.
- **Feature Engineering**: Crea variables clínicas avanzadas como el "Índice de Fragilidad", la "Carga Asistencial Pasada" y la "PolimedicaciónCrítica".
- **Precisión**: En las pruebas de mortalidad, el AUC-ROC medio es de **0.90+**.
