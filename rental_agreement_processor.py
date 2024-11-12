import boto3  # Import the boto3 library for AWS services
import botocore  # Import the botocore library for AWS low-level service operations
import json  # Import the json library for working with JSON data
import pdfplumber  # Import the pdfplumber library for PDF extraction
import docx2txt # Import docx2txt for word document extraction
import os  # Import the os module for interacting with the operating system
import glob # Read all file paths in folder
import pathlib # For different file extensions

from datetime import datetime  # Measure time taken for execution

# Setting up the default AWS session using the profile name from the environment variable
boto3.setup_default_session(profile_name=os.getenv('profile_name'))

# Setting up the Bedrock client with a custom timeout configuration
config = botocore.config.Config(connect_timeout=300, read_timeout=300)
bedrock = boto3.client('bedrock-runtime', 'us-east-1', config=config)
# Insert rental terms to DynamoDB table rental_agreements
dynamodb = boto3.resource('dynamodb')
dbtable = dynamodb.Table('rental_agreements')
    
#system prompt to the LLM model
system_prompt = f"""
You are a Data Processor. You will be provided the text of agreement of a real estate rental unit such as aparment, home or condo.
Extract the following items and information from the provided content and output them into a valid json array
    Rental agreement title (shorten the title to 6 words or less)
    Owner's name of the rental unit
    Tenant's name of the rental unit
    Tenancy Start and End Dates (convert the date format to mm/dd/yyyy if found as dd/mm/yyyy or dd.mm.yyyy) 
    Monthly Rent with currency (convert the currency into numbers)
    Deposit amount with currency (convert the currency into numbers)
    Terms on who will pay utility charges such as electricity, water, sewer, internet, etc.
    Terms of who will pay property tax and condo association fees
    Rental termination terms

Return your response in valid JSON, using the provided output format
<example_format>
{{"Rental Agreement Title": "(title)", "Owner Name": "(owner)", "Tenant Name": "(tenant)", "Tenancy Start Date": "(startdate - in mm/dd/yyy)", "Tenancy End Date": "(enddate - in mm/dd/yyy)", "Monthly Rent": "(monthlyrent)", "Deposit": "(deposit)", "Utility Terms": "(utilities)", "Property Tax and HOA": "(taxhoa)", "Rental Termination Terms": "(termination)"}}
</example_format>

When creating the summary, be sure to understand the legal language in the agreement and create a valid output

Think through each step of your thought process and write your thoughts down in <scratchpad> xml tags

return the valid json array with the extracted details in <output> xml tags, only including the valid json

"""


#Helper function to extract the value between XML tags from a given string.
def parse_xml(xml, tag):
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    
    start_index = xml.find(start_tag)
    if start_index == -1:
        return ""

    end_index = xml.find(end_tag)
    if end_index == -1:
        return ""

    value = xml[start_index+len(start_tag):end_index]
    return value

#Function to extract rental agreement terms from the given content.
def terms_extraction(content):

    # Prepare the content for the prompt
    content = [{
        "type": "text",
        "text": content
    }]
    
    # Create the prompt dictionary
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": [    
            {
                "role": "user",
                "content": f"<rental_agreement> {content} </rental_agreement>"
            }
        ]
    }

    # Convert the prompt to a JSON string
    prompt = json.dumps(prompt)
    #print(prompt)

    # Invoke the Bedrock model with the prompt
    response = bedrock.invoke_model(body=prompt, modelId="anthropic.claude-3-sonnet-20240229-v1:0", accept="application/json", contentType="application/json")
    #response = bedrock.invoke_model(body=prompt, modelId="anthropic.claude-3-haiku-20240307-v1:0", accept="application/json", contentType="application/json")
    response_body = json.loads(response.get('body').read())
    llmOutput = response_body['content'][0]['text']
    #print(llmOutput)

    # Parse the scratchpad and output from the LLM response
    scratch = parse_xml(llmOutput, "scratchpad")
    output = parse_xml(llmOutput, "output")

    return scratch, output

#Function to process rental agreement (.pdf or .docx word document)
def agreement_processing(file, extension):
    text = ""
    if (extension == '.pdf'):
        with pdfplumber.open(file) as pdf:
            # Loop through each page in the PDF
            for page in pdf.pages:
                # Extract the text from the page
                text = text + page.extract_text()
    else:
        text = docx2txt.process(file)
    # Print the extracted text
    #print(text)
    # Call LLM model    
    scratch, output = terms_extraction(text)
    # Get json output
    output_json = json.loads(output)

    response = dbtable.put_item(Item={"agreement_id": file,
                                    "agreement_title": output_json['Rental Agreement Title'], 
                                    "Owner Name": output_json["Owner Name"], 
                                    "Tenant Name": output_json["Tenant Name"], 
                                    "Tenancy Start Date": output_json["Tenancy Start Date"], 
                                    "Tenancy End Date": output_json["Tenancy End Date"], 
                                    "Monthly Rent": output_json["Monthly Rent"], 
                                    "Deposit": output_json["Deposit"], 
                                    "Utility Terms": output_json["Utility Terms"], 
                                    "Property Tax and HOA": output_json["Property Tax and HOA"], 
                                    "Rental Termination Terms": output_json["Rental Termination Terms"]  } )
    
    print("Inserted terms of the rental agreement - ", file)     
    
    # Display the extracted details in text input fields
    #for key in output_json:
     #   value = output_json[key]
      #  print("Key:", key, "  Value:", value)

    # Display the full JSON payload in an expander
    #print("Full JSON Payload:")
    #print(output)

print("Start Time of Agreement Processing:  ", datetime.now())
# Call agreement processing function to loop for all agreements in folder
for file in glob.glob("/home/ubuntu/environment/venv/agreements/*"):
    time = datetime.now()
    agreement_processing(file, pathlib.Path(file).suffix)
    print("Time taken to process ", file, " :  ", datetime.now() - time)
    
