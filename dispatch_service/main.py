from fastapi import FastAPI
from dispatch_service.routes import router

app = FastAPI()
app.include_router(router)

@app.get("/health")
def health_endpt():
    return {"message": "Healthy!"}

