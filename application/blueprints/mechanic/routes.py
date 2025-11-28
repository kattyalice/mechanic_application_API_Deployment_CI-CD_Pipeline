from flask import request, jsonify
from application.extensions import db
from application.models import Mechanic
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import mechanic_schema, mechanics_schema
from . import mechanic_bp


# Create mechanic
@mechanic_bp.route("", methods=["POST"])
def create_mechanic():

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "email" not in mechanic_data or not mechanic_data["email"]:
        return jsonify({"error": "Email is required"}), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with an account."}), 400

    new_mechanic = Mechanic(**mechanic_data)

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201



# Get all mechanics, updated with pagination
@mechanic_bp.route("", methods=["GET"])
def get_mechanics():
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))

        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)

        return mechanics_schema.jsonify(mechanics.items), 200

    except Exception:
        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(mechanics), 200


# Get mechanic by ID
@mechanic_bp.route("/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    return mechanic_schema.jsonify(mechanic), 200


# Update mechanic
# Update mechanic
@mechanic_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    incoming = request.get_json() or {}

    try:
        mechanic_data = mechanic_schema.load(incoming, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()

    return mechanic_schema.jsonify(mechanic), 200


# Delete mechanic
@mechanic_bp.route("/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": f"mechanic id {mechanic_id}, successfully deleted."}), 200


# Most active mechanic
@mechanic_bp.route("/most-active", methods=["GET"])
def get_most_active_mechanic():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mechanic: len(mechanic.tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics), 200