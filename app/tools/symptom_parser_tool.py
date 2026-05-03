"""
Custom tool for Symptom Triage assessment.

This tool acts as a deterministic fallback and real-world interface.
It parses symptom text, extracts known symptom keywords, identifies
red flags, and assigns severity/urgency levels. 

Real-world Interaction:
    It writes high-severity cases to a local alert log file, demonstrating
    agent capability to interact with the file system.
"""

from typing import Any, Dict, List
import os
from datetime import datetime

class SymptomParserTool:
    """
    Rule-based symptom parser and real-world logging tool for preliminary e-channeling triage.
    """

    LOG_FILE_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "emergency_alerts.log")

    SYMPTOM_CATALOG: Dict[str, List[str]] = {
        "chest pain": ["chest pain", "chest tightness", "pain in chest"],
        "shortness of breath": ["shortness of breath", "breathing difficulty", "difficulty breathing"],
        "dizziness": ["dizziness", "dizzy", "lightheaded"],
        "fever": ["fever", "high temperature"],
        "cough": ["cough", "coughing"],
        "headache": ["headache", "head pain"],
        "abdominal pain": ["abdominal pain", "stomach pain", "belly pain"],
        "skin rash": ["rash", "skin rash", "itchy skin"],
        "vomiting": ["vomiting", "vomit", "throwing up"],
        "back pain": ["back pain", "lower back pain"],
    }

    RED_FLAG_SYMPTOMS = {
        "chest pain",
        "shortness of breath",
        "dizziness",
    }

    SEVERITY_WEIGHTS: Dict[str, int] = {
        "chest pain": 3,
        "shortness of breath": 3,
        "dizziness": 2,
        "abdominal pain": 2,
        "vomiting": 2,
        "fever": 1,
        "cough": 1,
        "headache": 1,
        "skin rash": 1,
        "back pain": 1,
    }

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse patient symptom text and return structured triage data.

        Args:
            text: Patient-entered free-text symptom description.

        Returns:
            Dictionary containing symptoms, severity, urgency, red flags,
            confidence score, and triage note.

        Raises:
            ValueError: If symptom text is empty or invalid.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Symptom description cannot be empty.")

        normalized_text = text.lower().strip()
        symptoms = self._extract_symptoms(normalized_text)
        red_flags = [symptom for symptom in symptoms if symptom in self.RED_FLAG_SYMPTOMS]

        severity_score = sum(self.SEVERITY_WEIGHTS.get(symptom, 0) for symptom in symptoms)
        severity = self._classify_severity(severity_score, red_flags)
        urgency = self._classify_urgency(severity)

        confidence = self._calculate_confidence(symptoms)
        triage_note = self._build_triage_note(symptoms, severity, red_flags)

        # Real-world Interaction: Write to local log for high-severity or red-flag cases
        is_emergency = severity == "high" or len(red_flags) > 0
        if is_emergency:
            self._write_local_alert_log(symptoms, severity, red_flags)

        return {
            "symptoms": symptoms,
            "severity": severity,
            "urgency": urgency,
            "red_flags": red_flags,
            "severity_score": severity_score,
            "confidence": confidence,
            "triage_note": triage_note,
            "safety_disclaimer": (
                "This is a preliminary triage summary for specialist routing only, "
                "not a medical diagnosis."
            ),
            "emergency_logged": is_emergency
        }

    def _write_local_alert_log(self, symptoms: List[str], severity: str, red_flags: List[str]) -> None:
        """
        Write an alert to a local text file for real-world observability.
        
        Args:
            symptoms: List of extracted symptoms.
            severity: The assigned severity tier.
            red_flags: List of identified life-threatening symptoms.
            
        Raises:
            IOError: If unable to write the log file.
        """
        try:
            os.makedirs(os.path.dirname(self.LOG_FILE_PATH), exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alert_entry = (
                f"[{timestamp}] EMERGENCY ALERT | Severity: {severity.upper()}\n"
                f"   Red Flags: {', '.join(red_flags) if red_flags else 'None'}\n"
                f"   All Symptoms: {', '.join(symptoms) if symptoms else 'None'}\n"
                f"{'-'*60}\n"
            )
            with open(self.LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(alert_entry)
        except Exception as e:
            # Robust error handling: Log failure but do not crash the triage workflow
            print(f"Warning: Failed to write emergency alert to disk: {e}")

    def _extract_symptoms(self, normalized_text: str) -> List[str]:
        """Extract known symptoms from normalized text."""
        extracted: List[str] = []

        for symptom, keywords in self.SYMPTOM_CATALOG.items():
            if any(keyword in normalized_text for keyword in keywords):
                extracted.append(symptom)

        return extracted

    def _classify_severity(self, score: int, red_flags: List[str]) -> str:
        """Classify severity based on score and red-flag symptoms."""
        if len(red_flags) >= 2 or score >= 5:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

    def _classify_urgency(self, severity: str) -> str:
        """Map severity level to urgency level."""
        urgency_map = {
            "high": "Urgent attention required. Please seek medical help immediately.",
            "medium": "Priority medical evaluation is recommended.",
            "low": "Routine medical assessment is sufficient at your convenience.",
        }
        return urgency_map[severity]

    def _calculate_confidence(self, symptoms: List[str]) -> float:
        """Calculate simple confidence based on extracted symptoms."""
        if not symptoms:
            return 0.2
        if len(symptoms) >= 3:
            return 0.9
        if len(symptoms) == 2:
            return 0.75
        return 0.6

    def _build_triage_note(self, symptoms: List[str], severity: str, red_flags: List[str]) -> str:
        """Build a short explanation for downstream agents."""
        if not symptoms:
            return "No clear known symptoms were extracted from the patient input."

        if red_flags:
            return (
                f"Extracted {len(symptoms)} symptom(s). Red-flag symptoms detected: "
                f"{', '.join(red_flags)}. Severity classified as {severity}."
            )

        return f"Extracted {len(symptoms)} symptom(s). Severity classified as {severity}."


def symptom_parser_tool(text: str) -> Dict[str, Any]:
    """
    Tool wrapper for agent workflows.

    Args:
        text: Patient-entered symptom text.

    Returns:
        Structured triage dictionary.
    """
    return SymptomParserTool().parse(text)