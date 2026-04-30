"""
Main entry point for Multi-Agent E-Channeling System
Demonstrates full workflow with all 4 agents.
"""

from app.agents.travel_risk_agent import TravelRiskAgent
from app.tools.distance_calculator_tool import distance_calculator_tool
from app.logger_config import get_logger
import json
import argparse
import os

logger = get_logger(__name__)


def run_e_channeling_workflow(patient_input: dict, hospital_override: str = None, severity_override: str = None):
    """
    Simulate the complete multi-agent workflow.
    In production, this would use LangGraph/CrewAI for orchestration.
    """
    # Initial state
    state = {
        "patient_text": patient_input.get("symptoms", ""),
        "patient_city": patient_input.get("city", "Colombo, Sri Lanka"),
        "patient_location": patient_input.get("city", "Colombo, Sri Lanka"),
        "severity": None,  # To be set by Member 1
        "specialist": None,  # To be set by Member 2
        "hospital_city": None,  # To be set by Member 2
        "appointment": None,  # To be set by Member 3
        "travel_info": None,  # To be set by YOU (Member 4)
    }
    
    # Simulate Member 1 (Symptom Triage)
    logger.info("Step 1: Symptom Triage Agent")
    state["severity"] = "high"  # Placeholder
    
    # Simulate Member 2 (Medical Routing)
    logger.info("Step 2: Medical Routing Agent")
    state["specialist"] = "Cardiologist"
    # Default hospital assignment; allow override from caller or patient_input
    state["hospital_city"] = patient_input.get("hospital_city") or hospital_override or "Colombo, Sri Lanka"
    # Allow severity override if provided
    if severity_override:
        state["severity"] = severity_override
    
    # Simulate Member 3 (Appointment Coordinator)
    logger.info("Step 3: Appointment Coordinator Agent")
    state["appointment"] = {"date": "2024-12-15", "time": "10:00 AM"}
    
    # YOUR AGENT (Member 4): Travel Risk Assessment
    logger.info("Step 4: Travel Risk Assessment Agent")
    travel_agent = TravelRiskAgent()
    final_state = travel_agent.process(state)
    
    # Display results
    print("\n" + "="*60)
    print("FINAL APPOINTMENT RECOMMENDATION")
    print("="*60)
    print(travel_agent.get_travel_summary(final_state))
    
    if final_state.get("risk_assessment", {}).get("requires_alternative"):
        print("\n⚠️ ALTERNATIVE RECOMMENDATION: Consider local hospital or teleconsultation")
    
    return final_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run e-channeling workflow with custom inputs")
    parser.add_argument("--patient-city", type=str, default="Kandy, Sri Lanka", help="Patient city/location")
    parser.add_argument("--hospital-city", type=str, default=None, help="Hospital city/location")
    parser.add_argument("--severity", type=str, default=None, choices=[None, "low", "medium", "high", "urgent"], help="Patient severity")
    parser.add_argument("--symptoms", type=str, default="Chest pain and shortness of breath", help="Patient symptom text")

    args = parser.parse_args()

    # Build patient input from CLI args
    patient = {
        "symptoms": args.symptoms,
        "city": args.patient_city,
        "hospital_city": args.hospital_city
    }

    result = run_e_channeling_workflow(patient, hospital_override=args.hospital_city, severity_override=args.severity)

    # Save results for observability
    out_path = "app/logs/system/last_run.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Results written to {out_path}")