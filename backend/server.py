from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import asyncio
from db.requests import save_event_with_reminders  # імпортуємо функцію

app = Flask(__name__, static_folder="frontend/static", template_folder="frontend")
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/save_all", methods=["POST"])
def save_all():
    data = request.json
    try:
        event_data = data.get("event")
        remindings = data.get("remindings", [])
        remind_end = data.get("remind_end")

        event_id = asyncio.run(save_event_with_reminders(1, event_data, remindings, remind_end))
        return jsonify({"status": "ok", "event_id": event_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/miniapp")
def miniapp():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
