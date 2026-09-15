class TestRequestTrip:
    def test_requests_trip_successfully(self, client):
        # Setup: create a rider
        client.post("/riders", json={"name": "Abhi", "latitude": 34.0522, "longitude": -118.2437})

        response = client.post("/trips/request", json={
            "rider_id": 1,
            "dropoff_lat": 34.0622,
            "dropoff_long": -118.2537
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REQUESTED"
        assert data["driver_id"] is None
        assert data["price"] is not None

    def test_rejects_trip_for_nonexistent_rider(self, client):
        response = client.post("/trips/request", json={
            "rider_id": 999,
            "dropoff_lat": 34.0622,
            "dropoff_long": -118.2537
        })
        assert response.status_code == 404


class TestConfirmTrip:
    def _setup_trip(self, client):
        """Helper: create a driver, rider, and requested trip."""
        client.post("/drivers", json={"name": "Bob", "latitude": 34.0500, "longitude": -118.2400})
        client.post("/riders", json={"name": "Abhi", "latitude": 34.0522, "longitude": -118.2437})
        resp = client.post("/trips/request", json={
            "rider_id": 1,
            "dropoff_lat": 34.0622,
            "dropoff_long": -118.2537
        })
        return resp.json()["id"]

    def test_confirms_trip_successfully(self, client):
        trip_id = self._setup_trip(client)

        response = client.post(f"/trips/{trip_id}/confirm")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "MATCHED"
        assert data["driver_id"] is not None

    def test_rejects_confirm_when_no_drivers_available(self, client):
        # Create rider and trip but no drivers
        client.post("/riders", json={"name": "Abhi", "latitude": 34.0522, "longitude": -118.2437})
        resp = client.post("/trips/request", json={
            "rider_id": 1,
            "dropoff_lat": 34.0622,
            "dropoff_long": -118.2537
        })
        trip_id = resp.json()["id"]

        response = client.post(f"/trips/{trip_id}/confirm")
        assert response.status_code == 404
        assert "Driver" in response.json()["detail"]

    def test_rejects_double_confirm(self, client):
        trip_id = self._setup_trip(client)

        # First confirm works
        client.post(f"/trips/{trip_id}/confirm")

        # Second confirm should fail
        response = client.post(f"/trips/{trip_id}/confirm")
        assert response.status_code == 400

    def test_rejects_confirm_nonexistent_trip(self, client):
        response = client.post("/trips/999/confirm")
        assert response.status_code == 404

    def test_driver_becomes_unavailable_after_match(self, client):
        trip_id = self._setup_trip(client)
        client.post(f"/trips/{trip_id}/confirm")

        # Create another rider and trip — same driver should not be matched
        client.post("/riders", json={"name": "Jane", "latitude": 34.06, "longitude": -118.25})
        resp = client.post("/trips/request", json={
            "rider_id": 2,
            "dropoff_lat": 34.07,
            "dropoff_long": -118.26
        })
        trip_id_2 = resp.json()["id"]

        response = client.post(f"/trips/{trip_id_2}/confirm")
        assert response.status_code == 404
        assert "Driver" in response.json()["detail"]


class TestGetTrip:
    def test_gets_trip_successfully(self, client):
        client.post("/riders", json={"name": "Abhi", "latitude": 34.0522, "longitude": -118.2437})
        resp = client.post("/trips/request", json={
            "rider_id": 1,
            "dropoff_lat": 34.0622,
            "dropoff_long": -118.2537
        })
        trip_id = resp.json()["id"]

        response = client.get(f"/trips/{trip_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "REQUESTED"

    def test_returns_404_for_nonexistent_trip(self, client):
        response = client.get("/trips/999")
        assert response.status_code == 404
