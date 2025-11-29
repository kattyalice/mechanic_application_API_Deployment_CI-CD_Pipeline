from datetime import datetime, timedelta
from jose import jwt
from flask import current_app, request, jsonify
from functools import wraps
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"

def encode_token(customer_id):
    payload = {
        "customer_id": customer_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Invalid token format"}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.JWTError:
            return jsonify({"error": "Invalid token"}), 401

        return f(data["customer_id"], *args, **kwargs)

    return decorated