import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import json
from config import Config


def send_email(to_email, subject, html_body):
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        print(f'[EMAIL MOCK] To: {to_email} | Subject: {subject}')
        return True
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = Config.MAIL_FROM
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(Config.MAIL_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f'Email send failed: {e}')
        return False


def send_gchat_message(text):
    if not Config.GCHAT_WEBHOOK_URL:
        print(f'[GCHAT MOCK] {text}')
        return True
    try:
        data = json.dumps({'text': text}).encode('utf-8')
        req = urllib.request.Request(
            Config.GCHAT_WEBHOOK_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f'GChat send failed: {e}')
        return False
