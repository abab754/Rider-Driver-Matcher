FROM python:3.12-slim

WORKDIR /app

COPY pricing_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pricing_service/ ./pricing_service/

CMD ["python", "-m", "pricing_service.server"]