import requests
import time

from customer_validation.config import (
    APP_ID,
    API_KEY,
    CUSTOMER_OBJECT,
    RECORDS_OBJECT,
    ISSUES_OBJECT,
    CUSTOMER_FIELDS,
    RECORD_FIELDS,
    ISSUE_FIELDS
)

headers = {
    "X-Knack-Application-Id": APP_ID,
    "X-Knack-REST-API-Key": API_KEY,
}

CUSTOMER_URL = (
    f"https://api.knack.com/v1/objects/{CUSTOMER_OBJECT}/records"
    
)
RECORDS_URL = (
    f"https://api.knack.com/v1/objects/{RECORDS_OBJECT}/records"
)

ISSUES_URL = (
    f"https://api.knack.com/v1/objects/{ISSUES_OBJECT}/records"
)
###########         FETCHING DATA FROM KNACK      ###############
def get_customers():

    response = requests.get(
        CUSTOMER_URL,
        headers=headers
    )
    

    return response.json()


#-----------------------------------------------------------
############      SENDING DATA TO RECORDS TABLE    ###################
def send_to_records(customer):

    #EXTRACTING JUST EMAIL SEPARATELY FROM DICTIONARY, EMAIL IS A KEYWORD HERE
    raw_email = customer.get(CUSTOMER_FIELDS["email"], "")
    if isinstance(raw_email, dict):
        email = raw_email.get("email", "")
    else:
        email = raw_email


    #MAPPING DATA TO RECORDS TABLE FIELDS FROM CUSTOMERS TABLE
    data = {
        RECORD_FIELDS["customer_id"]: customer.get(CUSTOMER_FIELDS["customer_id"]),
        RECORD_FIELDS["first_name"]: customer.get(CUSTOMER_FIELDS["first_name"]),   # First Name
        RECORD_FIELDS["last_name"]: customer.get(CUSTOMER_FIELDS["last_name"]),   # Last Name
        RECORD_FIELDS["email"]: email,                     # Email
        RECORD_FIELDS["phone"]: customer.get(CUSTOMER_FIELDS["phone"]),   # Phone
        RECORD_FIELDS["age"]: customer.get(CUSTOMER_FIELDS["age"]),   # Age
        RECORD_FIELDS["country"]: customer.get(CUSTOMER_FIELDS["country"]),   # Country
        RECORD_FIELDS["join_date"]: customer.get(CUSTOMER_FIELDS["join_date"]),   # Join Date
        RECORD_FIELDS["balance"]: customer.get(CUSTOMER_FIELDS["balance"]),   # Balance
        RECORD_FIELDS["status"]: customer.get(CUSTOMER_FIELDS["status"]),   # Status
        # CONNECTION FIELD 'CUSTOMER' WILL STORE KNACK
        # INTERNAL UNIQUE ID ASSIGNED TO  EACH CUSTOMER
        # IT WILL HELP TO IDENTIFY WHICH CUSTOMER OWNS THIS ROW
        RECORD_FIELDS["Customer"]: customer.get("id"),
    }
    # APPLIED FOR LOOP TO RETRY IF UPLOAD FAILED 
    for retry in range(3):
        response = requests.post(
            RECORDS_URL,
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response
        time.sleep(30)
    return response
    


#-----------------------------------------------------------
############      SENDING DATA TO ISSUES TABLE    ###################
def send_to_issues(customer, issues):
#----------------------------------------------------
###########     EXTRACTING JUST EMAIL SEPARATELY FROM DICTIONARY, EMAIL IS A KEYWORD HERE ############
#-----------------------------------------------------
    raw_email = customer.get(CUSTOMER_FIELDS["email"], "")
    if isinstance(raw_email, dict):
        email = raw_email.get("email", "")
    else:
        email = raw_email

    ##  MERGING ISSUES TO STORE IN ONE FIELD JOINING THEM 
    issue_detail = ", ".join(issues)

    #MAPPING DATA TO ISSUES TABLE FIELDS 
    data = {
        ISSUE_FIELDS["customer_id"] : customer.get(CUSTOMER_FIELDS["customer_id"]),   #customer id
        ISSUE_FIELDS["first_name"] : customer.get(CUSTOMER_FIELDS["first_name"]),   # First Name
        ISSUE_FIELDS["last_name"] : customer.get(CUSTOMER_FIELDS["last_name"]),   # Last Name
        ISSUE_FIELDS["email"] : email,                       # Email
        ISSUE_FIELDS["phone"] : customer.get(CUSTOMER_FIELDS["phone"]),  # Phone
        ISSUE_FIELDS["age"] : customer.get(CUSTOMER_FIELDS["age"]),   # Age
        ISSUE_FIELDS["country"] : customer.get(CUSTOMER_FIELDS["country"]),   # Country
        ISSUE_FIELDS["join_date"] : customer.get(CUSTOMER_FIELDS["join_date"]),   # Join Date
        ISSUE_FIELDS["balance"] : customer.get(CUSTOMER_FIELDS["balance"]),   # Balance
        ISSUE_FIELDS["status"] : customer.get(CUSTOMER_FIELDS["status"]),   # Status
        ISSUE_FIELDS["issue_detail"] : issue_detail,
        ISSUE_FIELDS["customer_connection"] : customer.get("id"),


    }
#-----------------------------------------------
#####    SENDING DATA TO KNACK ###########
    for retry in range(3):
            response = requests.post(
                ISSUES_URL,
                headers=headers,
                json=data
            )
            if response.status_code == 200:
                return response
            time.sleep(30)
    return response
     # -----------------------------
    # Print response for debugging
    # -----------------------------
    #print("Status Code:", response.status_code)
    #print("Response Text:", response.text)

##########  UPDATING EXISTING CUSTOMER'S FIELD TO TRUE IF HE IS UPLOADED TO RECORDS OR ISSUES
def update_customer(customer):
    response = requests.put(
        f"{CUSTOMER_URL}/{customer['id']}",
        headers=headers,
        json={CUSTOMER_FIELDS["is_processed"]:True}
    )
    return response
#############  ADDING 'FAILED' HEADING TO THOSE ROW OF CUSTOMERS TABLE WHICH ARE FAILED DURING UPLOAD ##########
def upload_status(customer, response):
    
    response = requests.put(
        f"{CUSTOMER_URL}/{customer['id']}",
        headers=headers,
        json={CUSTOMER_FIELDS["upload_status"]:"Failed",
              CUSTOMER_FIELDS["fail_reason"]:error}
        
    )   
    return response
#######  ADDING REASON FOR FAILED UPLOADING TO CUSTOMER TABLE ROW #####




