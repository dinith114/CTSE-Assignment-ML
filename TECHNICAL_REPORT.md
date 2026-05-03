# Technical Report: Multi-Agent E-Channeling System

**SE4010 – Current Trends in Software Engineering**
**Assignment 2 – Machine Learning (Agentic AI)**
**Sri Lanka Institute of Information Technology**

---

## 1. Problem Domain

### 1.1 Background

Sri Lanka's healthcare system faces significant challenges in the patient channeling process. Patients must manually identify the correct specialist, find hospitals that offer the required specialty, check doctor availability, and assess whether travel to a distant hospital is feasible — especially for urgent medical cases. This multi-step, information-intensive process is error-prone and time-consuming, potentially endangering patients who require immediate care.

### 1.2 Problem Statement

The current e-channeling workflow requires patients to:
1. Self-diagnose their symptom severity (often inaccurately)
2. Identify the correct medical specialist
3. Search across multiple hospitals for availability
4. Manually assess whether travel distance and time are safe given their condition

Each step relies on fragmented, siloed information. No existing system unifies these decisions into a single, automated pipeline that considers the patient's clinical urgency, geographic location, and real-time doctor availability simultaneously.

### 1.3 Proposed Solution

We designed a **locally-hosted Multi-Agent System (MAS)** that automates the end-to-end e-channeling workflow. The system employs four specialized AI agents orchestrated via **LangGraph**, each equipped with a dedicated custom tool, a purpose-built system prompt, and access to a local **Ollama** Small Language Model (SLM) for reasoning and explainability. The entire system runs on consumer hardware with zero cloud costs and no paid API keys.

---

## 2. System Architecture

### 2.1 High-Level Architecture

The system follows a **Sequential Pipeline Model** where four agents execute in a strict linear order, each enriching a shared global state before passing it to the next agent.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                  │
│   (patient_text, patient_city)                                      │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LangGraph StateGraph                              │
│                                                                      │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────┐│
│  │  Symptom     │───▶│   Medical    │───▶│ Appointment  │───▶│Travel││
│  │  Triage      │    │   Routing    │    │ Coordinator  │    │ Risk ││
│  │  Agent       │    │   Agent      │    │ Agent        │    │Agent ││
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──┬───┘│
│         │                   │                   │               │    │
│  ┌──────▼───────┐    ┌──────▼───────┐    ┌──────▼───────┐  ┌───▼───┐│
│  │  Symptom     │    │  Hospital    │    │  Schedule    │  │Dist.  ││
│  │  Parser      │    │  DB Tool     │    │  Optimizer   │  │Calc.  ││
│  │  Tool        │    │              │    │  Tool        │  │Tool   ││
│  └──────────────┘    └──────────────┘    └──────────────┘  └───────┘│
│                                                                      │
│         ┌──────────────────────────────────────────────┐             │
│         │          Ollama LLM (llama3.2:3b)            │             │
│         │    Local SLM for reasoning & summaries       │             │
│         └──────────────────────────────────────────────┘             │
│                                                                      │
│         ┌──────────────────────────────────────────────┐             │
│         │         EChannelState (Global State)         │             │
│         │  patient_text, severity, specialist,         │             │
│         │  hospital_city, appointment, travel_info,    │             │
│         │  risk_assessment, conversation_log           │             │
│         └──────────────────────────────────────────────┘             │
└──────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FINAL OUTPUT                                      │
│  Specialist recommendation, appointment slot, travel risk,           │
│  safety warnings, LLM reasoning summaries                           │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **LLM Engine** | Ollama (llama3.2:3b) | Local SLM, zero cost, privacy-preserving |
| **Orchestrator** | LangGraph (StateGraph) | Typed state management, clear node-edge model |
| **Language** | Python 3.10+ | Rich ML/AI ecosystem, team familiarity |
| **APIs Used** | OpenStreetMap Nominatim (free), OSRM (free) | No paid API keys required |
| **Logging** | Python `logging` module | File + console, structured conversation logs |
| **Testing** | `unittest` + `unittest.mock` | Built-in, no external dependency |

### 2.3 Workflow Diagram

```
[Entry] ──▶ symptom_triage ──▶ medical_routing ──▶ appointment_coordination ──▶ travel_risk ──▶ [END]
```

Each node is a LangGraph node registered via `StateGraph.add_node()` and connected via `StateGraph.add_edge()`. The workflow is compiled into an executable graph and invoked with `app.invoke(initial_state)`.

