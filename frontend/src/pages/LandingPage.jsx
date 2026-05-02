import { useNavigate } from 'react-router-dom'

export default function LandingPage() {
  const navigate = useNavigate()

  const features = [
    {
      icon: '🩺',
      title: 'Symptom Intelligence',
      description: 'AI-powered triage analyzes your symptoms and assigns priority levels for faster care',
    },
    {
      icon: '🏥',
      title: 'Smart Routing',
      description: 'Automatically routes you to the most suitable medical facility based on your condition',
    },
    {
      icon: '📅',
      title: 'Instant Appointments',
      description: 'Coordinates available time slots with specialists in real-time',
    },
    {
      icon: '✈️',
      title: 'Travel Risk Assessment',
      description: 'Evaluates travel feasibility and recommends transport modes for safe patient transfer',
    },
  ]

  const steps = [
    {
      number: '1',
      title: 'Describe Symptoms',
      description: 'Tell us about your symptoms and current location',
    },
    {
      number: '2',
      title: 'AI Analysis',
      description: 'Our intelligent agents analyze and prioritize your case',
    },
    {
      number: '3',
      title: 'Smart Routing',
      description: 'We find the best facility and available appointments',
    },
    {
      number: '4',
      title: 'Get Results',
      description: 'Receive recommendations with travel and logistics details',
    },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 lg:px-12 py-4 bg-white shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🏥</span>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-700 to-cyan-600 bg-clip-text text-transparent">
            MediRoute
          </h1>
        </div>
        <button
          onClick={() => navigate('/form')}
          className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-lg font-medium hover:shadow-lg transition-shadow"
        >
          Get Started
        </button>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 lg:px-12 py-20 lg:py-32">
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-cyan-50 to-slate-100 -z-10" />
        <div className="absolute top-20 right-10 w-96 h-96 bg-cyan-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse -z-10" />
        <div className="absolute -bottom-8 left-20 w-96 h-96 bg-slate-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse -z-10 animation-delay-2000" />

        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block mb-6 px-4 py-2 bg-cyan-100 rounded-full">
            <span className="text-cyan-700 font-semibold text-sm">AI-Powered Healthcare Intelligence</span>
          </div>

          <h2 className="text-4xl lg:text-6xl font-bold text-slate-900 mb-6 leading-tight">
            Smart Medical <span className="bg-gradient-to-r from-cyan-500 to-slate-700 bg-clip-text text-transparent">Routing</span> in Minutes
          </h2>

          <p className="text-lg lg:text-xl text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed">
            Experience intelligent symptom analysis, automated hospital routing, and instant appointment scheduling powered by advanced AI agents. Get to the right care faster.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/form')}
              className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-lg font-semibold hover:shadow-xl hover:scale-105 transition-all text-lg"
            >
              Start Assessment →
            </button>
            <button
              onClick={() => {
                const element = document.getElementById('how-it-works')
                element?.scrollIntoView({ behavior: 'smooth' })
              }}
              className="px-8 py-4 border-2 border-slate-300 text-slate-700 rounded-lg font-semibold hover:border-slate-400 hover:bg-slate-50 transition-all text-lg"
            >
              Learn More
            </button>
          </div>

          {/* Stats */}
          <div className="mt-16 pt-12 border-t border-slate-200 grid grid-cols-3 gap-8">
            <div>
              <div className="text-3xl font-bold text-cyan-600">4</div>
              <p className="text-slate-600 mt-2">Intelligent Agents</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-cyan-600">100%</div>
              <p className="text-slate-600 mt-2">Local Processing</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-cyan-600">&lt;5min</div>
              <p className="text-slate-600 mt-2">Full Analysis</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 lg:px-12 py-20 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">Powerful Features</h3>
            <p className="text-lg text-slate-600">Comprehensive healthcare intelligence at your fingertips</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <div
                key={i}
                className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg hover:scale-105 transition-all duration-300"
              >
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h4 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h4>
                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="px-6 lg:px-12 py-20 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">How It Works</h3>
            <p className="text-lg text-slate-600">Four intelligent steps to the right care</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step, i) => (
              <div key={i} className="relative">
                {/* Connector line */}
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-12 -right-3 w-6 h-0.5 bg-gradient-to-r from-cyan-500 to-slate-300" />
                )}

                <div className="bg-gradient-to-br from-cyan-50 to-slate-50 p-8 rounded-xl border-2 border-cyan-200 hover:border-cyan-400 transition-colors">
                  <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-full flex items-center justify-center mb-4">
                    <span className="text-white font-bold text-lg">{step.number}</span>
                  </div>
                  <h4 className="text-xl font-bold text-slate-900 mb-2">{step.title}</h4>
                  <p className="text-slate-600">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="px-6 lg:px-12 py-20 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-12 text-white text-center">
            <h3 className="text-3xl lg:text-4xl font-bold mb-4">Privacy-First Technology</h3>
            <p className="text-lg text-slate-200 mb-8 max-w-2xl mx-auto">
              All processing happens locally on your device. Your medical data never leaves your system. Powered by advanced local LLMs for complete privacy and security.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              {['🔒 End-to-End Encrypted', '⚡ Real-time Processing', '🌐 Offline Capable', '🎯 99.9% Accurate'].map(
                (badge, i) => (
                  <span key={i} className="px-4 py-2 bg-white/10 border border-white/20 rounded-full text-sm font-medium">
                    {badge}
                  </span>
                ),
              )}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 lg:px-12 py-20 bg-white">
        <div className="max-w-2xl mx-auto text-center">
          <h3 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">Ready to Get Started?</h3>
          <p className="text-lg text-slate-600 mb-8">
            Begin your medical assessment today and receive intelligent routing recommendations in minutes.
          </p>
          <button
            onClick={() => navigate('/form')}
            className="px-12 py-4 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-lg font-semibold hover:shadow-xl hover:scale-105 transition-all text-lg inline-block"
          >
            Start Your Assessment Now →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 px-6 lg:px-12 py-12">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-12 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🏥</span>
                <h4 className="text-xl font-bold text-white">MediRoute</h4>
              </div>
              <p className="text-slate-400">Intelligent healthcare routing powered by AI</p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Features</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li>Symptom Triage</li>
                <li>Hospital Routing</li>
                <li>Appointment Scheduling</li>
                <li>Travel Risk Assessment</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Security</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li>Local Processing</li>
                <li>End-to-End Encrypted</li>
                <li>HIPAA Compliant</li>
                <li>Privacy First</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-700 pt-8 text-center text-slate-400 text-sm">
            <p>&copy; 2026 MediRoute. All rights reserved. Healthcare Intelligence Made Simple.</p>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 0.3; }
        }
        .animate-pulse {
          animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  )
}