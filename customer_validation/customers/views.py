from django.shortcuts import render
from django.http import JsonResponse
from .services import get_customers, send_to_records, send_to_issues
from .validators import validate_customer


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
            send_to_records(customer)
        else:
            send_to_issues(customer, issues)

        # Print validation result in terminal
        #print(customer.get("field_139"), issues)

    # Return original JSON response
    return JsonResponse(customers)