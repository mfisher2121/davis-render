import os
from functools import wraps
from flask import request, jsonify

_TOKEN = os.getenv("AUTH_TOKEN", "")


def require_auth(fn):

    @wraps(fn)
    def _wrap(*args, **kwargs):
        hdr = request.headers.get("Authorization", "")
        if not _TOKEN or not hdr.startswith("Bearer ") or hdr.split(
                " ", 1)[1] != _TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)

    return _wrap
