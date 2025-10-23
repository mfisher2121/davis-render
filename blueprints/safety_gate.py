from flask import Blueprint, jsonify, request
from auth.token_auth import require_auth
import re

# Initialize blueprint
safety = Blueprint("safety", __name__)


# ----------------------------
# Health check (optional, for testing)
# ----------------------------
@safety.get("/api/safety-gate/health")
def health():
    return jsonify({"ok": True, "service": "safety_gate"})


# ----------------------------
# Helpers for spam classification (rule-boost)
# ----------------------------
PROMO_KEYWORDS = [
    "limited time", "click now", "act fast", "exclusive deal", "special offer",
    "buy now", "free", "discount", "guaranteed", "save big", "50% off",
    "lowest price", "don’t miss", "don't miss"
]

LINK_RE = re.compile(r"https?://|\bwww\.", re.I)
PHONE_RE = re.compile(
    r"\b(?:\+?1[\s\-\.]?)?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b")
MONEY_RE = re.compile(r"\$\s?\d|\b\d+\s?(?:usd|dollars?)\b", re.I)
ALLCAPS_CTA_RE = re.compile(r"[A-Z]{3,}(?:!+)?")
PUNCT_RUN_RE = re.compile(r"([!?.])\1{2,}")  # !!!, ???, ...


def heuristic_spam_boost(text: str) -> float:
    """Return a boost (0..0.45) based on obvious promo/CTA signals."""
    t = text.lower()
    hits = 0

    # keyword hits
    hits += sum(1 for k in PROMO_KEYWORDS if k in t)

    # shouty caps words / long runs of punctuation
    hits += 1 if ALLCAPS_CTA_RE.search(text) else 0
    hits += 1 if PUNCT_RUN_RE.search(text) else 0

    # links / phone / money mentions
    hits += 1 if LINK_RE.search(text) else 0
    hits += 1 if PHONE_RE.search(text) else 0
    hits += 1 if MONEY_RE.search(text) else 0

    # cap total boost ~0.45 so model can still dominate
    return min(0.15 * hits, 0.45)


def base_keyword_score(text_lower: str) -> float:
    """
    Lightweight base score 0..1 from keyword presence (no model yet).
    If you later add a model prob_spam, replace this with the model output.
    """
    spam_words = ["buy now", "click here", "limited time", "free", "discount"]
    if not spam_words:
        return 0.0
    matches = sum(1 for w in spam_words if w in text_lower)
    return matches / len(spam_words)


# ----------------------------
# Spam evaluator (rule-boost + base score)
# ----------------------------
@safety.post("/api/safety-gate/evaluate/spam")
@require_auth
def spam():
    data = request.get_json(silent=True) or {}
    raw = (data.get("content") or "")
    text_lower = raw.lower().strip()

    if not text_lower:
        return jsonify({"error": "Missing content"}), 400

    # If you add a model later, set model_prob_spam = model.predict_proba(raw)
    model_prob_spam = base_keyword_score(text_lower)  # 0..1
    boosted = min(1.0, model_prob_spam + heuristic_spam_boost(raw))

    # Threshold: be reasonably strict in production
    label = "spam" if boosted >= 0.5 else "not_spam"

    return jsonify({
        "label": label,
        "score": round(boosted, 2),
        "signals": {
            "base": round(model_prob_spam, 2),
            "boost": round(heuristic_spam_boost(raw), 2)
        }
    })


# ----------------------------
# Helpful content evaluator (kept simple for now)
# ----------------------------
@safety.post("/api/safety-gate/evaluate/helpful")
@require_auth
def helpful():
    data = request.get_json(silent=True) or {}
    text = (data.get("content") or "").strip()

    if not text:
        return jsonify({"error": "Missing content"}), 400

    # Simple placeholder scoring logic
    score = 0.82 if len(text.split()) > 6 else 0.35

    return jsonify({
        "label": "helpful" if score >= 0.6 else "not_helpful",
        "score": round(score, 2)
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
