"""
Symptom Triage and Severity Assessment Agent.

This agent receives patient symptom text from the global workflow state,
uses a custom Python tool to parse symptoms, and updates the shared state
for downstream medical routing.
"""

from datetime import datetime
from typing import Any, Dict
import json

from app.logger_config import get_logger
from app.tools.symptom_parser_tool import symptom_parser_tool
from app.llm.ollama_client import run_ollama

logger = get_logger(__name__)


class SymptomTriageAgent:
    """
    Agent responsible for preliminary symptom triage.

    Persona:
        Clinical intake triage assistant for an e-channeling system.

    System Prompt:
        See SYSTEM_PROMPT.

    Constraints:
        - Do not diagnose diseases.
        - Do not prescribe medication.
        - Do not recommend treatment.
        - Do not invent symptoms.
        - Do not select a specialist or doctor.
        - Only produce structured triage data for downstream agents.
    """

    SYSTEM_PROMPT = """
    You are the Symptom Triage and Severity Assessment Agent in a local multi-agent e-channeling system.

    Your responsibilities:
    1. Read the patient's symptom description.
    2. Extract reported symptoms accurately.
    3. Determine severity (low, medium, high) and urgency (routine, priority, urgent).
    4. Identify red-flag symptoms.

    Constraints (CRITICAL):
    - DO NOT diagnose diseases.
    - DO NOT prescribe medication or recommend treatment.
    - DO NOT invent symptoms not explicitly stated by the patient.
    - DO NOT select a specialist or doctor.
    
    Output Format:
    You must return your findings in strict JSON format with the following keys:
    {
        "triage_summary_note": "A concise, 1-2 sentence clinical summary of the reported symptoms."
    }
    """

    def __init__(self) -> None:
        """Initialize the Symptom Triage Agent."""
        self.agent_name = "SymptomTriageAgent"
        self.system_prompt = self.SYSTEM_PROMPT

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process patient symptom text and update global state.

        Args:
            state: Shared workflow state containing patient_text and location data.

        Returns:
            Updated shared state with triage results.
        """
        logger.info("%s: Starting symptom triage", self.agent_name)

        patient_text = state.get("patient_text", "")

        try:
            # 1. Use the deterministic Python tool for extracting structured flags safely
            triage_result = symptom_parser_tool(patient_text)

            # 2. Use the SLM to create a clinical summary based on the prompt constraints,
            # demonstrating pure prompt engineering and SLM capabilities.
            llm_prompt = f"{self.SYSTEM_PROMPT}\n\nPatient Input: {patient_text}\n\nTriage JSON:"
            llm_response = run_ollama(llm_prompt)
            
            if llm_response:
                try:
                    # Attempt to parse SLM JSON output, allowing unescaped control chars like newlines
                    json_str = llm_response[llm_response.find("{"):llm_response.rfind("}")+1]
                    llm_data = json.loads(json_str, strict=False)
                    if "triage_summary_note" in llm_data:
                        triage_result["triage_note"] = llm_data["triage_summary_note"]
                except Exception as e:
                    logger.warning(f"Failed to parse LLM JSON response: {e}")

            state["symptoms"] = triage_result["symptoms"]
            state["severity"] = triage_result["severity"]
            state["urgency"] = triage_result["urgency"]
            state["red_flags"] = triage_result["red_flags"]
            state["triage_result"] = triage_result

            if not isinstance(state.get("conversation_log"), list):
                state["conversation_log"] = []

            state["conversation_log"].append(
                {
                    "agent": self.agent_name,
                    "timestamp": datetime.now().isoformat(),
                    "system_prompt_summary": (
                        "Extract symptoms, classify severity/urgency, "
                        "identify red flags, and avoid diagnosis or treatment advice."
                    ),
                    "input": {
                        "patient_text": patient_text,
                        "patient_city": state.get("patient_city"),
                    },
                    "tool_called": "symptom_parser_tool",
                    "output": triage_result,
                }
            )

            logger.info(
                "%s: Completed triage - severity=%s, urgency=%s",
                self.agent_name,
                triage_result["severity"],
                triage_result["urgency"],
            )

            return state

        except ValueError as error:
            error_message = str(error)
            logger.error("%s: Validation error - %s", self.agent_name, error_message)

            state["error"] = error_message
            state["triage_result"] = {"error": error_message}
            return state

        except Exception as error:
            error_message = f"Unexpected triage error: {error}"
            logger.exception("%s: %s", self.agent_name, error_message)

            state["error"] = error_message
            state["triage_result"] = {"error": error_message}
            return state


def create_symptom_triage_node():
    """Create a workflow-compatible symptom triage node."""
    agent = SymptomTriageAgent()
    return agent.process