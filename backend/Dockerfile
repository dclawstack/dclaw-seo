FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -e ".[prod]"

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

EXPOSE 8095

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8095"]
