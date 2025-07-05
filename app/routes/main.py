from flask import Blueprint, jsonify
from ..extensions import mongo

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    # return jsonify({"message": "Hello, Flask Project!"})
    try:
        # Ping MongoDB (official way)
        mongo.cx.admin.command("ping")
        return jsonify({"status": "success", "message": "MongoDB connected!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
