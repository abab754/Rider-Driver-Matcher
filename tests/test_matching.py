class TestNearestDriverMatching:
    def test_matches_nearest_driver(self, client):
        # Driver A: far away (San Francisco)
        client.post("/drivers", json={"name": "Far Driver", "latitude": 37.7749, "longitude": -122.4194})
        # Driver B: close (near downtown LA)
        client.post("/drivers", json={"name": "Close Driver", "latitude": 34.0530, "longitude": -118.2450})
        # Driver C: medium distance (Santa Monica)
        client.post("/drivers", json={"name": "Medium Driver", "latitude": 34.0195, "longitude": -118.4912})

        # Rider in downtown LA
        client.post("/riders", json={"name": "Abhi", "latitude": 34.0522, "longitude": -118.2437})

        resp = client.post("/trips/request", json={
            "rider_id": 1,
            "dropoff_lat": 34.0622,
            "dropoff_long": -118.2537
        })
        trip_id = resp.json()["id"]

        response = client.post(f"/trips/{trip_id}/confirm")
        assert response.status_code == 200
        # Should match Driver B (closest to rider)
        assert response.json()["driver_id"] == 2

    def test_second_trip_gets_next_closest_driver(self, client):
        # Driver A: closest
        client.post("/drivers", json={"name": "Closest", "latitude": 34.0530, "longitude": -118.2450})
        # Driver B: second closest
        client.post("/drivers", json={"name": "Second", "latitude": 34.0600, "longitude": -118.2500})
        # Driver C: farthest
        client.post("/drivers", json={"name": "Farthest", "latitude": 37.7749, "longitude": -122.4194})

        # Two riders
        client.post("/riders", json={"name": "Rider1", "latitude": 34.0522, "longitude": -118.2437})
        client.post("/riders", json={"name": "Rider2", "latitude": 34.0522, "longitude": -118.2437})

        # First trip takes the closest driver
        resp1 = client.post("/trips/request", json={"rider_id": 1, "dropoff_lat": 34.07, "dropoff_long": -118.26})
        client.post(f"/trips/{resp1.json()['id']}/confirm")

        # Second trip should get the second closest
        resp2 = client.post("/trips/request", json={"rider_id": 2, "dropoff_lat": 34.07, "dropoff_long": -118.26})
        response = client.post(f"/trips/{resp2.json()['id']}/confirm")
        assert response.status_code == 200
        assert response.json()["driver_id"] == 2

    def test_matches_only_available_drivers(self, client):
        # Only one driver, take them with first trip
        client.post("/drivers", json={"name": "Only Driver", "latitude": 34.0530, "longitude": -118.2450})
        client.post("/riders", json={"name": "Rider1", "latitude": 34.0522, "longitude": -118.2437})
        client.post("/riders", json={"name": "Rider2", "latitude": 34.0522, "longitude": -118.2437})

        resp1 = client.post("/trips/request", json={"rider_id": 1, "dropoff_lat": 34.07, "dropoff_long": -118.26})
        client.post(f"/trips/{resp1.json()['id']}/confirm")

        # Second trip should fail — no available drivers
        resp2 = client.post("/trips/request", json={"rider_id": 2, "dropoff_lat": 34.07, "dropoff_long": -118.26})
        response = client.post(f"/trips/{resp2.json()['id']}/confirm")
        assert response.status_code == 404

    def test_all_drivers_far_still_picks_nearest(self, client):
        # Both drivers are far, but one is closer than the other
        client.post("/drivers", json={"name": "New York", "latitude": 40.7128, "longitude": -74.0060})
        client.post("/drivers", json={"name": "Chicago", "latitude": 41.8781, "longitude": -87.6298})

        # Rider in LA
        client.post("/riders", json={"name": "Abhi", "latitude": 34.0522, "longitude": -118.2437})

        resp = client.post("/trips/request", json={"rider_id": 1, "dropoff_lat": 34.07, "dropoff_long": -118.26})
        response = client.post(f"/trips/{resp.json()['id']}/confirm")
        assert response.status_code == 200
        # Chicago is closer to LA than New York
        assert response.json()["driver_id"] == 2
