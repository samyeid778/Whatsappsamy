from flask import Flask, request, jsonify
import csv
import os
import tempfile
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

VERIFY_TOKEN = "samy123"
CSV_FILE = "message_status.csv"

# ----------------------------
# Google Sheets
# ----------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

sheet = None
incoming_sheet = None
conversation_sheet = None

try:

    credentials_json = os.environ.get(
        "GOOGLE_CREDENTIALS"
    )

    if credentials_json:

        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".json"
        ) as temp_file:

            temp_file.write(
                credentials_json
            )

            temp_json_path = (
                temp_file.name
            )

        creds = Credentials.from_service_account_file(
            temp_json_path,
            scopes=SCOPES
        )

        gc = gspread.authorize(
            creds
        )

        spreadsheet = gc.open(
            "WhatsApp Status Log"
        )

        sheet = spreadsheet.sheet1

        incoming_sheet = spreadsheet.worksheet(
            "Incoming_Messages"
        )

        conversation_sheet = spreadsheet.worksheet(
            "Conversation_Log"
        )

except Exception as e:

    print(
        "Google Sheets Error:"
    )

    print(str(e))


# ----------------------------
# Time Converter
# ----------------------------

def convert_timestamp(ts):

    try:

        return datetime.fromtimestamp(
            int(ts)
        ).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except:

        return ""


# ----------------------------
# Home
# ----------------------------

@app.route("/")
def home():

    return "Webhook Running"


# ----------------------------
# Payload Viewer
# ----------------------------

@app.route("/payload")
def payload():

    if not os.path.exists(
        CSV_FILE
    ):

        return "No data yet"

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return (
            "<pre>"
            + f.read()
            + "</pre>"
        )


# ----------------------------
# Verification
# ----------------------------

@app.route(
    "/webhook",
    methods=["GET"]
)
def verify_webhook():

    mode = request.args.get(
        "hub.mode"
    )

    token = request.args.get(
        "hub.verify_token"
    )

    challenge = request.args.get(
        "hub.challenge"
    )

    if (
        mode == "subscribe"
        and token == VERIFY_TOKEN
    ):

        return challenge, 200

    return (
        "Verification failed",
        403
    )


# ----------------------------
# Webhook Receiver
# ----------------------------

@app.route(
    "/webhook",
    methods=["POST"]
)
def receive_webhook():

    data = request.json

    try:

        entries = data.get(
            "entry",
            []
        )

        for entry in entries:

            changes = entry.get(
                "changes",
                []
            )

            for change in changes:

                value = change.get(
                    "value",
                    {}
                )

                # ==================
                # Incoming Messages
                # ==================

                messages = value.get(
                    "messages",
                    []
                )

                if messages and incoming_sheet:

                    for msg in messages:

                        phone = msg.get(
                            "from",
                            ""
                        )

                        msg_type = msg.get(
                            "type",
                            "unknown"
                        )

                        message_text = ""

                        if msg_type == "text":

                            message_text = (
                                msg.get(
                                    "text",
                                    {}
                                ).get(
                                    "body",
                                    ""
                                )
                            )

                        elif (
                            msg_type
                            == "interactive"
                        ):

                            message_text = (
                                str(
                                    msg.get(
                                        "interactive",
                                        {}
                                    )
                                )
                            )

                        timestamp = convert_timestamp(
                            msg.get(
                                "timestamp",
                                ""
                            )
                        )

                        incoming_sheet.append_row([
                            phone,
                            message_text,
                            timestamp,
                            msg_type
                        ])

                        if conversation_sheet:

                            conversation_sheet.append_row([
                                phone,
                                "incoming",
                                msg_type,
                                message_text,
                                timestamp
                            ])

                # ==================
                # Status Updates
                # ==================

                statuses = value.get(
                    "statuses",
                    []
                )

                for status_item in statuses:

                    message_id = (
                        status_item.get(
                            "id"
                        )
                    )

                    status = (
                        status_item.get(
                            "status"
                        )
                    )

                    recipient_id = (
                        status_item.get(
                            "recipient_id"
                        )
                    )

                    timestamp = (
   
