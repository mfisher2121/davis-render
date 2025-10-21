from flask import Blueprint, jsonify, request
from auth.token_auth import require_auth

safety_gate_bp = Blueprint("safety_gate", __name__)

@safety_gate_bp.get("/health")
def health():
    return jsonify({"ok": True, "service": "safety_gate"})

@safety_gate_bp.post("/evaluate/spam")
@require_auth
def evaluate_spam():
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").lower()
    score = 5
    if any(w in content for w in ["free", "click", "guarantee", "limited time"]):
        score = 65
    return jsonify({"passed": score < 60, "spam_score": score})
