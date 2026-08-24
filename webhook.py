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

            temp_json_path = temp_file.name

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

    print("Google Sheets Error:")
    print(str(e))

# ----------------------------
# Timestamp Converter
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
# ---
