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
                "location": state.get("patient_city", "Colombo")
            }
        }

        result_state = agent.run(routing_input)

        routing_data = result_state.get("routing", {})

        # ✅ KEEP EXISTING FIELDS (important for other members)
        state["specialist"] = routing_data.get("primary_specialty", "General Physician")
        state["hospital_city"] = state.get("patient_city", "Colombo")

        # ✅ ADD EXTRA DATA (safe extension)
        state["doctors"] = routing_data.get("doctors", [])
        state["routing_reason"] = routing_data.get("reason", "")

        return state

    except Exception as e:
        logger.error(f"Routing Error: {e}")
        state["error"] = "Routing agent failed"
        return state

def appointment_coordinator_node(state: EChannelState) -> EChannelState:
    logger.info("Step 3: Appointment Coordinator Agent")
    state["appointment"] = state.get("appointment") or {"date": "2024-12-15", "time": "10:00 AM"}
    return state


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
    app = build_workflow()
    return app.invoke(initial_state)
