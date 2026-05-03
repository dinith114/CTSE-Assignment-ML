import unittest
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.schedule_optimizer_tool import ScheduleOptimizerTool
from app.agents.appointment_coordinator_agent import AppointmentCoordinatorAgent

class TestScheduleOptimizerTool(unittest.TestCase):
    """Test suite for the schedule optimizer tool."""

    def setUp(self):
        """Set up test fixtures with a temporary JSON file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = os.path.join(self.temp_dir.name, 'schedules.json')
        
        self.mock_data = {
            "hospitals": [
                {
                    "id": "H001",
                    "name": "Nawaloka Hospital",
                    "city": "Colombo, Sri Lanka",
                    "departments": [
                        {
                            "specialty": "Cardiologist",
                            "doctors": [
                                {
                                    "id": "D001",
                                    "name": "Dr. Ruwan Perera",
                                    "rating": 4.8,
                                    "available_slots": [
                                        { "day": "Monday", "start": "09:00", "end": "13:00", "max_patients": 10, "booked": 2 }
                                    ]
                                },
                                {
                                    "id": "D002",
                                    "name": "Dr. Kamal Silva",
                                    "rating": 4.0,
                                    "available_slots": [
                                        { "day": "Tuesday", "start": "10:00", "end": "12:00", "max_patients": 10, "booked": 8 }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "H002",
                    "name": "Kandy Hospital",
                    "city": "Kandy, Sri Lanka",
                    "departments": [
                        {
                            "specialty": "Cardiologist",
                            "doctors": [
                                {
                                    "id": "D003",
                                    "name": "Dr. Anura Bandara",
                                    "rating": 4.5,
                                    "available_slots": [
                                        { "day": "Monday", "start": "09:00", "end": "13:00", "max_patients": 10, "booked": 0 }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.mock_data, f)
            
        self.tool = ScheduleOptimizerTool(data_file=self.data_path)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_load_schedules(self):
        """Test successful loading of JSON data."""
        self.assertEqual(len(self.tool.schedules["hospitals"]), 2)

    def test_find_slots_by_specialty_and_city(self):
        """Test filtering doctors by specialty and city."""
        slots = self.tool._filter_by_specialty("Cardiologist", "Colombo")
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0]["hospital_city"], "Colombo, Sri Lanka")

    def test_find_slots_fallback_to_any_city(self):
        """Test fallback when no doctors are available in requested city."""
        slots = self.tool.find_available_slots("Cardiologist", "Galle", "medium")
        # Should fallback to all cities and find 3 slots
        self.assertEqual(len(slots), 3)

    def test_scoring_urgent_priority(self):
        """Test that urgent priority ranks available slots higher."""
        slots_urgent = self.tool.find_available_slots("Cardiologist", "Colombo", "urgent")
        # D001 has more availability (8/10 free = 0.8) and higher rating (4.8)
        # D002 has less availability (2/10 free = 0.2) and lower rating (4.0)
        self.assertEqual(slots_urgent[0]["doctor_id"], "D001")
        self.assertGreater(slots_urgent[0]["urgency_score"], slots_urgent[1]["urgency_score"])

    def test_no_matching_specialist(self):
        """Test handling of unknown specialty."""
        slots = self.tool.find_available_slots("Dentist", "Colombo", "medium")
        self.assertEqual(len(slots), 0)

    def test_get_next_available(self):
        """Test returning best single recommendation with alternatives."""
        best = self.tool.get_next_available("Cardiologist", "Colombo", "medium")
        self.assertIsNotNone(best)
        self.assertEqual(best["doctor_id"], "D001")
        self.assertIn("alternatives", best)
        self.assertEqual(len(best["alternatives"]), 1)

class TestAppointmentCoordinatorAgent(unittest.TestCase):
    """Test suite for AppointmentCoordinatorAgent."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = os.path.join(self.temp_dir.name, 'schedules.json')
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump({"hospitals": []}, f)
            
        self.agent = AppointmentCoordinatorAgent(data_file=self.data_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_agent_process_requires_specialist(self):
        """Test validation for required state fields."""
        state = {"hospital_city": "Colombo", "severity": "urgent"}
        result = self.agent.process(state)
        
        self.assertIn("error", result)
        self.assertIn("Missing required specialist", result["error"])

    @patch.object(ScheduleOptimizerTool, 'get_next_available')
    def test_agent_updates_state_correctly(self, mock_get_next):
        """Test successful state update."""
        mock_get_next.return_value = {
            "doctor_name": "Dr. Test",
            "hospital_name": "Test Hospital",
            "time_slot": "09:00 - 13:00"
        }
        
        state = {
            "specialist": "Cardiologist",
            "hospital_city": "Colombo",
            "severity": "medium"
        }
        
        result = self.agent.process(state)
        
        self.assertIn("appointment", result)
        self.assertEqual(result["appointment"]["doctor_name"], "Dr. Test")
        self.assertIn("conversation_log", result)
        self.assertEqual(len(result["conversation_log"]), 1)

    @patch.object(ScheduleOptimizerTool, 'get_next_available')
    def test_fallback_on_no_slots(self, mock_get_next):
        """Test graceful fallback when no slots are found."""
        mock_get_next.return_value = None
        
        state = {
            "specialist": "Cardiologist",
            "hospital_city": "Colombo"
        }
        
        result = self.agent.process(state)
        
        self.assertIn("error", result["appointment"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
