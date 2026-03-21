FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install (from the new root context)
COPY llm-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and shared engine
COPY llm-service/app.py .
COPY decision-trees/decision_trees_engine.py .
COPY decision-trees/Database/ ./Database/

# Expose FastAPI port
EXPOSE 8000

CMD ["python", "app.py"]
