from locust import HttpUser, task, between
import random

class RiderUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Create a driver for this user
        lat = 34.0522 + random.uniform(-0.01, 0.01)
        lng = -118.2437 + random.uniform(-0.01, 0.01)
        resp = self.client.post("/drivers", json={
            "name": f"Driver-{random.randint(1, 100000)}",
            "latitude": lat,
            "longitude": lng
        })
        if resp.status_code != 200:
            self.driver_id = None
            self.rider_id = None
            return

        self.driver_id = resp.json().get("id")

        # Create a rider for this user
        resp = self.client.post("/riders", json={
            "name": f"Rider-{random.randint(1, 100000)}",
            "latitude": 34.0522,
            "longitude": -118.2437
        })
        if resp.status_code != 200:
            self.rider_id = None
            return

        self.rider_id = resp.json().get("id")       
                                                    
    @task
    def request_and_confirm_trip(self):
        if not self.rider_id or not self.driver_id:
            return

        resp = self.client.post("/trips/request", json={
            "rider_id": self.rider_id,
            "dropoff_lat": 34.0622 + random.uniform(-0.01, 0.01),
            "dropoff_long": -118.2537
        })
        if resp.status_code == 200:
            trip_id = resp.json().get("id")
            confirm_resp = self.client.post(f"/trips/{trip_id}/confirm")
            if confirm_resp.status_code == 200:
                self.client.post(f"/trips/{trip_id}/complete")
