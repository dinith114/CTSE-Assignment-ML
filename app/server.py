from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.workflow import run_e_channeling_workflow

class RunRequest(BaseModel):
    name: Optional[str] = None
    symptoms: str
    patient_city: Optional[str] = "Colombo, Sri Lanka"
    hospital_city: Optional[str] = None


app = FastAPI(title="E-Channeling API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/run")
def run_workflow_api(req: RunRequest):
    """Run the LangGraph workflow with provided patient input and return final state."""
    patient_input = {
        "symptoms": req.symptoms,
        "patient_city": req.patient_city,
        "hospital_city": req.hospital_city,
    }
    
    final_state = run_e_channeling_workflow(patient_input)
    return final_state
