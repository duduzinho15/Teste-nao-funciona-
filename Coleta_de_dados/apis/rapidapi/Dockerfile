# Dockerfile para Sistema de Produção RapidAPI - FASE 3
FROM python:3.9-slim

# Metadados
LABEL maintainer="RapidAPI Production Team"
LABEL version="3.0.0"
LABEL description="Sistema de Produção RapidAPI com ML e Prometheus"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash rapidapi && \
    mkdir -p /app /logs /models && \
    chown -R rapidapi:rapidapi /app /logs /models

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de requisitos
COPY requirements_fase2.txt requirements.txt

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/models /app/logs /app/config

# Define permissões
RUN chown -R rapidapi:rapidapi /app && \
    chmod +x /app/demo_fase2_ml_prometheus.py

# Muda para usuário não-root
USER rapidapi

# Expõe portas
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando padrão
CMD ["python", "demo_fase2_ml_prometheus.py"]
