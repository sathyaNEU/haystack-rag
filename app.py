import boto3
from uuid import uuid4
import logging
from logging import getLogger
from botocore.exceptions import NoCredentialsError
from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.encoders import jsonable_encoder
import uvicorn
from tempfile import NamedTemporaryFile
import os
from io import BytesIO
import json
from dotenv import load_dotenv
from rag.ingestion import ingest
from rag.retrieval_and_generation import get_result 
from rag.utils import pinecone_config
load_dotenv()

print("---------------------------")
app_logger = getLogger()
app_logger.addHandler(logging.StreamHandler())
app_logger.setLevel(logging.INFO)
print("---------------------------")

app = FastAPI()

s3_client = boto3.client(
    's3', 
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), 
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")  # e.g., 'us-east-1'
)

BUCKET_NAME = "haystack-docs"

import os
import requests

import os
import requests

def download_s3_object(s3_object_url: str):
    """
    Downloads a file from the given S3 object URL to a local directory `s3/`.
    Creates the directory if it does not exist.

    Args:
        s3_object_url (str): The S3 object URL (e.g., https://bucket-name.s3.amazonaws.com/uploads/file.txt).
    
    Returns:
        str: The fully qualified local file path where the object was saved.
    """
    # Extract file name from URL
    file_name = s3_object_url.split("/")[-1]
    
    # Local directory to save the file
    local_dir = "s3"
    
    # Create the directory if it doesn't exist
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # Full local file path
    local_file_path = os.path.join(local_dir, file_name)
    
    # Download the file from S3
    response = requests.get(s3_object_url)
    if response.status_code == 200:
        # Write the content to the local file
        with open(local_file_path, "wb") as file:
            file.write(response.content)
        print(f"File downloaded successfully: {local_file_path}")
    else:
        print(f"Failed to download file. HTTP Status Code: {response.status_code}")
        response.raise_for_status()
    
    # Return fully qualified local file path
    return os.path.abspath(local_file_path)



def upload_pdf_to_s3(file_bytes_io: BytesIO, filename: str):
    try:

        # Define S3 file path
        id = uuid4()
        s3_file_path = f"uploads/{id}.pdf"

        # Upload the file to S3 using upload_fileobj
        s3_client.upload_fileobj(file_bytes_io, BUCKET_NAME, s3_file_path)

        # Construct the public URL for the uploaded file
        object_url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_file_path}"

        return object_url
    except Exception as e:
        raise e

@app.post("/index_pdf")
async def index_pdf(file: UploadFile = File(...)):
    try:
        # Ensure file is a PDF and log the file info
        if not file.filename.endswith(".pdf"):
            return json.dumps(content={"error": "Only PDF files are supported.", "file": file.filename}, status_code=400)

        # Read the file content as bytes
        file_content = await file.read()
        size = len(file_content)

        # Convert file content to BytesIO
        file_bytes_io = BytesIO(file_content)

        # Upload the file to S3 and get the URL
        s3_file_path = upload_pdf_to_s3(file_bytes_io, file.filename)

        # Assuming your `ingest` function can handle the S3 file path
        document_store = pinecone_config()  # Call your function to configure Pinecone
        app_logger.info("<------------------->"+s3_file_path)
        ingest(document_store, download_s3_object(s3_file_path))  # Pass S3 path to your ingestion function

        # Return success response
        return {"message": f"PDF indexed successfully from {s3_file_path}"}

    except Exception as e:
        # Return error response if something goes wrong
        return {"error": f"An error occurred during indexing: {e}"}


@app.post("/get_result")
async def get_answer(request: Request):
  body = await request.json()
  query = body.get("query")
  answer = get_result(query)
  return {"answer":answer}

if __name__ == "__main__":
  uvicorn.run("app:app",host="0.0.0.0",port=8000,reload=True)
    
