"""
Davis & Davis HVAC – Validator API
Blueprints:
- /api/safety-gate
- /api/domination
- /api/authority
- /api/gbp-helper
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- App setup ---------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Config (env-driven; safe defaults for dev)
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change"),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
    JSON_SORT_KEYS=False,
)

# Logging: concise in prod, verbose in dev
logging.basicConfig(
    level=logging.INFO if os.getenv("FLASK_ENV") == "production" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("validators")


# --- Blueprints --------------------------------------------------------------
# (these modules must exist: blueprints/*.py)
from blueprints.safety_gate import safety_gate_bp  # noqa: E402
from blueprints.domination import domination_bp    # noqa: E402
from blueprints.authority import authority_bp      # noqa: E402
from blueprints.gbp_helper import gbp_helper_bp    # noqa: E402

app.register_blueprint(safety_gate_bp, url_prefix="/api/safety-gate")
app.register_blueprint(domination_bp,   url_prefix="/api/domination")
app.register_blueprint(authority_bp,    url_prefix="/api/authority")
app.register_blueprint(gbp_helper_bp,   url_prefix="/api/gbp-helper")


# --- Health + root -----------------------------------------------------------
@app.get("/health")
def health():
    return jsonify(
        status="healthy",
        service="davis-validators",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        endpoints={
            "safety_gate": "/api/safety-gate/health",
            "domination": "/api/domination/health",
            "authority": "/api/authority/health",
            "gbp_helper": "/api/gbp-helper/health",
        },
    ), 200


@app.get("/")
def index():
    return jsonify(
        service="Davis & Davis Content Validators",
        version="1.0.0",
        description="SEO validation microservices (Replit → n8n stack).",
        auth="Bearer token on protected POST endpoints",
        health="/health",
    ), 200


# --- Error handling (always JSON) -------------------------------------------
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="Bad Request", detail=str(e)), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error="Unauthorized", detail="Valid bearer token required"), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not Found", detail="Endpoint does not exist"), 404

@app.errorhandler(413)
def too_large(e):
    return jsonify(error="Payload Too Large", limit=app.config["MAX_CONTENT_LENGTH"]), 413

@app.errorhandler(Exception)
def internal_error(e):
    log.exception("Unhandled error: %s", e)
    return jsonify(error="Internal Server Error"), 500


# --- Local dev entrypoint (Gunicorn will import app:app) ---------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") != "production"
    print(
        f"\n🚀 Validators up on port {port} | debug={debug}\n"
        "Blueprints: safety_gate, domination, authority, gbp_helper\n"
    )
    app.run(host="0.0.0.0", port=port, debug=debug)
