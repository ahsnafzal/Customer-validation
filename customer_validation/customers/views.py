from django.shortcuts import render
from django.http import JsonResponse
from .services import get_customers,send_to_records, send_to_issues, update_customer, upload_status_fail_reason
from .validators import validate_customer
from customer_validation.config import CUSTOMER_FIELDS


def customer_list(request):
    """
    Fetch customer records from Knack,
    validate them and return the data.
    """

    # Get all customers from Knack
    customers = get_customers()
    

    # Loop through every customer record
    for customer in customers["records"]:
        # APPLIED IF STATEMENT TO CHECK IF DATA IS ALREADY PROCESSED
        # DON'T DO ANYTHING JUST TELL USTHAT ALREADY PROCESSED BY CHECKING
        # IS_PROCESSED FIELD FROM CUSTOMERS TABLE ONE BY ONE IF EACH CUSTOMER IS PROCESSED 
        # IT WILL SKIP ALL PROCESSES FOR THIS CUSTOMER AND GO BACK TO SECOND CUSTOMER
        if customer.get(CUSTOMER_FIELDS["is_processed"]) == "Yes":
            print(f"{customer.get(CUSTOMER_FIELDS["customer_id"])} is already processed")
            continue
        
        # Validate current customer
        issues = validate_customer(customer)

        if not issues:
            response = send_to_records(customer) 
# IF UPLOAD WAS SUCCESSFUL TO RECORDS TABLE CALL UPDATE CUSTOMER TO UPDATE DATA IN KNACK
            if response.status_code == 200:
                update_customer(customer)
                # IF UPLOAD FAILS EVEN AFTER RETRY, IT WILL CALL THIS
                # FUNCTION WHICH WILL WRITE FAILED IN UPLOAD_STATUS FIELD
            else:
                upload_status_fail_reason(customer,response)
        else:
            response = send_to_issues(customer, issues)
# IF UPLOAD WAS SUCCESSFUL TO ISSUES TABLE CALL UPDATE CUSTOMER TO UPDATE DATA IN KNACK
            if response.status_code == 200:
                update_customer(customer)
                # IF UPLOAD FAILS EVEN AFTER RETRY, IT WILL CALL THIS
                # FUNCTION WHICH WILL WRITE FAILED IN UPLOAD_STATUS FIELD
            else:
                upload_status_fail_reason(customer,response)        


    # Return original JSON response
    return JsonResponse(customers)