import os
from typing import Dict, Any, Optional
from datetime import datetime

from app.tools.schedule_optimizer_tool import ScheduleOptimizerTool
from app.llm.ollama_client import run_ollama
from app.logger_config import get_logger

logger = get_logger(__name__)

class AppointmentCoordinatorAgent:
    """
    Agent responsible for finding and recommending optimal appointment slots.
    """

    def __init__(self, data_file: str = "app/data/schedules.json"):
        self.tool = ScheduleOptimizerTool(data_file=data_file)
        self.agent_name = "AppointmentCoordinatorAgent"
        self.use_local_llm = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
        self.llm_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the appointment coordination for the current state.
        """
        logger.info(f"{self.agent_name}: Starting appointment coordination")

        specialist = state.get("specialist")
        hospital_city = state.get("hospital_city")
        severity = state.get("severity", "medium")

        if not specialist:
            error_msg = "Missing required specialist in state for appointment coordination."
            logger.error(error_msg)
            state["error"] = error_msg
            state["appointment"] = {"error": error_msg}
            return state

        try:
            appointment = self.tool.get_next_available(specialist, hospital_city, severity)

            if not appointment:
                msg = f"No available appointments found for {specialist} in {hospital_city or 'any city'}."
                logger.warning(msg)
                state["appointment"] = {"error": msg}
                return state

            # Generate reasoning if LLM is enabled
            if self.use_local_llm:
                reasoning = self._generate_llm_reasoning(specialist, hospital_city, severity, appointment)
                if reasoning:
                    appointment["llm_reasoning"] = reasoning

            state["appointment"] = appointment

            # Log to conversation
            if not isinstance(state.get("conversation_log"), list):
                state["conversation_log"] = []
            
            # Create a safe copy for logging without deeply nested huge dicts
            log_output = dict(appointment)
            if "alternatives" in log_output:
                log_output["alternatives_count"] = len(log_output["alternatives"])
                del log_output["alternatives"]

            state["conversation_log"].append({
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "input": {
                    "specialist": specialist,
                    "hospital_city": hospital_city,
                    "severity": severity
                },
                "output": log_output
            })

            logger.info(f"{self.agent_name}: Appointment scheduled with {appointment['doctor_name']}")
            return state

        except Exception as e:
            logger.error(f"{self.agent_name}: Error during appointment processing: {e}")
            state["error"] = str(e)
            state["appointment"] = {"error": str(e)}
            return state

    def _generate_llm_reasoning(
        self,
        specialist: str,
        hospital_city: str,
        severity: str,
        appointment: Dict[str, Any]
    ) -> Optional[str]:
        """Generates concise reasoning for the recommended appointment slot."""
        prompt = (
            "You are an Appointment Coordinator Agent in a Sri Lankan healthcare e-channeling system. "
            "Given the patient's severity, specialist need, and available doctor schedules, explain in 1-2 sentences why this specific appointment slot was recommended. "
            "Consider urgency, doctor availability, and patient convenience.\n"
            "Do not invent new facts; use only the provided case details.\n\n"
            f"Patient Severity: {severity}\n"
            f"Requested Specialist: {specialist}\n"
            f"Requested City: {hospital_city}\n"
            f"Recommended Doctor: {appointment.get('doctor_name')} (Rating: {appointment.get('doctor_rating')})\n"
            f"Hospital: {appointment.get('hospital_name')}, {appointment.get('hospital_city')}\n"
            f"Time Slot: {appointment.get('day')} {appointment.get('time_slot')}\n"
            f"Availability: {appointment.get('available')} slots left\n"
        )

        output = run_ollama(prompt=prompt, model=self.llm_model, timeout=30)
        if not output:
            logger.info("Local Ollama reasoning unavailable; using rule-based recommendation.")
            return None
        return output.strip()

def create_appointment_coordinator_node():
    """Factory function to create appointment coordinator agent node for workflow."""
    agent = AppointmentCoordinatorAgent()
    return agent.process
