import { useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function sanitizeText(value) {
  if (value == null) return value;
  const text = String(value);
  const noAnsi = text.replace(/\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])/g, '');
  const noCtrl = noAnsi.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/g, '');
  const deduped = noCtrl.replace(/\b([A-Za-z]{2,4})\s+(\1[A-Za-z]+)\b/g, '$2');
  return deduped.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n');
}

function InfoCard({ title, icon, children, gradient, delay }) {
  return (
    <div 
      className="group relative overflow-hidden rounded-2xl bg-white/95 backdrop-blur-sm shadow-xl transition-all duration-500 hover:shadow-2xl hover:-translate-y-2 animate-fade-in-up"
      style={{ animationDelay: `${delay || 0}ms` }}
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/5 to-transparent rounded-full -mr-16 -mt-16" />
      <div className="relative p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-100 to-blue-100 shadow-md group-hover:scale-110 transition-transform duration-300">
            <span className="text-2xl">{icon}</span>
          </div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
            {title}
          </h2>
        </div>
        {children}
      </div>
    </div>
  );
}

function KV({ label, value, icon }) {
  return (
    <div className="rounded-xl bg-gradient-to-br from-slate-50 to-white p-3 border border-slate-100 hover:border-cyan-200 hover:shadow-md transition-all duration-200 group">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm group-hover:scale-110 transition-transform">{icon}</span>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      </div>
      <p className="mt-1 whitespace-pre-wrap text-sm text-slate-800 font-medium">
        {sanitizeText(value) ?? 'N/A'}
      </p>
    </div>
  );
}

function SeverityBadge({ severity }) {
  const getSeverityColor = () => {
    switch (severity?.toLowerCase()) {
      case 'high': return 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-red-200';
      case 'medium': return 'bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-orange-200';
      case 'low': return 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-green-200';
      default: return 'bg-gradient-to-r from-gray-400 to-gray-500 text-white';
    }
  };

  const getSeverityIcon = () => {
    switch (severity?.toLowerCase()) {
      case 'high': return '🔴';
      case 'medium': return '🟠';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-md ${getSeverityColor()}`}>
      <span>{getSeverityIcon()}</span>
      {severity || 'N/A'}
    </span>
  );
}

function RiskBadge({ riskLevel }) {
  const getRiskColor = () => {
    switch (riskLevel?.toLowerCase()) {
      case 'high': return 'bg-gradient-to-r from-red-500 to-rose-500 text-white shadow-red-200';
      case 'medium': return 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-yellow-200';
      case 'low': return 'bg-gradient-to-r from-green-500 to-teal-500 text-white shadow-green-200';
      default: return 'bg-gradient-to-r from-gray-400 to-gray-500 text-white';
    }
  };

  const getRiskIcon = () => {
    switch (riskLevel?.toLowerCase()) {
      case 'high': return '⚠️';
      case 'medium': return '📊';
      case 'low': return '✅';
      default: return '❓';
    }
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-md ${getRiskColor()}`}>
      <span>{getRiskIcon()}</span>
      {riskLevel || 'N/A'}
    </span>
  );
}

