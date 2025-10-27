

import os,requests
from dotenv import load_dotenv
import logging
import redis
import json

load_dotenv()  # reads .env in current directory
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='app/logs/notifications.log',
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
      # Log successful notification
        logging.info(f"Notification sent to {user['phone_number']},assignee:( { user['manager_name'] if user.get('manager_name') else incident['accountId']}): {incident['key']} | Status: {req.status_code} | Response: {req.text}")
        
        print(req.status_code, req.text)
    except requests.exceptions.RequestException as e:
      # Log error if request fails
        logging.error(f"Failed to send notification to {user['phone_number']},( {user['manager_name'] if user.get('manager_name') else incident['accountId']}): {incident['key']} | Error: {str(e)}")
        raise



def messages(type: str ,incident:dict):
    # normal users notification
    if type == 'assignee':
        massage= f""" 
        - رخداد : {incident['key']}
        - پیام: {incident['summary']}
        - اولویت: {incident['priority']}
        {('- 🚫 وضعیت: رد شده' if incident.get('rejected') else '')}
        - ⚠️SLA : {incident['SLA']}
        """
    elif type == 'manager':
         massage= f""" 
        - رخداد : {incident['key']}
        - پیام: {incident['summary']}
        - انجام دهنده: {incident['accountId']}
        {('- 🚫 وضعیت: رد شده' if incident.get('rejected') else '')}
        - 🚨SLA : {incident['SLA']}
        """
       
    return massage

    # manager notification

    #🚫rejected incidents notification 

    #unassigned incidents notification

# def logging():

# def messages(type: str, incident: dict) -> str:
#     if type == 'assignee':
#         return (
#             f"- رخداد: {incident.get('key', '—')}\n"
#             f"- پیام: {incident.get('summary', '—')}\n"
#             f"{('- 🚫 وضعیت: رد شده\n' if incident.get('rejected')==False else '')}"
#             f"- ⏱️ SLA: {incident.get('SLA', '—')}"
#         )
#     elif type == 'manager':
#         return (
#             f"- رخداد: {incident.get('key', '—')}\n"
#             f"- پیام: {incident.get('summary', '—')}\n"
#             f"- انجام‌دهنده: {incident.get('accountId', '—')}\n"
#             f"{('- 🚫 وضعیت: رد شده\n' if incident.get('rejected')==False else '')}"
#             f"- 🚨 SLA: {incident.get('SLA', '—')}"
#         )
#     else:
#         return "نوع پیام ناشناخته است."
