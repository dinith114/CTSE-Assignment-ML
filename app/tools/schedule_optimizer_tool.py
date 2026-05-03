import json
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ScheduleOptimizerTool:
    """
    Tool to query hospital schedules and rank appointment slots based on patient needs.
    """

    def __init__(self, data_file: str = "app/data/schedules.json"):
        self.data_file = data_file
        self.schedules = self._load_schedules()

    def _load_schedules(self) -> Dict[str, Any]:
        """Loads schedule data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading schedules from {self.data_file}: {e}")
                return {"hospitals": []}
        else:
            logger.warning(f"Schedule data file {self.data_file} not found.")
            return {"hospitals": []}

    def _filter_by_specialty(self, specialty: str, city: Optional[str] = None) -> List[Dict[str, Any]]:
        """Finds all doctors and slots matching a specialty, optionally filtered by city."""
        results = []
        for hospital in self.schedules.get("hospitals", []):
            if city and city.lower() not in hospital.get("city", "").lower():
                continue
                
            for dept in hospital.get("departments", []):
                if dept.get("specialty", "").lower() == specialty.lower():
                    for doctor in dept.get("doctors", []):
                        for slot in doctor.get("available_slots", []):
                            # Skip fully booked slots
                            if slot.get("booked", 0) >= slot.get("max_patients", 0):
                                continue
                                
                            results.append({
                                "hospital_name": hospital["name"],
                                "hospital_city": hospital["city"],
                                "doctor_name": doctor["name"],
                                "doctor_id": doctor["id"],
                                "specialty": dept["specialty"],
                                "qualifications": doctor.get("qualifications", ""),
                                "consultation_fee": doctor.get("consultation_fee", 0),
                                "doctor_rating": doctor.get("rating", 0.0),
                                "day": slot["day"],
                                "time_slot": f"{slot['start']} - {slot['end']}",
                                "max_patients": slot["max_patients"],
                                "booked": slot["booked"],
                                "available": slot["max_patients"] - slot["booked"],
                                "booking_number": slot["booked"] + 1,
                                "avg_consultation_minutes": 15,
                                "estimated_time": self._estimate_consultation_time(
                                    slot["start"], slot["booked"], avg_minutes=15
                                )
                            })
        return results

    def _estimate_consultation_time(self, start_time: str, patients_before: int, avg_minutes: int = 15) -> str:
        """
        Estimates the patient's consultation time based on queue position.

        Args:
            start_time: Slot start time (e.g., "09:00").
            patients_before: Number of patients booked before this one.
            avg_minutes: Average consultation duration per patient in minutes.

        Returns:
            Estimated consultation time as a string (e.g., "11:30").
        """
        try:
            hours, minutes = map(int, start_time.split(":"))
            total_minutes = hours * 60 + minutes + (patients_before * avg_minutes)
            est_hours = total_minutes // 60
            est_mins = total_minutes % 60
            return f"{est_hours:02d}:{est_mins:02d}"
        except (ValueError, AttributeError):
            return start_time

    def _score_slot(self, slot: Dict[str, Any], severity: str) -> float:
        """
        Scores a slot based on severity.
        Urgent: Prioritizes earliest availability (simulated by availability percentage) and rating.
        Low/Medium: Balances rating and availability.
        """
        rating_score = slot["doctor_rating"] / 5.0
        
        availability_ratio = slot["available"] / max(1, slot["max_patients"])
        
        # Simplified scoring logic
        if severity.lower() in ["urgent", "high"]:
            # For urgent, availability ratio (chances of getting in early/walk-in) is weighted more
            score = (availability_ratio * 0.7) + (rating_score * 0.3)
        else:
            # For regular, prefer better rated doctors
            score = (rating_score * 0.6) + (availability_ratio * 0.4)
            
        return score

    def find_available_slots(self, specialty: str, hospital_city: Optional[str] = None, severity: str = "medium") -> List[Dict[str, Any]]:
        """Finds and ranks all available slots."""
        slots = self._filter_by_specialty(specialty, hospital_city)
        
        # If no slots found in the specific city, try without city filter
        if not slots and hospital_city:
            logger.info(f"No slots found in {hospital_city} for {specialty}. Searching all cities.")
            slots = self._filter_by_specialty(specialty, None)

        # Score and rank slots
        for slot in slots:
            slot["urgency_score"] = round(self._score_slot(slot, severity), 2)
            
        # Sort by urgency_score descending
        slots.sort(key=lambda x: x["urgency_score"], reverse=True)
        return slots

    def get_next_available(self, specialty: str, hospital_city: Optional[str] = None, severity: str = "medium") -> Optional[Dict[str, Any]]:
        """Returns the single best recommended slot and backup alternatives."""
        slots = self.find_available_slots(specialty, hospital_city, severity)
        
        if not slots:
            return None
            
        best_slot = slots[0]
        # Attach alternatives (up to 2)
        best_slot["alternatives"] = slots[1:3]
        
        return best_slot

def schedule_optimizer_tool(specialty: str, hospital_city: str, severity: str = "medium") -> dict:
    tool = ScheduleOptimizerTool()
    res = tool.get_next_available(specialty, hospital_city, severity)
    return res if res else {"error": "No available appointments found."}
