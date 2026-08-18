from django.shortcuts import render

from django.http import JsonResponse
from .services import (
    send_to_records,
    send_to_issues,
    update_customer,
    upload_status_fail_reason,
    get_users,
    assign_user,
    update_assigned_user,
    save_to_batch,
    get_oldest_batch,
    get_customers_from_batch
)
from .validators import validate_customer
from customer_validation.config import CUSTOMER_FIELDS, USER_FIELDS
from .utils.email import upload_fail_email, application_error_email


def download(request):
# SAVE_TO_BATCH CONTAIN GET_CUSTOMERS() SO NO NEED TO CALL IT AGAIN HERE
    batch = save_to_batch()
    
    return JsonResponse({
        "message":"successfully downloaded and saved data"
    })




def upload_validate(request):
    
# failed rows is a list which will which will contain the all failed rows (customers) after the process
    failed_rows = []
    
    try:
    
    
# RUN THE FUNCTION TO GET OLDEST BATCH FROM BATCH TABLE AND STORED IN VARIABLE batch
        batch = get_oldest_batch()
    
# IF THERE IS NOT ANY BATCH IN BATCH TABLE RETURN NO PENDING BATCH FOUND
        if not batch:
            return JsonResponse({
                "message":"There is not any pending batch"
            })
        
# RUN THIS FUNCTION TO GET ALL CUSTOMERS STORED IN THAT SPECIFIC BATCH
        customers = get_customers_from_batch(batch)
# GET USERS FROM KNACK USERS TABLE
        users = get_users()
        # extract list of users from whole dictionary of users
        user_records = users["records"]
                
# STORAGE ROW IS THE ROW IN WHICH LAST ASSIGNED USER IS LOCATED SO WE HAVE TO EXTRACT IT
        storage_row = user_records[0]
        last_assigned_user = storage_row.get(USER_FIELDS["Last Assigned User"])
    
# NOW LOOP THROUGH THESE ALL CUSTOMERS in this pending batch
        for pending_customer in customers:
        
# Take the actual customer data out of the database record and put it into the variable customer
# because we used customer variable to get data like customer.name, customer.email etc
            customer = pending_customer.data
        
# skip the customer who is already processed
            if customer.get(CUSTOMER_FIELDS["is_processed"]) == "Yes":
                print (
                    f"{customer.get(CUSTOMER_FIELDS["customer_id"])} is already processed"
                    )
                continue
        
# validate the customer and store issues in issues list 
            issues = validate_customer(customer)
        
            if not issues:
                response = send_to_records(customer)
                if response.status_code == 200:
# if upload is successful update the upload status to TRUE
                    update_customer(customer)
                else:
# if upload is not successful then mark upload_status 'FAIL' with 'fail reason'
                    upload_status_fail_reason(customer, response)
                    
##################### ASSIGNING USER TO FAILED ROWS LOGIC IN A CYCLE #######################
                   #Find the last assigned user.
                   #Get their index/position in the user list.
                   #Select the next user.
                   #% makes the cycle restart from the first user.
                   #Assign that selected user to the customer.
                    last_index = -1  
                    for index, user_record in enumerate(user_records):
                        if user_record['id'] == last_assigned_user:
                            last_index = index 
                            break
                    next_index = (last_index+1) % len(user_records)
# this user will be used in services which will tell KNACK that assign that user to this row
                    user = user_records[next_index]
## ASSIGN USER FUCNTION CREATED TO UPDATE THE 'ASSIGNED_USER' FIELD 
                    assign_user(customer, user)
## This function helps to update the last assigned user field in users table, with the user assigned
## just now above by the assign_user() function
                    update_assigned_user(user, storage_row)
# Save the ID of the user we just assigned as the new "last assigned user"
                    last_assigned_user = user['id']
                    
                       
                    #APPEND THE FAILED ROWS LIST with the following information of failed customers
                    # to send email for failure of upload       
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
            # use two parametres (customer and issues) because we have to send 
            # also issue detail along with customers
                response = send_to_issues(customer, issues)
            
                if response.status_code == 200:
# if upload is successful update the upload status to TRUE
                    update_customer(customer)
                else:
                    upload_status_fail_reason(customer, response)
##################### ASSIGNING USER TO FAILED ROWS LOGIC IN A CYCLE #######################
                   #Find the last assigned user.
                   #Get their index/position in the user list.
                   #Select the next user.
                   #% makes the cycle restart from the first user.
                   #Assign that selected user to the customer.
                    last_index = -1  
                    for index, user_record in enumerate(user_records):
                        if user_record['id'] == last_assigned_user:
                            last_index = index 
                            break
                    next_index = (last_index+1) % len(user_records)
# this user will be used in services which will tell KNACK that assign that user to this row
                    user = user_records[next_index]
## ASSIGN USER FUCNTION CREATED TO UPDATE THE 'ASSIGNED_USER' FIELD 
                    assign_user(customer, user)
## This function helps to update the last assigned user field in users table, with the user assigned
## just now above by the assign_user() function
                    update_assigned_user(user, storage_row)
# Save the ID of the user we just assigned as the new "last assigned user"
                    last_assigned_user = user['id']
                    
                    
                    
                       
## APPEND THE FAILED ROWS LIST WITH THE FOLLOWING INFORMATION OF failed CUSTOMERS to send email
                    failed_rows.append(
                        {
                            "customer_id": customer.get(CUSTOMER_FIELDS["customer_id"]),
                            "first_name": customer.get(CUSTOMER_FIELDS["first_name"]),
                            "last_name": customer.get(CUSTOMER_FIELDS["last_name"]),
                            "upload_status": "Failed",
                            "fail_reason": response.text,
                        }
                    )
    
                    
# is there are failed rows then send email to notify that following rows are failed 
        if failed_rows:
            upload_fail_email(failed_rows)
# Return customer data as JSON response
        return JsonResponse(customers)
    
# after ending TRY statement EXCEPT statement will run if any error occur in whole above process
    except Exception as error:
        application_error_email(error)
        return JsonResponse({"error": "Application error"}, status=500)
                
            
            
        
