

import os,requests
from dotenv import load_dotenv

load_dotenv()  # reads .env in current directory

url = os.environ["SPLUS_URL"]

headers = {
    "Authorization": os.environ["SPLUS_AUTH_TOKEN"],
    "Content-Type": "application/json",
}
payload = {"phone_number": 989334522831, "text": "test2"}

r = requests.post(url, headers=headers, json=payload, timeout=20)
r.raise_for_status()
print(r.status_code, r.text)



