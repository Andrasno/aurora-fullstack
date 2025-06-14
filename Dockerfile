FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "180", "api_aurora:app"]
