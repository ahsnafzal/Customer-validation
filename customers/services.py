import requests

import json
from customer_validation.config import retry_upload
from .models import Batch, PendingCustomer

from customer_validation.config import (
    APP_ID,
    API_KEY,
    CUSTOMER_OBJECT,
    RECORDS_OBJECT,
    ISSUES_OBJECT,
    USERS_OBJECT,
    CUSTOMER_FIELDS,
    RECORD_FIELDS,
    ISSUE_FIELDS,
    USER_FIELDS
    
)

headers = {
    "X-Knack-Application-Id": APP_ID,
    "X-Knack-REST-API-Key": API_KEY,
}

CUSTOMER_URL = f"https://api.knack.com/v1/objects/{CUSTOMER_OBJECT}/records"
RECORDS_URL = f"https://api.knack.com/v1/objects/{RECORDS_OBJECT}/records"

ISSUES_URL = f"https://api.knack.com/v1/objects/{ISSUES_OBJECT}/records"
USERS_URL = f"https://api.knack.com/v1/objects/{USERS_OBJECT}/records"


###########         FETCHING DATA FROM KNACK      ###############
def get_customers():

    # ADDING A FILTER TO SKIP THE DOWNLOADING OF ROWS WITH FAILED STATUS
    filters = {
        "rules": [
            {
                "field": CUSTOMER_FIELDS["upload_status"],
                "operator": "is not",
                "value": "Failed",
            }
        ]
    }

    response = requests.get(
        CUSTOMER_URL, headers=headers, params={"filters": json.dumps(filters)}
    )

    return response.json()

###################################################################################################
# Fetch customers from get_customers() and save them as a new pending batch to django db sqlite
# to use that data for validating and uploading 
def save_to_batch():
    customers = get_customers()
    batch = Batch.objects.create()
    
    for customer in customers["records"]:
        PendingCustomer.objects.create(
            batch=batch,
            data=customer
        )
    return batch


###########################################################################
# FUNCTION TO GET OLDEST BATCH SAVED IN DATABASE BATCH TABLE TO VALIDATE AND UPLOAD DATA IN IT
def get_oldest_batch():
    # get the batch with pending status and first oldest created 
    batch = Batch.objects.filter(status="pending").order_by("created_at").first()
    return batch


## FUNCTION TO FETCH ALL CUSTOMERS INSIDE EACH THE BATCH
def get_customers_from_batch(batch):
    # Give me all PendingCustomer records that belong to this batch
    customers = batch.customers.all()
    return customers
    



    



# -----------------------------------------------------------
############      SENDING DATA TO RECORDS TABLE    ###################
def send_to_records(customer):

    # EXTRACTING JUST EMAIL SEPARATELY FROM DICTIONARY, EMAIL IS A KEYWORD HERE
    raw_email = customer.get(CUSTOMER_FIELDS["email"], "")
    if isinstance(raw_email, dict):
        email = raw_email.get("email", "")
    else:
        email = raw_email

    # MAPPING DATA TO RECORDS TABLE FIELDS FROM CUSTOMERS TABLE
    data = {
        RECORD_FIELDS["customer_id"]: customer.get(CUSTOMER_FIELDS["customer_id"]),
        RECORD_FIELDS["first_name"]: customer.get(
            CUSTOMER_FIELDS["first_name"]
        ),  # First Name
        RECORD_FIELDS["last_name"]: customer.get(
            CUSTOMER_FIELDS["last_name"]
        ),  # Last Name
        RECORD_FIELDS["email"]: email,  # Email
        RECORD_FIELDS["phone"]: customer.get(CUSTOMER_FIELDS["phone"]),  # Phone
        RECORD_FIELDS["age"]: customer.get(CUSTOMER_FIELDS["age"]),  # Age
        RECORD_FIELDS["country"]: customer.get(CUSTOMER_FIELDS["country"]),  # Country
        RECORD_FIELDS["join_date"]: customer.get(
            CUSTOMER_FIELDS["join_date"]
        ),  # Join Date
        RECORD_FIELDS["balance"]: customer.get(CUSTOMER_FIELDS["balance"]),  # Balance
        RECORD_FIELDS["status"]: customer.get(CUSTOMER_FIELDS["status"]),  # Status
        # CONNECTION FIELD 'CUSTOMER' WILL STORE KNACK
        # INTERNAL UNIQUE ID ASSIGNED TO  EACH CUSTOMER
        # IT WILL HELP TO IDENTIFY WHICH CUSTOMER OWNS THIS ROW
        RECORD_FIELDS["Customer"]: customer.get("id"),
    }
    # APPLIED FOR LOOP TO RETRY IF UPLOAD FAILED
    response = retry_upload(RECORDS_URL, headers, data)
    return response


