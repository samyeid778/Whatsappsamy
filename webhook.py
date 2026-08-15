from flask import Flask, request, jsonify

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

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():

    raw_data = request.get_data(as_text=True)

    with open("payload.txt", "a", encoding="utf-8") as f:

        f.write(raw_data)
        f.write("\n\n========================\n\n")

    return jsonify(
        {
            "status": "ok"
        }
    ), 200


@app.route("/payload")
def show_payload():

    try:

        with open("payload.txt", "r", encoding="utf-8") as f:
            return f.read()

    except Exception:
        return "No payload yet"


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
