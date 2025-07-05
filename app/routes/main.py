# from flask import Blueprint, jsonify
# from ..extensions import mongo

# main_bp = Blueprint("main", __name__)

# @main_bp.route("/")
# def home():
#     # return jsonify({"message": "Hello, Flask Project!"})
#     try:
#         # Ping MongoDB (official way)
#         mongo.cx.admin.command("ping")
#         return jsonify({"status": "success", "message": "MongoDB connected!"})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

from flask import Blueprint, jsonify
from ..extensions import mongo

# ✅ Add prefix to group this under /api
main_bp = Blueprint("main", __name__, url_prefix="/api")

@main_bp.route("/")
def home():
    try:
        mongo.cx.admin.command("ping")
        return jsonify({"status": "success", "message": "MongoDB connected!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ Add this route
# @main_bp.route("/updates", methods=["GET"])
# def get_updates():
#     try:
#         events = list(mongo.db.github_events.find().sort("received_at", -1).limit(10))
#         for event in events:
#             event["_id"] = str(event["_id"])
#         return jsonify(events), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@main_bp.route("/updates", methods=["GET"])
def get_updates():
    try:
        events = list(mongo.db.github_events.find().sort("timestamp", -1).limit(10))
        
        cleaned_events = []
        for event in events:
            cleaned_events.append({
                "id": str(event["_id"]),
                "request_id": event.get("request_id"),
                "author": event.get("author"),
                "action": event.get("action"),
                "from_branch": event.get("from_branch"),
                "to_branch": event.get("to_branch"),
                "timestamp": event.get("timestamp"),
            })

        return jsonify(cleaned_events), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

