"""
Custom tool for Symptom Triage and Severity Assessment Agent.

Parses patient symptom text, extracts known symptom keywords, identifies
red flags, and assigns severity/urgency levels for downstream routing.
"""

from typing import Any, Dict, List


class SymptomParserTool:
    """Rule-based symptom parser for preliminary e-channeling triage."""

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
        }

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
            "high": "urgent",
            "medium": "priority",
            "low": "routine",
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