function StatCard({ label, value, icon, gradient }) {
  return (
    <div className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${gradient} p-4 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 animate-fade-in-up`}>
      <div className="absolute top-0 right-0 w-20 h-20 bg-white/10 rounded-full -mr-10 -mt-10" />
      <div className="relative flex items-center justify-between">
        <div>
          <p className="text-white/80 text-xs uppercase tracking-wide">{label}</p>
          <div className="mt-1">{value}</div>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}

export default function SummaryPage() {
  const navigate = useNavigate();

  const state = useMemo(() => {
    const raw = sessionStorage.getItem('workflow_result');
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }, []);

  if (!state) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?q=80&w=2070&auto=format&fit=crop"
            alt="Medical background"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900/85 via-cyan-900/50 to-slate-900/85" />
        </div>
        <div className="relative z-10 flex min-h-screen items-center justify-center p-6">
          <div className="max-w-xl rounded-3xl bg-white/95 backdrop-blur-xl p-10 text-center shadow-2xl border border-white/30 animate-fade-in-up">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-2xl mb-6 shadow-lg">
              <span className="text-5xl">📋</span>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-800 to-cyan-700 bg-clip-text text-transparent">
              No Summary Found
            </h1>
            <p className="mt-3 text-slate-600">Please complete the medical assessment form first to generate results.</p>
            <button
              onClick={() => navigate('/form')}
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-600 px-8 py-3.5 text-white font-semibold hover:shadow-xl hover:shadow-cyan-500/30 hover:scale-105 transition-all duration-300"
            >
              Go to Assessment Form
              <span className="text-lg">→</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const triage = state.triage_result || {
    symptoms: state.symptoms,
    severity: state.severity,
    urgency: state.urgency,
    red_flags: state.red_flags,
  };
  const travel = state.travel_info || {};
  const risk = state.risk_assessment || {};

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image Layer */}
      <div className="fixed inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1505751172876-fa1923c5c528?q=80&w=2070&auto=format&fit=crop"
          alt="Medical dashboard background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/75 via-cyan-900/40 to-slate-900/75" />
        
        {/* Animated background patterns */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 left-0 w-96 h-96 bg-cyan-400 rounded-full filter blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl animate-pulse-slow animation-delay-2000" />
        </div>

        {/* Floating medical icons */}
        <div className="absolute top-20 right-10 text-7xl opacity-10 animate-float">🩺</div>
        <div className="absolute bottom-20 left-10 text-8xl opacity-10 animate-float-delayed">🏥</div>
        <div className="absolute top-1/2 left-1/4 text-6xl opacity-10 animate-float-slow">💊</div>
        <div className="absolute bottom-1/3 right-20 text-7xl opacity-10 animate-float">🚑</div>
        <div className="absolute top-1/3 right-1/3 text-5xl opacity-10 animate-float-delayed">❤️</div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen p-6 lg:p-8">
        <div className="mx-auto max-w-7xl space-y-8">
          {/* Header Section */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-fade-in-up">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/20 backdrop-blur-md shadow-lg animate-pulse-subtle">
                  <span className="text-3xl">📊</span>
                </div>
                <div>
                  <h1 className="text-3xl lg:text-4xl font-bold text-white drop-shadow-lg">
                    Workflow Summary
                  </h1>
                  <p className="text-slate-200 text-sm mt-1">Comprehensive analysis powered by intelligent agents</p>
                </div>
              </div>
            </div>
            <Link
              to="/form"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-white/15 backdrop-blur-md rounded-xl text-white font-medium hover:bg-white/25 hover:scale-105 transition-all duration-300 border border-white/20 hover:border-white/40"
            >
              <span className="text-lg">🔄</span>
              New Assessment
            </Link>
          </div>

          {/* Stats Overview Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
            <StatCard 
              label="Severity Level" 
              value={<SeverityBadge severity={triage.severity} />} 
              icon="⚠️" 
              gradient="from-red-500 to-rose-500"
            />
            <StatCard 
              label="Risk Assessment" 
              value={<RiskBadge riskLevel={triage.severity} />} 
              icon="🎯" 
              gradient="from-orange-500 to-amber-500"
            />
            <StatCard 
              label="Distance" 
              value={travel.distance_km != null ? `${travel.distance_km} km` : 'Unable to calculate'} 
              icon="📍" 
              gradient="from-blue-500 to-cyan-500"
            />
            <StatCard 
              label="Travel Time" 
              value={travel.travel_time_hours != null ? `${travel.travel_time_hours} hours` : 'Unable to calculate'} 
              icon="⏱️" 
              gradient="from-purple-500 to-indigo-500"
            />
          </div>

          {/* Main Cards Grid - PRESERVING ALL ORIGINAL FIELDS */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Symptom Triage Card */}
            <InfoCard 
              title="Symptom Triage" 
              icon="🩺" 
              gradient="from-cyan-500 to-blue-500"
              delay={100}
            >
              <div className="space-y-3">
                <KV label="Symptoms" value={(triage.symptoms || []).join(', ') || 'N/A'} icon="📝" />
                <KV label="Severity" value={triage.severity} icon="⚠️" />
                <KV label="Urgency" value={triage.urgency} icon="🚨" />
                <KV label="Red Flags" value={(triage.red_flags || []).join(', ') || 'None'} icon="🚩" />
              </div>
            </InfoCard>

            {/* Medical Routing Card */}
            <InfoCard 
              title="Medical Routing" 
              icon="🏥" 
              gradient="from-purple-500 to-pink-500"
              delay={200}
            >
              <div className="space-y-3">
                <KV label="Specialist" value={state.specialist} icon="👨‍⚕️" />
                <KV label="Routing Reason" value={state.routing_reason || state.routing?.reason} icon="🎯" />
                <KV 
                  label="Doctors" 
                  value={(state.doctors || []).length ? JSON.stringify(state.doctors, null, 2) : 'No doctors found'} 
                  icon="👩‍⚕️" 
                />
              </div>
            </InfoCard>

            {/* Travel Risk Card - PRESERVING ALL ORIGINAL FIELDS WITHOUT ADDITIONS ()*/}
            <InfoCard 
              title="Travel Risk" 
              icon="✈️" 
              gradient="from-teal-500 to-emerald-500"
              delay={300}
            >
              <div className="space-y-3">
                <KV label="From" value={travel.source_city || state.patient_city} icon="📍" />
                <KV label="To" value={travel.destination_city || state.hospital_city} icon="🎯" />
                <KV label="Distance" value={travel.distance_km != null ? `${travel.distance_km} km` : 'Unable to calculate'} icon="📏" />
                <KV label="Time" value={travel.travel_time_hours != null ? `${travel.travel_time_hours} hours` : 'Unable to calculate'} icon="⏰" />
                <KV label="Risk Level" value={triage.severity} icon="⚠️" />
                <KV label="Recommendation" value={risk.llm_reasoning || risk.recommendation || 'No recommendation available'} icon="💡" />
              </div>
            </InfoCard>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-25px) rotate(5deg); }
        }
        @keyframes float-delayed {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(20px) rotate(-5deg); }
        }
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-15px) rotate(3deg); }
        }
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes pulse-slow {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.1);
          }
        }
        @keyframes pulse-subtle {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }
        .animate-float {
          animation: float 8s ease-in-out infinite;
        }
        .animate-float-delayed {
          animation: float-delayed 9s ease-in-out infinite;
        }
        .animate-float-slow {
          animation: float-slow 10s ease-in-out infinite;
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.6s ease-out forwards;
          opacity: 0;
        }
        .animate-pulse-slow {
          animation: pulse-slow 8s ease-in-out infinite;
        }
        .animate-pulse-subtle {
          animation: pulse-subtle 3s ease-in-out infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  );
}