import os
import requests
from django.template.loader import render_to_string

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"


####### FAILED ROWS UPLOAD ERROR EMAIL   ###########
def upload_fail_email(failed_rows):
    to_email = "cha84911@gmail.com"
    subject = "Records Upload Failure"
    html_content = render_to_string(
        "emails/failed_rows.html",
        {"failed_rows":failed_rows}
    )
    response = send_email(
        to_email,
        subject,
        html_content
    )
    return response

######### APPLICATION ERROR EMAIL SENDING ########
def application_error_email(error):
    to_email = "cha84911@gmail.com"
    subject = "Application Failure Error Email"
    html_content = render_to_string(
        "emails/application_error.html",
        {"error" : error}
    )
    response = send_email(
        to_email,
        subject,
        html_content
    )
    return response

#######   EMAIL SENDING FUNCTION ######
def send_email(to_email, subject, html_content):

    headers = {
        "accept" : "application/json",
        "api-key" : BREVO_API_KEY,
        "content-type" : "application/json"
    }
    data =  {
        "sender":{
            "email" : "cha84911@gmail.com"
        },
        "to" : [
            {
            "email" : to_email
        }
        ],
        "subject" : subject,
        "htmlContent" : html_content

    }
    response = requests.post(
        BREVO_URL,
        headers=headers,
        json=data
    )
    return response
    












