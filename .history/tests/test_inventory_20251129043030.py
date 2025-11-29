import unittest
from app import create_app
from app.extensions import db
from app.models import Customer, Inventory
from app.utils.auth import encode_token
from app.config import TestingConfig


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            customer = Customer(
                name="Test User",
                email="test@example.com",
                phone="456-456-4567",
                password="password"
            )
            db.session.add(customer)

            part = Inventory(
                name="Oil Filter",
                price=24.99
            )
            db.session.add(part)

            db.session.commit()

            self.customer_id = customer.id
            self.part_id = part.id

            self.token = encode_token(self.customer_id)

        self.client = self.app.test_client()

# Authorization
    def auth_header(self):
        return {"Authorization": f"Bearer {self.token}"}

# Create inventory item
    def test_create_inventory_item(self):
        payload = {
            "name": "Brake Pad",
            "price": 54.99
        }

        response = self.client.post(
            "/inventory",
            json=payload,
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Brake Pad")

    # Create inventory item (invalid)
    def test_create_inventory_invalid(self):
        payload = {
            "price": 49.99
        }

        response = self.client.post(
            "/inventory",
            json=payload,
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json)

# Get all inventory items
    def test_get_inventory_items(self):
        response = self.client.get("/inventory", headers=self.auth_header())

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

# Get inventory item by ID
    def test_get_inventory_item_by_id(self):
        response = self.client.get(
            f"/inventory/{self.part_id}",
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Oil Filter")

    # Get inventory item by ID (invalid)
    def test_get_inventory_item_invalid(self):
        response = self.client.get(
            "/inventory/9999",
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Part not found")

# Update inventory item
    def test_update_inventory(self):
        payload = {
            "name": "Premium Oil Filter",
            "price": 69.99
        }

        response = self.client.put(
            f"/inventory/{self.part_id}",
            json=payload,
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Premium Oil Filter")
        self.assertEqual(response.json["price"], 69.99)

    # Update inventory item (invalid)
    def test_update_inventory_invalid(self):
        payload = {
            "price": "not-a-number"
        }

        response = self.client.put(
            f"/inventory/{self.part_id}",
            json=payload,
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 400)

# Delete inventory item
    def test_delete_inventory_item(self):
        response = self.client.delete(
            f"/inventory/{self.part_id}",
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted", response.json["message"].lower())

    # Delete inventory item (invalid)
    def test_delete_inventory_item_invalid(self):
        response = self.client.delete(
            "/inventory/9999",
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Part not found")


if __name__ == "__main__":
    unittest.main()
