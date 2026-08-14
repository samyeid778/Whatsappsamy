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

    data = request.json

    print("Received Webhook:")
    print(data)

    return jsonify(
        {
            "status": "success"
        }
    ), 200


if name == "main":
    app.run(host="0.0.0.0", port=10000)
