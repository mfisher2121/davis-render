# main.py
from flask import Flask, jsonify
from flask_cors import CORS

# --- BLUEPRINT IMPORTS (one of each, no dupes) ---
from blueprints.safety_gate import safety as safety_bp        # /api/safety-gate/...
from blueprints.domination import domination_bp               # /api/domination/...
from blueprints.authority import authority_bp                 # /api/authority/...
from blueprints.gbp_helper import gbp_bp                      # /api/gbp/...

def create_app() -> Flask:
    app = Flask(__name__)
    # allow n8n / local testing to hit your APIs
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ---------- ROOT + HEALTH ----------
    @app.get("/")
    def root():
        return jsonify({"ok": True, "service": "davis-render", "status": "up"})

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    # ---------- BLUEPRINTS (one of each, no dupes) ----------
    app.register_blueprint(safety_bp,     url_prefix="/api/safety-gate")
    app.register_blueprint(domination_bp, url_prefix="/api/domination")
    app.register_blueprint(authority_bp,  url_prefix="/api/authority")
    app.register_blueprint(gbp_bp,        url_prefix="/api/gbp")

    # ---------- TEMP DEBUG: list all routes ----------
    @app.get("/routes")
    def routes():
        return jsonify(sorted([r.rule for r in app.url_map.iter_rules()]))

    # ---------- ERROR HANDLERS ----------
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "bad_request", "detail": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "unauthorized", "detail": str(e)}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not_found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "method_not_allowed"}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "server_error"}), 500

    return app

# gunicorn entrypoint
app = create_app()

# local dev
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
