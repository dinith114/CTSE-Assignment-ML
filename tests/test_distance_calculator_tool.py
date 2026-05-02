"""
Automated evaluation script for Distance Calculator Tool.
Includes property-based testing, edge case validation, and API integration tests.
"""

import unittest
import sys
import os
import json
import tempfile
import requests
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.distance_calculator_tool import DistanceCalculatorTool


class TestDistanceCalculatorTool(unittest.TestCase):
    """Test suite for the distance calculator custom tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary directory so Windows can cleanly remove the cache.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_path = os.path.join(self.temp_dir.name, 'cache.json')
        with open(self.cache_path, 'w', encoding='utf-8') as cache_file:
            json.dump({}, cache_file)
        self.tool = DistanceCalculatorTool(cache_file=self.cache_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_haversine_distance_known_values(self):
        """Property test: Distance calculation should be symmetric and accurate."""
        # Colombo (6.9271, 79.8612) to Kandy (7.2906, 80.6337)
        distance = self.tool._haversine_distance(6.9271, 79.8612, 7.2906, 80.6337)
        
        # Expected distance is about 94 km with the current coordinates
        self.assertAlmostEqual(distance, 94.3, delta=1.0)
        
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
        """Test Nominatim API integration with mock response."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                'lat': '6.9271',
                'lon': '79.8612'
            }
        ]
        mock_get.return_value = mock_response
        
        coords = self.tool._geocode_city("Colombo")
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 2)
        
        # Verify cache was saved
        self.assertIn("colombo", self.tool.cache)
    
    @patch('app.tools.distance_calculator_tool.requests.get')
    def test_geocoding_failure_handling(self, mock_get):
        """Test graceful handling of API failures."""
        mock_get.side_effect = requests.RequestException("API down")
        
        with self.assertRaises(Exception):
            self.tool._geocode_city("Unknown City")
    
    def test_calculate_travel_complete_flow(self):
        """Integration test: Complete travel calculation with deterministic mocked data."""
        with patch.object(self.tool, '_geocode_city') as mock_geocode, \
             patch.object(self.tool, '_get_road_distance') as mock_road:
            mock_geocode.side_effect = [(6.9271, 79.8612), (7.2906, 80.6337)]
            mock_road.return_value = 115.5
            result = self.tool.calculate_travel("Colombo, Sri Lanka", "Kandy, Sri Lanka", "high")
        
        # Validate output structure
        self.assertIn("distance_km", result)
        self.assertIn("estimated_travel_time_minutes", result)
        self.assertIn("route_advice", result)
        self.assertIn("warning_message", result)
        
        # Distance should reflect the mocked OSRM route
        self.assertAlmostEqual(result["distance_km"], 115.5, delta=0.1)
        
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
