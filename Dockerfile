# Dockerfile

# Passo 1: Começamos com uma imagem base oficial do Python.
# Usamos a versão 'slim' que é mais leve e ideal para produção.
FROM python:3.11-slim

# Passo 2: Definimos uma pasta de trabalho dentro do nosso ambiente virtual.
WORKDIR /app

# Passo 3: Instalamos as dependências do sistema operacional (A PARTE QUE FALTAVA!).
# Aqui, temos permissão para usar 'apt-get' porque estamos a construir a nossa própria "caixa".
RUN apt-get update && apt-get install -y --no-install-recommends libvips-dev

# Passo 4: Copiamos apenas o ficheiro de requisitos do Python para dentro da "caixa".
COPY backend/requirements.txt .

# Passo 5: Instalamos as dependências do Python.
# O pip usará o 'requirements.txt' que acabámos de copiar.
RUN pip install --no-cache-dir -r requirements.txt

# Passo 6: Copiamos todo o resto do nosso código do backend para dentro da "caixa".
COPY backend/ .

# Passo 7: Dizemos ao Render qual comando executar quando a "caixa" for ligada.
# O Render espera que a porta seja a 10000 para serviços Docker.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--worker-class", "gevent", "--timeout", "180", "api_aurora:app"]