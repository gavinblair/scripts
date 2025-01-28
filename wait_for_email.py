# Enable IMAP in Gmail:
# Go to Gmail Settings → "Forwarding and POP/IMAP"
# Enable "IMAP access"
# Generate an App Password (if using 2FA):
# Visit Google App Passwords
# Create a password for "Mail" (select "Other" if prompted)

#!/usr/bin/env python3
import imaplib
import email
import subprocess
import time
import requests
import argparse
import sys
from email.header import decode_header
from email.policy import default
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD") # not your password, it's an app password. 
CHECK_INTERVAL = 120  # Seconds between checks
TOAST_PATH = "/Users/gavinblair/Projects/apps/toast.sh"
OLLAMA_URL = "http://localhost:11434/api/generate"

def get_email_body(msg):
    """Extract plain text body from email"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return ""

def should_notify(sender, subject, body, user_query):
    """Use Ollama to determine if we should notify"""
    prompt = f"""EMAIL:
    
    From: {sender}
    Subject: {subject}
    Body: {body[:1000]}...  # Truncate long bodies

    Analyze this email and decide if it matches the query "{user_query}".
    
    Should the user be notified? Answer ONLY yes/no."""
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3.2:3b",  # Change to your preferred model
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
        )
        r = response.json()["response"].lower()
        print(f"LLM: {r}")
        return "yes" in response.json()["response"].lower()
    except Exception as e:
        print(f"Ollama error: {e}")
        return False

def check_emails(user_query):
    #print("[DEBUG] Connecting to Gmail IMAP server...")
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER, GMAIL_PASSWORD)
    #print("[DEBUG] Logged into Gmail successfully.")

    # Select inbox
    imap.select("INBOX")
    #print("[DEBUG] Selected INBOX.")

    # Search for unseen messages
    status, messages = imap.search(None, "UNSEEN")
    if status != "OK":
        print("[ERROR] Failed to search for unseen messages.")
        return

    if not messages[0]:
        #print("[INFO] No unseen emails found.")
        imap.close()
        imap.logout()
        return

    #print("[INFO] Found unseen emails. Processing them...")
    for msg_id in messages[0].split():
        #print(f"[DEBUG] Fetching email with ID: {msg_id.decode()} (peek mode)")
        
        # Use "peek" to avoid marking emails as read
        status, data = imap.fetch(msg_id, "(BODY.PEEK[])")
        if status != "OK":
            print(f"[ERROR] Failed to fetch email with ID: {msg_id.decode()}")
            continue

        # Parse email message
        #print("[DEBUG] Parsing email...")
        msg = email.message_from_bytes(data[0][1], policy=default)
        sender = email.utils.parseaddr(msg["From"])[1].lower()
        subject = str(decode_header(msg["Subject"])[0][0])
        body = get_email_body(msg)
        #print(f"[DEBUG] Email from: {sender}, Subject: {subject}")

        # Check if we should notify
        if should_notify(sender, subject, body, user_query):
            #print(f"[INFO] Match found! Notifying for email: {subject}")
            
            # Use the query as the notification title and subject as the message
            notification_title = f"{user_query}"
            notification_message = subject
            subprocess.run([TOAST_PATH, notification_title, notification_message])
            
            # Close IMAP connection and exit immediately
            #print("[DEBUG] Match found, closing IMAP connection and exiting.")
            imap.close()
            imap.logout()
            sys.exit(0)
        #else:
            #print(f"[INFO] No match for email: {subject}")

    #print("[DEBUG] No matches found, closing IMAP connection...")
    imap.close()
    imap.logout()

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Email notification script")
    parser.add_argument("user_query", type=str, help="The natural language query to match emails")
    args = parser.parse_args()

    # Run the email checker with the provided query
    while True:
        check_emails(args.user_query)
        time.sleep(CHECK_INTERVAL)

