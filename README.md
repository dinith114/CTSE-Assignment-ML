# E-Channeling Healthcare System - Multi-Agent AI Platform

A sophisticated **4-agent AI system** for intelligent medical routing, symptom analysis, appointment coordination, and travel risk assessment—powered by **LangGraph**, **local Ollama LLM**, and open-source geolocation APIs. All data is processed locally with zero cloud dependency.

**Key Features:**
- ✅ Multi-agent orchestration (Symptom Triage → Medical Routing → Appointment Coordination → Travel Risk)
- ✅ Local Ollama LLM reasoning (no API costs, runs on consumer hardware)
- ✅ Free geolocation APIs (Nominatim + OSRM for distance/routing)
- ✅ React frontend with real-time results
- ✅ Fully tested with pytest (15+ test cases)
- ✅ SQLite hospital database with 21+ doctors across 8 specialties

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                    │
│  Landing Page → Form Page → Backend Call → Summary Page         │
├─────────────────────────────────────────────────────────────────┤
│                  REACT ROUTER (Routing)                         │
│  / (Landing) → /form → /summary                                 │
├─────────────────────────────────────────────────────────────────┤
│              TAILWINDCSS + SWEETALERT2 (Styling)               │
│  Modern UI, Responsive Design, Toast Notifications             │
├──────────────────────┬──────────────────────────────────────────┤
│   API Gateway        │  Backend (FastAPI)                      │
│ POST /api/run        │  port: 8000                             │
│ ↓                    │  CORS Enabled                           │
├──────────────────────┼──────────────────────────────────────────┤
│                   LangGraph Workflow Orchestration              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Step 1: Symptom Triage Agent                               ││
│  │    - Analyzes patient symptoms                              ││
│  │    - Determines severity (low, medium, high, urgent)        ││
│  │    - Identifies red flags                                   ││
│  └──────────────────┬──────────────────────────────────────────┘│
│                     ↓                                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Step 2: Medical Routing Agent                              ││
│  │    - Recommends appropriate specialist                      ││
│  │    - Searches hospital database                             ││
│  │    - Finds available doctors                                ││
│  └──────────────────┬──────────────────────────────────────────┘│
│                     ↓                                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Step 3: Appointment Coordinator Agent                      ││
│  │    - Coordinates available time slots                       ││
│  │    - Schedules appointments                                 ││
│  └──────────────────┬──────────────────────────────────────────┘│
│                     ↓                                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Step 4: Travel Risk Assessment Agent                       ││
│  │    - Calculates distance (Nominatim API + OSRM)             ││
│  │    - Estimates travel time                                  ││
│  │    - Assesses travel risks                                  ││
│  │    - Recommends transport modes                             ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘

EXTERNAL APIs:
  • OpenStreetMap Nominatim - Geocoding
  • OpenStreetMap Routing Machine - Road distances
  • Ollama (Local) - LLM Reasoning
