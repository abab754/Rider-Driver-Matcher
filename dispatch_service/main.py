from fastapi import FastAPI
from dispatch_service.routes import router

app = FastAPI()
from dispatch_service.database import Base, engine               
import dispatch_service.models  # registers models with Base     
                                                                
Base.metadata.create_all(bind=engine)
app.include_router(router)

@app.get("/health")
def health_endpt():
    return {"message": "Healthy!"}