---

## 3. Agent Design

### 3.1 Agent 1: Symptom Triage Agent (Member 1)

**File:** `app/agents/symptom_triage_agent.py`

**System Prompt (embedded in agent):**
> *"You are a Triage Nurse Agent in a healthcare system. Analyze the patient's text and confirm the severity (urgent, high, medium, low). Output a single concise sentence summarizing the assessment."*

**Reasoning Logic:**
1. The `SymptomParserTool` performs keyword matching against a local knowledge base (`symptom_kb.json`) to extract symptoms and determine maximum severity.
2. The local LLM (Ollama) is invoked to confirm or refine the rule-based severity, providing a natural language summary.
3. Graceful fallback: if Ollama is unavailable, the rule-based severity is used directly.

**Constraints:**
- Defaults to `"medium"` severity if no symptoms are recognized or if an error occurs.
- LLM is prompted to output only a single sentence — preventing hallucinated medical advice.

**Input:** `patient_text` (raw symptom description)
**Output:** `severity`, `triage_analysis` (extracted symptoms, categories, LLM summary)

---

### 3.2 Agent 2: Medical Routing Agent (Member 2)

**File:** `app/agents/medical_routing_agent.py`

**System Prompt (embedded in agent):**
> *"You are a Medical Routing Agent. Based on the following information, determine the SINGLE most appropriate medical specialist type required for the patient. Respond ONLY with the specialist title."*

**Reasoning Logic:**
1. Maps symptom categories from triage (e.g., `Cardiovascular → Cardiologist`) using a deterministic lookup table.
2. Invokes LLM to confirm or override the mapping, constrained to respond with only the specialist title.
3. Queries `HospitalDBTool` to find hospitals offering that specialty.
4. City matching: prefers hospitals in the patient's city; falls back to any available hospital.

**Constraints:**
- LLM output is stripped of quotes, periods, and whitespace to ensure clean specialist names.
- Ultimate fallback to `"General Physician"` if no category matches.

**Input:** `triage_analysis.categories`, `patient_city`
**Output:** `specialist`, `hospital_city`

---

### 3.3 Agent 3: Appointment Coordinator Agent (Member 3)

**File:** `app/agents/appointment_coordinator_agent.py`

**System Prompt (embedded in agent):**
> *"You are an Appointment Coordinator Agent in a Sri Lankan healthcare e-channeling system. Given the patient's severity, specialist need, and available doctor schedules, explain in 1-2 sentences why this specific appointment slot was recommended. Consider urgency, doctor availability, and patient convenience."*

**Reasoning Logic:**
1. `ScheduleOptimizerTool` queries `schedules.json` (7 hospitals, 21 doctors, 8 specialties) to find all available slots matching the specialist and city.
2. Slots are scored using a **multi-criteria, severity-adaptive algorithm**:
   - **Urgent/High severity:** 70% weight on availability ratio, 30% on doctor rating (prioritizes getting seen quickly).
   - **Low/Medium severity:** 60% weight on doctor rating, 40% on availability (prioritizes quality of care).
3. Best slot is returned with:
   - **Booking number** (queue position, e.g., `#9`)
   - **Estimated consultation time** (calculated from slot start time + queue × avg 15 min)
   - **Queue size** (how many patients are before you)
   - **Seat availability** (remaining vs total capacity)
   - Up to **2 alternatives** with full details (expandable in Web UI)
4. LLM generates a human-readable justification for why this slot was chosen.
5. Graceful fallback: if Ollama is unavailable, rule-based recommendation is used.

**Constraints:**
- Fully booked slots (`booked >= max_patients`) are filtered out before scoring.
- Falls back to all cities if no slots are found in the requested city.
- LLM prompt is constrained to 1-2 sentences with no invented facts.
- Error handling: validates that `specialist` exists in state; returns structured error if missing.

**Input:** `specialist`, `hospital_city`, `severity`
**Output:** `appointment` (doctor name, qualifications, hospital, time slot, rating, fee, booking_number, estimated_time, queue, seats, alternatives, LLM reasoning)

**Web UI Integration:** The appointment card is displayed in the React frontend (`SummaryPage.jsx`) with a dedicated booking details panel and expandable alternative options accordion.

---

### 3.4 Agent 4: Travel Risk Assessment Agent (Member 4)

