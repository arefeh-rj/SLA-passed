
# from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from db.find_manager import get_manager_by_label
from app.jira import fetch_incidents
from app.splus import send_notification

def main():
   
    users_notif=[]
    #fetch incidents
    users_incidents = fetch_incidents(notifable="assignee" )
    # print(json.dumps(users_incidents, indent=2, ensure_ascii=False))
    for incident in users_incidents:
        # get users from DB 
        user = get_user(incident['accountId'])

        #fetch users phone number
        if user is not None: 
            users_notif.append({'incident':incident,'user':user})


    for user in users_notif:
        send_notification(user['incident'] , user['user'],'assignee')
   
   

if __name__ == "__main__":
    main()


