import os
import re
import base64
import subprocess
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
LAST_SEEN_FILE = 'Email Authenticator/last_seen_id.txt'
EMAIL_COUNT = 0

def log(msg):
    print(msg)

def get_gmail_service():
    creds = None
    if os.path.exists('Email Authenticator/token.json'):
        creds = Credentials.from_authorized_user_file('Email Authenticator/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('Email Authenticator/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('Email Authenticator/token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def read_last_seen_id():
    if os.path.exists(LAST_SEEN_FILE):
        with open(LAST_SEEN_FILE, 'r') as f:
            return f.read().strip()
    return None

def write_last_seen_id(msg_id):
    with open(LAST_SEEN_FILE, 'w') as f:
        f.write(msg_id)

def safe_base64_decode(data):
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)

def find_attachments(parts):
    for part in parts:
        if part.get("parts"):
            yield from find_attachments(part["parts"])
        elif part.get("filename") and part.get("body", {}).get("attachmentId"):
            yield part

def extract_text_from_parts(parts):
    text = ""
    for part in parts:
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")
        if data:
            decoded_data = safe_base64_decode(data).decode('utf-8', errors='ignore')
            if mime_type in ["text/plain", "text/html"]:
                text += decoded_data + "\n"
        if part.get("parts"):
            text += extract_text_from_parts(part["parts"])
    return text

def extract_links(text):
    url_pattern = r'(https?://[^\s"<]+)'
    links = re.findall(url_pattern, text)
    seen = set()
    unique_links = []
    for link in links:
        if link not in seen:
            unique_links.append(link)
            seen.add(link)
    return unique_links

def process_email(service):
    global EMAIL_COUNT
    results = service.users().messages().list(userId='me', maxResults=1, q="newer_than:1d").execute()
    messages = results.get('messages', [])
    if not messages:
        return

    msg_id = messages[0]['id']
    last_seen = read_last_seen_id()
    if last_seen == msg_id:
        return

    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg.get('payload', {})
    headers = payload.get('headers', [])
    parts = payload.get('parts', [])

    subject = sender = to_email = ""
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value'].replace('"', "'")
        if header['name'] == 'From':
            sender = header['value']
        if header['name'] == 'To':
            to_email = header['value']

    body_text = extract_text_from_parts(parts)
    links = extract_links(body_text)
    links_text = links[0] if links else "none"

    EMAIL_COUNT += 1
    log(f"\n==================== 📩 EMAIL #{EMAIL_COUNT} ====================")
    log(f"From   : {sender}")
    log(f"To     : {to_email}")
    log(f"Subject: {subject}")
    log(f"Links  : {links_text}")

    os.makedirs("attachments", exist_ok=True)
    attachment_paths = []
    attachment_names = []

    for part in find_attachments(parts):
        filename = part.get("filename")
        attachment_id = part.get("body", {}).get("attachmentId")
        if filename and attachment_id:
            attachment = service.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=attachment_id
            ).execute()
            file_data = safe_base64_decode(attachment['data'])
            filepath = os.path.join("attachments", filename)
            with open(filepath, 'wb') as f:
                f.write(file_data)
            attachment_paths.append(filepath)
            attachment_names.append(filename)
            log(f"✔ Saved: {filepath}")

    # Call main.py once with all attachment paths (comma-separated)
    subprocess.run([
        'python', 'merge.py',
        ','.join(attachment_paths) or 'none',
        sender or "Unknown",
        to_email or "Unknown",
        subject or "No Subject",
        links_text
    ])

    write_last_seen_id(msg_id)

if __name__ == "__main__":
    service = get_gmail_service()
    print("===================== SERVER STARTED =====================")
    try:
        while True:
            process_email(service)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n===================== SERVER STOPPED =====================")
