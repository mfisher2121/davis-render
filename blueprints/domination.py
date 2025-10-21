from flask import Blueprint, jsonify, request
from auth.token_auth import require_auth

domination_bp = Blueprint("domination", __name__)

@domination_bp.get("/health")
def health():
    return jsonify({"ok": True, "service": "domination"})

@domination_bp.post("/validate/content")
@require_auth
def validate():
    data = request.get_json(silent=True) or {}
    sections = data.get("sections", {})
    present = len([k for k,v in sections.items() if v])
    return jsonify({"sections_present": present, "passed": present >= 10})
