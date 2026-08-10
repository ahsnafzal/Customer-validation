from django.shortcuts import render
from django.http import JsonResponse
from .services import get_customers,send_to_records, send_to_issues, update_customer, upload_status_fail_reason
from .validators import validate_customer
from customer_validation.config import CUSTOMER_FIELDS
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
    
    
# Process each customer one by one
        for customer in customers["records"]:
        

# Skip customers that are already processed
            if customer.get(CUSTOMER_FIELDS["is_processed"]) == "Yes":
                print(f"{customer.get(CUSTOMER_FIELDS['customer_id'])} is already processed")
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
                    failed_rows.append({
                        "customer_id": customer.get(CUSTOMER_FIELDS["customer_id"]),
                        "first_name": customer.get(CUSTOMER_FIELDS["first_name"]),
                        "last_name": customer.get(CUSTOMER_FIELDS["last_name"]),
                        "upload_status": "Failed",
                        "fail_reason": response.text,
                        })
                    
                

# Upload invalid customer to Issues table
            else:
                response = send_to_issues(customer, issues)
            

# Mark customer as processed if upload succeeds
                if response.status_code == 200:
                    update_customer(customer)

# Mark upload_status as failed if upload fails
                else:
                    upload_status_fail_reason(customer, response)
                    failed_rows.append({
                        "customer_id": customer.get(CUSTOMER_FIELDS["customer_id"]),
                        "first_name": customer.get(CUSTOMER_FIELDS["first_name"]),
                        "last_name": customer.get(CUSTOMER_FIELDS["last_name"]),
                        "upload_status": "Failed",
                        "fail_reason": response.text,
                        })
        if failed_rows:
            upload_fail_email(failed_rows)

# Return customer data as JSON response
        return JsonResponse(customers)
    
# EXCEPT STATEMENT IS IMPLEMENTED THAT IF WHOLE UPPER CODE IS NOT PROCESSED THEN APPLICATION ERROR EMAIL WILL BE SENT
    except Exception as error:
        application_error_email(error)
        return JsonResponse(
            {"error": "Application error"},
            status=500
        )

