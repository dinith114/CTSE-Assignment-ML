"""
Main entry point for Multi-Agent E-Channeling System
Simple testing interface for the workflow.
"""

from app.workflow import run_e_channeling_workflow
from app.logger_config import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    # Example: Test the workflow with sample patient data
    patient_input = {
        "symptoms": "Chest pain and shortness of breath",
        "patient_city": "Sri Lanka Institute of Information Technology",
        "hospital_city": "Durdans Hospital, Sri Lanka"
    }
    
    result = run_e_channeling_workflow(patient_input)
    
    logger.info("✅ Workflow completed successfully")
