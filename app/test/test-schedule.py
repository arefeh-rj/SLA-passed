


import os
import time
import signal
import requests
from datetime import datetime
# import os,requests
from dotenv import load_dotenv

load_dotenv()

SPLUS_URL = os.environ["SPLUS_URL"]
SPLUS_AUTH_TOKEN = os.environ["SPLUS_AUTH_TOKEN"]

# Set these for your test
PHONE = os.getenv("TEST_PHONE", "989334522831")  # use string to avoid leading-zero issues
TEXT  = os.getenv("TEST_TEXT", "Test ping from scheduler")

HEADERS = {
    "Authorization": SPLUS_AUTH_TOKEN,
    "Content-Type": "application/json",
}

STOP = False
def _sig_handler(sig, frame):
    global STOP
    STOP = True

def send_once():
    payload = {"phone_number": PHONE, "text": TEXT}
    r = requests.post(SPLUS_URL, headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    print(f"[{datetime.now().isoformat(timespec='seconds')}] sent -> {PHONE} | {r.status_code}")

def sleep_to_next_2min():
    # align to 2-minute boundaries: 00, 02, 04, ...
    now = datetime.now()
    secs_since_even = (now.minute % 2) * 60 + now.second
    wait = (2 * 60) - secs_since_even
    if wait <= 0:
        wait = 2 * 60
    time.sleep(wait)

if __name__ == "__main__":
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _sig_handler)

    # send immediately, then every 2 minutes
    try:
        send_once()
    except Exception as e:
        print("First send failed:", repr(e))

    while not STOP:
        try:
            sleep_to_next_2min()
            if STOP: break
            send_once()
        except requests.HTTPError as e:
            # print server errors and continue next tick
            print("HTTP error:", e.response.status_code, e.response.text[:200])
        except Exception as e:
            print("Error:", repr(e))
