import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

export default function FormPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [patientCity, setPatientCity] = useState('');
  const [hospitalCity, setHospitalCity] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!symptoms.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Symptoms Required',
        text: 'Please describe your symptoms to proceed with the assessment.',
        background: '#fff',
        confirmButtonColor: '#0891b2',
      });
      return;
    }

    setLoading(true);
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
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const result = await res.json();
      sessionStorage.setItem('workflow_result', JSON.stringify(result));

      await Swal.fire({
        icon: 'success',
        title: 'Assessment Ready!',
        text: 'Your personalized medical routing results are ready.',
        timer: 1500,
        showConfirmButton: false,
        background: '#fff',
        iconColor: '#0891b2',
      });

      navigate('/summary');
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Request Failed',
        text: error.message || 'Unable to connect to the assessment server. Please try again.',
        background: '#fff',
        confirmButtonColor: '#0891b2',
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image Layer */}
      <div className="fixed inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?q=80&w=2080&auto=format&fit=crop"
          alt="Medical background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/80 via-cyan-900/40 to-slate-900/80" />
        
        {/* Animated gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 via-transparent to-blue-500/10 animate-slow-spin" />
        
        {/* Decorative medical icons floating */}
        <div className="absolute top-20 left-10 text-6xl opacity-10 animate-float">🩺</div>
        <div className="absolute bottom-20 right-10 text-7xl opacity-10 animate-float-delayed">🏥</div>
        <div className="absolute top-1/3 right-20 text-5xl opacity-10 animate-float-slow">💊</div>
        <div className="absolute bottom-1/3 left-20 text-6xl opacity-10 animate-float-delayed">🚑</div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-6">
        <div className="mx-auto max-w-5xl w-full">
          {/* Back Navigation */}
          <div className="mb-6">
            <button
              onClick={() => navigate('/')}
              className="group inline-flex items-center gap-2 px-5 py-2.5 bg-white/10 backdrop-blur-md rounded-full text-white hover:bg-white/20 transition-all duration-300 border border-white/20 hover:border-white/40"
            >
              <span className="group-hover:-translate-x-1 transition-transform">←</span>
              <span className="font-medium">Back to Home</span>
            </button>
          </div>

          {/* Form Card */}
          <div className="relative">
            {/* Glow effect behind card */}
            <div className="absolute -inset-1 bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 rounded-3xl blur-xl opacity-30 animate-pulse" />
            
            <div className="relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden">
              {/* Decorative top bar */}
              <div className="h-2 bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400" />
              
              <div className="p-8 md:p-12">
                {/* Header */}
                <div className="text-center mb-8">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-2xl mb-6 shadow-lg">
                    <span className="text-4xl">📋</span>
                  </div>
                  <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-slate-800 to-cyan-700 bg-clip-text text-transparent">
                    Medical Assessment
                  </h1>
                  <p className="mt-3 text-slate-500 text-lg max-w-md mx-auto">
                    Enter patient details to start the intelligent routing analysis
                  </p>
                </div>

                <form className="space-y-6" onSubmit={handleSubmit}>
                  {/* Name Field */}
                  <div className="group">
                    <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                      <span className="text-cyan-600">👤</span>
                      Patient Name
                      <span className="text-xs font-normal text-slate-400">(Optional)</span>
                    </label>
                    <input
                      className="w-full rounded-xl border border-slate-200 bg-white/80 px-5 py-3.5 outline-none transition-all duration-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 hover:border-slate-300"
                      placeholder="Enter patient's full name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>

                  {/* Symptoms Field */}
                  <div className="group">
                    <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                      <span className="text-orange-500">🩺</span>
                      Symptoms <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      className="min-h-32 w-full rounded-xl border border-slate-200 bg-white/80 px-5 py-3.5 outline-none transition-all duration-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 hover:border-slate-300 resize-none"
                      placeholder="Describe your symptoms in detail... (e.g., chest pain, shortness of breath, fever)"
                      value={symptoms}
                      onChange={(e) => setSymptoms(e.target.value)}
                      required
                    />
                    <p className="mt-1 text-xs text-slate-400">Provide as much detail as possible for accurate analysis</p>
                  </div>

                  {/* Location Fields Grid */}
                  <div className="grid gap-6 md:grid-cols-2">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                        <span className="text-blue-500">📍</span>
                        Patient City
                      </label>
                      <input
                        className="w-full rounded-xl border border-slate-200 bg-white/80 px-5 py-3.5 outline-none transition-all duration-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 hover:border-slate-300"
                        placeholder="e.g., Colombo, Homagama"
                        value={patientCity}
                        onChange={(e) => setPatientCity(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                        <span className="text-purple-500">🏥</span>
                        Preferred Hospital
                      </label>
                      <input
                        className="w-full rounded-xl border border-slate-200 bg-white/80 px-5 py-3.5 outline-none transition-all duration-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 hover:border-slate-300"
                        placeholder="e.g., Durdans Hospital, Asiri Surgical"
                        value={hospitalCity}
                        onChange={(e) => setHospitalCity(e.target.value)}
                      />
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="pt-6">
                    <button
                      type="submit"
                      disabled={loading}
                      className="group relative w-full overflow-hidden rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-600 px-8 py-4 text-white font-semibold text-lg transition-all duration-300 hover:shadow-xl hover:shadow-cyan-500/25 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      <span className="relative z-10 flex items-center justify-center gap-2">
                        {loading ? (
                          <>
                            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Processing Assessment...
                          </>
                        ) : (
                          <>
                            Run Medical Assessment
                            <span className="group-hover:translate-x-1 transition-transform">→</span>
                          </>
                        )}
                      </span>
                      {!loading && (
                        <div className="absolute inset-0 -z-0 bg-gradient-to-r from-cyan-600 to-cyan-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      )}
                    </button>
                  </div>

                  {/* Information Note */}
                  <div className="mt-8 p-4 bg-cyan-50/80 rounded-xl border border-cyan-100">
                    <div className="flex items-start gap-3">
                      <span className="text-cyan-600 text-xl">🔒</span>
                      <div className="text-sm text-slate-600">
                        <p className="font-medium text-slate-700">Your data is secure</p>
                        <p>All information is processed locally and encrypted end-to-end. We prioritize your privacy.</p>
                      </div>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>

          {/* Stats Footer */}
          <div className="mt-8 text-center">
            <div className="inline-flex items-center gap-6 px-6 py-3 bg-white/10 backdrop-blur-md rounded-full text-white/80 text-sm">
              <span className="flex items-center gap-1">🤖 AI-Powered Analysis</span>
              <span className="w-1 h-1 bg-white/40 rounded-full" />
              <span className="flex items-center gap-1">⚡ Real-time Routing</span>
              <span className="w-1 h-1 bg-white/40 rounded-full" />
              <span className="flex items-center gap-1">🔒 Privacy First</span>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(5deg); }
        }
        @keyframes float-delayed {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(15px) rotate(-5deg); }
        }
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-10px) rotate(3deg); }
        }
        @keyframes slow-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animate-float-delayed {
          animation: float-delayed 7s ease-in-out infinite;
        }
        .animate-float-slow {
          animation: float-slow 8s ease-in-out infinite;
        }
        .animate-slow-spin {
          animation: slow-spin 20s linear infinite;
        }
        .animate-pulse {
          animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}