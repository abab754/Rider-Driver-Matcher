FROM python:3.12-slim

WORKDIR /app

COPY dispatch_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dispatch_service/ ./dispatch_service/
COPY pricing_service/ ./pricing_service/

CMD ["uvicorn", "dispatch_service.main:app", "--host", "0.0.0.0", "--port", "8000"]