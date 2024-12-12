from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional, Dict, List
from tempfile import NamedTemporaryFile
import os
import re
from datetime import datetime
import pandas as pd

from new_form_builder.core.form_builder import CoalMineFormGenerator
from smp.core.smp import HazardAnalysisChain
from new_form_builder.core.doc_to_form import DocToForm
from chatbot.db.knowledge_base import KnowledgeBase
from new_form_builder.core.doc_reader import document_reader, authenticate_account
from chatbot.core.chatbot import KnowledgeBaseChatbot
from chatbot.agent.visualization.graph_plotter import chat2plot



load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Error: GOOGLE_API_KEY not found in environment variables.")

kb = KnowledgeBase(api_key=GOOGLE_API_KEY)

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
PROCESSOR_ID = os.getenv("PROCESSOR_ID")
MIME_TYPES = ["application/pdf", "text/plain"]

app = FastAPI(
    title="Coal Mine Form Generator & Hazard Analysis API",
    description="API to AI part of coalworks"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]  
)

form_generator = CoalMineFormGenerator(GOOGLE_API_KEY)
hazard_analysis_chain = HazardAnalysisChain(GOOGLE_API_KEY)
doc_to_form = DocToForm(GOOGLE_API_KEY)

class FormRequest(BaseModel):
    query: str
    form_type: str
    save: Optional[bool] = False
    data: Optional[Dict] = False
    
class HazardAnalysisRequest(BaseModel):
    activity_name: str
    input_info: Optional[str] = None
    
# class Pdf2FormRequest(BaseModel):
#     text: str
#     file_name: str
#     file_size: int

class ChatbotQueryRequest(BaseModel):
    query: str
    api_key: Optional[str] = None

# Pydantic model for context
class ContextEntry(BaseModel):
    source: str
    content: str

# Pydantic model for chat history
class ChatHistoryEntry(BaseModel):
    role: str
    timestamp: datetime
    content: str

# Pydantic model for response
class ChatbotQueryResponse(BaseModel):
    response: str
    context: List[ContextEntry] = Field(default_factory=list)
    status: str
    chat_history: List[ChatHistoryEntry] = Field(default_factory=list)


@app.get("/")
def root():
    return {"message": "Welcome to the Coal Mine Form Generator & Hazard Analysis API"}

@app.post("/generate-form/")
async def generate_form(request: FormRequest):
    """
    Generate a form based on the provided query and optionally save it as a JSON file.
    
    Parameters:
    Request: FormRequest object containing the query and save flag
    Returns a Generated form as a JSON response in the ShadCN format for webdevs to integrate. 
    """
    try:
        generated_form = form_generator.generate_form(request.query, request.form_type, request.data)
        if not generated_form:
            raise HTTPException(status_code=500, detail="Form generation failed.")

        if request.save:
            output_filename = f"generated_form_{request.query.replace(' ', '_')}.json"
            form_generator.save_form_to_json(generated_form, output_filename)
            return {
                "message": "Form generated and saved successfully.",
                "file_name": output_filename,
                "form": generated_form,
            }

        return {"message": "Form query processed", "form": generated_form}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hazard-analysis/")