```

### Technology Stack

**Frontend:**
- React 19.2.5 with Vite 8.0.10
- React Router v6 for multi-page navigation
- TailwindCSS for utility-first styling
- SweetAlert2 for notifications
- Responsive design (mobile-first)

**Backend:**
- Python 3.9+
- FastAPI for REST API
- LangGraph 0.0.20 for multi-agent orchestration
- Ollama with llama3.2:3b for local LLM reasoning

**Data & Storage:**
- SQLite (doctors.db) - Doctor and hospital information
- JSON caching - City coordinates
- SessionStorage - Frontend state management

**External Services:**
- OpenStreetMap Nominatim - Location geocoding (free, no API key)
- OpenStreetMap Routing Machine (OSRM) - Route distance calculation
- Haversine formula - Fallback distance calculation

---

## 📂 Project Structure

```
CTSE-Assignment-ML/
├── main.py                          # CLI entry point for testing
├── README.md                         # This file
├── requirements.txt                 # Python dependencies
│
├── app/                             # Backend application
│   ├── server.py                    # FastAPI application
│   ├── workflow.py                  # LangGraph orchestration
│   ├── logger_config.py             # Logging configuration
│   ├── state.py                     # Workflow state definitions
│   │
│   ├── agents/                      # Multi-agent system
│   │   ├── symptom_triage_agent.py          # Agent 1
│   │   ├── medical_routing_agent.py         # Agent 2
│   │   ├── appointment_coordinator_agent.py # Agent 3
│   │   └── travel_risk_agent.py             # Agent 4
│   │
│   ├── tools/                       # Tool implementations
│   │   ├── symptom_parser_tool.py
│   │   ├── hospital_db_tool.py
│   │   ├── schedule_optimizer_tool.py
│   │   └── distance_calculator_tool.py
│   │
│   ├── data/                        # Data storage
│   │   ├── city_distances/
│   │   │   └── city_coordinates.json       # Cached city coordinates
│   │   ├── database/
│   │   │   └── doctors.db                  # SQLite doctor database
│   │   ├── schedules.json                  # Doctor schedules
│   │   └── city_distances.json
│   │
│   └── logs/                        # Logging directory
│
├── frontend/                        # React frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   │
│   ├── public/                      # Static assets
│   │   └── icons.svg
│   │
│   └── src/
│       ├── main.jsx                 # React entry point
│       ├── App.jsx                  # Route outlet
│       ├── index.css                # Global styles
│       │
│       └── pages/
│           ├── LandingPage.jsx      # Hero & features
│           ├── FormPage.jsx         # Patient intake form
│           └── SummaryPage.jsx      # Results display
│
└── tests/                           # Test suite
    ├── test_distance_calculator.py
    ├── test_hospital_db.py
    ├── test_schedule_optimizer.py
    ├── test_symptom_parser.py
    └── test_travel_risk_agent.py
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (backend)
- **Node.js 16+** (frontend)
- **Ollama** with `llama3.2:3b` model (for LLM reasoning)
- **Git**

---

## 🤖 Installing and Running Ollama

Ollama provides a local, privacy-first LLM that powers the reasoning features in this project. No API keys or cloud required.

### Install Ollama

**Windows:**
1. Download from [ollama.ai](https://ollama.ai)
2. Run the installer
3. Ollama will be added to your PATH automatically

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### Download the Model

Run this once to download `llama3.2:3b` (~2GB):
```bash
ollama pull llama3.2:3b
```

### Start Ollama Service

**Option 1: Start the HTTP API Server (Recommended for this project)**
```bash
ollama serve
```
This runs the Ollama HTTP API at `http://localhost:11434`. Your agents will communicate with it automatically.
Keep this terminal open while running the workflow.

**Option 2: Run a Model Interactively**
```bash
ollama run llama3.2:3b
```
Type your prompt and press Enter. Type `/bye` to exit.

### Test Ollama

Verify Ollama is working by running:
```bash
ollama run llama3.2:3b "Explain travel risk assessment in healthcare in one sentence."
```

You should see a response like:
```
Travel risk assessment evaluates the safety, feasibility, and practical considerations for a patient to travel between their location and a healthcare facility.
```

### Control Ollama in Your Workflow

To enable/disable Ollama reasoning:
```bash
# Enable (default)
$env:USE_LOCAL_LLM = "true"

# Disable (use rule-based recommendations only)
$env:USE_LOCAL_LLM = "false"

# Specify model (optional, defaults to llama3.2:3b)
$env:OLLAMA_MODEL = "llama3.2:3b"

# Set timeout in seconds (optional, defaults to 60)
$env:OLLAMA_REASONING_TIMEOUT = "60"
```

Then run your workflow:
```bash
python main.py --patient-city "..." --hospital-city "..." --symptoms "..."
```

### Installation

**1. Clone the Repository**
```bash
git clone <repository-url>
cd CTSE-Assignment-ML
```

**2. Backend Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

cd ..
```

---

## 🎯 Running the Application

### Full Stack with Ollama (Complete Setup)

This is the **recommended way** to run the project with all features enabled.

**Terminal 1 - Start Ollama Service:**
```bash
ollama serve
```
Wait for it to say "Listening on" before proceeding.

**Terminal 2 - Start Backend API:**
```bash
# Activate virtual environment (if not already)
venv\Scripts\activate

# Start FastAPI server
uvicorn app.server:app --reload --port 8000
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
npm run dev
```

Then open your browser to `http://localhost:5173` and start entering patient symptoms.

---

### Quick CLI Test (Without Frontend)

**Terminal 1 - Start Ollama Service (if you want LLM reasoning):**
```bash
ollama serve
```

**Terminal 2 - Run the Workflow:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Test with default parameters
python main.py

# Test with custom parameters
python main.py \
  --patient-city "Colombo, Sri Lanka" \
  --hospital-city "Durdans Hospital, Sri Lanka" \
  --symptoms "Chest pain and shortness of breath"

# Test without LLM reasoning (rule-based only)
$env:USE_LOCAL_LLM = "false"
python main.py --patient-city "..." --hospital-city "..." --symptoms "..."
```

**Expected Output:**
```
2026-05-03 07:10:50 - INFO - Step 1: Symptom Triage Agent
2026-05-03 07:10:50 - INFO - Symptom Triage complete - severity=high
...
2026-05-03 07:10:51 - INFO - Step 2: Medical Routing Agent
...
2026-05-03 07:10:52 - INFO - Step 3: Appointment Coordinator Agent
...
2026-05-03 07:10:53 - INFO - Step 4: Travel Risk Assessment Agent

============================================================
FINAL APPOINTMENT RECOMMENDATION
============================================================
🚗 TRAVEL ASSESSMENT SUMMARY
📍 From: Colombo, Sri Lanka
🏥 To: Durdans Hospital, Sri Lanka
📏 Distance: 15.3 km
⏱️ Estimated travel time: 0.3 hours
🚦 Risk Level: high
💡 Recommendation: [LLM-generated or rule-based recommendation]
🗺️ Route Advice: Car or bus recommended
============================================================

📊 Observability: 4 agent(s) logged to conversation_log
```

Results are saved to `app/logs/system/last_run.json` for debugging.

---

### Backend API Only (No Frontend)

```bash
# Start Ollama
ollama serve

# In another terminal, start FastAPI
uvicorn app.server:app --reload --port 8000

# Test the API with curl
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John",
    "symptoms": "Chest pain",
    "patient_city": "Colombo, Sri Lanka",
    "hospital_city": "Durdans Hospital"
  }'
