from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import datetime
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Підключення до Postgres
conn = psycopg2.connect(
    dbname="MemoMate",
    user="postgres",
    password="130505",
    host="localhost",
    port="4321"
)

@app.route("/save_all", methods=["POST"])
def save_all():
    data = request.json
    try:
        cur = conn.cursor()

        now = datetime.datetime.utcnow()

        # початок транзакції
        cur.execute("BEGIN;")

        # Збереження event
        event_data = data["event"]
        name = event_data["name"]
        description = event_data.get("description", "")
        start = datetime.datetime.fromisoformat(event_data["start"])
        end = datetime.datetime.fromisoformat(event_data["end"])
        repeat_type = event_data["repeat_type"]
        start_repeat = event_data.get("start_repeat")
        repeat_indicator = event_data.get("repeat_indicator")
        repeat_duration = event_data.get("repeat_duration")
        end_repeat = event_data.get("end_repeat")

        if start <= now + datetime.timedelta(minutes=5):
            raise ValueError("Початок події має бути не раніше ніж через 5 хвилин")
        if end <= start:
            raise ValueError("Кінець події має бути після початку")

        cur.execute("""
            INSERT INTO event (name, description, start_time, end_time, repeat_type,
                               start_repeat, repeat_indicator, repeat_duration, end_repeat)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (name, description, start, end, repeat_type,
              start_repeat, repeat_indicator, repeat_duration, end_repeat))

        event_id = cur.fetchone()[0]

        # Збереження remindings
        remindings = data.get("remindings", [])
        remind_end = data.get("remind_end")

        for r in remindings:
            remind_before = r["remind_before"]
            remind_indicator = r["remind_indicator"]

            delta = calculate_timedelta(remind_before, remind_indicator)
            next_rem = start - delta
            if next_rem <= now + datetime.timedelta(minutes=5):
                next_rem = now + datetime.timedelta(minutes=6)

            cur.execute("""
                INSERT INTO remindings (event_id, remind_before, remind_indicator, next_rem, remind_end)
                VALUES (%s, %s, %s, %s, false)
            """, (event_id, remind_before, remind_indicator, next_rem))

        if remind_end:
            remind_before = remind_end["remind_before"]
            remind_indicator = remind_end["remind_indicator"]

            delta = calculate_timedelta(remind_before, remind_indicator)
            next_rem = end - delta
            if next_rem <= now + datetime.timedelta(minutes=5):
                next_rem = now + datetime.timedelta(minutes=6)

            cur.execute("""
                INSERT INTO remindings (event_id, remind_before, remind_indicator, next_rem, remind_end)
                VALUES (%s, %s, %s, %s, true)
            """, (event_id, remind_before, remind_indicator, next_rem))

        # кінець транзакції
        cur.execute("COMMIT;")
        cur.close()

        return jsonify({"status": "ok", "event_id": event_id})

    except Exception as e:
        print(e)
        cur.execute("ROLLBACK;")
        cur.close()
        return jsonify({"error": str(e)}), 500

def calculate_timedelta(value, indicator):
    if indicator == 1:  # Minutes
        return datetime.timedelta(minutes=value)
    elif indicator == 2:  # Hours
        return datetime.timedelta(hours=value)
    elif indicator == 3:  # Days
        return datetime.timedelta(days=value)
    elif indicator == 4:  # Weeks
        return datetime.timedelta(weeks=value)
    elif indicator == 5:  # Months
        return datetime.timedelta(days=value * 30)  # ~ approximation
    elif indicator == 6:  # Years
        return datetime.timedelta(days=value * 365)  # ~ approximation
    else:
        raise ValueError("Invalid remind_indicator")

@app.route("/miniapp")
def miniapp():
    return send_from_directory("frontend", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
