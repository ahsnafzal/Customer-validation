import os, json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from groq import Groq
from customer_validation.config import CUSTOMER_FIELDS
from .services import get_failed_customers







# client is variable which communicate with groq with api key stored in it 
client = Groq(api_key=GROQ_API_KEY)

'''def test_llm():
    # send a request
    response = client.chat.completions.create(
        # which model should process our request 
        model="openai/gpt-oss-120b",
        # message which we send to LLM to process
        messages=[
            {
                "role": "user",
                "content": "Explain what an LLM is in one sentence."
            }
        ]
    )
    # response which is returned by groq after processing by LLm model

    return response.choices[0].message.content'''




def customer_fix(customer, issues):
    # sending only these fields of customers to fix to LLM
    customer_for_llm={
        "field_30":customer[CUSTOMER_FIELDS["customer_id"]],
        "field_31": customer[CUSTOMER_FIELDS["first_name"]],
        "field_32": customer[CUSTOMER_FIELDS["last_name"]],
        "field_33_raw": customer[CUSTOMER_FIELDS["email"]],
        "field_34": customer[CUSTOMER_FIELDS["phone"]],
        "field_37": customer[CUSTOMER_FIELDS["join_date"]],
        "field_35": customer[CUSTOMER_FIELDS["age"]]
        }
      

    prompt = f'''You are helping fix customer data
    
    # sending data of customer to be fixed in json form
    Customer:{json.dumps(customer_for_llm)}
    Issues: {json.dumps(issues)}   
     
    Instructions:
    - Fix only the fields mentioned in the validation issues.
    - Do not change fields that have no issue.
    - Do not invent or guess customer information.
    - Do not create new validation rules.
    - Suggest a corrected value only when it can be reasonably determined.
    - If a field cannot reasonably be corrected, keep its original value.
    - Keep the EXACT same field names as the input customer.
    - Do not rename any fields.
    - Do not add any new fields.
    - Return the complete customer object as valid JSON.
    - Return ONLY JSON. Do not include explanations or markdown.
    - Return the corrected customer using the exact same field names provided in the Customer data.
    - Do not rename fields.
    - Do not return friendly names such as "email", "phone", or "first_name" if the input uses Knack field names.'''
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{
            "role":"user",
            "content":prompt
        }]
    )
    result = response.choices[0].message.content

    return json.loads(result)



## FUNCTION TO FIX THE FAILED ROWS ONLY DURING UPLOAD
def fix_failed_customers(customer):
    customer_for_llm={
        "field_30":customer[CUSTOMER_FIELDS["customer_id"]],
        "field_31": customer[CUSTOMER_FIELDS["first_name"]],
        "field_32": customer[CUSTOMER_FIELDS["last_name"]],
        "field_33_raw": customer[CUSTOMER_FIELDS["email"]],
        "field_34": customer[CUSTOMER_FIELDS["phone"]],
        "field_37": customer[CUSTOMER_FIELDS["join_date"]],
        "field_35": customer[CUSTOMER_FIELDS["age"]]
        }
    fail_reason = customer[CUSTOMER_FIELDS["fail_reason"]]
    
    
    prompt = f'''
    You are a customer data correction assistant.

    You will receive one customer record that failed to upload to the destination table.

    Customer data:
    {json.dumps(customer_for_llm)}

    Upload failure reason:
    {fail_reason}

    Your task is to correct the customer data only if the upload failure can reasonably be fixed using the information already provided.

    Rules:

    * Use the upload failure reason to identify which customer field caused the failure.
    * Fix only the field related to the upload failure.
    * Do not change fields that are unrelated to the failure.
    * Preserve all original customer information whenever possible.
    * Do not invent, guess, or create customer information.
    * Do not fill an empty field with made-up information.
    * Do not create new validation rules.
    * Only make a correction when it can be reasonably determined from the existing customer data or the stated failure reason.
    * If the failure cannot reasonably be fixed using the provided information, keep the original value unchanged.
    * Keep all customer values that do not require correction exactly as provided.
    * Keep the exact same Knack field names provided in the input.
    * Do not rename any fields.
    * Do not add any new fields.
    * Do not remove any fields.
    * Return the complete customer object.
    * Return valid JSON only.
    * Do not include explanations, comments, markdown, or any text outside the JSON object.

    The returned JSON must contain the same fields as the input customer object and must use the exact same field names.

    Example:

    Input:

    {{
    "field_30": "C2006",
    "field_31": "Sarah",
    "field_32": "Smith",
    "field_33_raw": "sarah@@gmail.com",
    "field_34": 923001112202,
    "field_35": 28,
    "field_37": "2024-02-15"
    }}

    Upload failure reason:
    Invalid email format

    Output:

    {{
    "field_30": "C2006",
    "field_31": "Sarah",
    "field_32": "Smith",
    "field_33_raw": "[sarah@gmail.com](mailto:sarah@gmail.com)",
    "field_34": 923001112202,
    "field_35": 28,
    "field_37": "2024-02-15"
    }}
    '''

    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{
            "role":"user",
            "content":prompt
        }]
    )
    result = response.choices[0].message.content

    return json.loads(result)
   

