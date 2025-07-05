# from flask import Blueprint, request, jsonify, current_app
# from ..extensions import mongo
# from ..utils.security import is_valid_signature
# from datetime import datetime
# from ..extensions import limiter

# webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")

# @webhook_bp.route("/", methods=["POST"])
# @limiter.limit("10/minute")  # Limit to 10 requests per IP per minute

# def github_webhook():
#     if not is_valid_signature(request):
#         return jsonify({"error": "Invalid signature"}), 403

#     try:
#         event_type = request.headers.get("X-GitHub-Event")
#         payload = request.get_json(force=True)

#         if not payload:
#             return jsonify({"error": "Invalid payload"}), 400

#         data_to_store = {
#             "event": event_type,
#             "received_at": datetime.utcnow(),
#             "payload": {}
#         }

#         if event_type == "push":
#             repo = payload.get("repository", {}).get("full_name")
#             pusher = payload.get("pusher", {}).get("name")
#             commits = payload.get("commits", [])
#             ref = payload.get("ref")

#             if not repo or not pusher or not ref:
#                 return jsonify({"error": "Missing push data"}), 400

#             data_to_store["payload"] = {
#                 "repo": repo,
#                 "pusher": pusher,
#                 "commits": commits,
#                 "ref": ref
#             }

#         elif event_type == "pull_request":
#             action = payload.get("action")
#             pr_data = payload.get("pull_request", {})
#             merged = pr_data.get("merged", False)

#             repo = payload.get("repository", {}).get("full_name")
#             pr_title = pr_data.get("title")
#             user = pr_data.get("user", {}).get("login")
#             pr_url = pr_data.get("html_url")

#             if not repo or not pr_title or not user or not pr_url:
#                 return jsonify({"error": "Missing PR data"}), 400

#             if action in ["opened", "closed"] and (action == "opened" or merged):
#                 data_to_store["payload"] = {
#                     "repo": repo,
#                     "action": action,
#                     "pr_title": pr_title,
#                     "user": user,
#                     "merged": merged,
#                     "pr_url": pr_url
#                 }
#             else:
#                 return jsonify({"status": "ignored"}), 200

#         else:
#             return jsonify({"status": "ignored"}), 200

#         mongo.db.github_events.insert_one(data_to_store)
#         return jsonify({"status": "success"}), 201

#     except Exception as e:
#         current_app.logger.error(f"[Webhook Error] {e}")
#         return jsonify({"error": "Internal server error"}), 500

from flask import Blueprint, request, jsonify
from ..extensions import mongo
from ..utils.security import is_valid_signature
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")

@webhook_bp.route("/", methods=["POST"])
def github_webhook():
    if not is_valid_signature(request):
        return jsonify({"error": "Invalid signature"}), 403

    event_type = request.headers.get("X-GitHub-Event")
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Invalid payload"}), 400

    event_data = {}

    if event_type == "push":
        event_data = {
            "request_id": payload["after"],  # last commit SHA
            "author": payload["pusher"]["name"],
            "action": "PUSH",
            "from_branch": payload.get("ref", "").split("/")[-1],
            "to_branch": payload.get("ref", "").split("/")[-1],  # same for push
            "timestamp": datetime.utcnow().isoformat()
        }

    elif event_type == "pull_request":
        pr = payload["pull_request"]
        action = payload.get("action")
        is_merged = pr.get("merged", False)

        if action == "closed" and is_merged:
            # MERGE event
            event_data = {
                "request_id": str(pr["id"]),
                "author": pr["user"]["login"],
                "action": "MERGE",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": pr["merged_at"]
            }
        elif action == "opened":
            # New PR opened
            event_data = {
                "request_id": str(pr["id"]),
                "author": pr["user"]["login"],
                "action": "PULL_REQUEST",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": pr["created_at"]
            }
        else:
            return jsonify({"status": "ignored"}), 200

    else:
        return jsonify({"status": "ignored"}), 200

    mongo.db.github_events.insert_one(event_data)
    return jsonify({"status": "success"}), 201



