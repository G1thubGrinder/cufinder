from flask import Blueprint, request, jsonify, send_file
from bson import ObjectId
from bson.errors import InvalidId
import io
from app.db import get_db, get_gridfs
from app.errors import NotFound
from app.images.schemas import MAX_BYTES, ALLOWED_MIME

images_bp = Blueprint("images", __name__, url_prefix="/api/images")


def stub_require_user():
    # TODO(Guy): swap with real require_user() from app.auth.guards on Day 3
    pass


@images_bp.post("")
def upload_image():
    stub_require_user()

    if "file" not in request.files:
        return jsonify({"error": "missing_file"}), 400

    file = request.files["file"]

    if file.filename == "" or "." not in file.filename:
        return jsonify({"error": "invalid_filename"}), 400

    if file.mimetype not in ALLOWED_MIME:
        return jsonify({"error": "unsupported_mime"}), 400

    data = file.read()
    if len(data) > MAX_BYTES:
        return jsonify({"error": "file_too_large"}), 400

    fs = get_gridfs()
    oid = fs.put(data, filename=file.filename, content_type=file.mimetype)

    return jsonify({"id": str(oid)}), 201


@images_bp.get("/<id>")
def get_image(id):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise NotFound

    fs = get_gridfs()
    if not fs.exists(oid):
        raise NotFound

    grid_out = fs.get(oid)
    return send_file(
        io.BytesIO(grid_out.read()),
        mimetype=grid_out.content_type,
    )