from flask import request, jsonify
from application.extensions import db
from application.models import Customer
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import customer_schema, customers_schema, login_schema
from . import customer_bp
from application.utils.auth import encode_token, token_required


# Create customer
@customer_bp.route("", methods=["POST"])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data["email"])
    existing_customer = db.session.execute(query).scalars().first()

    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400

    new_customer = Customer(**customer_data)

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


# Get all customers, updated with pagination
@customer_bp.route("", methods=["GET"])
def get_customers():
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))

        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)

        return customers_schema.jsonify(customers.items), 200

    except Exception:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers), 200


# Get customer by ID
@customer_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    return customer_schema.jsonify(customer), 200


# Update customer
@customer_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()

    return customer_schema.jsonify(customer), 200


# Delete customer
@customer_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": f"Customer id {customer_id}, successfully deleted."}), 200


# Login (generates token)
@customer_bp.route("/login", methods=["POST"])
def login():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    email = credentials["email"]
    password = credentials["password"]

    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if not customer or customer.password != password:
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(customer.id)

    return jsonify({
        "status": "success",
        "message": "Successfully logged in",
        "auth_token": token
    }), 200