```

---

## 📊 API Reference

### Endpoint: POST /api/run

**Request Body:**
```json
{
  "name": "John Doe",
  "symptoms": "Chest pain and shortness of breath",
  "patient_city": "Colombo, Sri Lanka",
  "hospital_city": "National Hospital"
}
```

**Response:**
```json
{
  "patient_text": "Chest pain and shortness of breath",
  "patient_city": "Colombo, Sri Lanka",
  "severity": "high",
  "urgency": "urgent",
  "specialist": "Cardiologist",
  "hospital_city": "Colombo, Sri Lanka",
  "symptoms": ["chest pain", "shortness of breath"],
  "red_flags": ["chest pain", "shortness of breath"],
  "appointment": {
    "doctor_name": "Dr. Ruwan Perera",
    "qualifications": "MBBS, MD (Cardiology), FRCP",
    "hospital_name": "Nawaloka Hospital",
    "hospital_city": "Colombo, Sri Lanka",
    "day": "Monday",
    "time_slot": "09:00 - 13:00",
    "doctor_rating": 4.8,
    "consultation_fee": 3500,
    "booking_number": 3,
    "estimated_time": "09:30",
    "booked": 2,
    "available": 8,
    "max_patients": 10,
    "urgency_score": 0.85,
    "llm_reasoning": "This slot was recommended because...",
    "alternatives": [{"doctor_name": "...", "...": "..."}]
  },
  "travel_info": {
    "distance_km": 15.3,
    "travel_time_hours": 0.3,
    "source_city": "Colombo, Sri Lanka",
    "destination_city": "Colombo, Sri Lanka"
  },
  "risk_assessment": {
    "risk_level": "MEDIUM",
    "recommendation": "Proceed with caution",
    "llm_reasoning": "Short distance. Car or bus recommended."
  }
}
```

---

## 🔬 How the Workflow Works

### Sequential 4-Agent Pipeline

```
1️⃣ SYMPTOM TRIAGE AGENT
   Input: Patient symptoms (text)
   ↓
   - Uses symptom_parser_tool to extract medical keywords
   - Uses Ollama (if enabled) to correct spelling & extract nuanced symptoms
   - Outputs: severity (low/medium/high/urgent), urgency, red flags
   
