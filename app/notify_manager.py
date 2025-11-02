
# from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from db.find_manager import get_managers_by_label
from app.jira import fetch_incidents
from app.splus import send_notification
import re
import json

def dedupe_by_manager(managers, prefer_primary=True):
    keep_at = {}   # manager_id -> index in result
    out = []
    for row in managers:
        mid = row.get("manager_id")
        if mid not in keep_at:
            keep_at[mid] = len(out)
            out.append(row)
        else:
            # conflict: decide which to keep
            i = keep_at[mid]
            cur = out[i]
            if prefer_primary and row.get("is_primary") and not cur.get("is_primary"):
                out[i] = row  
            # else keep existing
    return out

# send each product's manager less than 4 hours befor SLA
def get_managers(manager_incidents):
     managers_notif=[]
     for incident in manager_incidents:

        managers = []
        product_tags = [m for s in incident['NTA TPS CIs'] for m in re.findall(r'\bNTC-\d{5}\b', s)]
        
        #fetch managers by project label
        for item in product_tags:
           
            tag_managers = get_managers_by_label(item)

            for manager in tag_managers:
                managers.append(manager)
        
        managers_dedupe = dedupe_by_manager(managers)          # unique by manager across all labels
        managers_notif.append({'incident':incident,'managers':managers_dedupe})



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
    manager_incidents= fetch_incidents(notifable="manager")

    #first notify assignee
    for item in manager_incidents:
        
        user = get_user(item.get('accountId'))
        send_notification(item ,user, 'manager')


    #second notify managers
        managers= get_managers(manager_incidents)
    

    for item in managers:
        for manager in item.get('managers'):
            send_notification(item['incident'] ,manager, 'manager')

   

   

if __name__ == "__main__":
    main()