"""
Travel Risk Assessment Agent for E-Channeling System
Evaluates travel distance, time, and risk for patient appointments.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, Optional
from datetime import datetime
import logging
from app.tools.distance_calculator_tool import DistanceCalculatorTool
from app.llm.ollama_client import run_ollama
from app.logger_config import get_logger

logger = get_logger(__name__)


class TravelRiskAgent:
    """
    Agent responsible for assessing travel risks and providing route advice.
    
    Responsibilities:
    1. Calculate travel distance and time between patient and hospital cities
    2. Generate route advice based on distance
    3. Raise warnings for urgent/high-severity patients with long travel times
    4. Provide structured output for appointment coordinator
    
    System Prompt (embedded in agent logic):
    You are a Travel Risk Assessment Agent in a healthcare e-channeling system.
    Your goal is to ensure patient safety by evaluating travel feasibility.
    You MUST:
    - Always calculate distance before providing advice
    - Flag any travel time > 2 hours for urgent cases as high risk
    - Suggest alternative modes of transport for medium-risk scenarios
    - Never recommend travel that would compromise patient health
    """
    
    def __init__(self, cache_file: str = "app/data/city_distances/city_coordinates.json"):
        """
        Initialize the Travel Risk Agent.
        
        Args:
            cache_file: Path to coordinate cache file
        """
        self.distance_tool = DistanceCalculatorTool(cache_file=cache_file)
        self.agent_name = "TravelRiskAssessmentAgent"
        self.use_local_llm = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
        self.llm_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the travel risk assessment for the current appointment state.
        
        Args:
            state: Global state containing patient info, severity, and hospital
            
        Returns:
            Updated state with travel_info and risk_assessment
        """
        logger.info(f"{self.agent_name}: Starting travel risk assessment")
        
        # Extract required information from state
        patient_city = state.get("patient_city")
        hospital_city = state.get("hospital_city")
        severity = state.get("severity", "medium")
        
        if not patient_city or not hospital_city:
            error_msg = "Missing patient_city or hospital_city in state"
            logger.error(error_msg)
            state["error"] = error_msg
            state["travel_info"] = {"error": error_msg}
            return state
        
        try:
            # Calculate travel information
            travel_info = self.distance_tool.calculate_travel(
                patient_city=patient_city,
                hospital_city=hospital_city,
                severity=severity,
                travel_mode=state.get("travel_mode", "default")
            )
            
            # Perform risk assessment
            risk_assessment = self._assess_risk(travel_info, severity)

            # Optional local LLM reasoning for explainability.
            if self.use_local_llm:
                llm_reasoning = self._generate_llm_reasoning(
                    patient_city=patient_city,
                    hospital_city=hospital_city,
                    severity=severity,
                    travel_info=travel_info,
                    risk_assessment=risk_assessment,
                )
                if llm_reasoning:
                    risk_assessment["llm_reasoning"] = llm_reasoning
            
            # Update state with results
            state["travel_info"] = travel_info
            state["risk_assessment"] = risk_assessment
            
            # Add to conversation log for observability
            if not isinstance(state.get("conversation_log"), list):
                state["conversation_log"] = []
            state["conversation_log"].append({
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "input": {
                    "patient_city": patient_city,
                    "hospital_city": hospital_city,
                    "severity": severity
                },
                "output": travel_info,
                "risk_assessment": risk_assessment
            })
            
            logger.info(f"{self.agent_name}: Assessment complete - {risk_assessment['risk_level']}")
            return state
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Error processing travel assessment: {e}")
            state["error"] = str(e)
            state["travel_info"] = {"error": str(e)}
            return state

    def _generate_llm_reasoning(
        self,
        patient_city: str,
        hospital_city: str,
        severity: str,
        travel_info: Dict[str, Any],
        risk_assessment: Dict[str, Any],
    ) -> Optional[str]:
        """
        Generate a concise local-LLM explanation for the recommendation.

        Returns None if Ollama is unavailable.
        """
        prompt = (
            "You are a healthcare travel risk assistant for Sri Lanka. "
            "Provide one or two concise sentences explaining the recommendation. "
            "Only discuss road or local travel options such as car, bus, train, teleconsultation, or nearest facility. "
            "Do not mention flights, airplanes, domestic flights, or any unrelated transport. "
            "Do not invent new facts; use only the provided case details.\n"
            f"Patient location: {patient_city}\n"
            f"Hospital location: {hospital_city}\n"
            f"Severity: {severity}\n"
            f"Distance km: {travel_info.get('distance_km')}\n"
            f"Travel hours: {travel_info.get('travel_time_hours')}\n"
            f"Risk level: {risk_assessment.get('risk_level')}\n"
            f"Recommendation: {risk_assessment.get('recommendation')}"
        )

        output = run_ollama(prompt=prompt, model=self.llm_model, timeout=30)
        if not output:
            logger.info("Local Ollama reasoning unavailable; continuing with rule-based output.")
            return None
        return output.strip()
    
    def _assess_risk(self, travel_info: Dict[str, Any], severity: str) -> Dict[str, Any]:
        """
        Assess the risk level based on travel information and patient severity.
        
        Args:
            travel_info: Dictionary with travel details
            severity: Patient severity level
            
        Returns:
            Risk assessment dictionary
        """
        distance = travel_info.get("distance_km", 0)
        travel_hours = travel_info.get("travel_time_hours", 0)
        
        # Risk matrix based on severity and travel time
        if severity.lower() in ["high", "urgent"]:
            if travel_hours > 2:
                risk_level = "CRITICAL"
                recommendation = "DO NOT TRAVEL - Seek immediate local care or emergency transport"
            elif travel_hours > 1:
                risk_level = "HIGH"
                recommendation = "Strongly recommend teleconsultation or nearest facility"
            else:
                risk_level = "MEDIUM"
                recommendation = "Proceed with caution - prioritize appointment scheduling"
        else:  # low or medium severity
            if travel_hours > 4:
                risk_level = "MEDIUM"
                recommendation = "Consider overnight stay or alternative closer hospital"
            elif travel_hours > 2:
                risk_level = "LOW"
                recommendation = "Travel feasible - plan accordingly"
            else:
                risk_level = "VERY_LOW"
                recommendation = "No significant travel concerns"
        
        return {
            "risk_level": risk_level,
            "recommendation": recommendation,
            "travel_time_hours": travel_hours,
            "distance_km": distance,
            "severity": severity,
            "requires_alternative": risk_level in ["CRITICAL", "HIGH"]
        }
    
    def get_travel_summary(self, state: Dict[str, Any]) -> str:
        """
        Generate a human-readable travel summary for frontend display.
        
        Args:
            state: Current global state with travel_info
            
        Returns:
            Formatted travel summary string
        """
        travel_info = state.get("travel_info", {})
        risk = state.get("risk_assessment", {})
        
        if "error" in travel_info:
            return f"❌ Travel assessment error: {travel_info['error']}"
        
        summary = f"""
        🚗 TRAVEL ASSESSMENT SUMMARY
        📍 From: {travel_info.get('source_city', 'Unknown')}
        🏥 To: {travel_info.get('destination_city', 'Unknown')}
        📏 Distance: {travel_info.get('distance_km', 0)} km
        ⏱️ Estimated travel time: {travel_info.get('travel_time_hours', 0)} hours
        🚦 Risk Level: {risk.get('risk_level', 'Unknown')}
        💡 Recommendation: {risk.get('recommendation', 'N/A')}
        🗺️ Route Advice: {travel_info.get('route_advice', 'N/A')}
        """

        if risk.get("llm_reasoning"):
            summary += f"\n🤖 LLM Reasoning: {risk['llm_reasoning']}"
        
        if travel_info.get('warning_message'):
            summary += f"\n⚠️ {travel_info['warning_message']}"
        
        return summary


# For integration with LangGraph/CrewAI workflows
def create_travel_risk_node():
    """Factory function to create travel risk agent node for workflow."""
    agent = TravelRiskAgent()
    return agent.process