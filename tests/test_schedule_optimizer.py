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


class TestPropertyBasedValidation(unittest.TestCase):
    """Property-based tests to validate mathematical invariants of the scheduling algorithm."""

    def setUp(self):
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
                                    "qualifications": "MBBS, MD",
                                    "consultation_fee": 3500,
                                    "available_slots": [
                                        { "day": "Monday", "start": "09:00", "end": "13:00", "max_patients": 20, "booked": 5 },
                                        { "day": "Wednesday", "start": "14:00", "end": "18:00", "max_patients": 15, "booked": 14 },
                                        { "day": "Friday", "start": "08:00", "end": "12:00", "max_patients": 10, "booked": 10 }
                                    ]
                                },
                                {
                                    "id": "D002",
                                    "name": "Dr. Kamal Silva",
                                    "rating": 3.5,
                                    "qualifications": "MBBS",
                                    "consultation_fee": 2000,
                                    "available_slots": [
                                        { "day": "Tuesday", "start": "10:00", "end": "14:00", "max_patients": 10, "booked": 0 }
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
        self.temp_dir.cleanup()

    def test_booking_number_equals_booked_plus_one(self):
        """Property: booking_number must ALWAYS equal booked + 1."""
        slots = self.tool.find_available_slots("Cardiologist", "Colombo", "medium")
        for slot in slots:
            self.assertEqual(
                slot["booking_number"], slot["booked"] + 1,
                f"Booking number invariant violated for {slot['doctor_name']} on {slot['day']}: "
                f"booking_number={slot['booking_number']} but booked={slot['booked']}"
            )

    def test_estimated_time_is_after_or_equal_to_start(self):
        """Property: estimated consultation time must ALWAYS be >= slot start time."""
        slots = self.tool.find_available_slots("Cardiologist", "Colombo", "medium")
        for slot in slots:
            start_h, start_m = map(int, slot["time_slot"].split(" - ")[0].split(":"))
            est_h, est_m = map(int, slot["estimated_time"].split(":"))
            start_total = start_h * 60 + start_m
            est_total = est_h * 60 + est_m
            self.assertGreaterEqual(
                est_total, start_total,
                f"Estimated time {slot['estimated_time']} is before start time {slot['time_slot']} "
                f"for {slot['doctor_name']} on {slot['day']}"
            )

    def test_urgency_score_is_bounded_zero_to_one(self):
        """Property: urgency_score must ALWAYS be in range [0.0, 1.0]."""
        for severity in ["low", "medium", "high", "urgent"]:
            slots = self.tool.find_available_slots("Cardiologist", "Colombo", severity)
            for slot in slots:
                self.assertGreaterEqual(slot["urgency_score"], 0.0,
                    f"Score below 0 for severity={severity}: {slot['urgency_score']}")
                self.assertLessEqual(slot["urgency_score"], 1.0,
                    f"Score above 1 for severity={severity}: {slot['urgency_score']}")

    def test_fully_booked_slots_are_excluded(self):
        """Property: slots where booked >= max_patients must NEVER appear in results."""
        slots = self.tool.find_available_slots("Cardiologist", "Colombo", "medium")
        for slot in slots:
            self.assertGreater(
                slot["available"], 0,
                f"Fully booked slot leaked through: {slot['doctor_name']} {slot['day']} "
                f"(booked={slot['booked']}, max={slot['max_patients']})"
            )

    def test_available_equals_max_minus_booked(self):
        """Property: available seats must ALWAYS equal max_patients - booked."""
        slots = self.tool.find_available_slots("Cardiologist", "Colombo", "medium")
        for slot in slots:
            self.assertEqual(
                slot["available"], slot["max_patients"] - slot["booked"],
                f"Availability mismatch for {slot['doctor_name']} on {slot['day']}"
            )

    def test_urgent_scores_higher_for_more_availability(self):
        """Property: for urgent cases, a slot with more availability should score higher
        than one with less availability (assuming same rating)."""
        slots = self.tool.find_available_slots("Cardiologist", "Colombo", "urgent")
        # D001 Monday (15 available) should score higher than D001 Wednesday (1 available)
        if len(slots) >= 2:
            high_avail = [s for s in slots if s["available"] > 5]
            low_avail = [s for s in slots if s["available"] <= 5]
            if high_avail and low_avail:
                self.assertGreater(high_avail[0]["urgency_score"], low_avail[0]["urgency_score"])


# ─────────────────────────────────────────────────────────────
# LLM-as-a-Judge Evaluation
# ─────────────────────────────────────────────────────────────

def run_llm_as_judge_evaluation():
    """
    LLM-as-a-Judge evaluation for the Appointment Coordinator Agent.
    
    Uses local Ollama to judge whether the agent's appointment recommendations
    are clinically reasonable given the patient's severity and specialist need.
    
    This runs OUTSIDE of unittest (requires Ollama to be running).
    """
    try:
        from app.llm.ollama_client import run_ollama
    except ImportError:
        print("❌ Cannot import ollama_client. Ensure you're running from project root.")
        return

    print("\n" + "=" * 60)
    print("🧑‍⚖️  LLM-as-a-Judge: Appointment Coordinator Evaluation")
    print("=" * 60)

    tool = ScheduleOptimizerTool(data_file="app/data/schedules.json")

    # Define test scenarios
    scenarios = [
        {
            "name": "Urgent Cardiologist in Kandy",
            "specialty": "Cardiologist",
            "city": "Kandy",
            "severity": "urgent",
            "expected_behavior": "Should prioritize availability over rating for urgent cases"
        },
        {
            "name": "Low-severity Dermatologist in Colombo",
            "specialty": "Dermatologist",
            "city": "Colombo",
            "severity": "low",
            "expected_behavior": "Should prioritize higher-rated doctor for non-urgent cases"
        },
        {
            "name": "General Physician fallback (no city match)",
            "specialty": "General Physician",
            "city": "Jaffna",
            "severity": "medium",
            "expected_behavior": "Should fall back to other cities if no match in Jaffna"
        },
    ]

    results = []
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   Specialist: {scenario['specialty']}, City: {scenario['city']}, Severity: {scenario['severity']}")

        recommendation = tool.get_next_available(
            scenario["specialty"], scenario["city"], scenario["severity"]
        )

        if not recommendation:
            print("   ⚠️  No recommendation generated (no matching slots)")
            results.append({"scenario": scenario["name"], "verdict": "SKIP", "reason": "No slots available"})
            continue

        # Build judge prompt
        judge_prompt = (
            "You are a medical scheduling expert evaluating an AI appointment recommendation system. "
            "Judge whether the following appointment recommendation is REASONABLE and SAFE.\n\n"
            f"PATIENT CONTEXT:\n"
            f"- Severity: {scenario['severity']}\n"
            f"- Needs: {scenario['specialty']}\n"
            f"- City: {scenario['city']}\n\n"
            f"RECOMMENDATION:\n"
            f"- Doctor: {recommendation.get('doctor_name')} (Rating: {recommendation.get('doctor_rating')}/5.0)\n"
            f"- Hospital: {recommendation.get('hospital_name')}, {recommendation.get('hospital_city')}\n"
            f"- Schedule: {recommendation.get('day')} {recommendation.get('time_slot')}\n"
            f"- Booking #{recommendation.get('booking_number')}, Est. Time: {recommendation.get('estimated_time')}\n"
            f"- Availability: {recommendation.get('available')}/{recommendation.get('max_patients')} seats\n\n"
            f"EXPECTED BEHAVIOR: {scenario['expected_behavior']}\n\n"
            "Respond with EXACTLY one of these verdicts on the first line, followed by a brief explanation:\n"
            "PASS - if the recommendation is reasonable and aligns with expected behavior\n"
            "FAIL - if the recommendation is unreasonable or potentially harmful\n"
        )

        print(f"   🏥 Recommended: {recommendation.get('doctor_name')} @ {recommendation.get('hospital_name')}")
        print(f"   📅 {recommendation.get('day')} {recommendation.get('time_slot')} (Booking #{recommendation.get('booking_number')})")

        # Call Ollama as judge
        judge_response = run_ollama(prompt=judge_prompt, model="llama3.2:3b", timeout=30)

        if not judge_response:
            print("   ⚠️  LLM judge unavailable — skipping")
            results.append({"scenario": scenario["name"], "verdict": "SKIP", "reason": "Ollama unavailable"})
            continue

        verdict = "PASS" if judge_response.strip().upper().startswith("PASS") else "FAIL"
        emoji = "✅" if verdict == "PASS" else "❌"
        print(f"   {emoji} Judge Verdict: {verdict}")
        print(f"   💬 Judge says: {judge_response.strip()[:200]}")
        results.append({"scenario": scenario["name"], "verdict": verdict, "reason": judge_response.strip()[:200]})

    # Summary
    print("\n" + "=" * 60)
    print("📊 LLM-as-a-Judge Summary")
    print("=" * 60)
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = sum(1 for r in results if r["verdict"] == "FAIL")
    skipped = sum(1 for r in results if r["verdict"] == "SKIP")
    total = len(results)
    
    for r in results:
        emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}[r["verdict"]]
        print(f"  {emoji} {r['scenario']}: {r['verdict']}")
    
    print(f"\nResults: {passed}/{total} PASSED, {failed} FAILED, {skipped} SKIPPED")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    if "--llm-judge" in sys.argv:
        sys.argv.remove("--llm-judge")
        run_llm_as_judge_evaluation()
    else:
        unittest.main(verbosity=2)
