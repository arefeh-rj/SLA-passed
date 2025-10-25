

import os,requests
from dotenv import load_dotenv
import logging
import redis
import json

load_dotenv()  # reads .env in current directory
os.makedirs('logs', exist_ok=True)

# r = redis.Redis(host="localhost", port=6379, db=0,  password='redis_pw', decode_responses=True)
   
# Configure logging
logging.basicConfig(
    filename='logs/notifications.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def send_notification(incident:dict , user:dict):
    url = os.environ["SPLUS_URL"]
    headers = {
        "Authorization": os.environ["SPLUS_AUTH_TOKEN"],
        "Content-Type": "application/json",
    }

    massage= f"""test:  
        - Massage: {incident['summary']}
        - 🚨SLA : {incident['SLA']}
        """
    payload = {"phone_number": user['phone_number'], "text":massage }
 
    # if check_cache(incident['key']):

    try:

        req = requests.post(url, headers=headers, json=payload, timeout=20)
        req.raise_for_status()
        # Log successful notification
        logging.info(f"Notification sent to {user['phone_number']},( {user['accountId']}): {incident['key']} | Status: {req.status_code} | Response: {req.text}")
        # set_incident_cache(incident['key'],user['user_name'])
        # get_incident_cache(incident['key'])
        print(req.status_code, req.text)
    except requests.exceptions.RequestException as e:
        # Log error if request fails
        logging.error(f"Failed to send notification to {user['phone_number']},( {user['accountId']}): {incident['key']} | Error: {str(e)}")
        raise

# def notification_logs():


# def set_incident_cache(key: str, userName:str):
#     if r.exists(key):
#         r.hincrby(key, "count", 1)
#     else:
#         r.hset(key, mapping={"incident": key, "userName": userName, "count": 1})
   

# def check_cache(key:str):
#     if r.exists(key) and r.hgetall(key)['count'] >= 4:
#         return True
#     return False

    # return r.get(key)
