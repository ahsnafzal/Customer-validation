from django.shortcuts import render
from django.http import JsonResponse
from .services import get_customers,send_to_records, send_to_issues, update_customer, upload_status_fail_reason
from .validators import validate_customer
from customer_validation.config import CUSTOMER_FIELDS


def customer_list(request):
    """
    Fetch customer data, validate it,
    and upload it to the appropriate table.
    """

    # Fetch all customer records from Knack
    customers = get_customers()
    

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

        # Upload invalid customer to Issues table
        else:
            response = send_to_issues(customer, issues)

            # Mark customer as processed if upload succeeds
            if response.status_code == 200:
                update_customer(customer)

            # Mark upload as failed if upload fails
            else:
                upload_status_fail_reason(customer, response)

    # Return customer data as JSON response
    return JsonResponse(customers)