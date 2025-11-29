from flask import request, jsonify
from app.extensions import db, limiter, cache
from app.models import ServiceTicket, Customer, Mechanic, Inventory
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import service_ticket_schema, service_tickets_schema
from . import ticket_bp
from app.utils.auth import token_required


# Create service ticket
@ticket_bp.route("", methods=["POST"])
@token_required
def create_service_ticket(customer_id):
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, ticket_data["customer_id"])
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    new_ticket = ServiceTicket(**ticket_data)

    db.session.add(new_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_ticket), 201


# Assigne mechanic to ticket
@ticket_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("3 per hour")
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to this ticket."}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


# Remove mechanic from ticket
@ticket_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic is not assigned to this ticket."}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


# Get all service tickets, updated with pagination
@ticket_bp.route("", methods=["GET"])
@cache.cached(timeout=30)
def get_service_tickets():

    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))

        query = select(ServiceTicket)
        tickets = db.paginate(query, page=page, per_page=per_page)

        return service_tickets_schema.jsonify(tickets.items), 200

    except Exception:
        query = select(ServiceTicket)
        tickets = db.session.execute(query).scalars().all()
        return service_tickets_schema.jsonify(tickets), 200


# Get logged in customers tickets
@ticket_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(customer_id):

    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(tickets), 200


# Add inventory item
@ticket_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["PUT"])
@token_required
def add_part_to_ticket(customer_id, ticket_id, part_id):

    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 400

    if ticket.customer_id != int(customer_id):
        return jsonify({"error": "Not authorized to modify this ticket"}), 403

    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found."}), 404

    if part in ticket.parts:
        return jsonify({"error": "Part already assigned to this ticket."}), 400

    ticket.parts.append(part)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200