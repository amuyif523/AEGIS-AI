from locust import HttpUser, task, between
import random

class AegisUser(HttpUser):
    wait_time = between(1, 5)
    token = None

    def on_start(self):
        # Create a unique user for this runner
        import uuid
        username = f"loadtest_{str(uuid.uuid4())[:8]}"
        password = "password123"
        
        # Register
        self.client.post("/users/", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password
        })
        
        # Login
        response = self.client.post("/token", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def view_incidents(self):
        self.client.get("/incidents/")

    @task(1)
    def view_alerts(self):
        self.client.get("/alerts/")

    @task(1)
    def view_stats(self):
        self.client.get("/analytics/stats")

    @task(1)
    def report_incident(self):
        # Simulate a random incident
        types = ["fire", "accident", "medical", "crime", "other"]
        severities = ["low", "medium", "high", "critical"]
        
        lat = 9.005401 + (random.random() - 0.5) * 0.1
        lon = 38.763611 + (random.random() - 0.5) * 0.1
        
        payload = {
            "title": "Load Test Incident",
            "description": "This is a simulated incident from the load tester.",
            "latitude": lat,
            "longitude": lon,
            "incident_type": random.choice(types),
            "severity": random.choice(severities) # The API might override this with AI, which is good
        }
        
        # We need to handle the fact that our API expects a certain schema
        # And authentication might be optional for reporting depending on our implementation
        # In main.py: create_incident depends on get_current_user_optional
        
        self.client.post("/incidents/", json=payload)

