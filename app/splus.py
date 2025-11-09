

import os,requests
from dotenv import load_dotenv
import logging
# import json

load_dotenv()  # reads .env in current directory
os.makedirs('logs', exist_ok=True)


# Configure logging
logging.basicConfig(
    filename='logs/notifications.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def send_notification(incident:dict , user:dict , type:str):
    # print(json.dumps(user, indent=2, ensure_ascii=False))
    
    url = os.environ["SPLUS_URL"]
    headers = {
        "Authorization": os.environ["SPLUS_AUTH_TOKEN"],
        "Content-Type": "application/json",
    }

    massage = messages(type , incident)
    
    payload = {"phone_number": user['phone_number'], "text": massage  }
    
    try:

        req = requests.post(url, headers=headers, json=payload, timeout=20)
        req.raise_for_status()
      
        logging.info(f"Notification sent to {user['phone_number']},assignee:( { user['manager_name'] if user.get('manager_name') else incident['accountId']}): {incident['key']} | Status: {req.status_code} | Response: {req.text}")
        # print(req.status_code, req.text)
        print(f"✔️Notification sent to {user['phone_number']},assignee:( { user['manager_name'] if user.get('manager_name') else incident['accountId']}): {incident['key']} | Status: {req.status_code} | Response: {req.text}")
    except requests.exceptions.RequestException as e:
     
        logging.error(f"Failed to send notification to {user['phone_number']},( {user['manager_name'] if user.get('manager_name') else incident['accountId']}): {incident['key']} | Error: {str(e)}")
        raise




def messages(type: str, incident: dict):
    base = os.environ["JIRA_URL"].rstrip("/")

    # Common header part
    message = (
        f"رخداد: {base}/browse/{incident.get('key', '-')}\n"
        f"اولویت: {incident.get('priority', '-')}\n"
    )

   
    # Handle unassigned logic (adds or replaces assignee info)
    if incident.get('unassigned'):
        message += "انجام دهنده: Unassigned\n"
    elif type == 'assignee' or type == 'manager' :  # only add if not already added for manager
        message += f"انجام دهنده: {incident.get('accountId', 'نامشخص')}\n"

    # Optionally handle rejected status (uncomment if needed)
    # if incident.get('rejected'):
    #     message += "- 🚫 وضعیت: رد شده\n"

 # SLA line differs based on type
    if type == 'assignee':
        message += f"⚠️SLA: {incident.get('SLA', '-')}\n"
    elif type == 'manager':
        message += (
            f"🚨SLA: {incident.get('SLA', '-')}\n"
        )

    return message

