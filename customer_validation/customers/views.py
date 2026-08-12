from django.shortcuts import render

from django.http import JsonResponse
from .services import (
    get_customers,
    send_to_records,
    send_to_issues,
    update_customer,
    upload_status_fail_reason,
    get_users,
    assign_user,
    update_assigned_user
)
from .validators import validate_customer
from customer_validation.config import CUSTOMER_FIELDS, USER_FIELDS
from .utils.email import upload_fail_email, application_error_email



def customer_list(request):
    """
    Fetch customer data, validate it,
    and upload it to the appropriate table.
    """
    failed_rows = []
    try:
        # Fetch all customer records from Knack
        customers = get_customers()

        # FAILED ROWS LIST IS CREATED TO STORE ALL FAILED ROWS
        users = get_users()
        
        # extract list of users from whole dictionary of users
        user_records = users["records"]
        
        # STORAGE ROW IS THE ROW IN WHICH LAST ASSIGNED USER IS LOCATED SO WE HAVE TO EXTRACT IT
        storage_row = user_records[0]
        last_assigned_user = storage_row.get(USER_FIELDS["Last Assigned User"])
        

        

        # Process each customer one by one
        for customer in customers["records"]:

            # Skip customers that are already processed
            if customer.get(CUSTOMER_FIELDS["is_processed"]) == "Yes":
                print(
                    f"{customer.get(CUSTOMER_FIELDS['customer_id'])} is already processed"
                )
                continue

            # Validate the current customer
            issues = validate_customer(customer)

            # Upload valid customer to Records table
            if not issues:
                response = send_to_records(customer)

                # Mark customer as processed if upload succeeds
                if response.status_code == 200:
                    update_customer(customer)

                # Mark upload as failed if upload fails
                else:
                    upload_status_fail_reason(customer, response)
            
                # Find the last assigned user's position
                    last_index = -1
                    for index, user_record in enumerate(user_records):
                        if user_record['id'] == last_assigned_user:
                            last_index = index
                            break
                        # Select the next user
                    next_index = (last_index + 1) % len(user_records)
                    user = user_records[next_index]
                    
                    
                    
## ASSIGN USER FUCNTION CREATED TO UPDATE THE 'ASSIGNED_USER' FIELD WITH USER NAME FROM USERS TABLE
                    assign_user(customer, user)
## THIS FUCNTION UPDATES THE LAST ASSIGNED USER FIELD IN USERS TABLE WITH THE USER ON WHICH PROGRAM 
## STOPPED TO START AGAIN THE CYCLE FROM THIS SPECIFIC USER 
                    update_assigned_user(user, storage_row)
                    
# Update Python variable for the next failed customer
                    last_assigned_user = user["id"]
                    
                    
                    
                    failed_rows.append(
                        {
                            "customer_id": customer.get(CUSTOMER_FIELDS["customer_id"]),
                            "first_name": customer.get(CUSTOMER_FIELDS["first_name"]),
                            "last_name": customer.get(CUSTOMER_FIELDS["last_name"]),
                            "upload_status": "Failed",
                            "fail_reason": response.text,
                        }
                    )
###################################################################################################
################### Upload invalid customer to Issues table ###########################################
            else:
                response = send_to_issues(customer, issues)

                # Mark customer as processed if upload succeeds
                if response.status_code == 200:
                    update_customer(customer)

                # Mark upload_status as failed if upload fails
                else:
                    upload_status_fail_reason(customer, response)
# Start with -1 to indicate that the last assigned user has not been found yet
                    last_index = -1
# GIVE ME USER RECORDS FROM USER_RECORDS LIST WITH INDEX POSITION AND USER DATA BOTH
                    for index, user_record in enumerate(user_records):
                        if user_record['id'] == last_assigned_user:
                            last_index = index
                            break
                    # Select the next user
                    next_index = (last_index + 1) % len(user_records)
                    user = user_records[next_index]
                                             
                    ## ASSIGN USER FUCNTION CREATED TO UPDATE THE 'ASSIGNED_USER' FIELD WITH USER NAME FROM USERS TABLE
                    assign_user(customer, user)
                    ## THIS FUCNTION UPDATES THE LAST ASSIGNED USER FIELD IN USERS TABLE WITH THE USER ON WHICH PROGRAM 
                    ## STOPPED TO START AGAIN THE CYCLE FROM THIS SPECIFIC USER 
                    update_assigned_user(user, storage_row)
                                        
                    # Update Python variable for the next failed customer
                    last_assigned_user = user["id"]
                    
                    
                    failed_rows.append(
                        {
                            "customer_id": customer.get(CUSTOMER_FIELDS["customer_id"]),
                            "first_name": customer.get(CUSTOMER_FIELDS["first_name"]),
                            "last_name": customer.get(CUSTOMER_FIELDS["last_name"]),
                            "upload_status": "Failed",
                            "fail_reason": response.text,
                        }
                    )
        if failed_rows:
            upload_fail_email(failed_rows)

        # Return customer data as JSON response
        return JsonResponse(customers)

    # EXCEPT STATEMENT IS IMPLEMENTED THAT IF WHOLE UPPER CODE IS NOT PROCESSED THEN APPLICATION ERROR EMAIL WILL BE SENT
    except Exception as error:
        application_error_email(error)
        return JsonResponse({"error": "Application error"}, status=500)
