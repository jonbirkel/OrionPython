from types import NoneType
import requests
import base64
import json
from utilities.Objects import Objects

class Billing_Actions:
    def __init__(self):
        pass

    def login_to_database(self, session: requests.Session, username: str, password: str, al_client_id: int):
        """
        Logs in, retrieves an access token, and switches to the specified database.
        Returns the final session token for further API calls.
        """
        # Step 1: Authenticate and Get Token
        auth_url = "https://testapi.orionadvisor.com/api/v1/Security/Token"

        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }

        response = session.get(auth_url, headers=headers)
        response.raise_for_status()

        data = response.json()
        access_token = data.get("access_token")
        print("Token Status Code:", response.status_code)
        print("Login Successful")

        # Step 2: Switch Database
        print(f"Switching to database: {al_client_id}...")

        session.headers.update({
            "Accept": "application/json",
            "ALClientID": str(al_client_id),
            "Authorization": f"Switch {access_token}"
        })

        switch_response = session.get(auth_url)
        switch_response.raise_for_status()

        switch_data = switch_response.json()
        switch_token = switch_data.get("access_token")

        print("Switch Database Successful.")

        session.headers.update({
        "Authorization": f"Session {switch_token}"
        }) 

    def get_information(self, session: requests.Session):
        url = "https://testapi.orionadvisor.com/api/v1/Billing/PostPayments/HHAndDate"
        print("Connecting to: ", url)

        response = session.get(url)
        if response.status_code == 200:
            data = response.json()
            amount = sum(item.get('amountToPost', 0) for item in data)
            print("Total Amount To Post:", amount)
        else:
            print("Error fetching data:", response.status_code, response.text)

        return response

    def create_a_bill_instance(self, session: requests.Session):
        url = "https://testapi.orionadvisor.com/api/v1/Billing/BillGenerator/Action/Instance"
        print("Connecting to: ", url)

        obj = Objects.BillInstance(
            nickName="Python - Rep Splits", 
            keys=[26305], 
            runFor=7, 
            isMockBill=False
        )

        response = session.post(url, json=obj.BillInstanceObject)

        if response.status_code == 200:
            print("Bill Instance Created", response.text)
        else:
            print("Error fetching data:", response.status_code, response.text)

        bill_data = response.json()
        bill_id = bill_data.get("id")

        url = f"https://testapi.orionadvisor.com/api/v1/Billing/Instances/{bill_id}/Action/Generate?lockDown=false"
        response = session.put(url)

        if response.status_code == 200:
            print("Bill Instance Generating!!!", response.text)
        else:
            print("Error fetching data:", response.status_code, response.text)

        return response

    def clear_notifications(self, session: requests.Session):
        url_get = (
            "https://testapi.orionadvisor.com/api/v1/Reporting/Fuse/Notifications"
            "?byLastDays=-1&status%5B%5D=Unread&status%5B%5D=Read"
        )
        print("Connecting to:", url_get)

        response_get = session.get(url_get)
        if response_get.status_code == 200:
            notifications = response_get.json()
            print("Notifications Retrieved:", notifications)
        else:
            print("Error fetching notification data:", response_get.status_code, response_get.text)
            return None

        url_put = "https://testapi.orionadvisor.com/api/v1/Integrations/Notifications/Action/UpdateStatus?status=Deleted"

        results = []

        for notification in notifications:
            notification_id = notification.get("id")
            payload = f"[{notification_id}]"

            response_put = session.put(url_put, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
        
            if response_put.status_code == 200:
                print(f"Notification {notification_id} marked as Deleted:", response_put.text)
            else:
                print(f"Error deleting notification {notification_id}:", response_put.status_code, response_put.text)
        
            results.append({
                "notification_id": notification_id,
                "status_code": response_put.status_code,
                "response": response_put.text
            })

        return results  

    def create_new_household(self, session: requests.Session):
        url_get = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Accounts/NewPortfolio/New")
        print("Getting New Household household framework...")
        response_get = session.get(url_get)
        data = response_get.json()

        url_get = ("https://testapi.orionadvisor.com/api/v1/Settings/UserDefinedFields/Definitions/client")
        print("Getting Client User Defined Fields...")
        response_get = session.get(url_get)
        client_user_defined_fields = response_get.json()
        
        client_udf = []

        for item in client_user_defined_fields:
            new_item = {
                "entity": "Household",
                "value": None,  
                "name": item.get("description", "No Description Provided"),
                "input": None,
                "options": item.get("options", []),
                "type": item.get("type"),
                "sequence": item.get("sequence"),
                "code": item.get("code"),
                "category": item.get("category"),
                "securityCode": item.get("securityCode")
            }
            if new_item["category"] == "":
                new_item["category"] = "No Category"
            if new_item["category"] == None:
                new_item["category"] = "No Category"
            # if new_item["type"] == "Check box":
            #     new_item["value"] = False
            # if new_item["type"] == "Date":
            #     new_item["value"] = ""
            client_udf.append(new_item)

            # print(client_udf)
        else:
            if response_get.status_code == 200:
                print("User Defined Fields Set.")
            else:
                print("Something went wrong...:", response_get.status_code)

        url_get = ("https://testapi.orionadvisor.com/api/v1/Settings/UserDefinedFields/Definitions/registration")
        print("Getting Registration User Defined Fields...")
        response_get = session.get(url_get)
        registration_user_defined_fields = response_get.json()

        registration_udf = []

        for item in registration_user_defined_fields:
            new_item = {
                "entity": "Registration",
                "value": None,  
                "name": item.get("description", "No Description Provided"),
                "input": None,
                "options": item.get("options", []),
                "type": item.get("type"),
                "sequence": item.get("sequence"),
                "code": item.get("code"),
                "category": item.get("category", "No Category"),
                "securityCode": item.get("securityCode")
            }
            if new_item["category"] == "":
                new_item["category"] = "No Category"
            if new_item["category"] == None:
                new_item["category"] = "No Category"
            registration_udf.append(new_item)

            # print(registration_udf)
        else:
            if response_get.status_code == 200:
                print("User Defined Fields Set.")
            else:
                print("Something went wrong...:", response_get.status_code)

        url_get = ("https://testapi.orionadvisor.com/api/v1/Settings/UserDefinedFields/Definitions/account")
        print("Getting Account User Defined Fields...")
        response_get = session.get(url_get)
        account_user_defined_fields = response_get.json()

        account_udf = []

        for item in account_user_defined_fields:
            new_item = {
                "entity": "Account",
                "value": None,  
                "name": item.get("description", "No Description Provided"),
                "input": None,
                "options": item.get("options", []),
                "type": item.get("type"),
                "sequence": item.get("sequence"),
                "code": item.get("code"),
                "category": item.get("category", "No Category"),
                "securityCode": item.get("securityCode")
            }
            if new_item["category"] == "":
                new_item["category"] = "No Category"
            if new_item["category"] == None:
                new_item["category"] = "No Category"
            if new_item["name"] == "Managed Account":
                new_item["value"] = False
            if new_item["name"] == "Anniversary Date":
                new_item["value"] = ""
            if new_item["name"] == "Margin":
                new_item["value"] = False
            if new_item["name"] == "Hobby":
                new_item["value"] = ""
            if new_item["name"] == "TAS Last Reconciled Effective Date":
                new_item["value"] = None
                new_item["input"] = ""

            account_udf.append(new_item)

            # print(account_udf)
        else:
            if response_get.status_code == 200:
                print("User Defined Fields Set.")
            else:
                print("Something went wrong...:", response_get.status_code)

        firstName = input("Enter the desired First Name: ")
        lastName = input("Enter the desired Last Name: ")
        name = firstName + " " + lastName
        abort = input(f"The Full Name is: {name}. Press 'n' to abort: ")
        if abort == "n":
            return

        accountnumber = input("Enter the desired Account Number: ")
        abort = input(f"The Account Number is: {accountnumber} press 'n' to abort.")
        if abort == "n":
            return

        data["client"]["billing"]["statusType"] = "Ready to Bill"
        data["client"]["portfolio"]["firstName"] = firstName
        data["client"]["portfolio"]["lastName"] = lastName
        data["client"]["portfolio"]["name"] = name
        data["client"]["userDefinedFields"] = client_udf
        data["registration"]["portfolio"]["firstName"] = firstName
        data["registration"]["portfolio"]["lastName"] = lastName
        data["registration"]["portfolio"]["name"] = name
        data["registration"]["portfolio"]["typeId"] = 1
        data["registration"]["userDefinedFields"] = registration_udf
        data["account"]["portfolio"]["custodianId"] = 3
        data["account"]["portfolio"]["fundFamilyId"] = 45
        data["account"]["portfolio"]["accountStatusDescription"] = "Pending"
        data["account"]["portfolio"]["accountStatusDescription"] = "Pending"
        data["account"]["billing"]["custodialAccountNumber"] = accountnumber
        data["account"]["billing"]["useFeeHierarchy"] = False
        data["account"]["modelingInfo"]["dollarModelAmount"] = 0
        data["account"]["userDefinedFields"] = account_udf

        # json_data = json.dumps(data)

        session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

        #post the new household information
        url_post = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Accounts/NewPortfolio")
        response_post = session.post(url_post, json=data)
        if response_post.status_code == 200:
            print("New Household Created!!!", response_post.text)
        else:
            print("Error creating new household:", response_post.status_code, response_post.text)

        client_Id = response_post.json().get("client", {}).get("id")
        account_id = response_post.json().get("account", {}).get("id")
        account_number = response_post.json().get("account", {}).get("billing", {}).get("custodialAccountNumber")

        assetId = self.create_new_asset(session, account_id, account_number)
        self.create_starting_value_transaction(session, client_Id, assetId)
        self.create_cashflows(session, client_Id, assetId)

        print("Household Creation Complete!")

    def create_new_asset(self, session: requests.Session, account_Id, accountNumber):
        get_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Assets/Verbose/New")
        print("Getting Asset Framework...")
        response_get = session.get(get_url)

        asset_info = response_get.json()

        get_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Products/Search?Top=20&Search=cash")
        print("Getting Cash Product...")
        response_get = session.get(get_url)

        cash_product = None
        for product in response_get.json():
            if product.get("productName") == "CASH" and product.get("ticker") == "SAVINGS":
                cash_product = product
                break
        cash_product_id = cash_product.get("productId")

        get_url = ("https://testapi.orionadvisor.com/api/v1/Global/DownloadSymbols/Product/675681")
        print("Getting Download Symbol...")
        response_get = session.get(get_url)

        download_symbol_id = None
        for download_symbol in response_get.json():
            if download_symbol.get("symbol") == "SAVINGS":
                download_symbol_id = download_symbol.get("id")
                break

        asset_info["portfolio"]["productId"] = cash_product_id
        asset_info["portfolio"]["downloadSymbol"] = download_symbol_id
        asset_info["portfolio"]["accountNumber"] = accountNumber
        asset_info["portfolio"]["accountId"] = account_Id
        asset_info["portfolio"]["currentShares"] = 0

        payload = {"portfolio": asset_info["portfolio"]}

        post_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Assets/Verbose/")
        response_post = session.post(post_url, json=payload)
        if response_post.status_code == 200:
            print("Asset Created!!!", response_post.text)
        else:
            print("Error creating new asset:", response_post.status_code, response_post.text)
            print("Here the json...")
            print(json.dumps(payload, indent=4))

        assetId = response_post.json().get("id")
        return assetId

    def create_starting_value_transaction(self, session: requests.Session, client_Id, asset_Id):
        get_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/New")
        print("Getting Transaction Framework...")
        response_get = session.get(get_url)

        transaction_info = response_get.json()

        transaction_info["portfolio"]["transTypeId"] = 61   #Starting Value
        transaction_info["portfolio"]["transDate"] = "01/01/2005"
        transaction_info["portfolio"]["transTime"] = "1900-01-01T21:30:00.000Z"
        transaction_info["portfolio"]["transAmount"] = 100000
        transaction_info["portfolio"]["noUnits"] = 100000
        transaction_info["portfolio"]["navPrice"] = 1
        transaction_info["portfolio"]["assetId"] = asset_Id
        transaction_info["portfolio"]["notes"] = "Python API Script"
        transaction_info["portfolio"]["advisorNotes"] = "Python API Script"
        transaction_info["portfolio"]["clientId"] = client_Id

        payload = {"portfolio": transaction_info["portfolio"],
                   "id": 0}

        post_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/")
        response_post = session.post(post_url, json=payload)
        print("Starting Value Transaction Created!!!")

    def create_cashflows(self, session: requests.Session, client_Id, asset_Id):
        while True:
            choice = input("Would you like to create cashflows? (y/n):").strip().lower()
            if choice == "n":
                return
            elif choice  == "y":
                get_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/New")
                print("Getting Cash Flow Transaction Framework...")
                cashflow_info = None
                try:
                    response_get = session.get(get_url)
                    response_get.raise_for_status()
                    cashflow_info = response_get.json()
                except requests.exceptions.RequestException as e:
                    print(f"Failed to retrieve cash flow template: {e}")
                    return

                cashflow_info["portfolio"]["transTypeId"] = 39   #Merge In From Other Account
                cashflow_info["portfolio"]["transDate"] = "02/15/2025"
                cashflow_info["portfolio"]["transTime"] = "1900-01-01T21:30:00.000Z"
                cashflow_info["portfolio"]["transAmount"] = 1000
                cashflow_info["portfolio"]["noUnits"] = 1000
                cashflow_info["portfolio"]["navPrice"] = 1
                cashflow_info["portfolio"]["assetId"] = asset_Id
                cashflow_info["portfolio"]["notes"] = "Python API Script"
                cashflow_info["portfolio"]["advisorNotes"] = "Python API Script"
                cashflow_info["portfolio"]["clientId"] = client_Id

                payload = {"portfolio": cashflow_info["portfolio"],
                            "id": 0}

                post_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/")
                response_post = session.post(post_url, json=payload)

                merge_in_transaction_id = response_post.json().get("id")

                get_url = (f"https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/{merge_in_transaction_id}?expand=billing")
                print("Getting Merge In Transaction...")
                response_get = session.get(get_url)

                merge_in_transaction = response_get.json()

                merge_in_transaction["billing"]["isNMReady"] = True

                put_url = (f"https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/{merge_in_transaction_id}?reverseOffset=false")

                payload = {"billing": merge_in_transaction["billing"],
                           "id": merge_in_transaction_id}

                response_put = session.put(put_url, json=payload)
                if response_put.status_code == 200:
                    print("Merge In Transaction Created!!!", response_put.text)
                else:
                    print("Error sad:", response_put.status_code, response_put.text)
                
                get_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/New")
                print("Getting Cash Flow Transaction Framework...")
                response_get = session.get(get_url)

                cashflow_info = response_get.json()

                cashflow_info["portfolio"]["transTypeId"] = 42   #Merge Out From Other Account
                cashflow_info["portfolio"]["transDate"] = "01/20/2025"
                cashflow_info["portfolio"]["transTime"] = "1900-01-01T21:30:00.000Z"
                cashflow_info["portfolio"]["transAmount"] = 500
                cashflow_info["portfolio"]["noUnits"] = 500
                cashflow_info["portfolio"]["navPrice"] = 1
                cashflow_info["portfolio"]["assetId"] = asset_Id
                cashflow_info["portfolio"]["notes"] = "Python API Script"
                cashflow_info["portfolio"]["advisorNotes"] = "Python API Script"
                cashflow_info["portfolio"]["clientId"] = client_Id

                payload = {"portfolio": cashflow_info["portfolio"],
                            "id": 0}

                post_url = ("https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/")
                response_post = session.post(post_url, json=payload)

                merge_out_transaction_id = response_post.json().get("id")

                get_url = (f"https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/{merge_out_transaction_id}?expand=billing")
                print("Getting Merge Out Transaction...")
                response_get = session.get(get_url)

                merge_out_transaction = response_get.json()

                merge_out_transaction["billing"]["isAdvanceBilled"] = True

                put_url = (f"https://testapi.orionadvisor.com/api/v1/Portfolio/Transactions/Verbose/{merge_out_transaction_id}?reverseOffset=false")

                payload = {"billing": merge_out_transaction["billing"],
                           "id": merge_out_transaction_id}

                response_put = session.put(put_url, json=payload)
                if response_put.status_code == 200:
                    print("Merge Out Transaction Created!!!", response_put.text)
                else:
                    print("Error sad:", response_put.status_code, response_put.text)

                break
            else:
                print("Invalid choice. Please enter y or n.")
            






