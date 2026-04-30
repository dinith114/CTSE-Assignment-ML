from app.tools.hospital_db_tool import hospital_db_tool

class MedicalRoutingAgent:
    def __init__(self):
        pass

    def map_symptoms_to_specialist(self, symptoms: list[str]) -> tuple[str, list[str], str]:
        """
        Hybrid mapping: rule-based + fallback
        """

        symptom_map = {
            "chest pain": "cardiologist",
            "shortness of breath": "cardiologist",
            "skin rash": "dermatologist",
            "headache": "neurologist",
            "fever": "general physician",
        }

        for symptom in symptoms:
            if symptom.lower() in symptom_map:
                return symptom_map[symptom.lower()], ["general physician"], f"{symptom} indicates {symptom_map[symptom.lower()]}"

        # fallback
        return "general physician", [], "Defaulted due to unclear symptoms"

    def run(self, state: dict) -> dict:
        triage_data = state.get("triage", {})

        symptoms = triage_data.get("symptoms", [])
        location = triage_data.get("location", "Colombo")

        primary, alternatives, reason = self.map_symptoms_to_specialist(symptoms)

        doctors = hospital_db_tool(primary, location)

        state["routing"] = {
            "primary_specialty": primary,
            "alternative_specialties": alternatives,
            "doctors": doctors,
            "reason": reason
        }

        return state