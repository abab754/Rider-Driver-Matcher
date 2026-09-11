from fastapi.testclient import TestClient
from dispatch_service.main import app

client = TestClient(app)

def test_hello_endpt():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"message": "Healthy!"}

