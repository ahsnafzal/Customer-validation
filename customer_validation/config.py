import requests, time


APP_ID = "6a8c49bd2e0c0d59e98bda1e"
API_KEY = "5d43922b-885d-440a-b50b-334b2e358292"


CUSTOMER_OBJECT = "object_3"
ISSUES_OBJECT = "object_44"
RECORDS_OBJECT = "object_55"
USERS_OBJECT = "object_6"

THREAD_WORKERS = 3

############    CUSTOMERS MAPPING ########
CUSTOMER_FIELDS = {
    "customer_id": "field_30",
    "first_name": "field_31",
    "last_name": "field_32",
    "email": "field_33_raw",
    "phone": "field_34",
    "age": "field_35",
    "country": "field_36",
    "join_date": "field_37",
    "balance": "field_38",
    "status": "field_39",
    "is_processed": "field_65",
    "upload_status": "field_66",
    "fail_reason": "field_63",
    "Assigned_user": "field_67",
}
############   RECORDS MAPPING #########
RECORD_FIELDS = {
    "customer_id": "field_104",
    "first_name": "field_105",
    "last_name": "field_106",
    "email": "field_109",
    "phone": "field_110",
    "age": "field_111",
    "country": "field_112",
    "join_date": "field_115",
    "balance": "field_116",
    "status": "field_117",
    "Customer": "field_118",
}

######## ISSUES MAPPING ########
ISSUE_FIELDS = {
    "customer_id": "field_91",
    "first_name": "field_92",
    "last_name": "field_93",
    "email": "field_94",
    "phone": "field_95",
    "age": "field_96",
    "country": "field_97",
    "join_date": "field_98",
    "balance": "field_113",
    "status": "field_101",
    "issue_detail": "field_102",
    "customer_connection": "field_103",
}

######## USERS MAPPING ########
USER_FIELDS = {
    "Name": "field_54",
    "Last Assigned User": "field_61",
}

######## retry logic if upload failed
def retry_upload(url, headers, data):
    for retry in range(3):
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response
        time.sleep(3)
    return response
    

        
    
        
