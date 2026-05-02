import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Swal from 'sweetalert2'

export default function FormPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [symptoms, setSymptoms] = useState('')
  const [patientCity, setPatientCity] = useState('')
  const [hospitalCity, setHospitalCity] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!symptoms.trim()) {
      Swal.fire({ icon: 'warning', title: 'Symptoms are required' })
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          symptoms,
          patient_city: patientCity || undefined,
          hospital_city: hospitalCity || undefined,
        }),
      })

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`)
      }

      const result = await res.json()
      sessionStorage.setItem('workflow_result', JSON.stringify(result))

      await Swal.fire({
        icon: 'success',
        title: 'Assessment Ready',
        text: 'Redirecting to summary page...',
        timer: 1200,
        showConfirmButton: false,
      })

      navigate('/summary')
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Request failed',
        text: error.message || 'Unable to connect to backend',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50 to-orange-50 p-6">
      {/* Back to Landing */}
      <div className="mx-auto max-w-4xl mb-4">
        <button
          onClick={() => navigate('/')}
          className="text-slate-600 hover:text-slate-900 font-medium flex items-center gap-2 transition"
        >
          ← Back to Home
        </button>
      </div>

      <div className="mx-auto max-w-4xl rounded-3xl border border-white/70 bg-white/80 p-8 shadow-glow backdrop-blur">
        <h1 className="text-3xl font-bold text-ink">E-Channeling Intake</h1>
        <p className="mt-2 text-slate-600">Enter patient details and submit to run all agents.</p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Patient Name</label>
            <input
              className="w-full rounded-xl border border-mist bg-white px-4 py-3 outline-none transition focus:border-coral"
              placeholder="Optional"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Symptoms</label>
            <textarea
              className="min-h-28 w-full rounded-xl border border-mist bg-white px-4 py-3 outline-none transition focus:border-coral"
              placeholder="e.g. chest pain and shortness of breath"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              required
            />
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">Patient City</label>
              <input
                className="w-full rounded-xl border border-mist bg-white px-4 py-3 outline-none transition focus:border-coral"
                placeholder="e.g. Homagama"
                value={patientCity}
                onChange={(e) => setPatientCity(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">Hospital</label>
              <input
                className="w-full rounded-xl border border-mist bg-white px-4 py-3 outline-none transition focus:border-coral"
                placeholder="e.g. Durdans Hospital, Sri Lanka"
                value={hospitalCity}
                onChange={(e) => setHospitalCity(e.target.value)}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center rounded-xl bg-ink px-6 py-3 text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Running...' : 'Run Assessment'}
          </button>
        </form>
      </div>
    </div>
  )
}
