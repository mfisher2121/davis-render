from flask import Blueprint, jsonify, request
from auth.token_auth import require_auth

gbp_helper_bp = Blueprint("gbp_helper", __name__)

@gbp_helper_bp.get("/health")
def health():
    return jsonify({"ok": True, "service": "gbp_helper"})

@gbp_helper_bp.post("/validate/advanced")
@require_auth
def advanced():
    data = request.get_json(silent=True) or {}
    body = (data.get("post_body") or "").lower()
    flags = {
        "has_city": any(tag in body for tag in data.get("cities", [])),
        "has_cta": any(kw in body for kw in ["call", "schedule", "book", "get a quote"])
    }
    return jsonify({"passed": all(flags.values()), "flags": flags})