**File:** `app/agents/travel_risk_agent.py`

**System Prompt (embedded in agent):**
> *"You are a Travel Risk Assessment Agent in a healthcare e-channeling system. Your goal is to ensure patient safety by evaluating travel feasibility. You MUST: Always calculate distance before providing advice; flag any travel time > 2 hours for urgent cases as high risk; suggest alternative modes of transport for medium-risk scenarios; never recommend travel that would compromise patient health."*

**Reasoning Logic:**
1. `DistanceCalculatorTool` geocodes patient and hospital cities using OpenStreetMap Nominatim API.
2. Calculates actual road distance via OSRM API; falls back to Haversine formula if OSRM is unavailable.
3. Estimates travel time based on configurable average speeds (car: 60 km/h, bus: 50 km/h, train: 80 km/h).
4. Applies a severity-aware risk matrix:

| Severity | Travel Time | Risk Level | Action |
|----------|-------------|------------|--------|
| Urgent/High | > 2 hours | CRITICAL | Do not travel — seek local care |
| Urgent/High | 1-2 hours | HIGH | Recommend teleconsultation |
| Urgent/High | < 1 hour | MEDIUM | Proceed with caution |
| Low/Medium | > 4 hours | MEDIUM | Consider overnight stay |
| Low/Medium | 2-4 hours | LOW | Travel feasible |
| Low/Medium | < 2 hours | VERY_LOW | No concerns |

5. LLM generates a contextual, Sri Lanka-specific travel recommendation (constrained to avoid mentioning flights/air travel).

**Constraints:**
- Caches geocoding results to minimize API calls.
- Validates that both cities are provided; returns error state if missing.
- Minimum travel time capped at 5 minutes for very short distances.

**Input:** `patient_city`, `hospital_city`, `severity`
**Output:** `travel_info`, `risk_assessment` (risk level, recommendation, LLM reasoning)

---

## 4. Custom Tools — Description and Example Usage

### 4.1 SymptomParserTool

**File:** `app/tools/symptom_parser_tool.py`

**Purpose:** Parses unstructured patient text to extract known symptoms and determine severity using a local JSON knowledge base.

**API / File Interaction:** Reads `app/data/symptom_kb.json` (12 symptom entries with severity and category mappings).

**Example Usage:**
```python
tool = SymptomParserTool(kb_file="app/data/symptom_kb.json")
result = tool.analyze_symptoms("I have severe chest pain and shortness of breath")
# Output: {
#   "extracted_symptoms": ["chest pain", "shortness of breath"],
#   "severity": "urgent",
#   "categories": ["Cardiovascular", "Respiratory"],
#   "requires_immediate_attention": True
# }
```

---

### 4.2 HospitalDBTool

**File:** `app/tools/hospital_db_tool.py`

**Purpose:** Queries the hospital database to find hospitals offering a specific medical specialty.

**API / File Interaction:** Reads `app/data/schedules.json` (5 hospitals across Colombo, Kandy, Galle, Jaffna, Kurunegala with 9 doctors and multiple time slots).

**Example Usage:**
```python
tool = HospitalDBTool(data_file="app/data/schedules.json")
result = tool.find_hospitals_by_specialty("Cardiologist")
# Output: [
#   {"hospital_name": "Nawaloka Hospital", "city": "Colombo, Sri Lanka"},
#   {"hospital_name": "Asiri Hospital", "city": "Kandy, Sri Lanka"}
# ]
```

---

### 4.3 ScheduleOptimizerTool

**File:** `app/tools/schedule_optimizer_tool.py`

**Purpose:** Queries doctor schedules, scores and ranks appointment slots using a multi-criteria algorithm that adapts to patient severity. Provides booking metadata including queue position, estimated consultation time, and seat availability.

**API / File Interaction:** Reads `app/data/schedules.json` (7 hospitals, 21 doctors across 8 specialties). Filters by specialty, city, and availability. Applies urgency-weighted scoring.

**Key Methods:**
- `_filter_by_specialty(specialty, city)` — Finds matching slots, skips fully booked
- `_estimate_consultation_time(start_time, patients_before, avg_minutes)` — Calculates estimated start time
- `_score_slot(slot, severity)` — Severity-adaptive multi-criteria scoring
- `find_available_slots(specialty, city, severity)` — Full filtered + ranked list
- `get_next_available(specialty, city, severity)` — Best slot + 2 alternatives

