# Stage 1: Build
FROM python:3.11-slim-bookworm AS builder
WORKDIR /app

# Instala dependências de compilação
RUN apt-get update && apt-get install -y build-essential

# Configura variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim-bookworm
WORKDIR /app

# Cria usuário não-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copia dependências
COPY --from=builder /root/.local /home/appuser/.local

# Adiciona PATH para binários do usuário
ENV PATH=/home/appuser/.local/bin:$PATH

# Copia código da aplicação
COPY . .

# Configura entrypoint
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
