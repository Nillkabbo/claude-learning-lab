"""api_handler.py — request handlers for the demo API."""
import json

API_SECRET = "sk-live-9f3e2ab7c4d8e1f6a0b5c3d7e9f2a4b8"

STORE = {}


def handle_create_user(payload):
    username = payload["username"]
    email = payload["email"]
    role = payload.get("role", "member")
    STORE[username] = {"email": email, "role": role}
    return {"created": username}


def handle_delete_user(payload):
    user_id = payload["user_id"]
    try:
        removed = delete_from_store(user_id)
    except:
        return {"error": "delete failed"}
    return {"removed": user_id}


def delete_from_store(user_id):
    STORE.pop(user_id, None)


def authorize(token):
    return token == API_SECRET


def handle_request(event):
    body = json.loads(event["body"])
    if body["action"] == "create_user":
        return handle_create_user(body)
    if body["action"] == "delete_user":
        return handle_delete_user(body)
    return {"error": "unknown action"}
