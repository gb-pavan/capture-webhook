from flask import Blueprint, request, jsonify
from ..extensions import mongo
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def github_webhook():
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Invalid payload"}), 400

    # Filter specific events
    data_to_store = {
        "event": event_type,
        "received_at": datetime.utcnow(),
        "payload": {}
    }

    if event_type == "push":
        data_to_store["payload"] = {
            "repo": payload["repository"]["full_name"],
            "pusher": payload["pusher"]["name"],
            "commits": payload.get("commits", []),
            "ref": payload.get("ref")
        }

    elif event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "closed"] and payload["pull_request"].get("merged", False if action == "closed" else True):
            data_to_store["payload"] = {
                "repo": payload["repository"]["full_name"],
                "action": action,
                "pr_title": payload["pull_request"]["title"],
                "user": payload["pull_request"]["user"]["login"],
                "merged": payload["pull_request"].get("merged"),
                "pr_url": payload["pull_request"]["html_url"]
            }
        else:
            return jsonify({"status": "ignored"}), 200

    else:
        return jsonify({"status": "ignored"}), 200

    # Store in MongoDB
    mongo.db.github_events.insert_one(data_to_store)

    return jsonify({"status": "success"}), 201
