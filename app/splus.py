

import os,requests
from dotenv import load_dotenv
import logging

load_dotenv()  # reads .env in current directory
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='logs/notifications.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_notification(phone:int , text:str):
    url = os.environ["SPLUS_URL"]

    headers = {
        "Authorization": os.environ["SPLUS_AUTH_TOKEN"],
        "Content-Type": "application/json",
    }
    payload = {"phone_number": phone, "text":text }

    # r = requests.post(url, headers=headers, json=payload, timeout=20)
    # r.raise_for_status()
    # print(r.status_code, r.text)

    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        # Log successful notification
        logging.info(f"Notification sent to {phone}: {text} | Status: {r.status_code} | Response: {r.text}")
        print(r.status_code, r.text)
    except requests.exceptions.RequestException as e:
        # Log error if request fails
        logging.error(f"Failed to send notification to {phone}: {text} | Error: {str(e)}")
        raise

