from flask import Flask, request, jsonify
import csv
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

VERIFY_TOKEN = "samy123"

CSV_FILE = "message_status.csv"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "google_credentials.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)

sheet = gc.open(
    "WhatsApp Status Log"
).sheet1

@app.route("/")
def home():
    return "Webhook Running"


@app.route("/payload")
def payload():

    if not os.path.exists(CSV_FILE):
        return "No data yet"

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        return "<pre>" + f.read() + "</pre>"


@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():

    data = request.json

    try:

        entries = data.get("entry", [])

        for entry in entries:

            changes = entry.get("changes", [])

            for change in changes:

                value = change.get("value", {})

                statuses = value.get("statuses", [])

                for status_item in statuses:

                    message_id = status_item.get("id")
                    status = status_item.get("status")
                    recipient_id = status_item.get("recipient_id")
                    timestamp = status_item.get("timestamp")

                    file_exists = os.path.exists(CSV_FILE)

                    with open(
                        CSV_FILE,
                        "a",
                        newline="",
                        encoding="utf-8"
                    ) as f:

                        writer = csv.writer(f)

                        if not file_exists:

                            writer.writerow([
                                "message_id",
                                "status",
                                "recipient_id",
                                "timestamp"
                            ])

                        writer.writerow([
                            message_id,
                            status,
                            recipient_id,
                            timestamp
                        ])
sheet.append_row([
    message_id,
    status,
    recipient_id,
    timestamp
])
    except Exception as e:

        print(str(e))

    return jsonify(
        {
            "status": "ok"
        }
    ), 200


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
