FROM python:3.11-slim

# Cria um usuário não-root por motivos de segurança (Boas Práticas de K8s)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instala dependências, asyncpg, e gunicorn para produção
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir asyncpg psycopg2-binary gunicorn

COPY . .

# Corrige permissões para o usuário não-root
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Executa migrações usando sh e inicia servidor com múltiplos workers (UvicornWorker via Gunicorn)
CMD ["sh", "-c", "alembic upgrade head && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000"]