**Example Usage:**
```python
tool = ScheduleOptimizerTool(data_file="app/data/schedules.json")
best = tool.get_next_available("Cardiologist", "Kandy", "urgent")
# Output: {
#   "doctor_name": "Dr. Anura Bandara",
#   "qualifications": "MBBS, MD, FRCP (Edinburgh)",
#   "hospital_name": "Asiri Hospital",
#   "hospital_city": "Kandy, Sri Lanka",
#   "day": "Saturday", "time_slot": "08:00 - 13:00",
#   "doctor_rating": 4.5, "consultation_fee": 3000,
#   "booking_number": 6, "estimated_time": "09:15",
#   "booked": 5, "available": 15, "max_patients": 20,
#   "urgency_score": 0.85,
#   "alternatives": [{...}, {...}]  # Up to 2 backup options with full details
# }
```

---

### 4.4 DistanceCalculatorTool

**File:** `app/tools/distance_calculator_tool.py`

**Purpose:** Calculates travel distance and time between patient and hospital locations using free, public APIs with intelligent caching.

**API / File Interaction:**
- **OpenStreetMap Nominatim API** (free, no API key) — Geocoding city names to coordinates
- **OSRM (Open Source Routing Machine)** (free, no API key) — Actual road distance calculation
- **Haversine formula** — Mathematical fallback if OSRM is unavailable
- **Local cache** (`app/data/city_distances/city_coordinates.json`) — Avoids redundant API calls

**Example Usage:**
```python
tool = DistanceCalculatorTool()
result = tool.calculate_travel("Kandy, Sri Lanka", "Colombo, Sri Lanka", "urgent")
# Output: {
#   "distance_km": 115.5,
#   "travel_time_hours": 2.1,
#   "route_advice": "Medium distance. Train or car recommended.",
#   "warning_message": "⚠️ CAUTION: Urgent severity patient requires 2.1h travel..."
# }
```

---

## 5. State Management

### 5.1 Global State Structure

The system uses a **TypedDict** (`EChannelState`) as the single source of truth, passed through all agents via LangGraph's `StateGraph`:

```python
class EChannelState(TypedDict, total=False):
    patient_text: str                  # Raw symptom input from patient
    patient_city: str                  # Patient's current location
    patient_location: str              # Alias for patient_city
    severity: str                      # Set by Agent 1 (urgent/high/medium/low)
    specialist: str                    # Set by Agent 2 (e.g., "Cardiologist")
    hospital_city: str                 # Set by Agent 2 (e.g., "Colombo, Sri Lanka")
    appointment: Dict[str, Any]        # Set by Agent 3 (doctor, time, hospital)
    travel_info: Dict[str, Any]        # Set by Agent 4 (distance, time, advice)
    risk_assessment: Dict[str, Any]    # Set by Agent 4 (risk level, recommendation)
    conversation_log: list             # Append-only log from ALL agents
    error: str                         # Error message if any agent fails
```

### 5.2 How Context Is Passed Between Agents

1. **LangGraph manages state immutably**: Each agent receives the full state, modifies its designated fields, and returns the updated state. LangGraph merges the updates before passing to the next node.
2. **No context loss**: Because the state is a single dictionary flowing through the graph, every downstream agent has access to all upstream outputs. For example, Agent 4 can access `severity` (set by Agent 1) and `appointment` (set by Agent 3) simultaneously.
3. **Append-only conversation log**: Every agent appends a structured entry to `conversation_log` with its name, timestamp, inputs, and outputs — ensuring full traceability without overwriting previous entries.

### 5.3 State Flow Example

```
Initial State: {patient_text: "chest pain", patient_city: "Kandy"}
    │
    ▼ Agent 1 adds: severity="urgent", triage_analysis={...}
    │
    ▼ Agent 2 adds: specialist="Cardiologist", hospital_city="Kandy, Sri Lanka"
    │
    ▼ Agent 3 adds: appointment={doctor: "Dr. Anura Bandara", day: "Saturday", ...}
    │
    ▼ Agent 4 adds: travel_info={distance: 0km, ...}, risk_assessment={risk: "VERY_LOW"}
    │
Final State: All fields populated, conversation_log has 4 entries
```

---

## 6. LLMOps / AgentOps & Observability

### 6.1 Logging Infrastructure

**File:** `app/logger_config.py`