2️⃣ MEDICAL ROUTING AGENT
   Input: Severity, red flags, location
   ↓
   - Queries hospital_db_tool (SQLite)
   - Determines specialist (Cardiologist, Emergency Physician, etc.)
   - Outputs: primary specialist, alternative specialists, available doctors
   
3️⃣ APPOINTMENT COORDINATOR AGENT
   Input: Specialist, hospital city, severity
   ↓
   - Uses schedule_optimizer_tool to rank available slots
   - Multi-criteria scoring: urgency-weighted availability × doctor rating
   - Calculates booking number, queue position, estimated time
   - Uses Ollama (if enabled) to explain recommendation
   - Outputs: recommended slot, alternatives, queue details
   
4️⃣ TRAVEL RISK ASSESSMENT AGENT
   Input: Patient city, hospital city, severity
   ↓
   - Uses distance_calculator_tool to:
     • Geocode locations (Nominatim API)
     • Calculate road distance (OSRM API)
     • Estimate travel time
   - Assesses risk based on severity × travel hours
   - Uses Ollama (if enabled) to recommend transport mode (ambulance, taxi, bus, train, etc.)
   - Outputs: distance, travel time, risk level, transport recommendation
```

### Verifying Ollama is Being Used

Check the JSON output from your last run:

**File:** `app/logs/system/last_run.json`

Look for `llm_reasoning` fields:
```json
{
  "risk_assessment": {
    "recommendation": "Proceed with caution - prioritize appointment scheduling",
    "llm_reasoning": "Based on the provided details, I recommend..."
  }
}
```

- If `llm_reasoning` contains a **detailed explanation** → Ollama is running
- If `llm_reasoning` is **missing or short fallback text** → Ollama is unavailable (using rules)

Or check your terminal logs:
```
TravelRiskAssessmentAgent: Assessment complete - MEDIUM
AppointmentCoordinatorAgent: Appointment scheduled with Dr. Manuja
```

If you see these log messages with timestamps, agents ran successfully.

---

## 🛡️ LLM Control Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `USE_LOCAL_LLM` | `true` | Enable/disable Ollama reasoning |
| `OLLAMA_MODEL` | `llama3.2:3b` | Which model to use |
| `OLLAMA_REASONING_TIMEOUT` | `60` | Seconds to wait for LLM response |

Set before running:
```bash
# PowerShell
$env:USE_LOCAL_LLM = "false"
$env:OLLAMA_MODEL = "llama3.2:3b"
$env:OLLAMA_REASONING_TIMEOUT = "30"

# Then run
python main.py --patient-city "..." --hospital-city "..." --symptoms "..."
```

---

### Agent 1: Symptom Triage Agent
**Purpose:** Analyze patient symptoms, classify severity, and identify red flags

**Processing Pipeline:**
1. Calls `symptom_parser_tool` (deterministic Python rules)
   - Pattern matches for known symptoms
   - Classifies severity based on red flags (chest pain, difficulty breathing, etc.)
   - Returns: symptoms list, severity, urgency, red flags
2. Optionally calls Ollama (if `USE_LOCAL_LLM=true`)
   - Corrects misspelled medical terms (e.g., "diebetes" → "diabetes")
   - Extracts subtle symptoms from narrative text
   - Merges with tool output for comprehensive results

**Example:**
```
Input: "I have chest pan and cant breath"
Tool output: symptoms=[chest pain, shortness of breath], severity=high
Ollama output: "chest pan" → "chest pain", adds "dyspnea"
Final: symptoms=[chest pain, dyspnea, shortness of breath], severity=high ✓
```

**Output:**
- Severity level (low, medium, high, urgent)
- Urgency category (routine, priority, emergency)
- Identified red flags
- Corrected symptoms list

**Code:** `app/agents/symptom_triage_agent.py`

---

### Agent 2: Medical Routing Agent
**Purpose:** Recommend specialist and find available doctors

**Processing:**
1. Queries `hospital_db_tool` (SQLite database)
   - Looks for specialists matching severity + symptoms
   - Searches location-specific first, then broadens to all locations
2. Optionally calls Ollama for routing explanation
3. Returns matching doctors and alternative specialists

**Example:**
```
Input: severity=high, symptoms=[chest pain, shortness of breath], location=Colombo
Output: 
  primary_specialty: "Cardiologist"
  doctors: [{name: "Dr. Ruwan Perera", hospital: "Nawaloka", ...}]
  reason: "High severity cardiac symptoms require immediate cardiologist"
