from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = "samy123"


@app.route("/")
def home():
    return "Webhook Running"


@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("VERIFY REQUEST RECEIVED")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():

    data = request.json

    print("\n====================")
    print("WEBHOOK RECEIVED")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("====================\n")

    with open("webhook_log.txt", "a", encoding="utf-8") as file:

        file.write("\n====================\n")
        file.write(str(datetime.now()))
        file.write("\n")

        file.write(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            )
        )

        file.write("\n====================\n")

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
