"""
Main entry point for Multi-Agent E-Channeling System
Demonstrates full workflow with all 4 agents.
"""

from app.workflow import run_e_channeling_workflow
from app.logger_config import get_logger
import json
import argparse
import os
import sys

# Fix Windows CMD encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = get_logger(__name__)


def display_results(final_state):
    """Display comprehensive results from ALL agents in a structured format."""
    print("\n" + "="*60)
    print("🏥  E-CHANNELING MULTI-AGENT SYSTEM — FINAL RESULTS")
    print("="*60)

    # ── Agent 1: Symptom Triage ──
    triage = final_state.get("triage_result", {})
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│  🩺  AGENT 1 — Symptom Triage Agent                    │")
    print("├─────────────────────────────────────────────────────────┤")
    print(f"│  Patient Input : {final_state.get('patient_text', 'N/A')}")
    symptoms = final_state.get("symptoms", triage.get("extracted_symptoms", []))
    categories = triage.get("categories", [])
    print(f"│  Symptoms Found: {', '.join(symptoms) if symptoms else 'None detected'}")
    print(f"│  Categories    : {', '.join(categories) if categories else 'General'}")
    print(f"│  Severity      : {(final_state.get('severity') or 'N/A').upper()}")
    print(f"│  Urgency       : {(final_state.get('urgency') or final_state.get('severity') or 'N/A').upper()}")
    red_flags = final_state.get("red_flags", [])
    if red_flags:
        print(f"│  🚨 Red Flags  : {', '.join(red_flags)}")
    print("└─────────────────────────────────────────────────────────┘")

    # ── Agent 2: Medical Routing ──
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│  🔀  AGENT 2 — Medical Routing Agent                   │")
    print("├─────────────────────────────────────────────────────────┤")
    print(f"│  Specialist    : {final_state.get('specialist', 'N/A')}")
    print(f"│  Hospital City : {final_state.get('hospital_city', 'N/A')}")
    if final_state.get("routing_reason"):
        print(f"│  Reason        : {final_state['routing_reason']}")
    doctors = final_state.get("doctors", [])
    if doctors:
        print(f"│  Doctors Found : {len(doctors)}")
    print("└─────────────────────────────────────────────────────────┘")

    # ── Agent 3: Appointment Coordinator ──
    appt = final_state.get("appointment", {})
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│  📅  AGENT 3 — Appointment Coordinator Agent           │")
    print("├─────────────────────────────────────────────────────────┤")
    if not appt or "error" in appt:
        err = appt.get("error", "No appointment data") if appt else "Agent not executed"
        print(f"│  ❌ Error: {err}")
    else:
        print(f"│  Doctor        : {appt.get('doctor_name', 'N/A')}")
        print(f"│  Qualifications: {appt.get('qualifications', 'N/A')}")
        print(f"│  Hospital      : {appt.get('hospital_name', 'N/A')}, {appt.get('hospital_city', '')}")
        print(f"│  Day & Time    : {appt.get('day', 'N/A')} | {appt.get('time_slot', 'N/A')}")
        print(f"│  Doctor Rating : {'⭐' * int(appt.get('doctor_rating', 0))} ({appt.get('doctor_rating', 'N/A')}/5.0)")
        print(f"│  Fee           : LKR {appt.get('consultation_fee', 'N/A')}")
        print(f"│  ─────────────────────────────────────────────────────")
        print(f"│  🎫 Booking No  : #{appt.get('booking_number', 'N/A')}")
        print(f"│  ⏰ Est. Time   : {appt.get('estimated_time', 'N/A')} (approx.)")
        print(f"│  👥 Queue       : {appt.get('booked', 0)} patient(s) before you")
        print(f"│  💺 Seats Left  : {appt.get('available', 'N/A')} / {appt.get('max_patients', 'N/A')}")
        print(f"│  ─────────────────────────────────────────────────────")
        if appt.get("llm_reasoning"):
            print(f"│  🤖 LLM Reason : {appt['llm_reasoning']}")
        alternatives = appt.get("alternatives", [])
        if alternatives:
            print(f"│  📋 Alternatives: {len(alternatives)} other option(s) available")
            for i, alt in enumerate(alternatives, 1):
                print(f"│  ┌── Alternative {i} ──────────────────────────────────")
                print(f"│  │  Doctor       : {alt.get('doctor_name', 'N/A')}")
                print(f"│  │  Hospital     : {alt.get('hospital_name', 'N/A')}, {alt.get('hospital_city', '')}")
                print(f"│  │  Day & Time   : {alt.get('day', 'N/A')} | {alt.get('time_slot', 'N/A')}")
                print(f"│  │  Rating       : {'⭐' * int(alt.get('doctor_rating', 0))} ({alt.get('doctor_rating', 'N/A')}/5.0)")
                print(f"│  │  Fee          : LKR {alt.get('consultation_fee', 'N/A')}")
                print(f"│  │  🎫 Booking # : #{alt.get('booking_number', '?')}")
                print(f"│  │  ⏰ Est. Time  : {alt.get('estimated_time', 'N/A')}")
                print(f"│  │  👥 Queue      : {alt.get('booked', 0)} patient(s) before you")
                print(f"│  │  💺 Seats Left : {alt.get('available', 'N/A')} / {alt.get('max_patients', 'N/A')}")
                print(f"│  └─────────────────────────────────────────────────")
    print("└─────────────────────────────────────────────────────────┘")

    # ── Agent 4: Travel Risk Assessment ──
    travel = final_state.get("travel_info", {})
    risk = final_state.get("risk_assessment", {})
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│  🚗  AGENT 4 — Travel Risk Assessment Agent            │")
    print("├─────────────────────────────────────────────────────────┤")
    if not travel or "error" in travel:
        err = travel.get("error", "No travel data") if travel else "Agent not executed"
        print(f"│  ❌ Error: {err}")
    else:
        print(f"│  From         : {travel.get('source_city', final_state.get('patient_city', 'N/A'))}")
        print(f"│  To           : {travel.get('destination_city', final_state.get('hospital_city', 'N/A'))}")
        print(f"│  Distance     : {travel.get('distance_km', 0)} km")
        print(f"│  Travel Time  : {travel.get('travel_time_hours', 0)} hours")
        print(f"│  Risk Level   : {risk.get('risk_level', 'N/A')}")
        print(f"│  Recommendation: {risk.get('recommendation', 'N/A')}")
        if travel.get("route_advice"):
            print(f"│  Route Advice : {travel['route_advice']}")
        if travel.get("warning_message"):
            print(f"│  ⚠️  Warning  : {travel['warning_message']}")
        if risk.get("llm_reasoning"):
            print(f"│  🤖 LLM Reason: {risk['llm_reasoning']}")
    print("└─────────────────────────────────────────────────────────┘")

    # ── Final Verdict ──
    if risk.get("requires_alternative"):
        print("\n⚠️  ALERT: Travel risk is too high. Consider local hospital or teleconsultation.")

    # ── Observability Summary ──
    conv_log = final_state.get("conversation_log", [])
    print(f"\n📊 Observability: {len(conv_log)} agent(s) logged to conversation_log")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run e-channeling workflow with custom inputs")
    parser.add_argument("--patient-city", type=str, default="Kandy, Sri Lanka", help="Patient city/location")
    parser.add_argument("--hospital-city", type=str, default=None, help="Hospital city/location")
    parser.add_argument("--symptoms", type=str, default="Chest pain and shortness of breath", help="Patient symptom text")

    args = parser.parse_args()

    # Build patient input from CLI args
    patient = {
        "symptoms": args.symptoms,
        "patient_city": args.patient_city,
        "hospital_city": args.hospital_city
    }

    result = run_e_channeling_workflow(patient)

    # Display nice output
    display_results(result)

    # Save results for observability
    out_path = "app/logs/system/last_run.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"Results written to {out_path}")
    logger.info("[SUCCESS] Workflow completed successfully")
