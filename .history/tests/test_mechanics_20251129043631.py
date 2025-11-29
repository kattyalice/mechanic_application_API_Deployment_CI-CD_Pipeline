import unittest
from app import create_app
from app.extensions import db
from app.models import Mechanic
from config import TestingConfig


class TestMechanic(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.mechanic = Mechanic(
                name="John Mechanic",
                email="john@example.com",
                phone="111-222-3333",
                salary=55000
            )
            db.session.add(self.mechanic)
            db.session.commit()

            self.mechanic_id = self.mechanic.id

# Create mechanic
    def test_create_mechanic(self):
        payload = {
            "name": "New Mechanic",
            "email": "newmech@example.com",
            "phone": "555-555-5555",
            "salary": 60000
        }

        response = self.client.post("/mechanics", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "New Mechanic")

    # Create mechanic (invalid)
    def test_create_mechanic_invalid(self):
        payload = {
            "name": "Missing Email Mechanic",
            "phone": "555-555-5555",
            "salary": 60000
        }

        response = self.client.post("/mechanics", json=payload)

        self.assertEqual(response.status_code, 400)

# Get all mechanics
    def test_get_mechanics(self):
        response = self.client.get("/mechanics")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

# Get mechanic by ID
    def test_get_mechanic_by_id(self):
        response = self.client.get(f"/mechanics/{self.mechanic_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["email"], "john@example.com")

    # Get mechanic by ID (invalid)
    def test_get_mechanic_invalid(self):
        response = self.client.get("/mechanics/9999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Mechanic not found.")

# Update mechanic
    def test_update_mechanic(self):
        payload = {
            "name": "Updated Mechanic",
            "salary": 70000
        }

        response = self.client.put(
            f"/mechanics/{self.mechanic_id}",
            json=payload
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Updated Mechanic")

    # Update mechanic (invalid)
    def test_update_mechanic_invalid(self):
        payload = {"email": "not-an-email"}

        response = self.client.put(
            f"/mechanics/{self.mechanic_id}",
            json=payload
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json)

# Delete mechanic
    def test_delete_mechanic(self):
        response = self.client.delete(f"/mechanics/{self.mechanic_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully deleted", response.json["message"])

    # Delete mechanic (invalid)
    def test_delete_mechanic_invalid(self):
        response = self.client.delete("/mechanics/9999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Mechanic not found.")

# Most active mechanic
    def test_get_most_active_mechanic(self):
        response = self.client.get("/mechanics/most-active")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
