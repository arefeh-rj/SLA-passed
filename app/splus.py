

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
        - اولویت: {incident['priority']}
        - انجام دهنده: {incident['accountId']}
        {('- 🚫 وضعیت: رد شده' if incident.get('rejected') else '')}
        - 🚨SLA : {incident['SLA']}
        """
       
    return massage

    # manager notification

    #🚫rejected incidents notification 

    #unassigned incidents notification

# def logging():
# def messages(role: str, incident: dict) -> str:
#     key      = incident.get('key', '—')
#     summary  = incident.get('summary', '—')
#     priority = incident.get('priority', '—')
#     sla      = incident.get('SLA', '—')
#     rejected = "<b>🚫 وضعیت:</b> رد شده\n" if incident.get('rejected') else ""

#     if role == 'manager':
#         assignee = incident.get('accountId', '—')
#         return (
#             f"<b>رخداد:</b> {key}\n"
#             f"<b>پیام:</b> {summary}\n"
#             f"<b>اولویت:</b> {priority}\n"
#             f"<b>انجام‌دهنده:</b> {assignee}\n"
#             f"{rejected}"
#             f"<b>🚨 SLA:</b> {sla}"
#         )
#     # assignee
#     return (
#         f"<b>رخداد:</b> {key}\n"
#         f"<b>پیام:</b> {summary}\n"
#         f"<b>اولویت:</b> {priority}\n"
#         f"{rejected}"
#         f"<b>⚠️ SLA:</b> {sla}"
#     )

