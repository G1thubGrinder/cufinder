from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, session

from ..db import get_db
from .guards import require_user
from .schemas import LoginRequest

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _serialize_user(user: dict) -> dict:
    loc_id = user.get("admin_location_id")
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "display_name": user["display_name"],
        "role": user["role"],
        "admin_location_id": str(loc_id) if loc_id else None,
    }


@auth_bp.post("/login")
def login():
    body = LoginRequest.model_validate(request.get_json(force=True) or {})
    db = get_db()
    # Upsert: create the user on first login; never overwrite an existing role.
    db.users.update_one(
        {"email": body.email},
        {
            "$setOnInsert": {
                "email": body.email,
                "display_name": body.email.split("@")[0],
                "role": "user",
                "admin_location_id": None,
                "created_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    user = db.users.find_one({"email": body.email})
    session["user_id"] = str(user["_id"])
    return jsonify(_serialize_user(user)), 200


@auth_bp.post("/logout")
def logout():
    session.clear()
    return "", 204


@auth_bp.get("/me")
def me():
    user = require_user()
    return jsonify(_serialize_user(user)), 200
