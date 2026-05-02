import React from 'react'

function pretty(obj) {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

export default function Summary({ state }) {
  if (!state) return null

  const triage = state.triage_result || state.triage || {
    symptoms: state.symptoms,
    severity: state.severity,
    urgency: state.urgency,
    red_flags: state.red_flags,
  }

  const routing = state.routing || { primary_specialty: state.specialist, reason: state.routing_reason }
  const travel = state.travel_info || state.travel || {}
  const risk = state.risk_assessment || state.risk || {}

  return (
    <div className="summary-root">
      <section className="card">
        <h3>Symptom Triage</h3>
        <div className="grid">
          <div><strong>Symptoms</strong><pre>{pretty(triage.symptoms || [])}</pre></div>
          <div><strong>Severity</strong><pre>{triage.severity || 'N/A'}</pre></div>
          <div><strong>Urgency</strong><pre>{triage.urgency || 'N/A'}</pre></div>
          <div><strong>Red Flags</strong><pre>{pretty(triage.red_flags || [])}</pre></div>
        </div>
      </section>

      <section className="card">
        <h3>Medical Routing</h3>
        <div className="grid">
          <div><strong>Specialist</strong><pre>{routing.primary_specialty || state.specialist || 'N/A'}</pre></div>
          <div><strong>Reason</strong><pre>{routing.reason || state.routing_reason || 'N/A'}</pre></div>
          <div style={{gridColumn: '1 / -1'}}><strong>Doctors</strong><pre>{pretty(state.doctors || routing.doctors || [])}</pre></div>
        </div>
      </section>

      <section className="card">
        <h3>Travel Risk Assessment</h3>
        <div className="grid">
          <div><strong>From</strong><pre>{travel.source_city || travel.source || state.patient_city || 'N/A'}</pre></div>
          <div><strong>To</strong><pre>{travel.destination_city || travel.destination || state.hospital_city || 'N/A'}</pre></div>
          <div><strong>Distance (km)</strong><pre>{travel.distance_km ?? travel.distance ?? 'N/A'}</pre></div>
          <div><strong>Travel time (hrs)</strong><pre>{travel.travel_time_hours ?? (travel.estimated_travel_time_minutes ? (travel.estimated_travel_time_minutes/60).toFixed(1) : 'N/A')}</pre></div>
          <div><strong>Risk level</strong><pre>{risk.risk_level || 'N/A'}</pre></div>
          <div><strong>Recommendation</strong><pre>{risk.recommendation || 'N/A'}</pre></div>
          <div style={{gridColumn: '1 / -1'}}><strong>Route advice</strong><pre>{travel.route_advice || 'N/A'}</pre></div>
          {risk.llm_reasoning && <div style={{gridColumn: '1 / -1'}}><strong>LLM Reasoning</strong><pre>{risk.llm_reasoning}</pre></div>}
        </div>
      </section>
    </div>
  )
}
