from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
from db.requests import save_event_with_reminders, get_event_by_id, delete_events_remindings, update_event_data, save_reminders

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "frontend", "static"),
    template_folder=os.path.join(BASE_DIR, "frontend")
)

# app = Flask(__name__, static_folder="frontend/static", template_folder="frontend")
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/save_all", methods=["POST"])
async def save_all():
    data = request.json
    try:
        # event_data = data.get("event")
        # remindings = data.get("remindings", [])
        # remind_end = data.get("remind_end")

        # event_id = asyncio.run(save_event_with_reminders(1, event_data, remindings, remind_end))
        await save_event_with_reminders(data.get("userId"), data)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e), "type": type(e).__name__}), 500

@app.route("/get_event/<int:event_id>", methods=["GET"])
async def get_event(event_id):
    try:
        event_data = await get_event_by_id(event_id) 
        return jsonify(event_data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/miniapp")
def miniapp():
    return render_template("index.html")

@app.route("/update_event/<int:event_id>", methods=["POST"])
async def update_event(event_id):
    data = request.json
    try:
        await update_event_data(event_id, data) 
        await delete_events_remindings(event_id)
        await save_reminders(event_id, data)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)