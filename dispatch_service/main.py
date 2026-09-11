from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_endpt():
    return {"message": "Healthy!"}

