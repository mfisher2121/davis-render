# blueprints/gbp_helper.py
from flask import Blueprint, jsonify, request
from auth.token_auth import require_auth

# export name must match main.py import
gbp_bp = Blueprint("gbp", __name__)

@g bp_bp.get("/health")
def health():
    return jsonify({"ok": True, "service": "gbp"})

# Example placeholder endpoint: GBP post preview
@g bp_bp.post("/posts/preview")
@require_auth
def preview_post():
    data = request.get_json(silent=True) or {}
    # pretend we build a GBP post payload
    post = {
        "title": data.get("title", "Untitled"),
        "body": data.get("body", "")[:1500],
        "utm": data.get("utm", {"source": "gbp", "medium": "post"})
    }
    return jsonify({"ok": True, "post": post})
