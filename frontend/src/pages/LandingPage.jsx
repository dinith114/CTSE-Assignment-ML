import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: '🩺',
      title: 'Symptom Intelligence',
      description: 'AI-powered triage analyzes your symptoms and assigns priority levels for faster care',
      gradient: 'from-cyan-500 to-blue-500',
    },
    {
      icon: '🏥',
      title: 'Smart Routing',
      description: 'Automatically routes you to the most suitable medical facility based on your condition',
      gradient: 'from-indigo-500 to-purple-500',
    },
    {
      icon: '📅',
      title: 'Instant Appointments',
      description: 'Coordinates available time slots with specialists in real-time',
      gradient: 'from-rose-500 to-pink-500',
    },
    {
      icon: '✈️',
      title: 'Travel Risk Assessment',
      description: 'Evaluates travel feasibility and recommends transport modes for safe patient transfer',
      gradient: 'from-emerald-500 to-teal-500',
    },
  ];

  const steps = [
    {
      number: '01',
      title: 'Describe Symptoms',
      description: 'Tell us about your symptoms and current location',
    },
    {
      number: '02',
      title: 'AI Analysis',
      description: 'Our intelligent agents analyze and prioritize your case',
    },
    {
      number: '03',
      title: 'Smart Routing',
      description: 'We find the best facility and available appointments',
    },
    {
      number: '04',
      title: 'Get Results',
      description: 'Receive recommendations with travel and logistics details',
    },
  ];

  const stats = [
    { value: '4', label: 'Intelligent Agents', suffix: '' },
    { value: '100', label: 'Local Processing', suffix: '%' },
    { value: '5', label: 'Full Analysis', suffix: 'min' },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="flex items-center justify-between px-6 lg:px-12 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-2 group cursor-pointer" onClick={() => navigate('/')}>
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-400 rounded-full blur-md opacity-60 group-hover:opacity-100 transition-opacity"></div>
              <span className="relative text-2xl">🏥</span>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-cyan-600 bg-clip-text text-transparent">
              MediRoute
            </h1>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-slate-600 hover:text-cyan-600 transition-colors">Features</a>
            <a href="#how-it-works" className="text-slate-600 hover:text-cyan-600 transition-colors">How it Works</a>
            <a href="#technology" className="text-slate-600 hover:text-cyan-600 transition-colors">Technology</a>
          </div>
          <button
            onClick={() => navigate('/form')}
            className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-full font-medium hover:shadow-lg hover:shadow-cyan-200 transition-all hover:scale-105"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section with Background Image */}
      <section className="relative overflow-hidden pt-24 lg:pt-32">
        {/* Background Image Layer */}
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900/70 via-slate-800/50 to-slate-900/70 z-10" />
          <img
            src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop"
            alt="Medical background"
            className="w-full h-full object-cover object-center"
          />
        </div>

        {/* Animated particles effect */}
        <div className="absolute inset-0 z-10 overflow-hidden">
          <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse animation-delay-2000" />
        </div>

        <div className="relative z-20 max-w-6xl mx-auto px-6 lg:px-12 py-16 lg:py-24 text-center">
          <div className="inline-block mb-6 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
            <span className="text-white font-semibold text-sm tracking-wide">✨ AI-Powered Healthcare Intelligence</span>
          </div>

          <h2 className="text-4xl lg:text-7xl font-bold text-white mb-6 leading-tight drop-shadow-lg">
            Smart Medical{' '}
            <span className="bg-gradient-to-r from-cyan-300 via-blue-200 to-cyan-300 bg-clip-text text-transparent">
              Routing
            </span>{' '}
            in Minutes
          </h2>

          <p className="text-lg lg:text-xl text-slate-100 mb-10 max-w-2xl mx-auto leading-relaxed drop-shadow">
            Experience intelligent symptom analysis, automated hospital routing, and instant appointment scheduling powered by advanced AI agents. Get to the right care faster.
          </p>

          <div className="flex flex-col sm:flex-row gap-5 justify-center">
            <button
              onClick={() => navigate('/form')}
              className="group px-8 py-4 bg-gradient-to-r from-cyan-400 to-cyan-600 text-white rounded-full font-semibold hover:shadow-xl hover:shadow-cyan-500/30 hover:scale-105 transition-all text-lg flex items-center justify-center gap-2"
            >
              Start Assessment
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </button>
            <button
              onClick={() => {
                const element = document.getElementById('how-it-works');
                element?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="px-8 py-4 border-2 border-white/30 backdrop-blur-sm text-white rounded-full font-semibold hover:bg-white/10 hover:border-white/50 transition-all text-lg"
            >
              Learn More
            </button>
          </div>

          {/* Stats */}
          <div className="mt-20 pt-10 border-t border-white/20 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-4xl lg:text-5xl font-bold text-white">
                  {stat.value}{stat.suffix}
                </div>
                <p className="text-slate-200 mt-2 text-sm lg:text-base">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Curved bottom edge */}
        <div className="absolute bottom-0 left-0 right-0 z-20">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 120L60 110C120 100 240 80 360 75C480 70 600 80 720 85C840 90 960 90 1080 85C1200 80 1320 70 1380 65L1440 60V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="white"/>
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-6 lg:px-12 py-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-cyan-600 font-semibold text-sm uppercase tracking-wider bg-cyan-50 px-4 py-2 rounded-full">Why Choose Us</span>
            <h3 className="text-4xl lg:text-5xl font-bold text-slate-900 mt-4 mb-4">Powerful Features</h3>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">Comprehensive healthcare intelligence at your fingertips</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, i) => (
              <div
                key={i}
                className="group relative bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border border-slate-100"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-500`} />
                <div className="relative">
                  <div className="text-5xl mb-5 group-hover:scale-110 transition-transform duration-300 inline-block">
                    {feature.icon}
                  </div>
                  <h4 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h4>
                  <p className="text-slate-600 leading-relaxed">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="px-6 lg:px-12 py-24 bg-gradient-to-br from-slate-50 via-white to-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-cyan-600 font-semibold text-sm uppercase tracking-wider bg-cyan-50 px-4 py-2 rounded-full">Simple Process</span>
            <h3 className="text-4xl lg:text-5xl font-bold text-slate-900 mt-4 mb-4">How It Works</h3>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">Four intelligent steps to the right care</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, i) => (
              <div key={i} className="relative">
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 -right-4 w-8 h-0.5 bg-gradient-to-r from-cyan-300 to-slate-300" />
                )}
                <div className="group relative bg-white p-8 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border border-slate-100 hover:border-cyan-200">
                  <div className="absolute -top-4 -left-4 w-14 h-14 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <span className="text-white font-bold text-xl">{step.number}</span>
                  </div>
                  <div className="mt-4">
                    <h4 className="text-xl font-bold text-slate-900 mb-3 pt-4">{step.title}</h4>
                    <p className="text-slate-600 leading-relaxed">{step.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section id="technology" className="px-6 lg:px-12 py-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-800 via-slate-900 to-slate-800 p-12 text-white">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 left-0 w-72 h-72 bg-cyan-400 rounded-full filter blur-3xl" />
              <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl" />
            </div>

            <div className="relative z-10 text-center max-w-3xl mx-auto">
              <div className="inline-block mb-6 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full">
                <span className="text-cyan-300 font-semibold text-sm">🔒 Privacy-First Technology</span>
              </div>
              <h3 className="text-3xl lg:text-5xl font-bold mb-6">Local Processing, Complete Privacy</h3>
              <p className="text-lg text-slate-200 mb-10 leading-relaxed">
                All processing happens locally on your device. Your medical data never leaves your system. Powered by advanced local LLMs for complete privacy and security.
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                {['🔒 End-to-End Encrypted', '⚡ Real-time Processing', '🌐 Offline Capable', '🎯 99.9% Accurate'].map(
                  (badge, i) => (
                    <span key={i} className="px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-sm font-medium hover:bg-white/20 transition-colors">
                      {badge}
                    </span>
                  ),
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="px-6 lg:px-12 py-24 bg-gradient-to-r from-cyan-50 to-blue-50">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center mx-auto shadow-lg">
              <span className="text-3xl">⭐</span>
            </div>
          </div>
          <blockquote className="text-2xl lg:text-3xl font-medium text-slate-800 leading-relaxed">
            "MediRoute transformed how we handle patient routing. The AI is incredibly accurate and the privacy-first approach gives us complete peace of mind."
          </blockquote>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 lg:px-12 py-24 bg-white">
        <div className="max-w-3xl mx-auto text-center">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-100 via-transparent to-cyan-100 rounded-3xl blur-3xl opacity-50" />
            <div className="relative bg-white p-12 rounded-3xl shadow-xl border border-slate-100">
              <h3 className="text-3xl lg:text-5xl font-bold text-slate-900 mb-4">Ready to Get Started?</h3>
              <p className="text-lg text-slate-600 mb-8 max-w-md mx-auto">
                Begin your medical assessment today and receive intelligent routing recommendations in minutes.
              </p>
              <button
                onClick={() => navigate('/form')}
                className="group px-10 py-4 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-full font-semibold hover:shadow-xl hover:shadow-cyan-200 hover:scale-105 transition-all text-lg inline-flex items-center gap-2"
              >
                Start Your Assessment Now
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 px-6 lg:px-12 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div className="col-span-1">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🏥</span>
                <h4 className="text-xl font-bold text-white">MediRoute</h4>
              </div>
              <p className="text-slate-400 text-sm leading-relaxed">Intelligent healthcare routing powered by advanced AI agents.</p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="text-slate-400 hover:text-cyan-400 transition-colors">Features</a></li>
                <li><a href="#how-it-works" className="text-slate-400 hover:text-cyan-400 transition-colors">How it Works</a></li>
                <li><a href="#technology" className="text-slate-400 hover:text-cyan-400 transition-colors">Technology</a></li>
                <li><a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Security</h4>
              <ul className="space-y-2 text-sm">
                <li className="text-slate-400">Local Processing</li>
                <li className="text-slate-400">End-to-End Encrypted</li>
                <li className="text-slate-400">HIPAA Compliant</li>
                <li className="text-slate-400">Privacy First</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Connect</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">Twitter</a></li>
                <li><a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">LinkedIn</a></li>
                <li><a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">GitHub</a></li>
                <li><a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">Contact Us</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center text-slate-500 text-sm">
            <p>&copy; 2026 MediRoute. All rights reserved. Healthcare Intelligence Made Simple.</p>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.2; transform: scale(1); }
          50% { opacity: 0.3; transform: scale(1.05); }
        }
        .animate-pulse {
          animation: pulse 6s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .animation-delay-2000 {
          animation-delay: 3s;
        }
        html {
          scroll-behavior: smooth;
        }
      `}</style>
    </div>
  );
}