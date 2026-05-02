import { useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function sanitizeText(value) {
  if (value == null) return value
  const text = String(value)
  const noAnsi = text.replace(/\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])/g, '')
  const noCtrl = noAnsi.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/g, '')
  const deduped = noCtrl.replace(/\b([A-Za-z]{2,4})\s+(\1[A-Za-z]+)\b/g, '$2')
  return deduped.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n')
}

function InfoCard({ title, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold text-ink">{title}</h2>
      {children}
    </section>
  )
}

function KV({ label, value }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 whitespace-pre-wrap text-sm text-slate-800">{sanitizeText(value) ?? 'N/A'}</p>
    </div>
  )
}

export default function SummaryPage() {
  const navigate = useNavigate()

  const state = useMemo(() => {
    const raw = sessionStorage.getItem('workflow_result')
    if (!raw) return null
    try {
      return JSON.parse(raw)
    } catch {
      return null
    }
  }, [])

  if (!state) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <div className="max-w-xl rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h1 className="text-2xl font-bold text-ink">No Summary Found</h1>
          <p className="mt-2 text-slate-600">Submit the form first to generate agent outputs.</p>
          <button
            onClick={() => navigate('/form')}
            className="mt-5 rounded-xl bg-ink px-5 py-2 text-white hover:bg-slate-800"
          >
            Go To Form
          </button>
        </div>
      </div>
    )
  }

  const triage = state.triage_result || {
    symptoms: state.symptoms,
    severity: state.severity,
    urgency: state.urgency,
    red_flags: state.red_flags,
  }
  const travel = state.travel_info || {}
  const risk = state.risk_assessment || {}

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-cyan-50 p-6">
      <div className="mx-auto max-w-6xl space-y-5">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-ink">Workflow Summary</h1>
          <Link to="/form" className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
            New Assessment
          </Link>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          <InfoCard title="Symptom Triage">
            <div className="grid gap-3">
              <KV label="Symptoms" value={(triage.symptoms || []).join(', ') || 'N/A'} />
              <KV label="Severity" value={triage.severity} />
              <KV label="Urgency" value={triage.urgency} />
              <KV label="Red Flags" value={(triage.red_flags || []).join(', ') || 'None'} />
            </div>
          </InfoCard>

          <InfoCard title="Medical Routing">
            <div className="grid gap-3">
              <KV label="Specialist" value={state.specialist} />
              <KV label="Routing Reason" value={state.routing_reason || state.routing?.reason} />
              <KV label="Doctors" value={(state.doctors || []).length ? JSON.stringify(state.doctors, null, 2) : 'No doctors found'} />
            </div>
          </InfoCard>

          <InfoCard title="Travel Risk">
            <div className="grid gap-3">
              <KV label="From" value={travel.source_city || state.patient_city} />
              <KV label="To" value={travel.destination_city || state.hospital_city} />
              <KV label="Distance" value={travel.distance_km != null ? `${travel.distance_km} km` : 'N/A'} />
              <KV label="Time" value={travel.travel_time_hours != null ? `${travel.travel_time_hours} hours` : 'N/A'} />
              <KV label="Risk Level" value={risk.risk_level} />
              <KV label="Recommendation" value={risk.recommendation} />
              <KV label="Route Advice" value={travel.route_advice} />
              <KV label="LLM Reasoning" value={risk.llm_reasoning || 'N/A'} />
            </div>
          </InfoCard>
        </div>
      </div>
    </div>
  )
}
