# The f1-points-finish API (lesson 05) as a container image.
# The image holds the code, not the model: the API loads MODEL_URI from the MLflow server at start-up.
#
# Build:  docker build -t f1-api:1 exercises/serve-model
# Run:    docker run --rm --network host f1-api:1        (Linux, the codespace)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MLFLOW_DISABLE_AGENT_HINT=1 \
    MLFLOW_TRACKING_URI=http://127.0.0.1:5000 \
    MODEL_URI=models:/f1-points-finish@champion \
    PORT=8000

WORKDIR /app
# Install the packages first: Docker reuses this layer until requirements-serve.txt changes.
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

COPY app.py .
# Do not run as root.
RUN useradd --create-home api
USER api

EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
