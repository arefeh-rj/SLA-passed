
from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from app.jira import fetch_incidents
from app.splus import send_notification
import json


def main():
   
    users_notif=[]
    #fetch incidents
    incidents = fetch_incidents(project_key="NTA TPS SM", lookback_minutes=60)
    for incident in incidents:
        user = get_user(incident['accountId'])

        massage= f"""test:  
        - Massage: {incident['summary']}
        - SLA : {incident['SLA']}
        """

        #fetch users phone number
        if user is not None: 
            users_notif.append({'id':incident['accountId'],'phone':user['phone_number'],'summery':massage})

        
    for user in users_notif:
        send_notification(user['phone'] , user['summery'])
    

if __name__ == "__main__":
    main()
