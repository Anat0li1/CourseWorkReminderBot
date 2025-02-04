from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Дозволяє запити з будь-якого домену (небезпечно у проді!)

users = {
    123456: {"has_subscription": True, "reminder": {"date": "2024-02-05T10:30", "repeat": "daily", "description": "Йти на тренування"}},
    654321: {"has_subscription": False, "reminder": {"date": "2024-02-06T14:00", "repeat": "none", "description": "Зустріч з другом"}}
}

@app.route("/get_reminder")
def get_reminder():
    user_id = int(request.args.get("user_id"))
    user_data = users.get(user_id, {"has_subscription": False, "reminder": {}})
    return jsonify({**user_data["reminder"], "has_subscription": user_data["has_subscription"]})

@app.route("/save_reminder", methods=["POST"])
def save_reminder():
    data = request.json
    user_id = int(data["user_id"])

    if user_id in users:
        users[user_id]["reminder"] = {
            "date": data["date"],
            "repeat": data["repeat"],
            "description": data["description"]
        }
        return jsonify({"status": "ok"})

    return jsonify({"error": "Користувач не знайдений"}), 404

@app.route("/miniapp")
def miniapp():
    return send_from_directory("frontend", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
