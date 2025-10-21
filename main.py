from flask import Flask, jsonify

# Import blueprints
from blueprints.safety_gate import safety
from blueprints.gbp_helper import gbp_helper_bp
from blueprints.domination import domination_bp
from blueprints.authority import authority_bp

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(safety)
    app.register_blueprint(gbp_helper_bp)
    app.register_blueprint(domination_bp)
    app.register_blueprint(authority_bp)

    @app.get("/")
    def root():
        return jsonify({"ok": True, "service": "root"})

    return app

# Gunicorn entry point (Render)
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
