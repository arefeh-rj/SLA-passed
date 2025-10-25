
# from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from db.find_manager import get_manager_by_label
from app.jira import fetch_incidents
from app.splus import send_notification
import json
import redis

def main():
   
    users_notif=[]
    # label = get_manager_by_label('NTC-19397')
    # print(label)

    #fetch incidents
    users_incidents = fetch_incidents(notifable="assignee" )

    for incident in users_incidents:
        # with open("incident.json", "w", encoding="utf-8") as f:
        #     json.dump(incident, f, indent=2, ensure_ascii=False)
        # print(json.dumps(incident, indent=2, ensure_ascii=False))
        
        # get users from DB 
        user = get_user(incident['accountId'])
        # print(user)

        #fetch users phone number
        if user is not None: 
            users_notif.append({'incident':incident,'user':user})


    for user in users_notif:
        send_notification(user['incident'] , user['user'])
   
    # print('hello',users_notif)
    # print("⚠️ Warning: Action needed!")      # ⚠️
    # print("🚨 Alert: SLA breached!")         # 🚨
    # print("❗ Important notice")              # ❗
    # print("❕Minor issue detected")           # ❕
    # print("🔥 Critical failure")  

if __name__ == "__main__":
    main()
