import { useState } from 'react'

export default function Form({ onSubmit }) {
  const [name, setName] = useState('')
  const [symptoms, setSymptoms] = useState('')
  const [patientCity, setPatientCity] = useState('')
  const [hospitalCity, setHospitalCity] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit({ name, symptoms, patient_city: patientCity, hospital_city: hospitalCity })
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Patient name (optional)" />
      </div>

      <div className="form-row">
        <label>Symptoms</label>
        <textarea value={symptoms} onChange={(e) => setSymptoms(e.target.value)} placeholder="e.g. chest pain and shortness of breath" required />
      </div>

      <div className="form-row two">
        <div>
          <label>Patient location</label>
          <input value={patientCity} onChange={(e) => setPatientCity(e.target.value)} placeholder="e.g. Homagama" />
        </div>
        <div>
          <label>Hospital</label>
          <input value={hospitalCity} onChange={(e) => setHospitalCity(e.target.value)} placeholder="e.g. Durdans Hospital, Sri Lanka" />
        </div>
      </div>

      <div className="form-row actions">
        <button type="submit">Submit</button>
      </div>
    </form>
  )
}
