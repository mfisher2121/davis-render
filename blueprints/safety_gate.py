from flask import Blueprint, jsonify, request
from auth.token_auth import require_auth

# Initialize blueprint
safety = Blueprint("safety", __name__)

# ----------------------------
# Health check (optional, for testing)
# ----------------------------
@safety.get("/api/safety-gate/health")
def health():
    return jsonify({"ok": True, "service": "safety_gate"})

# ----------------------------
# Spam evaluator
# ----------------------------
@safety.post("/api/safety-gate/evaluate/spam")
@require_auth
def spam():
    data = request.get_json(silent=True) or {}
    text = (data.get("content") or "").lower()

    if not text:
        return jsonify({"error": "Missing content"}), 400

    spam_words = ["buy now", "click here", "limited time", "free", "discount"]
    score = sum(word in text for word in spam_words) / len(spam_words)
    label = "spam" if score > 0.2 else "not_spam"

    return jsonify({
        "label": label,
        "score": round(score, 2)
    })

# ----------------------------
# Helpful content evaluator
# ----------------------------
@safety.post("/api/safety-gate/evaluate/helpful")
@require_auth
def helpful():
    data = request.get_json(silent=True) or {}
    text = (data.get("content") or "").strip()

    if not text:
        return jsonify({"error": "Missing content"}), 400

    # Simple placeholder scoring logic
    # (Example: longer, instructional content = more "helpful")
    score = 0.82 if len(text.split()) > 6 else 0.35

    return jsonify({
        "label": "helpful" if score >= 0.6 else "not_helpful",
        "score": score
    })

# ----------------------------
# Optional: future placeholder for unsafe / toxicity checks
# ----------------------------
@safety.post("/api/safety-gate/evaluate/safety")
@require_auth
def safety_eval():
    data = request.get_json(silent=True) or {}
    text = (data.get("content") or "").strip()
    if not text:
        return jsonify({"error": "Missing content"}), 400

    return jsonify({"label": "safe", "score": 0.99})
