from google.oauth2.service_account import Credentials
from google.cloud import documentai
import os
from dotenv import load_dotenv

def authenticate_account(service_account_file):
    """
    Authenticates using a service account JSON key file.

    Args:
        service_account_file (str): Path to the service account JSON key file.

    Returns:
        documentai.DocumentProcessorServiceClient: Authenticated Document AI client.
    """
    credentials = Credentials.from_service_account_file(service_account_file)
    return documentai.DocumentProcessorServiceClient(credentials=credentials)

def document_reader(client, project_id, location, processor_id, file_path, mime_type):
    """
    Extracts text from a document using Google Document AI.

    Args:
        client (DocumentProcessorServiceClient): Authenticated Document AI client.
        project_id (str): Google Cloud project ID.
        location (str): Location of the processor (e.g., 'us' or 'eu').
        processor_id (str): Processor ID in Document AI.
        file_path (str): Path to the input document file.
        mime_type (str): MIME type of the input file (e.g., 'application/pdf').

    Returns:
        str: Extracted text from the document.
    """
    resource_name = client.processor_path(project_id, location, processor_id)
    with open(file_path, "rb") as file:
        file_content = file.read()
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)
    result = client.process_document(request=request)
    document_object = result.document
    return document_object.text

# if __name__ == "__main__":
#     load_dotenv()

#     SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT")
#     PROJECT_ID = os.getenv("PROJECT_ID")
#     LOCATION = os.getenv("LOCATION")
#     PROCESSOR_ID = os.getenv("PROCESSOR_ID")
#     FILE_PATH = "new_form_builder/data/Overman register.pdf"
#     MIME_TYPE = "application/pdf"
#     client = authenticate_with_service_account(SERVICE_ACCOUNT_FILE)
#     extracted_text = document_reader(
#         client,
#         PROJECT_ID,
#         LOCATION,
#         PROCESSOR_ID,
#         FILE_PATH,
#         MIME_TYPE
#     )

#     print("Document processing complete.")
#     print(f"Extracted Text: {extracted_text}")
