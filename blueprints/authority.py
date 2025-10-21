from flask import Blueprint, jsonify, request
from auth.token_auth import require_auth

authority_bp = Blueprint("authority", __name__)

@authority_bp.get("/health")
def health():
    return jsonify({"ok": True, "service": "authority"})

@authority_bp.post("/validate/awards")
@require_auth
def awards():
    data = request.get_json(silent=True) or {}
    links = data.get("external_links", [])
    return jsonify({"has_external_validation": len(links) >= 2})
