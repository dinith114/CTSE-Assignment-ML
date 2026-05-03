"""LangGraph orchestration for the e-channeling multi-agent workflow."""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

from app.agents.travel_risk_agent import TravelRiskAgent
from app.agents.symptom_triage_agent import SymptomTriageAgent
from app.logger_config import get_logger
from app.agents.medical_routing_agent import MedicalRoutingAgent

logger = get_logger(__name__)


class EChannelState(TypedDict, total=False):
    patient_text: str
    patient_city: str
    patient_location: str
    severity: str
    specialist: str
    hospital_city: str
    appointment: Dict[str, Any]
    travel_info: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    conversation_log: list
    error: str
    symptoms: list
    urgency: str
    red_flags: list
    triage_result: Dict[str, Any]
    doctors: list
    routing_reason: str


def symptom_triage_node(state: EChannelState) -> EChannelState:
    logger.info("Step 1: Symptom Triage Agent")
    
    agent = SymptomTriageAgent()
    return agent.process(state)


def medical_routing_node(state: EChannelState) -> EChannelState:
    logger.info("Step 2: Medical Routing Agent")

    try:
        agent = MedicalRoutingAgent()

        # Prepare input for your agent
        routing_input = {
            "triage": {
                "symptoms": state.get("symptoms", []),  # safe fallback
                "severity": state.get("severity", "medium"),
                "red_flags": state.get("red_flags", []),
                "location": state.get("patient_city", "Colombo")
            }
        }

        result_state = agent.run(routing_input)

        routing_data = result_state.get("routing", {})

        # ✅ KEEP EXISTING FIELDS (important for other members)
        state["specialist"] = routing_data.get("primary_specialty", "General Physician")
        # ✅ Preserve hospital_city from initial state (don't overwrite)
        if not state.get("hospital_city"):
            state["hospital_city"] = state.get("patient_city", "Colombo")

        # ✅ ADD EXTRA DATA (safe extension)
        state["doctors"] = routing_data.get("doctors", [])
        state["routing_reason"] = routing_data.get("reason", "")

        return state

    except Exception as e:
        logger.error(f"Routing Error: {e}")
        state["error"] = "Routing agent failed"
        # Ensure downstream agents still work with safe defaults
        if not state.get("specialist"):
            state["specialist"] = "General Physician"
        if not state.get("hospital_city"):
            state["hospital_city"] = state.get("patient_city", "Colombo, Sri Lanka")
        return state

def appointment_coordinator_node(state: EChannelState) -> EChannelState:
    logger.info("Step 3: Appointment Coordinator Agent")
    from app.agents.appointment_coordinator_agent import AppointmentCoordinatorAgent
    agent = AppointmentCoordinatorAgent()
    return agent.process(state)


def travel_risk_node(state: EChannelState) -> EChannelState:
    logger.info("Step 4: Travel Risk Assessment Agent")
    agent = TravelRiskAgent()
    return agent.process(state)


def build_workflow():
    graph = StateGraph(EChannelState)
    graph.add_node("symptom_triage", symptom_triage_node)
    graph.add_node("medical_routing", medical_routing_node)
    graph.add_node("appointment_coordination", appointment_coordinator_node)
    graph.add_node("travel_risk", travel_risk_node)

    graph.set_entry_point("symptom_triage")
    graph.add_edge("symptom_triage", "medical_routing")
    graph.add_edge("medical_routing", "appointment_coordination")
    graph.add_edge("appointment_coordination", "travel_risk")
    graph.add_edge("travel_risk", END)

    return graph.compile()


def run_workflow(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the compiled workflow with the given initial state."""
    app = build_workflow()
    return app.invoke(initial_state)


def create_initial_state(patient_input: dict) -> EChannelState:
    """
    Initialize workflow state from patient input dictionary.
    
    Args:
        patient_input: Dict with keys: symptoms, patient_city, hospital_city
    
    Returns:
        EChannelState ready for workflow execution
    """
    return {
        "patient_text": patient_input.get("symptoms", ""),
        "patient_city": patient_input.get("patient_city", "Colombo, Sri Lanka"),
        "patient_location": patient_input.get("patient_city", "Colombo, Sri Lanka"),
        "severity": None,
        "specialist": None,
        "hospital_city": patient_input.get("hospital_city"),
        "appointment": None,
        "travel_info": None,
    }


def run_e_channeling_workflow(patient_input: dict) -> Dict[str, Any]:
    """
    Run the complete multi-agent e-channeling workflow.
    
    Args:
        patient_input: Dict with keys: symptoms, patient_city (optional), hospital_city (optional)
    
    Returns:
        Final workflow state with results from all agents
    """
    initial_state = create_initial_state(patient_input)
    final_state = run_workflow(initial_state)
    
    # Return complete state
    return final_state