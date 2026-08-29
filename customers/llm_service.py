import os, json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from groq import Groq
from customer_validation.config import CUSTOMER_FIELDS







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
   
   
    
