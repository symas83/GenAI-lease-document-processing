# GenAI-lease-document-processing

## Overview

This project uses AWS Bedrock and large language models (LLMs) to automatically process and extract key information from rental leases and agreements. It can handle both PDF and Word document formats, extracting crucial details such as tenant and owner names, rental dates, costs, and specific terms. The extracted information is then stored in an AWS DynamoDB table for easy access and management.

## Features

- Processes both PDF and Word (.docx) documents
- Extracts key information from rental agreements using AWS Bedrock's LLM capabilities
- Stores extracted data in AWS DynamoDB for efficient data management
- Handles multiple documents in batch processing

## Prerequisites

- AWS account with access to Bedrock and DynamoDB
- Python 3.7+
- AWS CLI configured with appropriate permissions
- Required Python libraries: boto3, botocore, json, pdfplumber, docx2txt, os, glob, pathlib

## Setup

1. Clone this repository to your local machine.
2. Install the required Python libraries:

    

pip install boto3 botocore pdfplumber docx2txt

    
3. Set up your AWS credentials and configure the AWS CLI.
4. Create a DynamoDB table named `rental_agreements`.
5. Ensure you have the necessary permissions to access AWS Bedrock and DynamoDB.

## Configuration

- Set the `profile_name` environment variable to your AWS profile name.
- Adjust the `modelId` in the `terms_extraction` function if you want to use a different Bedrock model.
- Modify the file path in the glob statement at the end of the script to point to your directory containing the rental agreements.

## Usage

1. Place your rental agreement documents (PDF or DOCX) in the specified directory.
2. Run the script:

    

python rental_agreement_processor.py

    
3. The script will process each document, extract the information, and store it in the DynamoDB table.

## Key Components

### AWS Services Used
- **AWS Bedrock**: Used for natural language processing and information extraction.
- **AWS DynamoDB**: Used for storing the extracted information.

### Main Functions
- `terms_extraction(content)`: Sends the document content to the Bedrock LLM and processes the response.
- `agreement_processing(file, extension)`: Handles the file reading and calls `terms_extraction`.
- `parse_xml(xml, tag)`: Helper function to parse XML tags in the LLM response.

### Data Extraction
The script extracts the following information from each rental agreement:
- Rental agreement title
- Owner's name
- Tenant's name
- Tenancy start and end dates
- Monthly rent
- Deposit amount
- Utility payment terms
- Property tax and HOA fee terms
- Rental termination terms

## Output

The extracted information is stored in the DynamoDB table `rental_agreements` with the following structure:

- `agreement_id`: The filename of the processed document
- `agreement_title`: A shortened title of the rental agreement
- `Owner Name`: Name of the property owner
- `Tenant Name`: Name of the tenant
- `Tenancy Start Date`: Start date of the tenancy
- `Tenancy End Date`: End date of the tenancy
- `Monthly Rent`: Monthly rental amount
- `Deposit`: Deposit amount
- `Utility Terms`: Terms for utility payments
- `Property Tax and HOA`: Terms for property tax and HOA fees
- `Rental Termination Terms`: Terms for terminating the rental agreement

## Limitations and Future Improvements

- The current implementation is designed for English language documents.
- Error handling could be improved for more robust processing.
- The script could be extended to handle more document types or extract additional information.