# -----------------------------------------------------------
############      SENDING DATA TO ISSUES TABLE    ###################
def send_to_issues(customer, issues):
    # ----------------------------------------------------
    ###########     EXTRACTING JUST EMAIL SEPARATELY FROM DICTIONARY, EMAIL IS A KEYWORD HERE ############
    # -----------------------------------------------------
    raw_email = customer.get(CUSTOMER_FIELDS["email"], "")
    if isinstance(raw_email, dict):
        email = raw_email.get("email", "")
    else:
        email = raw_email

    ##  MERGING ISSUES TO STORE IN ONE FIELD JOINING THEM
    issue_detail = ", ".join(issues)

    # MAPPING DATA TO ISSUES TABLE FIELDS
    data = {
        ISSUE_FIELDS["customer_id"]: customer.get(
            CUSTOMER_FIELDS["customer_id"]
        ),  # customer id
        ISSUE_FIELDS["first_name"]: customer.get(
            CUSTOMER_FIELDS["first_name"]
        ),  # First Name
        ISSUE_FIELDS["last_name"]: customer.get(
            CUSTOMER_FIELDS["last_name"]
        ),  # Last Name
        ISSUE_FIELDS["email"]: email,  # Email
        ISSUE_FIELDS["phone"]: customer.get(CUSTOMER_FIELDS["phone"]),  # Phone
        ISSUE_FIELDS["age"]: customer.get(CUSTOMER_FIELDS["age"]),  # Age
        ISSUE_FIELDS["country"]: customer.get(CUSTOMER_FIELDS["country"]),  # Country
        ISSUE_FIELDS["join_date"]: customer.get(
            CUSTOMER_FIELDS["join_date"]
        ),  # Join Date
        ISSUE_FIELDS["balance"]: customer.get(CUSTOMER_FIELDS["balance"]),  # Balance
        ISSUE_FIELDS["status"]: customer.get(CUSTOMER_FIELDS["status"]),  # Status
        ISSUE_FIELDS["issue_detail"]: issue_detail,
        ISSUE_FIELDS["customer_connection"]: customer.get("id"),
    }
    # -----------------------------------------------
    #####    retry logic if upload fails ###########
    response = retry_upload(ISSUES_URL, headers, data)
    print (response.text)
    return response


##########  UPDATING EXISTING CUSTOMER'S FIELD TO TRUE IF HE IS UPLOADED TO RECORDS OR ISSUES
def update_customer(customer):
    response = requests.put(
        f"{CUSTOMER_URL}/{customer['id']}",
        headers=headers,
        json={CUSTOMER_FIELDS["is_processed"]: True},
    )
    return response


#############  ADDING 'FAILED' AND 'FAIL REASON' HEADING TO THOSE ROW OF CUSTOMERS TABLE WHICH ARE FAILED DURING UPLOAD ##########
def upload_status_fail_reason(customer, response):
    error = response.text
    response = requests.put(
        f"{CUSTOMER_URL}/{customer['id']}",
        headers=headers,
        json={
            CUSTOMER_FIELDS["upload_status"]: "Failed",
            # ERROR WILL SHOW FAIL REASON OF UPLOADING
            CUSTOMER_FIELDS["fail_reason"]: error,
        },
    )
    return response


# getting users from knack users table
def get_users():
    response = requests.get(
        USERS_URL,
        headers=headers,
    )
    return response.json()


## ASSIGN USER FUCNTION CREATED TO UPDATE THE 'ASSIGNED_USER' FIELD WITH USER NAME FROM USERS TABLE
def assign_user(customer, user):

    response = requests.put(
        f"{CUSTOMER_URL}/{customer['id']}",
        headers=headers,
        json={CUSTOMER_FIELDS["Assigned_user"]: user["id"]},
    )
    return response

## Function to update existing field in users table to assign last user assigned by enumerate cycle
def update_assigned_user(user, storage_row ):
    #storage_row   → the Users-table row used to store the state
    response = requests.put(
        f"{USERS_URL}/{storage_row['id']}",
        headers=headers,
        json={USER_FIELDS["Last Assigned User"]:user['id']}
    )
    return response