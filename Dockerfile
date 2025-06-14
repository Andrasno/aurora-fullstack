# Dockerfile (Versão Robusta)

# 1. Começamos com uma imagem base do Python mais completa (não 'slim').
#    Isto garante que temos todas as ferramentas de sistema necessárias.
FROM python:3.11

# 2. Definimos variáveis de ambiente para otimizar o pip e o ambiente Python.
ENV PYTHONUNBUFFERED True
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

# 3. Criamos e definimos o diretório de trabalho.
WORKDIR /app

# 4. O passo mais importante: Atualizamos o sistema e instalamos a 'libvips'.
#    Combinamos os comandos para criar menos "camadas" no Docker e ser mais eficiente.
#    No final, limpamos o cache do 'apt' para manter a imagem final mais pequena.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libvips-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiamos e instalamos os requisitos do Python.
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# 6. Copiamos o resto do nosso código do backend.
COPY backend/ .

# 7. Definimos o comando para iniciar a aplicação.
#    O Render usa a porta 10000 para serviços Docker.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "180", "api_aurora:app"]