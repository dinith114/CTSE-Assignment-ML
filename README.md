# E-Channeling Healthcare System - Multi-Agent AI Platform

A sophisticated multi-agent AI system for intelligent medical routing, symptom analysis, and appointment coordination powered by LangGraph and local LLMs.

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

### Option 1: Full Stack (Recommended)

**Terminal 1 - Start Backend API:**
```bash
uvicorn app.server:app --reload --port 8000
```

**Terminal 2 - Start Frontend Development Server:**
```bash
cd frontend
npm run dev
```

Then open your browser to `http://localhost:5173`

### Option 2: Backend Only (CLI Testing)

**Test with Default Data:**
```bash
python main.py
```

**Test with Custom Parameters:**
```bash
python main.py --patient-city "Rathnapura" --hospital-city "Barista Express Maharagama" --severity medium --symptoms "Chest pain and shortness of breath"
```

**Example Output:**
```
2026-05-02 07:10:50,890 - app.workflow - INFO - Step 1: Symptom Triage Agent
2026-05-02 07:10:50,890 - app.agents.symptom_triage_agent - INFO - SymptomTriageAgent: Starting symptom triage
2026-05-02 07:10:50,890 - app.agents.symptom_triage_agent - INFO - SymptomTriageAgent: Completed triage - severity=medium, urgency=priority

Step 2: Medical Routing Agent
Step 3: Appointment Coordinator Agent
Step 4: Travel Risk Assessment Agent

FINAL APPOINTMENT RECOMMENDATION
============================================================
        🚗 TRAVEL ASSESSMENT SUMMARY
        📍 From: Rathnapura
        🏥 To: Barista Express Maharagama
        📏 Distance: XX.X km
        ⏱️ Estimated travel time: X.X hours
        🚦 Risk Level: VERY_LOW
        💡 Recommendation: No significant travel concerns
        🗺️ Route Advice: [Contextual advice based on distance]
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
  "doctors": [
    {
      "name": "Dr. Smith",
      "specialty": "Cardiologist",
      "hospital": "National Hospital",
      "available": true
    }
  ],
  "distance_km": 15.3,
  "travel_time_hours": 0.3,
  "risk_assessment": {
    "risk_level": "MEDIUM",
    "recommendation": "Proceed with caution",
    "travel_advice": "Short distance. Car or bus recommended."
  }
}
```

---

## 🧠 Multi-Agent Workflow

### Agent 1: Symptom Triage Agent
**Purpose:** Analyze patient symptoms and determine severity

**Input:**
- Patient symptoms (text)
- Medical history (optional)

**Output:**
- Severity level (low, medium, high, urgent)
- Urgency category (routine, priority, emergency)
- Identified red flags

**LLM Prompt:** Analyzes symptoms using local Ollama LLM with medical reasoning

---

### Agent 2: Medical Routing Agent
**Purpose:** Recommend appropriate specialist and find available doctors

**Input:**
- Symptom severity
- Red flags
- Patient location

**Output:**
- Recommended specialist type
- Alternative specialists
- Available doctors matching the specialty
- Routing reasoning

**Data Source:** SQLite database (doctors.db)

---

### Agent 3: Appointment Coordinator Agent
**Purpose:** Coordinate available appointment slots

**Input:**
- Specialist type
- Hospital
- Patient availability

**Output:**
- Available time slots
- Appointment confirmation
- Doctor assignment

**Data Source:** schedules.json (doctor schedules)

---

### Agent 4: Travel Risk Assessment Agent
**Purpose:** Evaluate travel feasibility and safety

**Input:**
- Patient location
- Hospital location
- Severity level
- Distance

**Output:**
- Travel distance (km)
- Estimated travel time
- Risk level assessment
- Transport mode recommendation
- LLM-generated reasoning

**APIs Used:**
- Nominatim (geocoding)
- OSRM (route distance)
- Haversine formula (fallback)

---

## 🛠️ Customization

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

- Member 1: Symptom Triage Agent
- Member 2: Medical Routing Agent
- Member 3: Appointment Coordinator Agent
- Member 4: Travel Risk Assessment Agent

---

## 🔗 External Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [OpenStreetMap Nominatim](https://nominatim.org/)
- [OSRM (Routing Machine)](https://project-osrm.org/)

---

**Last Updated:** May 2, 2026
