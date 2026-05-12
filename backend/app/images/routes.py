from flask import Blueprint

images_bp = Blueprint(
    "images",
    __name__,
    url_prefix="/api/images",
)


@images_bp.post("")
def upload_image():
    pass


@images_bp.get("/<id>")
def get_image(id):
    pass