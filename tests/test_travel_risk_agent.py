"""
Automated evaluation script for Travel Risk Assessment Agent.
Includes property-based testing, edge case validation, and security checks.
"""

import unittest
import sys
import os
import subprocess
from unittest.mock import patch
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.travel_risk_agent import TravelRiskAgent


class TestTravelRiskAgent(unittest.TestCase):
    """Test suite for the Travel Risk Agent's reasoning and state management."""
    
    def setUp(self):
        self.agent = TravelRiskAgent()
    
    def test_agent_process_requires_cities(self):
        """Test agent properly validates input state."""
        state = {"severity": "high"}  # Missing cities
        result = self.agent.process(state)
        
        self.assertIn("error", result)
        self.assertIn("missing", result["error"].lower())
    
    def test_agent_updates_state_correctly(self):
        """Test agent correctly updates global state with travel info."""
        state = {
            "patient_city": "Colombo, Sri Lanka",
            "hospital_city": "Kandy, Sri Lanka",
            "severity": "urgent"
        }
        
        # Mock the distance tool to avoid API calls
        with patch.object(self.agent.distance_tool, 'calculate_travel') as mock_calc:
            mock_calc.return_value = {
                "distance_km": 115.5,
                "estimated_travel_time_minutes": 126,
                "route_advice": "Test advice",
                "warning_message": "Test warning"
            }
            
            result = self.agent.process(state)
        
        self.assertIn("travel_info", result)
        self.assertIn("risk_assessment", result)
        self.assertIn("conversation_log", result)
        self.assertEqual(len(result["conversation_log"]), 1)

    def test_agent_uses_original_places_without_ollama_extraction(self):
        """Test that place names are passed through directly (Ollama place extraction disabled)."""
        state = {
            "patient_city": "Homagoma",
            "hospital_city": "Asiri Surgcal",
            "severity": "medium"
        }

        with patch("app.agents.travel_risk_agent.run_ollama", return_value=None), \
             patch.object(self.agent.distance_tool, 'calculate_travel') as mock_calc:
            mock_calc.return_value = {"distance_km": 12.3, "travel_time_hours": 0.2}

            result = self.agent.process(state)

        mock_calc.assert_called_once()
        called_kwargs = mock_calc.call_args.kwargs
        self.assertEqual(called_kwargs["patient_city"], "Homagoma")
        self.assertEqual(called_kwargs["hospital_city"], "Asiri Surgcal")
        self.assertEqual(result["travel_info"]["original_patient_city"], "Homagoma")
        self.assertEqual(result["travel_info"]["original_hospital_city"], "Asiri Surgcal")
        self.assertEqual(result["patient_city"], "Homagoma")
        self.assertEqual(result["hospital_city"], "Asiri Surgcal")
    
    def test_agent_handles_institution_names(self):
        """Test that agent correctly handles institution names like 'Sri Lanka Institute of Information Technology'."""
        state = {
            "patient_city": "Sri Lanka Institute of Information Technology",
            "hospital_city": "Colombo",
            "severity": "medium"
        }

        with patch("app.agents.travel_risk_agent.run_ollama", return_value=None), \
             patch.object(self.agent.distance_tool, 'calculate_travel') as mock_calc:
            mock_calc.return_value = {"distance_km": 25, "travel_time_hours": 0.5}

            result = self.agent.process(state)

        mock_calc.assert_called_once()
        called_kwargs = mock_calc.call_args.kwargs
        self.assertEqual(called_kwargs["patient_city"], "Sri Lanka Institute of Information Technology")
        self.assertEqual(called_kwargs["hospital_city"], "Colombo")
        self.assertEqual(result["travel_info"]["original_patient_city"], "Sri Lanka Institute of Information Technology")
        self.assertEqual(result["patient_city"], "Sri Lanka Institute of Information Technology")

    def test_agent_retries_with_nominatim_suggestions_when_geocode_fails(self):
        """If Ollama normalization is unavailable, retry with Nominatim suggestions after geocode failure."""
        state = {
            "patient_city": "Homagoma",
            "hospital_city": "Kolombuwa",
            "severity": "medium"
        }

        with patch("app.agents.travel_risk_agent.run_ollama", return_value=None), \
             patch.object(self.agent, '_nominatim_suggest') as mock_suggest, \
             patch.object(self.agent.distance_tool, 'calculate_travel') as mock_calc:
            mock_calc.side_effect = [
                ValueError("Could not geocode hospital city: Kolombuwa"),
                {"distance_km": 18.0, "travel_time_hours": 0.4}
            ]

            def suggest_side_effect(name):
                mapping = {
                    "Homagoma": "Homagama, Sri Lanka",
                    "Kolombuwa": "Colombo, Sri Lanka",
                }
                return mapping.get(name)

            mock_suggest.side_effect = suggest_side_effect

            result = self.agent.process(state)

        self.assertEqual(mock_calc.call_count, 2)
        retry_kwargs = mock_calc.call_args.kwargs
        self.assertEqual(retry_kwargs["patient_city"], "Homagama, Sri Lanka")
        self.assertEqual(retry_kwargs["hospital_city"], "Colombo, Sri Lanka")
        self.assertEqual(result["patient_city"], "Homagama, Sri Lanka")
        self.assertEqual(result["hospital_city"], "Colombo, Sri Lanka")
    
    def test_risk_assessment_matrix(self):
        """Property test: Risk assessment follows defined matrix rules."""
        # CRITICAL case: urgent + >2 hours travel
        risk = self.agent._assess_risk({"travel_time_hours": 3, "distance_km": 200}, "urgent")
        self.assertEqual(risk["risk_level"], "CRITICAL")
        self.assertTrue(risk["requires_alternative"])
        
        # VERY_LOW case: low severity + short travel
        risk = self.agent._assess_risk({"travel_time_hours": 0.5, "distance_km": 30}, "low")
        self.assertEqual(risk["risk_level"], "VERY_LOW")
        self.assertFalse(risk["requires_alternative"])
        
        # MEDIUM case: medium severity + very long travel
        risk = self.agent._assess_risk({"travel_time_hours": 5, "distance_km": 300}, "medium")
        self.assertEqual(risk["risk_level"], "MEDIUM")
    
    def test_get_travel_summary_format(self):
        """Test summary generation for frontend display."""
        state = {
            "severity": "low",
            "travel_info": {
                "source_city": "Galle",
                "destination_city": "Colombo",
                "distance_km": 120,
                "travel_time_hours": 2.2,
                "route_advice": "Take highway",
                "warning_message": None
            },
            "risk_assessment": {
                "risk_level": "LOW",
                "recommendation": "Travel feasible"
            }
        }
        
        summary = self.agent.get_travel_summary(state)
        self.assertIn("Galle", summary)
        self.assertIn("Colombo", summary)
        self.assertIn("low", summary)
    
    def test_observability_logging(self):
        """Test that agent logs all inputs and outputs for tracking."""
        test_state = {
            "patient_city": "Negombo",
            "hospital_city": "Colombo",
            "severity": "medium"
        }
        
        with patch.object(self.agent.distance_tool, 'calculate_travel') as mock_calc:
            mock_calc.return_value = {"distance_km": 40}
            result = self.agent.process(test_state)
        
        log_entry = result["conversation_log"][0]
        self.assertEqual(log_entry["agent"], "TravelRiskAssessmentAgent")
        self.assertIn("timestamp", log_entry)
        self.assertIn("input", log_entry)
        self.assertIn("output", log_entry)
        self.assertEqual(log_entry["input"]["patient_city"], "Negombo")


