
# from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from db.find_manager import get_manager_by_label
from app.jira import fetch_incidents
from app.splus import send_notification
import re


# send each product's manager less than 4 hours befor SLA
def send_managers(manager_incidents):
     managers_notif=[]
     for incident in manager_incidents:

        managers = []
        product_tags = [m for s in incident['NTA TPS CIs'] for m in re.findall(r'\bNTC-\d{5}\b', s)]
        
        #fetch managers by project label
        for item in product_tags:
            managers.append(get_manager_by_label(item))

        for manager in managers:
            if manager is not None: 
                managers_notif.append({'incident':incident,'manager':manager})

     return managers_notif

# send incidents to assginee
def send_users(assignee_incidents):
    users_notif=[]
    for incident in assignee_incidents:
        # get users from DB 
        user = get_user(incident['accountId'])

        #fetch users phone number
        if user is not None: 
            users_notif.append({'incident':incident,'user':user})

    return users_notif




def main():
   
    #fetch incidents
    manager_incidents= fetch_incidents(notifable="manager" )
    assignee_incidents=fetch_incidents(notifable="assignee" )
    # print(json.dumps(manager_incidents, indent=2, ensure_ascii=False))

    managers= send_managers(manager_incidents)
    assignee= send_users(assignee_incidents)


    for item in managers:
        send_notification(item['incident'] ,item['manager'], 'manager')

    for user in assignee:
        send_notification(user['incident'] ,user['user'], 'assignee')

   

if __name__ == "__main__":
    main()