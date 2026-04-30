"""LangGraph orchestration for the e-channeling multi-agent workflow."""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

from app.agents.travel_risk_agent import TravelRiskAgent
from app.logger_config import get_logger

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


def symptom_triage_node(state: EChannelState) -> EChannelState:
    logger.info("Step 1: Symptom Triage Agent")
    if not state.get("severity"):
        state["severity"] = "high"
    return state


def medical_routing_node(state: EChannelState) -> EChannelState:
    logger.info("Step 2: Medical Routing Agent")
    state["specialist"] = state.get("specialist") or "Cardiologist"
    state["hospital_city"] = state.get("hospital_city") or "Colombo, Sri Lanka"
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
