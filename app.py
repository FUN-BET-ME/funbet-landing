from flask import Flask, request, jsonify, redirect
import smtplib
import ssl
import uuid
import os
import json
import requests
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

app = Flask(__name__)
VERIFY_URL = "http://localhost:5000/verify"
TOKENS_FILE = "tokens.json"
RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")
ZOHO_API_URL = "https://www.zohoapis.com/crm/v2/Leads"

def refresh_access_token():
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    url = "https://accounts.zoho.eu/oauth/v2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print("✅ Refreshed token:", access_token)
        return access_token
    else:
        print("❌ Failed to refresh token:", response.text)
        return None

if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, 'w') as f:
        json.dump({}, f)

def save_token(email, token):
    with open(TOKENS_FILE, 'r') as f:
        data = json.load(f)
    data[token] = email
    with open(TOKENS_FILE, 'w') as f:
        json.dump(data, f)

def load_email_from_token(token):
    with open(TOKENS_FILE, 'r') as f:
        data = json.load(f)
    return data.get(token)

def verify_recaptcha(response_token):
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': RECAPTCHA_SECRET,
        'response': response_token
    }
    response = requests.post(url, data=payload)
    result = response.json()
    return result.get("success", False)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    recaptcha_response = request.form.get("g-recaptcha-response")

    if not email or not recaptcha_response:
        return jsonify({"error": "Missing email or reCAPTCHA"}), 400

    if not verify_recaptcha(recaptcha_response):
        return jsonify({"error": "reCAPTCHA verification failed"}), 400

    token = str(uuid.uuid4())
    save_token(email, token)
    send_verification_email(email, token)
    return "Check your inbox for a verification link!"

def send_verification_email(email, token):
    msg = EmailMessage()
    msg["Subject"] = "Verify your FUN-BET.ME signup"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = email
    link = f"{VERIFY_URL}?token={token}"
    msg.set_content(f"Welcome to FUN-BET.ME! Please verify your email by clicking this link: {link}")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), 465, context=context) as server:
        server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)

def add_to_zoho_crm(email):
    token = refresh_access_token()
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "Content-Type": "application/json"
    }
    data = {
        "data": [{
            "Last_Name": email.split("@")[0],
            "Email": email,
            "Lead_Source": "Website",
            "Description": "Double opt-in verified from landing page"
        }]
    }
    response = requests.post(ZOHO_API_URL, headers=headers, json=data)
    return response.status_code in [200, 201]

@app.route("/verify")
def verify():
    token = request.args.get("token")
    email = load_email_from_token(token)
    if email:
        success = add_to_zoho_crm(email)
        if success:
            return f"Thanks, {email} – you’re now verified and signed up!"
        return "Verification succeeded, but failed to add to CRM.", 500
    return "Invalid or expired token.", 400

if __name__ == "__main__":
    app.run(debug=True)
