import unittest
from app import create_app
from app.extensions import db
from app.models import Customer, Mechanic, Inventory, ServiceTicket
from app.utils.auth import encode_token
from app.config import TestingConfig


class TestServiceTickets(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            customer = Customer(
                name="Test User",
                email="test@example.com",
                password="test1234",
                phone="111-111-1111"
            )
            db.session.add(customer)

            mech = Mechanic(
                name="John Mechanic",
                email="john@example.com",
                phone="111-222-3333",
                salary=55000
            )
            db.session.add(mech)

            part = Inventory(
                name="Brake Pads",
                price=120.00,
                quantity=5
            )
            db.session.add(part)
            
            db.session.flush()

            ticket = ServiceTicket(
                VIN="TEST123",
                service_date="2025-01-01",
                service_desc="Broken brakes",
                customer_id=customer.id
            )
            db.session.add(ticket)

            db.session.commit()

            self.customer_id = customer.id
            self.mech_id = mech.id
            self.part_id = part.id
            self.ticket_id = ticket.id

            self.token = encode_token(self.customer_id)

        self.client = self.app.test_client()

# Authorization
    def auth_header(self):
        return {"Authorization": f"Bearer {self.token}"}

# Create service ticket
    def test_create_ticket(self):
        payload = {
            "VIN": "XYZ999",
            "service_date": "2025-02-10",
            "service_desc": "Brake repair",
            "customer_id": self.customer_id
        }

        response = self.client.post(
            "/service-tickets",
            json=payload,
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["VIN"], "XYZ999")

    # Create service ticket (invalid)
    def test_create_ticket_invalid(self):
        payload = {
            "service_desc": "Missing VIN",
            "customer_id": self.customer_id
        }

        response = self.client.post(
            "/service-tickets",
            json=payload,
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("VIN", response.json)

# Get all tickets
    def test_get_all_tickets(self):
        response = self.client.get("/service-tickets")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

# My tickets
    def test_get_my_tickets(self):
        response = self.client.get(
            "/service-tickets/my-tickets",
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]["customer_id"], self.customer_id)

    # My tickets (invalid)
    def test_get_my_tickets_invalid(self):
        response = self.client.get("/service-tickets/my-tickets")
        self.assertEqual(response.status_code, 401)

# Assign mechanic
    def test_assign_mechanic(self):
        response = self.client.put(
            f"/service-tickets/{self.ticket_id}/assign-mechanic/{self.mech_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["mechanics"]), 1)
        self.assertEqual(response.json["mechanics"][0]["name"], "John Mechanic")

    # Assign mechanic (invalid)
    def test_assign_mechanic_ticket_invalid(self):
        response = self.client.put(
            "/service-tickets/9999/assign-mechanic/1"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Service ticket not found.")

# Remove mechanic
    def test_remove_mechanic(self):
        self.client.put(
            f"/service-tickets/{self.ticket_id}/assign-mechanic/{self.mech_id}"
        )

        response = self.client.put(
            f"/service-tickets/{self.ticket_id}/remove-mechanic/{self.mech_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["mechanics"]), 0)

    # Remove mechanic (invalid)
    def test_remove_mechanic_invalid(self):
        response = self.client.put(
            "/service-tickets/9999/remove-mechanic/9999"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Service ticket not found.")

# Add part to ticket
    def test_add_part_to_ticket(self):
        response = self.client.put(
            f"/service-tickets/{self.ticket_id}/add-part/{self.part_id}",
            headers=self.auth_header()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["parts"]), 1)

    # Add part to ticket (invalid)
    def test_add_part_to_ticket_invalid(self):
        with self.app.app_context():
            wrong_customer = Customer(
                name="Wrong",
                email="wrong@test.com",
                phone="0000000000",
                password="123"
            )
            db.session.add(wrong_customer)
            db.session.commit()

            wrong_token = encode_token(wrong_customer.id)

        response = self.client.put(
            f"/service-tickets/{self.ticket_id}/add-part/{self.part_id}",
            headers={"Authorization": f"Bearer {wrong_token}"}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json["error"], "Not authorized to modify this ticket")


if __name__ == "__main__":
    unittest.main()
