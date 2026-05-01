"""
Automated tests for Symptom Triage and Severity Assessment Agent.
"""

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.symptom_triage_agent import SymptomTriageAgent
from app.tools.symptom_parser_tool import symptom_parser_tool


class TestSymptomParserTool(unittest.TestCase):
    """Test suite for symptom_parser_tool."""

    def test_empty_input_raises_error(self) -> None:
        """Empty symptom text should raise ValueError."""
        with self.assertRaises(ValueError):
            symptom_parser_tool("")

    def test_extracts_basic_symptoms(self) -> None:
        """Tool should extract common symptoms from free text."""
        result = symptom_parser_tool("I have fever and cough since yesterday.")

        self.assertIn("fever", result["symptoms"])
        self.assertIn("cough", result["symptoms"])
        self.assertEqual(result["severity"], "medium")

    def test_high_severity_for_red_flags(self) -> None:
        """Chest pain and breathing difficulty should be urgent/high severity."""
        result = symptom_parser_tool("I have chest pain and shortness of breath.")

        self.assertEqual(result["severity"], "high")
        self.assertEqual(result["urgency"], "urgent")
        self.assertIn("chest pain", result["red_flags"])
        self.assertIn("shortness of breath", result["red_flags"])

    def test_low_severity_for_single_minor_symptom(self) -> None:
        """Single low-risk symptom should be classified as low severity."""
        result = symptom_parser_tool("I have a skin rash.")

        self.assertEqual(result["severity"], "low")
        self.assertEqual(result["urgency"], "routine")
        self.assertEqual(result["red_flags"], [])

    def test_output_schema(self) -> None:
        """Tool output should contain all required fields."""
        result = symptom_parser_tool("I feel dizzy and have a headache.")

        expected_keys = {
            "symptoms",
            "severity",
            "urgency",
            "red_flags",
            "severity_score",
            "confidence",
            "triage_note",
            "safety_disclaimer",
        }

        self.assertTrue(expected_keys.issubset(result.keys()))

    def test_no_diagnosis_is_returned(self) -> None:
        """Tool should not return disease diagnosis fields."""
        result = symptom_parser_tool("I have chest pain.")

        self.assertNotIn("diagnosis", result)
        self.assertNotIn("disease", result)


class TestSymptomTriageAgent(unittest.TestCase):
    """Test suite for SymptomTriageAgent."""

    def setUp(self) -> None:
        """Create agent before each test."""
        self.agent = SymptomTriageAgent()

    def test_agent_updates_state(self) -> None:
        """Agent should update shared state with triage result."""
        state = {
            "patient_text": "I have chest pain and dizziness.",
            "patient_city": "Colombo",
        }

        result = self.agent.process(state)

        self.assertIn("triage_result", result)
        self.assertIn("symptoms", result)
        self.assertIn("severity", result)
        self.assertIn("urgency", result)
        self.assertEqual(result["severity"], "high")

    def test_agent_adds_conversation_log(self) -> None:
        """Agent should add observability log entry to shared state."""
        state = {
            "patient_text": "I have fever and cough.",
            "patient_city": "Kandy",
        }

        result = self.agent.process(state)

        self.assertIn("conversation_log", result)
        self.assertEqual(result["conversation_log"][0]["agent"], "SymptomTriageAgent")
        self.assertEqual(result["conversation_log"][0]["tool_called"], "symptom_parser_tool")

    def test_agent_handles_invalid_input(self) -> None:
        """Agent should store error in state for invalid input."""
        state = {
            "patient_text": "",
            "patient_city": "Colombo",
        }

        result = self.agent.process(state)

        self.assertIn("error", result)
        self.assertIn("triage_result", result)
        self.assertIn("error", result["triage_result"])


if __name__ == "__main__":
    unittest.main(verbosity=2)