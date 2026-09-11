class TestCreateRider:
    def test_creates_rider_successfully(self, client):
        response = client.post("/riders", json={
            "name": "Abhi",
            "latitude": 37.7749,
            "longitude": -122.4194
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Abhi"
        assert data["id"] is not None

    def test_rejects_missing_name(self, client):
        response = client.post("/riders", json={
            "latitude": 37.7749,
            "longitude": -122.4194
        })
        assert response.status_code == 422

    def test_rejects_missing_location(self, client):
        response = client.post("/riders", json={
            "name": "Abhi"
        })
        assert response.status_code == 422
