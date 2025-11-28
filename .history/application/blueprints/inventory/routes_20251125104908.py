from flask import request, jsonify
from application.extensions import db
from application.models import Inventory
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import inventory_schema, inventories_schema
from . import inventory_bp
from application.utils.token_utils import token_required


# Create inventory item
@inventory_bp.route("", methods=["POST"])
@token_required
def create_inventory(customer_id):
    try:
        part_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_part = Inventory(**part_data)

    db.session.add(new_part)
    db.session.commit()

    return inventory_schema.jsonify(new_part), 201


# Get all inventory items, updated with pagination
@inventory_bp.route("", methods=["GET"])
@token_required
def get_inventory(customer_id):

    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))

        query = select(Inventory)
        parts = db.paginate(query, page=page, per_page=per_page)

        return inventories_schema.jsonify(parts.items), 200

    except Exception:
        query = select(Inventory)
        parts = db.session.execute(query).scalars().all()

        return inventories_schema.jsonify(parts), 200


# Get inventory item by ID
@inventory_bp.route("/<int:part_id>", methods=["GET"])
@token_required
def get_inventory_item(customer_id, part_id):

    part = db.session.get(Inventory, part_id)

    if not part:
        return jsonify({"error": "Part not found"}), 404

    return inventory_schema.jsonify(part), 200


# Update inventory item
@inventory_bp.route("/<int:part_id>", methods=["PUT"])
@token_required
def update_inventory(customer_id, part_id):

    part = db.session.get(Inventory, part_id)

    if not part:
        return jsonify({"error": "Part not found"}), 404

    try:
        update_data = inventory_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in update_data.items():
        setattr(part, key, value)

    db.session.commit()

    return inventory_schema.jsonify(part), 200


# Delete inventory item
@inventory_bp.route("/<int:part_id>", methods=["DELETE"])
@token_required
def delete_inventory(customer_id, part_id):
    part = db.session.get(Inventory, part_id)

    if not part:
        return jsonify({"error": "Part not found"}), 404

    db.session.delete(part)
    db.session.commit()

    return jsonify({"message": f"Part {part_id} deleted successfully."}), 200