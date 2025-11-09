import os, sys
# import json
import logging
# import traceback
# Always add the project root to sys.path dynamically
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from db.find_users import get_user
# from db.find_manager import get_manager_by_label
from app.jira import fetch_incidents
from app.splus import send_notification

def main():
   
    users_notif=[]
    #fetch incidents
    users_incidents = fetch_incidents(notifable="assignee" )
    # print(json.dumps(users_incidents, indent=2, ensure_ascii=False))
    for incident in users_incidents:
        
        # handle unassigned incidents
        if not incident['accountId'] :
            incident['accountId'] = "t.rashki"
            incident['unassigned'] = True
    
        # get users from DB 
        user = get_user(incident['accountId'])

        # fetch users phone number
        if user is not None: 
            users_notif.append({'incident':incident,'user':user})


    for item in users_notif:
        try:
            send_notification(item['incident'], item['user'], 'assignee')
        except Exception as e:
            logging.error(
                "Continuing after notification failure | incident=%s user=%s error=%s",
                item['incident'].get('key'),
                item['user'].get('accountId'),
                e,
                exc_info=True,
            )
        # continue to next item automatically

        # send_notification(user['incident'] , user['user'],'assignee')
   
   

if __name__ == "__main__":
    main()


