import requests
from Credentials.NameInformation import Name_Information
from utilities.Actions import Billing_Actions

if __name__ == "__main__":
    name_info = Name_Information()
    billing_actions = Billing_Actions()
    
    with requests.Session() as session:
        # 1. Login and change DB to get token
        billing_actions.login_to_database(session, name_info.first_name, name_info.last_name, al_client_id=1586)
        # 2. Perform Actions with token
        billing_actions.create_a_bill_instance(session)

        #AL CLIENT IDs
        #Orion_Billing (regression) = 1586
        #Creative Planning (test) = 557
        #Earned (test) = 3666