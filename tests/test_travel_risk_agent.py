"""
Automated evaluation script for Travel Risk Assessment Agent.
Includes property-based testing, edge case validation, and security checks.
"""

import unittest
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.distance_calculator_tool import DistanceCalculatorTool
from app.agents.travel_risk_agent import TravelRiskAgent


class TestDistanceCalculatorTool(unittest.TestCase):
    """Test suite for the distance calculator custom tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use temporary file for cache during tests
        self.temp_cache = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.cache_path = self.temp_cache.name
        self.tool = DistanceCalculatorTool(cache_file=self.cache_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.cache_path):
            os.unlink(self.cache_path)
    
    def test_haversine_distance_known_values(self):
        """Property test: Distance calculation should be symmetric and accurate."""
        # Colombo (6.9271, 79.8612) to Kandy (7.2906, 80.6337)
        distance = self.tool._haversine_distance(6.9271, 79.8612, 7.2906, 80.6337)
        
        # Expected distance ~115 km
        self.assertAlmostEqual(distance, 115, delta=10)
        
        # Test symmetry
        distance_reverse = self.tool._haversine_distance(7.2906, 80.6337, 6.9271, 79.8612)
        self.assertAlmostEqual(distance, distance_reverse, delta=0.1)
    
    def test_estimate_travel_time(self):
        """Test travel time estimation for various distances."""
        # Short distance should have minimum time
        short_time = self.tool._estimate_travel_time(1)
        self.assertEqual(short_time, 5)  # Minimum 5 minutes
        
        # 100 km at 55 km/h = ~109 minutes
        med_time = self.tool._estimate_travel_time(100)
        self.assertTrue(100 < med_time < 120)
        
        # Different modes should give different times
        car_time = self.tool._estimate_travel_time(100, "car")
        bus_time = self.tool._estimate_travel_time(100, "bus")
        self.assertLess(car_time, bus_time)
    
    def test_generate_warning_for_urgent_cases(self):
        """Critical test: Urgent cases with long travel must trigger warnings."""
        # Urgent + long travel (>2 hours)
        warning = self.tool._generate_warning(200, 180, "urgent")
        self.assertIsNotNone(warning)
        self.assertIn("URGENT WARNING", warning)
        
        # Low severity + long travel - no warning
        warning = self.tool._generate_warning(400, 300, "low")
        self.assertIsNone(warning)
        
        # Medium + moderate travel
        warning = self.tool._generate_warning(50, 60, "medium")
        self.assertIsNone(warning)
    
    @patch('app.tools.distance_calculator_tool.requests.get')
    def test_geocoding_api_call(self, mock_get):
        """Test Photon API integration with mock response."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'features': [{
                'geometry': {'coordinates': [79.8612, 6.9271]},
                'properties': {'name': 'Colombo'}
            }]
        }
        mock_get.return_value = mock_response
        
        coords = self.tool._geocode_city("Colombo")
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 2)
        
        # Verify cache was saved
        self.assertIn("colombo", self.tool.cache)
    
    @patch('app.tools.distance_calculator_tool.requests.get')
    def test_geocoding_failure_handling(self, mock_get):
        """Test graceful handling of API failures."""
        mock_get.side_effect = Exception("API down")
        
        with self.assertRaises(Exception):
            self.tool._geocode_city("Unknown City")
    
    def test_calculate_travel_complete_flow(self):
        """Integration test: Complete travel calculation with real API."""
        # Skip if no internet (for CI/CD)
        import socket
        try:
            socket.create_connection(("photon.komoot.io", 80), timeout=5)
        except OSError:
            self.skipTest("No internet connection")
        
        result = self.tool.calculate_travel("Colombo, Sri Lanka", "Kandy, Sri Lanka", "high")
        
        # Validate output structure
        self.assertIn("distance_km", result)
        self.assertIn("estimated_travel_time_minutes", result)
        self.assertIn("route_advice", result)
        self.assertIn("warning_message", result)
        
        # Distance should be roughly 100-130 km
        self.assertTrue(80 < result["distance_km"] < 150)
        
        # High severity should generate warning for this distance
        self.assertIsNotNone(result["warning_message"])
    
    def test_edge_case_empty_city_names(self):
        """Test handling of invalid inputs."""
        with self.assertRaises(ValueError):
            self.tool.calculate_travel("", "Colombo", "medium")
        
        with self.assertRaises(ValueError):
            self.tool.calculate_travel("Colombo", "", "medium")
    
    def test_edge_case_nonexistent_city(self):
        """Test graceful handling of non-existent cities."""
        with self.assertRaises(ValueError):
            self.tool.calculate_travel("FakeCityXYZ123", "Colombo", "medium")


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
        self.assertIn("LOW", summary)
    
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