from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
import os
from new_form_builder.core.form_builder import CoalMineFormGenerator
from smp.core.smp import HazardAnalysisChain

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Error: GOOGLE_API_KEY not found in environment variables.")

app = FastAPI(
    title="Coal Mine Form Generator & Hazard Analysis API",
    description="API to AI part of coalworks"
)

form_generator = CoalMineFormGenerator(GOOGLE_API_KEY)
hazard_analysis_chain = HazardAnalysisChain(GOOGLE_API_KEY)

class FormRequest(BaseModel):
    query: str
    save: Optional[bool] = False
    
class HazardAnalysisRequest(BaseModel):
    activity_name: str
    input_info: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Welcome to the Coal Mine Form Generator & Hazard Analysis API"}

@app.post("/generate-form/")
async def generate_form(request: FormRequest):
    """
    Generate a form based on the provided query and optionally save it as a JSON file.
    
    :param request: FormRequest object containing the query and save flag
    :return: Generated form as a JSON response
    """
    try:
        generated_form = form_generator.generate_form(request.query)
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
    
    :param request: HazardAnalysisRequest object containing activity_name and optional input_info
    :return: Hazard analysis results as a JSON response
    """
    try:
        result = hazard_analysis_chain.perform_hazard_analysis(
            activity_name=request.activity_name,
            input_info=request.input_info or ""
        )
        return {"message": "Hazard analysis completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