def run_llm_as_judge_evaluation():
    """
    LLM-as-a-Judge evaluation for agent outputs.
    Requires Ollama running locally with a model like llama3.
    """
    import subprocess
    import json
    
    def query_ollama(prompt: str, model: str = "llama3.2:3b") -> str:
        """Query local Ollama model."""
        try:
            result = subprocess.run(
                ['ollama', 'run', model, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Ollama query failed: {e}")
            return ""
    
    # Test scenarios for LLM evaluation
    test_scenarios = [
        {
            "name": "Urgent case with long travel should warn",
            "input": {
                "patient_city": "Jaffna",
                "hospital_city": "Colombo", 
                "severity": "urgent"
            },
            "expected_behavior": "WARNING should be present",
            "critical_keywords": ["URGENT", "WARNING", "ambulance"]
        },
        {
            "name": "Low severity with short travel no warning",
            "input": {
                "patient_city": "Colombo",
                "hospital_city": "Colombo",
                "severity": "low"
            },
            "expected_behavior": "NO warning message",
            "critical_keywords": ["warning"]  # Should NOT contain
        }
    ]
    
    tool = DistanceCalculatorTool()
    
    for scenario in test_scenarios:
        print(f"\n🧪 LLM Judge Evaluating: {scenario['name']}")
        result = tool.calculate_travel(**scenario['input'])
        
        judge_prompt = f"""
        You are evaluating a travel risk assessment system for healthcare.
        
        Scenario: {scenario['name']}
        Expected behavior: {scenario['expected_behavior']}
        
        Actual output:
        distance: {result.get('distance_km')} km
        warning: {result.get('warning_message')}
        route_advice: {result.get('route_advice')}
        
        Does the actual output match the expected behavior? 
        Answer with just "PASS" or "FAIL" and a one-sentence reason.
        """
        
        judge_result = query_ollama(judge_prompt)
        print(f"Judge verdict: {judge_result}")


if __name__ == "__main__":
    # Run standard unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run LLM-as-Judge evaluation (requires Ollama)
    print("\n" + "="*50)
    print("Running LLM-as-Judge Evaluation")
    print("="*50)
    run_llm_as_judge_evaluation()