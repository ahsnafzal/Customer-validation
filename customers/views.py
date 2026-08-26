from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


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
from customer_validation.config import CUSTOMER_FIELDS, USER_FIELDS, THREAD_WORKERS
from .utils.email import upload_fail_email, application_error_email
from concurrent.futures import ThreadPoolExecutor


class DownloadView(APIView):
    def get(self, request):
# SAVE_TO_BATCH CONTAIN GET_CUSTOMERS() SO NO NEED TO CALL IT AGAIN HERE
        batch = save_to_batch()
    
        return Response({
            "message":"successfully downloaded and saved data"
        })





                


@api_view(["POST"])
def process_customer(request):

    # --------------------------------------------------
    # MAIN THREAD
    # --------------------------------------------------
    try:
        
    # Get the oldest pending batch
    
        batch = get_oldest_batch()

        if not batch:
            return Response({
                "message": "There is no pending batch"
            })

    # Get all customers belonging to this batch
    
        customers = get_customers_from_batch(batch)
        
        
        
        
        
# GET USERS FROM KNACK USERS TABLE TO USE THEM FOR ASSIGNING USER TO FAILD CUSTOMER ONLY
        users = get_users()
        # extract list of users from whole dictionary of users
        user_records = users["records"]
                
# STORAGE ROW IS THE ROW IN WHICH LAST ASSIGNED USER IS LOCATED SO WE HAVE TO EXTRACT IT
        storage_row = user_records[0]
        last_assigned_user = storage_row.get(USER_FIELDS["Last Assigned User"])



    # This list will store Future objects
    
        futures = []
    
        failed_rows = []

    # 'THREAD_WORKERS' defined in config.py 
        with ThreadPoolExecutor(max_workers=THREAD_WORKERS) as executor:

        # --------------------------------------------------
        # SUBMIT CUSTOMERS TO WORKER THREADS
        # --------------------------------------------------

            for pending_customer in customers:

                customer = pending_customer.data

            # Skip customers which have already been processed
                if customer.get(CUSTOMER_FIELDS["is_processed"]) == "Yes":

                    print(
                        f"{customer.get(CUSTOMER_FIELDS['customer_id'])} "
                        "is already processed"
                    )

                    continue

# Give this customer to a worker thread
                future = executor.submit(process_one_customer,customer)

# Store the Future so we can collect its result later
                futures.append(future)

        # --------------------------------------------------
        # COLLECT RESULTS BY LOOPING ALL FUTURES
        # --------------------------------------------------
            for future in futures:

# Wait for this worker to finish and collect the result of row upload FAILED or SUCCESS
                result = future.result()
                
                
## APPEND THE FAILED ROWS LIST WITH THE FOLLOWING INFORMATION OF failed CUSTOMERS to send email
                if result["status"] == "failed":
# failed_customer variable is created to store result of current FAILED row specifically
                    failed_customer = result["customer"]
                    
                    
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
                    assign_user(failed_customer, user)
## This function helps to update the last assigned user field in users table, with the user assigned
## just now above by the assign_user() function
                    update_assigned_user(user, storage_row)
# Save the ID of the user we just assigned as the new "last assigned user"
                    last_assigned_user = user['id']
                    
                    
                    


## APPEND THE FAILED ROWS LIST WITH THE FOLLOWING INFORMATION OF failed CUSTOMERS to send email
                    failed_rows.append({
                        "customer_id": failed_customer.get(CUSTOMER_FIELDS["customer_id"]),
                        "first_name": failed_customer.get(CUSTOMER_FIELDS["first_name"]),
                        "last_name": failed_customer.get(CUSTOMER_FIELDS["last_name"]),
                        "upload_status": "Failed",
                        "fail_reason": result["fail_reason"], 
                    })



    # ALL CUSTOMERS HAVE FINISHED

# is there are failed rows then send email to notify that following rows are failed 
            if failed_rows:
                upload_fail_email(failed_rows)
                
                
# Return customer data as JSON response
        return Response({
            "message": "Customers processed successfully"
        })
        
        
#after ending TRY statement EXCEPT statement will run if any error occur in whole above process
    except Exception as error:
        application_error_email(error)
        return Response({"error": "Application error"}, status=500)
        
        
        
        
        
        
# Worker thread: handles the complete validation and upload process for one customer.
def process_one_customer(customer):
    
    
    # validate the customer and store issues in issues list 
    issues = validate_customer(customer)
        
    if not issues:
        response = send_to_records(customer)
        if response.status_code == 200:
# if upload is successful update the upload status to TRUE
            update_customer(customer)
            return {
                "customer": customer,"status": "success"
                }
        else:
# if upload is not successful then mark upload_status 'FAIL' with 'fail reason'
            upload_status_fail_reason(customer, response)
            return {
                "customer": customer,"status": "failed","fail_reason": response.text
                }
            
            
            
            
###################################################################################################
################### Upload invalid customer to Issues table ###########################################
    else:
    # use two parametres (customer and issues) because we have to send 
    # also issue detail along with customers
        response = send_to_issues(customer, issues)
            
        if response.status_code == 200:
# if upload is successful update the upload status to TRUE
            update_customer(customer)
            return {
                "customer": customer,"status": "success"
                }
            
        else:
            upload_status_fail_reason(customer, response)
            return {
                "customer": customer,"status": "failed","fail_reason": response.text
                }
            

    
    

    
    

    

                         
            
        
