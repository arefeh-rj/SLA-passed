
# from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from db.find_manager import get_manager_by_label
from app.jira import fetch_incidents
from app.splus import send_notification
import json
import redis
import re

def main():
   
    managers_notif=[]

    #fetch incidents
    managers= fetch_incidents(notifable="manager" )

    for incident in managers:
        
        managers = []
        product_tags = [m for s in incident['NTA TPS CIs'] for m in re.findall(r'\bNTC-\d{5}\b', s)]
        # print(result)
        for item in product_tags:
            managers.append(get_manager_by_label(item))

        #fetch users phone number
        for manager in managers:
            if manager is not None: 
                managers_notif.append({'incident':incident,'manager':manager})

    # print(json.dumps(managers_notif, indent=2, ensure_ascii=False))

    for manager in managers_notif:
        send_notification(manager['incident'] , manager['manager'], 'manager')
   

if __name__ == "__main__":
    main()
