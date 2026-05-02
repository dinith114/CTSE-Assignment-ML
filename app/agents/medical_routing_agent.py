import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.hospital_db_tool import hospital_db_tool
from app.llm.ollama_client import run_ollama
from app.logger_config import get_logger

logger = get_logger(__name__)

class MedicalRoutingAgent:
    """
    Agent responsible for routing patients to the appropriate medical specialist
    based on symptoms, severity, and identified red flags.
    """
    
    def __init__(self):
        self.agent_name = "MedicalRoutingAgent"
        self.use_local_llm = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
        self.llm_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def _determine_specialist_via_llm(self, symptoms: List[str], severity: str, red_flags: List[str]) -> Tuple[str, List[str], str]:
        """
        Uses an LLM to accurately determine the required medical specialist.
        """
        prompt = (
            "You are an expert Medical Routing Agent in a hospital e-channeling system. "
            "Your job is to read the patient's symptoms, severity, and red flags, and output ONLY "
            "a JSON object with the most appropriate medical specialist. DO NOT diagnose the patient.\n\n"
            f"Symptoms: {', '.join(symptoms)}\n"
            f"Severity: {severity}\n"
            f"Red Flags: {', '.join(red_flags) if red_flags else 'None'}\n\n"
            "Return EXACTLY this JSON string:\n"
            '{"primary_specialist": "specialist", "alternative_specialists": ["other_specialist"], "reasoning": "reason"}'
        )

        try:
            # Query the LLM
            response_text = run_ollama(prompt, model=self.llm_model)
            
            # --- DEBUG: Print exactly what Triage sent and what LLM answered ---
            print("\n" + "-"*40)
            print(f"📥 INPUT FROM TRIAGE: Symptoms={symptoms}, Severity={severity}, RedFlags={red_flags}")
            print(f"🤖 RAW LLM RESPONSE:\n{response_text}")
            print("-"*40 + "\n")

            # --- ROBUST JSON EXTRACTION ---
            import re
            
            # Remove all forms of newlines immediately to prevent json.loads() from failing on multi-line text
            response_flat = response_text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')

            # Extract only the content between the first { and the last }
            json_match = re.search(r'(\{.*\})', response_flat)
            
            if json_match:
                cleaned_response = json_match.group(1)
                # Ensure no weird ascii characters are left
                cleaned_response = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', cleaned_response)
                
                try:
                    result = json.loads(cleaned_response, strict=False)
                except json.JSONDecodeError as decode_err:
                    raise ValueError(f"Extracted json was invalid. Error: {decode_err}. Extracted string: {cleaned_response}")
            else:
                 raise ValueError(f"No JSON object found in LLM response: {response_flat}")
            
            return (
                result.get("primary_specialist", "general physician"), 
                result.get("alternative_specialists", ["general physician"]), 
                result.get("reasoning", "LLM routing successful.")
            )
        except Exception as e:
            logger.error(f"{self.agent_name}: LLM parsing failed, using fallback. Error: {e}")
            # Fallback in case the LLM is down or hallucinates bad JSON
            return "general physician", [], "Fallback due to LLM parsing error."

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the medical routing for the current appointment state.
        """
        logger.info(f"{self.agent_name}: Starting medical routing assessment")

        triage_data = state.get("triage", {})
        
        # 1. Analyze symptoms, severity, red flags
        symptoms = triage_data.get("symptoms", [])
        severity = triage_data.get("severity", "medium")
        red_flags = triage_data.get("red_flags", [])
        location = triage_data.get("location", "Colombo")

        # 2. Determine appropriate specialist via LLM
        primary, alternatives, reason = self._determine_specialist_via_llm(symptoms, severity, red_flags)

        # 3. Query the local doctor database using the custom tool
        try:
            doctors = hospital_db_tool(primary, location)
            
            # If no doctors found, try finding alternatives automatically (handling edge case)
            if not doctors and alternatives:
                 logger.info(f"{self.agent_name}: No {primary} found. Trying alternative {alternatives[0]}.")
                 doctors = hospital_db_tool(alternatives[0], location)
                 if doctors:
                     primary = alternatives[0] # Swap the primary if we found an alternative
                     reason += f" (Note: Defaulted to alternative '{primary}' because the original primary was unavailable in {location})."
                     
        except Exception as e:
            logger.error(f"{self.agent_name}: Error querying hospital database: {e}")
            doctors = []
            reason = f"Database query failed: {str(e)}"

        # 4. Update Global State
        routing_result = {
            "primary_specialty": primary,
            "alternative_specialties": alternatives,
            "doctors": doctors,
            "reason": reason
        }
        
        state["routing"] = routing_result
        
        # Debugging print statement so you can see it in terminal!
        print("\n" + "="*60)
        print("MEDICAL ROUTING ASSESSMENT RESULTS")
        print("="*60)
        print(f"🏥 Selected Specialist: {primary.upper()}")
        print(f"💬 Reason: {reason}")
        if doctors:
            print("👨‍⚕️ Available Doctors Found:")
            for doc in doctors:
                print(f"   - {doc['name']} at {doc['hospital']} ({', '.join(doc['available_days'])})")
        else:
            print("⚠️ No doctors found in that location/specialty combination.")
        print("="*60 + "\n")

        # 5. Add to conversation log for observability (LLMOps compliance)
        if not isinstance(state.get("conversation_log"), list):
            state["conversation_log"] = []
            
        state["conversation_log"].append({
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "input": {
                "symptoms": symptoms,
                "severity": severity,
                "red_flags": red_flags,
                "location": location
            },
            "output": routing_result
        })

        logger.info(f"{self.agent_name}: Assessment complete. Routed to {primary}.")
        
        return state