```

**Output:**
- Recommended specialist type
- Alternative specialists
- Available doctors matching the specialty
- Routing reasoning

**Data Source:** `app/data/database/doctors.db` (21+ doctors, 8 specialties)

**Code:** `app/agents/medical_routing_agent.py`

---

### Agent 3: Appointment Coordinator Agent
**Purpose:** Find, rank, and recommend best appointment slots with full booking details

**Scoring Algorithm:**
- For **urgent/high severity**: 70% availability + 30% rating (get seen quickly)
- For **low/medium severity**: 40% availability + 60% rating (prioritize quality)

**Output Details:**
```json
{
  "doctor_name": "Dr. Manuja Weerasinghe",
  "hospital_name": "Lanka Hospital",
  "day": "Friday",
  "time_slot": "14:00 - 17:00",
  "booking_number": 2,           ← Your queue position
  "booked": 1,                   ← Patients already booked
  "available": 5,                ← Remaining slots
  "estimated_time": "14:15",     ← Your estimated consultation time
  "urgency_score": 0.88,
  "alternatives": [...]          ← 2 backup options
}
```

**Calculation:**
```
Estimated Time = Base Time + (Booking Number × 15 minutes avg)
              = 14:00 + (2 × 15 min) = 14:30
```

**Features:**
- ✅ City fallback (search all cities if none found locally)
- ✅ Works fully without Ollama
- ✅ Returns up to 2 alternative slots
- ✅ LLM reasoning explains why this slot is recommended

**Data Source:** `app/data/schedules.json` (7 hospitals, 21 doctors, 8 specialties)

**Code:** `app/agents/appointment_coordinator_agent.py`

---

### Agent 4: Travel Risk Assessment Agent
**Purpose:** Evaluate travel feasibility and recommend safe transport modes

**Processing:**
1. Calls `distance_calculator_tool`:
   - Geocodes locations using Nominatim API
   - Calculates road distance using OSRM API
   - Estimates travel time based on distance + vehicle speed
2. Assesses risk based on severity × travel hours:
   ```
   HIGH severity + >2 hours travel = CRITICAL risk
   HIGH severity + 1-2 hours travel = HIGH risk
   MEDIUM severity + <2 hours travel = LOW risk
   etc.
   ```
3. Optionally calls Ollama to recommend transport:
   - High severity → "1990 Suwa Seriya or ambulance"
   - Long distance (>50km) → "car or taxi"
   - Short distance → "bus, train, or taxi"

**Example Output:**
```json
{
  "distance_km": 16.2,
  "travel_time_hours": 0.3,
  "risk_level": "MEDIUM",
  "recommendation": "Proceed with caution",
  "llm_reasoning": "For a severity of high and short travel (0.3 hours), I recommend car or bus for flexibility."
}
```

**Fallbacks:**
- If Nominatim fails → Try OSRM directly
- If OSRM fails → Use Haversine formula (straight-line distance)
- If Ollama unavailable → Use rule-based recommendations

**APIs Used:**
- OpenStreetMap Nominatim (free geocoding)
- OpenStreetMap Routing Machine OSRM (free routing)

**Code:** `app/agents/travel_risk_agent.py`

---

## � Troubleshooting

### Issue: Agents running but Ollama reasoning not appearing

**Check:**
1. Ollama service is running: `ollama serve`
2. Environment variable set: `$env:USE_LOCAL_LLM` should be `true`
3. Check logs:
   ```bash
   # Look for this message in terminal
   TravelRiskAssessmentAgent: Assessment complete
   
   # Or check the JSON output
   cat app/logs/system/last_run.json | findstr "llm_reasoning"
   ```

**Solution:**
```bash
# Start Ollama service in a separate terminal
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

