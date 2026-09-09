import requests, time


APP_ID = "6aa1450abb5820e0bdf1d217"
API_KEY = "158893b8-c65e-4a49-9a22-281fc2a7f106"


CUSTOMER_OBJECT = "object_3"
ISSUES_OBJECT = "object_4"
RECORDS_OBJECT = "object_5"
USERS_OBJECT = "object_6"

THREAD_WORKERS = 3

############    CUSTOMERS MAPPING ########
CUSTOMER_FIELDS = {
    "customer_id": "field_23",
    "first_name": "field_30",
    "last_name": "field_31",
    "email": "field_32_raw",
    "phone": "field_34",
    "age": "field_35",
    "country": "field_36",
    "join_date": "field_37",
    "balance": "field_38",
    "status": "field_39",
    "is_processed": "field_41",
    "upload_status": "field_42",
    "fail_reason": "field_40",
    "Assigned_user": "field_92",
    "AI_fixed_issues":"field_43"
}
############   RECORDS MAPPING #########
RECORD_FIELDS = {
    "customer_id": "field_62",
    "first_name": "field_69",
    "last_name": "field_70",
    "email": "field_71",
    "phone": "field_72",
    "age": "field_73",
    "country": "field_74",
    "join_date": "field_75",
    "balance": "field_76",
    "status": "field_77",
    "Customer": "field_78",
}

######## ISSUES MAPPING ########
ISSUE_FIELDS = {
    "customer_id": "field_44",
    "first_name": "field_51",
    "last_name": "field_52",
    "email": "field_53",
    "phone": "field_54",
    "age": "field_55",
    "country": "field_56",
    "join_date": "field_57",
    "balance": "field_61",
    "status": "field_58",
    "issue_detail": "field_59",
    "customer_connection": "field_60",
}

######## USERS MAPPING ########
USER_FIELDS = {
    "Name": "field_79",
    "Last Assigned User": "field_86",
}

######## retry logic if upload failed
def retry_upload(url, headers, data):
    for retry in range(3):
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response
        time.sleep(3)
    return response
    

        
    
        
