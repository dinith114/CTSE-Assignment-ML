"""
Travel Risk Assessment Agent for E-Channeling System
Evaluates travel distance, time, and risk for patient appointments.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, Optional
from datetime import datetime
import json
import requests
import logging
import re
import textwrap
from app.tools.distance_calculator_tool import DistanceCalculatorTool
from app.llm.ollama_client import run_ollama
from app.logger_config import get_logger

logger = get_logger(__name__)


class TravelRiskAgent:
    """
    Agent responsible for assessing travel risks and providing route advice.
    
    Responsibilities:
    1. Calculate travel distance and time between patient and hospital locations (cities or institutions)
    2. Normalize location names (handles city names like "Homagama" or institution names like "Sri Lanka Institute of Information Technology")
    3. Generate route advice based on distance
    4. Raise warnings for urgent/high-severity patients with long travel times
    5. Provide structured output for appointment coordinator
    
    Note: patient_city and hospital_city can be either:
    - City names (e.g., "Colombo", "Homagama")
    - Institution/landmark names (e.g., "Sri Lanka Institute of Information Technology")
    - Misspelled versions of the above (will be normalized via LLM + Nominatim fallback)
    
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
        self.reasoning_timeout = int(os.getenv("OLLAMA_REASONING_TIMEOUT", "60"))
        
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
            # Place extraction/normalization via Ollama is intentionally disabled.
            # Use user-provided places directly, then rely on geocoding fallback if needed.
            normalized_patient_city = patient_city
            normalized_hospital_city = hospital_city

            state["patient_city"] = normalized_patient_city
            state["hospital_city"] = normalized_hospital_city

            # Calculate travel information. If geocoding fails, retry once with
            # Nominatim suggestions (useful when Ollama is unavailable and input has typos).
            travel_mode = state.get("travel_mode", "default")
            try:
                travel_info = self.distance_tool.calculate_travel(
                    patient_city=normalized_patient_city,
                    hospital_city=normalized_hospital_city,
                    severity=severity,
                    travel_mode=travel_mode
                )
            except ValueError as geocode_error:
                logger.warning(
                    f"{self.agent_name}: Initial geocoding failed ({geocode_error}). Trying Nominatim suggestion fallback."
                )

                try:
                    fallback_patient = self._nominatim_suggest(normalized_patient_city) or normalized_patient_city
                except Exception:
                    fallback_patient = normalized_patient_city

                try:
                    fallback_hospital = self._nominatim_suggest(normalized_hospital_city) or normalized_hospital_city
                except Exception:
                    fallback_hospital = normalized_hospital_city

                # Retry only if at least one location changed.
                if (
                    fallback_patient == normalized_patient_city
                    and fallback_hospital == normalized_hospital_city
                ):
                    raise

                normalized_patient_city = fallback_patient
                normalized_hospital_city = fallback_hospital
                state["patient_city"] = normalized_patient_city
                state["hospital_city"] = normalized_hospital_city

                travel_info = self.distance_tool.calculate_travel(
                    patient_city=normalized_patient_city,
                    hospital_city=normalized_hospital_city,
                    severity=severity,
                    travel_mode=travel_mode
                )
            
            # Perform risk assessment
            risk_assessment = self._assess_risk(travel_info, severity)

            # Optional local LLM reasoning for explainability.
            if self.use_local_llm:
                llm_reasoning = self._generate_llm_reasoning(
                    patient_city=normalized_patient_city,
                    hospital_city=normalized_hospital_city,
                    severity=severity,
                    travel_info=travel_info,
                    risk_assessment=risk_assessment,
                )
                if llm_reasoning:
                    risk_assessment["llm_reasoning"] = llm_reasoning
            
            # Fallback recommendation if LLM unavailable
            if "llm_reasoning" not in risk_assessment:
                risk_assessment["llm_reasoning"] = risk_assessment.get("recommendation", "No recommendation available")
            
            # Update state with results
            travel_info["original_patient_city"] = patient_city
            travel_info["original_hospital_city"] = hospital_city
            travel_info["normalized_patient_city"] = normalized_patient_city
            travel_info["normalized_hospital_city"] = normalized_hospital_city
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
            
            # Print travel summary for immediate visibility
            print("\n" + "="*60)
            print("FINAL APPOINTMENT RECOMMENDATION")
            print("="*60)
            print(self.get_travel_summary(state))
            
            logger.info(f"{self.agent_name}: Assessment complete - {risk_assessment['risk_level']}")
            return state
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Error processing travel assessment: {e}")
            state["error"] = str(e)
            # Provide fallback travel_info with error message but still include original locations
            state["travel_info"] = {
                "error": str(e),
                "source_city": patient_city,
                "destination_city": hospital_city,
                "distance_km": None,
                "travel_time_hours": None,
                "travel_time_minutes": None,
                "route_advice": "Unable to calculate travel details due to geocoding error.",
                "warning_message": None
            }
            # Still provide fallback risk assessment
            state["risk_assessment"] = {
                "risk_level": severity.upper(),
                "recommendation": "Unable to assess travel risk. Please check location names and try again.",
                "llm_reasoning": "Unable to assess travel risk. Please check location names and try again.",
                "requires_alternative": False
            }
            return state

    def _resolve_locations_from_llm(self, patient_city: str, hospital_city: str, severity: str) -> Dict[str, str]:
        """
        Legacy placeholder for place normalization.

        Ollama-based place extraction is disabled; return original values unchanged.
        """
        return {
            "patient_city": patient_city,
            "hospital_city": hospital_city,
        }

    def _nominatim_suggest(self, name: str) -> Optional[str]:
        """Query Nominatim for a best-match display name for a possibly-misspelled place.

        Returns the `display_name` from the first match, or None if no match.
        """
        if not name:
            return None

        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": name, "format": "json", "limit": 1}
        headers = {"User-Agent": "E-Channeling-System/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if data and isinstance(data, list) and len(data) > 0:
            display = data[0].get("display_name")
            if display:
                # Keep display_name concise: prefer up to first 3 comma-separated parts
                parts = [p.strip() for p in display.split(',')]
                short = ', '.join(parts[:3])
                return short
        return None

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
            "Follow this priority order exactly: (1) if severity is high or urgent, recommend 1990 Suwa Seriya or ambulance first; (2) if the trip is long (over 50 km) and severity is not high, recommend car or taxi; (3) otherwise recommend other options such as bus, train, teleconsultation, or nearest facility. "
            "Do not recommend only bus for long trips. "
            "Only discuss practical Sri Lankan travel and care options such as car, taxi, bus, train, ambulance, 1990 Suwa Seriya, teleconsultation, or nearest facility. "
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

        output = run_ollama(
            prompt=prompt,
            model=self.llm_model,
            timeout=self.reasoning_timeout,
        )
        if not output:
            logger.info("Local Ollama reasoning unavailable; continuing with rule-based output.")
            output = ""

        clean_output = self._sanitize_text(output)
        distance_km = float(travel_info.get("distance_km", 0) or 0)
        severity_lower = severity.lower()

        if severity_lower in ["high", "urgent"]:
            fallback = (
                "Because this is a high-severity case, use 1990 Suwa Seriya or an ambulance first, "
                "and seek the nearest facility if urgent transport is needed."
            )
        elif distance_km > 50:
            fallback = (
                "Because the journey is long, car or taxi is recommended for direct travel, "
                "with teleconsultation or bus/train as secondary options if appropriate."
            )
        else:
            fallback = (
                "For this shorter trip, consider bus, train, taxi, or teleconsultation depending on comfort and urgency."
            )

        if not clean_output:
            return fallback

        normalized = clean_output.lower()
        if severity_lower in ["high", "urgent"]:
            if "1990" not in normalized and "ambulance" not in normalized:
                return fallback
        elif distance_km > 50:
            if "car" not in normalized and "taxi" not in normalized:
                return fallback
        else:
            if all(option not in normalized for option in ["bus", "train", "taxi", "teleconsultation"]):
                return fallback

        return clean_output

    def _sanitize_text(self, text: str) -> str:
        """Remove ANSI/control characters that can leak from local CLI output."""
        if not text:
            return ""

        # Remove ANSI escape sequences, e.g. "\x1b[3D\x1b[K".
        no_ansi = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)
        # Remove non-printable control chars except newline/tab for readability.
        no_ctrl = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]", "", no_ansi)

        # Fix wrapped fragment duplicates from terminal-style rendering,
        # e.g. "sho short" -> "short", "fo for" -> "for".
        cleaned = re.sub(r"\b([A-Za-z]{2,4})\s+(\1[A-Za-z]+)\b", r"\2", no_ctrl)

        # Normalize repeated whitespace while preserving line breaks.
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _extract_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract a JSON object from LLM output when it returns fenced or surrounding text."""
        if not text:
            return None

        candidate = text.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
            candidate = re.sub(r"\s*```$", "", candidate)

        try:
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", candidate, flags=re.DOTALL)
        if not match:
            return None

        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    
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
        severity = state.get("severity", "Unknown")
        
        # Format distance and time with fallback for None values
        distance = travel_info.get('distance_km')
        distance_str = f"{distance} km" if distance is not None else "Unable to calculate"
        
        time = travel_info.get('travel_time_hours')
        time_str = f"{time} hours" if time is not None else "Unable to calculate"
        
        # Get recommendation with fallback
        recommendation = risk.get('llm_reasoning') or risk.get('recommendation') or 'No recommendation available'
        
        summary = textwrap.dedent(f"""
        🚗 TRAVEL ASSESSMENT SUMMARY
        📍 From: {travel_info.get('source_city', 'Unknown')}
        🏥 To: {travel_info.get('destination_city', 'Unknown')}
        📏 Distance: {distance_str}
        ⏱️ Estimated travel time: {time_str}
        🚦 Risk Level: {severity}
        💡 Recommendation: {recommendation}
        """).strip()
        
        if travel_info.get('warning_message'):
            summary += f"\n⚠️ {travel_info['warning_message']}"
        
        if "error" in travel_info and travel_info['error']:
            summary += f"\n❌ Error: {travel_info['error']}"
        
        return summary