---

### Issue: API returns error "Connection refused"

**Problem:** Backend or Ollama not running

**Solution:**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend (check exit code)
uvicorn app.server:app --reload --port 8000

# Terminal 3: Check if running
curl http://localhost:8000/docs
```

---

### Issue: Frontend can't connect to backend

**Problem:** CORS error or backend not running

**Solution:**
1. Check backend is running on port 8000:
   ```bash
   netstat -ano | findstr :8000
   ```
2. Check frontend API endpoint in `frontend/src/pages/FormPage.jsx`:
   ```javascript
   const response = await fetch("http://localhost:8000/api/run", ...)
   ```
3. Verify CORS is enabled in `app/server.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # For dev only
       ...
   )
   ```

---

### Issue: Ollama model not found

**Solution:**
```bash
# Check installed models
ollama list

# Download if missing
ollama pull llama3.2:3b

# Test it
ollama run llama3.2:3b "Hello"
```

---

### Issue: Tests are failing

**Solution:**
```bash
# Run tests with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_travel_risk_agent.py -v

# Stop on first failure
python -m pytest tests/ -x
```

---

## 📊 Performance Tips

- **First Ollama run will be slow** (model loads into memory ~10-30s) — subsequent runs are much faster
- **Disable LLM reasoning for speed**: `$env:USE_LOCAL_LLM = "false"` uses rule-based recommendations (~100ms)
- **Cache geocoding results** — repeat location queries use cached coordinates
- **Run all 4 terminals** for full system: Ollama + Backend + Frontend + optional debug terminal

---

## �🛠️ Customization

### Adding New Hospitals

Edit `app/data/city_distances/city_coordinates.json`:
```json
{
  "hospital name": [latitude, longitude]
}
```

Or let the system auto-geocode by querying the Nominatim API.

### Adding New Doctors

Insert into `app/data/database/doctors.db`:
```
INSERT INTO doctors (name, specialty, hospital, contact, available_days)
VALUES ('Dr. Name', 'Specialty', 'Hospital', 'Contact', 'Days');
```

### Modifying Agents

Each agent is located in `app/agents/`:
- Edit the prompt templates
- Modify the processing logic
- Integrate additional data sources

---

## 🧪 Testing

**Run All Tests:**
```bash
pytest tests/
```

**Run Specific Test:**
```bash
pytest tests/test_distance_calculator.py -v
```

**Test Travel Risk Assessment:**
```bash
python -m pytest tests/test_travel_risk_agent.py -v
```

---

## 📋 Frontend Pages

### 1. Landing Page (`/`)
- Hero section with value proposition
- Features showcase
- How it works (4-step visual)
- Privacy-first technology section
- Call-to-action buttons

### 2. Form Page (`/form`)
- Patient name input (optional)
- Symptoms textarea (required)
- Patient city input
- Hospital city input
- Run Assessment button
- Form validation with SweetAlert2

### 3. Summary Page (`/summary`)
- Symptom Triage results
- Medical Routing recommendations
- Appointment details
- Travel Risk Assessment
- Distance and travel time
- Transport recommendations

---

## 🔧 Configuration

### Backend Configuration

**Port:** 8000 (customizable in `uvicorn` command)

**CORS:** Enabled for all origins (modify in `app/server.py` for production)

**Logging:** INFO level (change in `app/logger_config.py`)

### Frontend Configuration

**Port:** 5173 (Vite default, or automatically finds next available)

**API Endpoint:** `http://localhost:8000` (modify in `frontend/src/pages/FormPage.jsx`)

**Build:** `npm run build` (creates production-ready build in `dist/`)

---

## 🌐 Deployment

### Backend (Production)

```bash
# Using Gunicorn + Uvicorn
gunicorn app.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend (Production)

```bash
# Build
npm run build

# Serve with any static server
npx serve -s dist
```

---

## 📝 Environment Variables

Create `.env` file in project root:
```
OLLAMA_MODEL=llama3.2:3b
OLLAMA_HOST=http://localhost:11434
API_PORT=8000
API_HOST=127.0.0.1
NOMINATIM_TIMEOUT=10
OSRM_TIMEOUT=10
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Cannot connect to Ollama"**
- Ensure Ollama is running: `ollama serve`
- Check model exists: `ollama list`
- Verify port 11434 is accessible

