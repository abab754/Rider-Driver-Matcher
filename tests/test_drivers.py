class TestCreateDriver:
    def test_creates_driver_successfully(self, client):
        response = client.post("/drivers", json={
            "name": "Bob",
            "latitude": 34.0522,
            "longitude": -118.2437
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Bob"
        assert data["id"] is not None
        assert data["latitude"] == 34.0522
        assert data["longitude"] == -118.2437

    def test_rejects_missing_name(self, client):
        response = client.post("/drivers", json={
            "latitude": 34.0522,
            "longitude": -118.2437
        })
        assert response.status_code == 422

    def test_rejects_missing_location(self, client):
        response = client.post("/drivers", json={
            "name": "Bob"
        })
        assert response.status_code == 422

    def test_rejects_invalid_latitude_type(self, client):
        response = client.post("/drivers", json={
            "name": "Bob",
            "latitude": "not_a_number",
            "longitude": -118.2437
        })
        assert response.status_code == 422

    def test_creates_multiple_drivers(self, client):
        client.post("/drivers", json={"name": "Alice", "latitude": 34.0, "longitude": -118.0})
        client.post("/drivers", json={"name": "Bob", "latitude": 35.0, "longitude": -119.0})
        # Each should get a unique id
        r1 = client.post("/drivers", json={"name": "Charlie", "latitude": 36.0, "longitude": -120.0})
        assert r1.json()["id"] == 3
