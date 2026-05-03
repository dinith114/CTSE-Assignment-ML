"""
Main entry point for Multi-Agent E-Channeling System
Simple testing interface for the workflow.
"""

import argparse
from app.workflow import run_e_channeling_workflow
from app.logger_config import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Medical MAS")
    parser.add_argument("--symptoms", type=str, default="Chest pain and shortness of breath")
    parser.add_argument("--patient-city", type=str, default="Sri Lanka Institute of Information Technology")
    parser.add_argument("--hospital-city", type=str, default="Durdans Hospital, Sri Lanka")
    parser.add_argument("--severity", type=str, default="")
    args = parser.parse_args()

    patient_input = {
        "symptoms": args.symptoms,
        "patient_city": args.patient_city,
        "hospital_city": args.hospital_city
    }
    
    result = run_e_channeling_workflow(patient_input)
    
    logger.info("[SUCCESS] Workflow completed successfully")