**2. "Module not found" errors**
- Activate virtual environment
- Run `pip install -r requirements.txt`
- Check Python version (3.9+)

**3. "CORS error" on frontend**
- Backend CORS is enabled for all origins
- Verify backend is running on port 8000
- Check network connectivity

**4. Distance calculations incorrect**
- Verify coordinates in `city_coordinates.json`
- Check internet connection (APIs need to fetch data)
- Test with OSRM directly: `https://router.project-osrm.org/route/v1/...`

---

## 📚 Documentation

### Key Classes

- **DistanceCalculatorTool**: `app/tools/distance_calculator_tool.py`
- **MedicalRoutingAgent**: `app/agents/medical_routing_agent.py`
- **TravelRiskAgent**: `app/agents/travel_risk_agent.py`
- **SymptomTriageAgent**: `app/agents/symptom_triage_agent.py`

### Workflow Files

- **Orchestration**: `app/workflow.py`
- **State Definition**: `app/state.py`
- **API Server**: `app/server.py`

---

## 📄 License

Educational project for CTSE Assignment 2 (Y4 S1)

---

## 👥 Authors

- Member 1 - Wickramasinghe D.P : Symptom Triage Agent
- Member 2 - Rathnamalala D M J P : Medical Routing Agent
- Member 3 - P V P M Vithanage : Appointment Coordinator Agent
- Member 4 - L.D Nimla Samadinee : Travel Risk Assessment Agent

---

## 🔗 External Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [OpenStreetMap Nominatim](https://nominatim.org/)
- [OSRM (Routing Machine)](https://project-osrm.org/)

---

## ⚡ Quick Reference Commands

### Setup (One-time)
```bash
# Clone and setup
git clone <repo> && cd CTSE-Assignment-ML
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### Run Full Application (4 terminals)
```bash
# Terminal 1: Ollama Service
ollama serve

# Terminal 2: Backend
python -m venv venv && venv\Scripts\activate
uvicorn app.server:app --reload --port 8000

# Terminal 3: Frontend
cd frontend && npm run dev

# Terminal 4: Testing (optional)
python main.py --patient-city "..." --hospital-city "..." --symptoms "..."
```

### Testing
```bash
# All tests
pytest tests/ -v

# Specific agent
pytest tests/test_travel_risk_agent.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### CLI Testing (without frontend)
```bash
# Default test
python main.py

# Custom test
python main.py \
  --patient-city "Colombo" \
  --hospital-city "Durdans Hospital" \
  --symptoms "Chest pain" \
  --severity "high"

# With Ollama disabled
$env:USE_LOCAL_LLM = "false"
python main.py --patient-city "..." --hospital-city "..." --symptoms "..."
```

### Ollama Commands
```bash
# List models
ollama list

# Download model
ollama pull llama3.2:3b

# Start service
ollama serve

# Run interactive
ollama run llama3.2:3b

# Test with prompt
ollama run llama3.2:3b "Your prompt here"

# Check API health
curl http://localhost:11434/api/tags
```

### Environment Variables (PowerShell)
```bash
# Enable/disable LLM
$env:USE_LOCAL_LLM = "true"
$env:USE_LOCAL_LLM = "false"

# Set model
$env:OLLAMA_MODEL = "llama3.2:3b"

# Set timeout
$env:OLLAMA_REASONING_TIMEOUT = "60"

# Check variable
$env:USE_LOCAL_LLM
```

### Database
```bash
# Browse SQLite
sqlite3 app/data/database/doctors.db

# Query doctors
SELECT name, specialty FROM doctors;

# Export to CSV
.mode csv
.output doctors.csv
SELECT * FROM doctors;
```

### Development
```bash
# View logs
tail -f app/logs/system/last_run.json

# Format code
black app/ tests/

# Type check
mypy app/ --ignore-missing-imports

# Lint
flake8 app/ tests/
```

---

**Last Updated:** May 3, 2026
