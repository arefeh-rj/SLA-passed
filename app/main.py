
from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from app.jira import fetch_incidents
from app.splus import send_notification
import json
import redis

def main():
   
    users_notif=[]
    #fetch incidents
    incidents = fetch_incidents(project_key="NTA TPS SM", lookback_minutes=60)

    for incident in incidents:
        user = get_user(incident['accountId'])
        print(user)

        #fetch users phone number
        if user is not None: 
            users_notif.append({'incident':incident,'user':user})


    # for user in users_notif:
    #     send_notification(user['incident'] , user['user'])
   
    # print('hello',users_notif)
    # print("⚠️ Warning: Action needed!")      # ⚠️
    # print("🚨 Alert: SLA breached!")         # 🚨
    # print("❗ Important notice")              # ❗
    # print("❕Minor issue detected")           # ❕
    # print("🔥 Critical failure")  

if __name__ == "__main__":
    main()
