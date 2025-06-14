# Dockerfile (Versão Robusta e à Prova de Falhas)

# 1. Usamos uma imagem base específica do Debian ("Bookworm") para garantir compatibilidade com 'apt-get'.
FROM python:3.11-bookworm

# 2. Definimos uma variável de ambiente crucial que previne que o 'apt-get' pare à espera de input do utilizador.
ENV DEBIAN_FRONTEND=noninteractive

# 3. Definimos o diretório de trabalho.
WORKDIR /app

# 4. O passo mais importante e agora mais robusto:
#    Atualizamos a lista de pacotes, instalamos o 'libvips' e as suas dependências recomendadas,
#    e depois limpamos o cache do apt para manter a imagem final mais pequena.
#    Tudo num único comando 'RUN' para otimização.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libvips-dev && \
    rm -rf /var/lib/apt/lists/*

# 5. Copiamos o ficheiro de requisitos do Python.
COPY backend/requirements.txt .

# 6. ATUALIZAÇÃO: Primeiro, atualizamos o pip. Depois, instalamos as dependências.
#    Isto garante que estamos a usar a versão mais recente e evita avisos no log.
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copiamos o nosso código do backend.
COPY backend/ .

# 8. Expomos a porta que a nossa aplicação vai usar. O Render usa a porta 10000 para serviços Docker.
EXPOSE 10000

# 9. Definimos o comando para iniciar a aplicação quando o contentor arrancar.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "180", "api_aurora:app"]