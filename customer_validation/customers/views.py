from django.shortcuts import render
from django.http import JsonResponse
from .services import get_customers, send_to_records, send_to_issues, update_customer
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
        
        

        # Validate current customer
        issues = validate_customer(customer)

        if not issues:
            response = send_to_records(customer) 
# IF UPLOAD WAS SUCCESSFUL TO RECORDS TABLE CALL UPDATE CUSTOMER TO UPDATE DATA IN KNACK
            if response.status_code == 200:
                update_customer(customer)
        else:
            response = send_to_issues(customer, issues)
# IF UPLOAD WAS SUCCESSFUL TO ISSUES TABLE CALL UPDATE CUSTOMER TO UPDATE DATA IN KNACK
            if response.status_code == 200:
                update_customer(customer)
        

        # Print validation result in terminal
        #print(customer.get("field_139"), issues)

    # Return original JSON response
    return JsonResponse(customers)