async def perform_hazard_analysis(request: HazardAnalysisRequest):
    """
    Perform hazard analysis for a given activity in coal mining.
    
    Parameters:
    request: HazardAnalysisRequest object containing activity_name and input_info(optional information)
    
    Returns Hazard analysis results as a JSON response
    """
    try:
        result = hazard_analysis_chain.perform_hazard_analysis(
            activity_name=request.activity_name,
            input_info=request.input_info or ""
        )
        return {"message": "Hazard analysis completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

DATA_FOLDER = "data"
@app.post("/ocr-form/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and save it to the data folder.
    
    Parameters:
    - file: The PDF file to be uploaded.
    
    Returns:
    - A message indicating the success of the operation and the file location.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_location = os.path.join(DATA_FOLDER, file.filename)
    
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    try:
        res = doc_to_form.doc2form(file_location)
        return {"message": "Form generated successfully", "form": res}
    except Exception as e:
        raise ValueError("Error generating Form...")
    
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    if file.content_type not in MIME_TYPES:
        if file.content_type not in ["audio/mpeg", "video/mp4"]:
            try:
                with NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(file.file.read())
                    temp_file_path = temp_file.name

                client = authenticate_account(SERVICE_ACCOUNT_FILE)
                extracted_text = document_reader(client=client, file_path=temp_file_path, mime_type=file.content_type, location=LOCATION, project_id=PROJECT_ID, processor_id=PROCESSOR_ID)
                os.remove(temp_file_path)
                kb.add_documents([extracted_text], document_type="txt")

                return JSONResponse(content={"message": "File processed and added to knowledge base.", "extracted_text": extracted_text})
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing file with Document AI: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, text, or readable formats are allowed.")
    
    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name
    
        if file.content_type == "application/pdf":
            kb.add_documents([temp_file_path], document_type="pdf")
        elif file.content_type == "text/plain":
            kb.add_documents([temp_file_path], document_type="txt")
    
        os.remove(temp_file_path)
        return JSONResponse(content={"message": "File successfully added to knowledge base."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding file to knowledge base: {str(e)}")
    
@app.post("/chatbot-query", response_model=ChatbotQueryResponse)
async def chatbot_query(request: ChatbotQueryRequest):
    """
    Endpoint for querying the knowledge base chatbot
    
    - Handles user queries 
    - Retrieves knowledge base context
    - Generates chatbot response
    - Returns comprehensive query results
    """
    try:
        # Use API key from request or environment variable
        api_key = request.api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="No API key provided. Please supply an API key."
            )
        
        # Initialize chatbot 
        chatbot = KnowledgeBaseChatbot(
            api_key=api_key,
            knowledge_base_path="data/vector_db/faiss_index"
        )
        
        graph_terms = ["graph", "visualization", "chart", "plot", "IoT"]
        if any(term in request.query.lower() for term in graph_terms):
            # Step 1: Locate the latest CSV file in the specified folder
            folder_path = "data/iot"
            file_pattern = r"iot_data_(\d+)\.csv"

            files = [f for f in os.listdir(folder_path) if re.match(file_pattern, f)]
            latest_file = max(files, key=lambda x: int(re.search(file_pattern, x).group(1)))
            latest_file_path = os.path.join(folder_path, latest_file)

            print(f"Using latest file: {latest_file_path}")
            df = pd.read_csv(latest_file_path, encoding='latin1')
            print("DataFrame Loaded:")
            print(df.head())
            print("\n" + "-"*50 + "\n")

            # Step 3: Create a chat2plot instance
            print("Step 3: Initializing ChartPlotter...")
            plotter = chat2plot(df)
            print("Chat2Plot instance created.")
            print(f"Instance type: {type(plotter)}")
            print("\n" + "-"*50 + "\n")

            # Step 4: Query the LLM to generate the bar chart
            query = "Create a chart showing some kind of simple relation in the data. Clean the data if required."
            print(f"Step 4: Querying ChartPlotter with: '{query}'")
            result = plotter(query, show_plot=True)
            print("Query executed. Result obtained.")
            print("\n" + "-"*50 + "\n")

            # Step 5: Display LLM Output
            llm_explanation = result.explanation if result.explanation else "No explanation returned."
            llm_config = result.config if result.config else "No valid configuration returned."

            # Step 6: Return the result
            return ChatbotQueryResponse(
                response=llm_explanation,
                context=[{"source": "ChartPlotter", "content": llm_config}],
                status="ok",
                chat_history=[{
                    "role": "user",
                    "timestamp": "2024-12-12",  # Example timestamp
                    "content": request.query
                }]
            )
        
        # Generate response
        response = chatbot.generate_response(request.query)
        
        # Process knowledge base context
        context_str = chatbot._retrieve_knowledge_base_context(request.query)
        
        # Parse context string into list of dictionaries
        context = []
        if context_str:
            # Split by source and parse
            context_chunks = context_str.split('Source: ')[1:]
            for chunk in context_chunks:
                lines = chunk.split('\n', 1)
                if len(lines) == 2:
                    source = lines[0].strip()
                    content = lines[1].replace('Content: ', '').strip()
                    context.append({
                        "source": source,
                        "content": content
                    })
        
        # Prepare chat history
        chat_history = [
            {
                "role": msg.role,
                "timestamp": msg.timestamp,
                "content": msg.content
            } for msg in chatbot.chat_history
        ]
        
        # Construct response
        return {
            "response": response,
            "context": context,
            "status": "success",
            "chat_history": chat_history
        }
    
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while processing the query: {str(e)}"
        )