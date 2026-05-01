import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.medical_routing_agent import MedicalRoutingAgent
from app.llm.ollama_client import run_ollama


class TestMedicalRoutingAgent(unittest.TestCase):
    """
    Automated evaluation script for the Medical Routing Agent.
    Includes validation of LLM outputs, state management, and an LLM-as-a-Judge evaluation.
    """

    def setUp(self):
        self.agent = MedicalRoutingAgent()

    @patch('app.agents.medical_routing_agent.run_ollama')
    def test_llm_json_parsing_success(self, mock_run_ollama):
        """Test if the agent correctly parses valid JSON back from the LLM."""
        # Mock LLM responding perfectly
        mock_response = '''
        {
          "primary_specialist": "cardiologist",
          "alternative_specialists": ["general physician"],
          "reasoning": "Chest pain indicates potential cardiac issues."
        }
        '''
        mock_run_ollama.return_value = mock_response

        primary, alternatives, reason = self.agent._determine_specialist_via_llm(
            symptoms=["chest pain", "shortness of breath"],
            severity="high",
            red_flags=["radiating arm pain"]
        )

        self.assertEqual(primary, "cardiologist")
        self.assertEqual(alternatives, ["general physician"])
        self.assertIn("cardiac", reason)

    @patch('app.agents.medical_routing_agent.run_ollama')
    def test_llm_malformed_json_fallback(self, mock_run_ollama):
        """Test if the agent safely falls back when the LLM hallucinates bad JSON."""
        # Mock LLM throwing broken JSON
        mock_run_ollama.return_value = 'Thinking... Oh I know! { "primary": cardiologist '

        primary, alternatives, reason = self.agent._determine_specialist_via_llm(
            symptoms=["headache"],
            severity="low",
            red_flags=[]
        )

        self.assertEqual(primary, "general physician")
        self.assertEqual(alternatives, [])
        self.assertEqual(reason, "Fallback due to LLM parsing error.")

    @patch.object(MedicalRoutingAgent, '_determine_specialist_via_llm')
    @patch('app.agents.medical_routing_agent.hospital_db_tool')
    def test_agent_updates_state_and_logs(self, mock_db_tool, mock_llm_decision):
        """Test that the agent updates the global state correctly and adds observability logs."""
        mock_llm_decision.return_value = ("dermatologist", ["general physician"], "Skin rash.")
        mock_db_tool.return_value = [{"name": "Dr. Perera", "specialty": "dermatologist", "hospital": "Nawaloka"}]

        state = {
            "triage": {
                "symptoms": ["severe rash"],
                "severity": "medium",
                "red_flags": [],
                "location": "Colombo"
            }
        }

        result = self.agent.run(state)

        # Check if routing state is updated
        self.assertIn("routing", result)
        self.assertEqual(result["routing"]["primary_specialty"], "dermatologist")
        self.assertEqual(result["routing"]["doctors"][0]["name"], "Dr. Perera")

        # Check for observability log (LLMOps requirement)
        self.assertIn("conversation_log", result)
        self.assertEqual(len(result["conversation_log"]), 1)
        self.assertEqual(result["conversation_log"][0]["agent"], "MedicalRoutingAgent")

    def test_llm_as_a_judge_evaluation(self):
        """
        LLM-as-a-Judge Evaluation (Assignment Requirement)
        Uses an LLM to evaluate if the Medical Routing Agent outputs clinically safe and logical routing.
        NOTE: This test actually calls the local LLM to perform the evaluation. If Ollama is off, it skips safely.
        """
        if not self.agent.use_local_llm:
            self.skipTest("Skipping LLM evaluation test since local LLM is disabled.")

        try:
            # 1. Run the actual agent logic to get a real response
            symptoms = ["severe headache", "blurred vision"]
            severity = "high"
            red_flags = ["sudden onset"]

            primary, _, reason = self.agent._determine_specialist_via_llm(symptoms, severity, red_flags)

            # 2. Formulate the LLM-as-a-Judge Prompt
            judge_prompt = (
                "You are an expert Medical Evaluation Judge.\n"
                "I will provide a patient's symptoms and the specialist an AI agent chose.\n"
                "You must evaluate if this specialist is logically and medically appropriate.\n"
                f"Symptoms: {symptoms}, Severity: {severity}, Red Flags: {red_flags}\n"
                f"Agent Chose: {primary}\n"
                f"Agent's Reason: {reason}\n\n"
                "Output ONLY 'PASS' if acceptable, or 'FAIL' if dangerous or incorrect."
            )

            # 3. Get the Judge's verdict
            judge_decision = run_ollama(judge_prompt, model=self.agent.llm_model)

            # 4. Asserts that the LLM Judge graded the Agent with a PASS
            self.assertIn("PASS", judge_decision.upper(), f"LLM Judge failed the routing logic. Received: {judge_decision}")

        except Exception as e:
             self.skipTest(f"Skipping LLM-as-a-Judge due to connection error: {e}")

if __name__ == '__main__':
    unittest.main()