The system implements a dual-output logging mechanism:

| Channel | Format | Location |
|---------|--------|----------|
| **Console** | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | `stdout` |
| **File** | Same format | `app/logs/system/YYYYMMDD.log` |

Every agent logs:
- Entry point (`"Starting symptom triage"`)
- Key decisions (`"Assessed severity as urgent"`)
- Errors with full exception details
- Exit point with summary

### 6.2 Structured Conversation Log

Each agent appends a structured JSON entry to the `conversation_log` list in the global state:

```json
{
    "agent": "SymptomTriageAgent",
    "timestamp": "2026-05-02T10:15:30.123456",
    "input": {"patient_text": "chest pain and shortness of breath"},
    "output": {
        "extracted_symptoms": ["chest pain", "shortness of breath"],
        "severity": "urgent",
        "categories": ["Cardiovascular", "Respiratory"]
    }
}
```

This provides a complete, serializable trace of every agent's decision for debugging, auditing, and demonstration purposes.

### 6.3 Run Output Persistence

After each workflow execution, the full final state (including all conversation logs) is serialized to `app/logs/system/last_run.json` for post-hoc analysis.

---

## 7. Evaluation Methodology

### 7.1 Testing Strategy

The project employs a **unified testing harness** (`tests/` directory) with each member contributing test cases for their specific agent and tool.

| Test File | Tests | What It Validates |
|-----------|-------|------------------|
| `test_symptom_triage.py` | 3 tests | Tool extracts correct symptoms; agent sets severity; conversation log created |
| `test_medical_routing.py` | 2 tests | Tool finds hospitals by specialty; agent maps categories to specialists |
| `test_schedule_optimizer.py` | 9 tests | Slot filtering; urgency scoring; city fallback; alternatives; state validation; error handling |
| `test_travel_risk_agent.py` | 11 tests + LLM-as-Judge | Haversine accuracy; travel time estimation; warning generation; API mocking; risk matrix validation; observability logging |

### 7.2 Testing Techniques Used

1. **Property-Based Testing:** Verifying mathematical properties (e.g., Haversine distance symmetry, minimum travel time bounds).
2. **Mock-Based Unit Testing:** All external API calls (Nominatim, OSRM, Ollama) are mocked using `unittest.mock.patch` to ensure deterministic, offline-capable tests.
3. **Integration Testing:** Complete `calculate_travel` flow tested with mocked geocoding and routing to validate end-to-end output structure.
4. **Edge Case Testing:** Empty inputs, non-existent cities, fully booked slots, missing state fields.
5. **Security Validation:** Input validation ensures no injection through city names; error states are handled gracefully without exposing internal details.
6. **LLM-as-a-Judge:** `test_travel_risk_agent.py` includes an automated LLM evaluation (`run_llm_as_judge_evaluation()`) that uses a local Ollama model to judge whether agent outputs match expected behavior for defined scenarios.

### 7.3 Running Tests

```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific member's tests
python -m pytest tests/test_symptom_triage.py -v        # Member 1
python -m pytest tests/test_medical_routing.py -v        # Member 2
python -m pytest tests/test_schedule_optimizer.py -v     # Member 3
python -m pytest tests/test_travel_risk_agent.py -v      # Member 4

# Run LLM-as-Judge evaluation (requires Ollama)
python tests/test_travel_risk_agent.py
```

### 7.4 Reliability Analysis

| Agent | Failure Mode | Mitigation |
|-------|-------------|------------|
| Symptom Triage | Unknown symptom keywords | Defaults to "medium" severity |
| Medical Routing | LLM hallucinated specialist name | Stripped output + fallback to rule-based mapping |
| Appointment Coordinator | No available slots | Returns error in state + logs warning |
| Travel Risk | Geocoding API timeout | Haversine fallback + coordinate caching |
| All Agents | Ollama unavailable | Graceful fallback to rule-based logic (system fully functional without LLM) |

---

## 8. Individual Contributions

### Member 1 — Symptom Triage Agent
- **Agent Developed:** `SymptomTriageAgent` — Parses patient text, extracts symptoms, determines severity with LLM confirmation.
- **Tool Implemented:** `SymptomParserTool` — Keyword matching against `symptom_kb.json` with severity ranking.
- **Challenges Faced:** Balancing the knowledge base size to cover common symptoms without creating false positive matches from substring overlaps (e.g., "headache" vs. "severe headache"). Solved by ordering matches by specificity (longer matches take priority via severity ranking).

