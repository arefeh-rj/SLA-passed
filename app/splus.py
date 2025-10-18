

import os,requests
from dotenv import load_dotenv

load_dotenv()  # reads .env in current directory

def send_notification(phone:int , text:str):
    url = os.environ["SPLUS_URL"]

    headers = {
        "Authorization": os.environ["SPLUS_AUTH_TOKEN"],
        "Content-Type": "application/json",
    }
    payload = {"phone_number": phone, "text":text }

    r = requests.post(url, headers=headers, json=payload, timeout=20)
    r.raise_for_status()
    print(r.status_code, r.text)



