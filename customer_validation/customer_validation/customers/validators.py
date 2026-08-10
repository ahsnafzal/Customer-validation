import re
from datetime import datetime


#Validate one customer record.
def validate_customer(customer):
    #list is created to store the issue before uploading it to database table 
    issues = []



#---------------------------------------------------
#################      CUSTOMER ID      ###############
    customer_id = customer.get("field_138").strip()
    if not customer_id:
         issues.append("Missing customer id")
    elif not re.match(r"^C\d+$", customer_id):
         issues.append("Invalid Customer ID")


#---------------------------------------------------
#################      NAMES CHECKING      ###############
    # Get customer name safely
    first_name = customer.get("field_139","").strip()

    # Check if name exists
    if not first_name:
        issues.append("Missing first name")

    last_name = customer.get("field_140","").strip()

    if not last_name:
            issues.append("Missing last name")


#---------------------------------------------------------
#########    EMAIL CHECKING        #############
    #checking if email exists or inavlid
    raw_email = customer.get("field_141_raw", "")
    #taking out email string from raw email dictionary skiping label 'email' is a key value here
    if isinstance(raw_email, dict):
         email = raw_email.get("email", "").strip()
    else:
         email = raw_email.strip()

    if not email:
         issues.append("Missing email")
    elif not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
         issues.append("Invalid email")

#--------------------------------------------------------------------------
#########   PHONE VALIDATION     ##############

    phone = str(customer.get("field_142", "")).strip()
    if not phone:
         issues.append("Missing phone")

    elif not re.match(r"^\d{10,15}$", phone):
         issues.append("Invalid phone")


#-----------------------------------------------------------
#################   SIGNUP DATE VALIDATION       ###############
    signup_date = customer.get("field_145", "").strip()
    
    if not signup_date:
         issues.append("Missing Signup Date")
    else:
        try:
             ## Convert text into a real date object
             signup_date = datetime.strptime(signup_date, "%Y-%m-%d").date()

              # Get today's current date
             today = datetime.today().date()

             # Check if signup date is in the future
             if signup_date > today:
                  issues.append("Invalid signup date")
        except ValueError:
             issues.append("Invalid Signup Date")

#--------------------------------------------------------------------------
###################      AGE VALIDATION     ########################

    age = str(customer.get("field_143", "")).strip()
    
    if not age:
         issues.append("Missing age")
    else:
         try:
              ## Convert age into a number
              age = int(age)
              # Check valid age range
              if age < 18 or age > 100:
                   issues.append("Invalid age")
         except ValueError:
              issues.append("Invalid Age")


    return issues