### Member 2 — Medical Routing Agent
- **Agent Developed:** `MedicalRoutingAgent` — Maps symptom categories to specialist types, finds hospitals.
- **Tool Implemented:** `HospitalDBTool` — Queries hospital database by specialty with city-aware matching.
- **Challenges Faced:** Handling LLM output variability — the model sometimes returned specialist names with extra punctuation or qualifiers. Solved by stripping quotes, periods, and whitespace from LLM output.

### Member 3 — Appointment Coordinator Agent
- **Agent Developed:** `AppointmentCoordinatorAgent` — Finds and ranks optimal appointment slots with booking number, estimated consultation time, queue position, and seat availability.
- **Tool Implemented:** `ScheduleOptimizerTool` — Multi-criteria slot scoring (availability ratio + doctor rating) with severity-adaptive weighting. Includes `_estimate_consultation_time()` method for queue-based time prediction.
- **Frontend Contribution:** Added the Appointment Coordinator card to `SummaryPage.jsx` with a booking details panel (2×2 grid showing booking #, estimated time, queue, seats) and an expandable alternatives accordion with full doctor details per alternative.
- **Data:** Expanded `schedules.json` to 7 hospitals, 21 doctors across 8 specialties (Cardiology, Neurology, Orthopedics, Dermatology, Pulmonology, General Medicine, Gastroenterology, Ophthalmology).
- **Tests Written:** 9 test cases in `test_schedule_optimizer.py` covering slot filtering, urgency scoring, city fallback, alternatives, state validation, and error handling.
- **Challenges Faced:** 
  1. Designing a fair scoring algorithm that balances urgency with quality — solved by using different weight distributions (70/30 for urgent, 60/40 for regular).
  2. Estimating consultation time from queue position — solved by calculating `start_time + (patients_before × 15 min)`.
  3. Handling the case where routing agent crashes (LLM parsing error) but appointment agent should still work — solved by adding fallback defaults for `specialist` and `hospital_city` in `workflow.py`.

### Member 4 — Travel Risk Assessment Agent
- **Agent Developed:** `TravelRiskAgent` — Evaluates travel feasibility and generates safety recommendations.
- **Tool Implemented:** `DistanceCalculatorTool` — Geocoding + road distance calculation via free APIs with caching and Haversine fallback.
- **Challenges Faced:** OSRM API occasionally returns no routes for Sri Lankan city pairs. Solved by implementing a two-tier distance strategy (OSRM → Haversine fallback) and caching successful geocoding results to minimize API calls. Also constrained the LLM prompt to avoid irrelevant suggestions (e.g., domestic flights in Sri Lanka).

---

## 9. GitHub Repository

**Repository Link:** [https://github.com/dinith114/CTSE-Assignment-ML](https://github.com/dinith114/CTSE-Assignment-ML)

### How to Run

```bash
# 1. Clone the repository
git clone https://github.com/dinith114/CTSE-Assignment-ML.git
cd CTSE-Assignment-ML

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama (Windows)
winget install Ollama.Ollama

# 4. Pull the local SLM model
ollama pull llama3.2:3b

# 5. Run the full workflow
python main.py --symptoms "I have severe chest pain" --patient-city "Kandy, Sri Lanka"

# 6. Run all tests
python -m pytest tests/ -v
```

---

## 10. Conclusion

This Multi-Agent E-Channeling System demonstrates the core principles of Agentic AI through a practical healthcare application. The system successfully:

- Orchestrates **4 distinct agents** in a sequential pipeline using **LangGraph**
- Employs **4 custom Python tools** with strict type hinting, comprehensive docstrings, and robust error handling
- Leverages a **local Ollama SLM** (llama3.2:3b) for reasoning, confirmation, and explainability — with zero cloud costs
- Maintains **global state** securely across agents using a typed dictionary with no context loss
- Implements **comprehensive observability** through file logging, structured conversation logs, and run output persistence
- Validates correctness through **property-based testing, mock-based unit tests, integration tests, and LLM-as-a-Judge evaluation**
- Runs entirely on **local infrastructure** without any paid API keys

The system handles edge cases gracefully, including API failures, unknown symptoms, fully booked hospitals, and unavailable LLM — ensuring reliability in real-world deployment scenarios.
