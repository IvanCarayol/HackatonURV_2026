import { useState } from 'react'
import Home from './components/Home'
import Login from './components/Login'
import DoctorDashboard from './components/DoctorDashboard'
import FormInput from './components/FormInput'
import ChatInput from './components/ChatInput'
import ResultPanel from './components/ResultPanel'
import CitizenStatus from './components/CitizenStatus'
import './App.css'

export default function App() {
  const [view, setView] = useState('home') // 'home', 'login', 'doctor_dashboard', 'predictor'
  const [mode, setMode] = useState('chat')
  const [result, setResult] = useState(null)
  const [doctorInfo, setDoctorInfo] = useState(null)

  function handleResult(data) {
    setResult(data)
    setTimeout(() => {
      document.getElementById('result')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  function navigateTo(target) {
    setView(target)
    setResult(null)
    window.scrollTo(0, 0)
  }

  function handleLoginSuccess(info) {
    setDoctorInfo(info)
    setView('doctor_dashboard')
  }

  if (view === 'home') {
    return (
      <div className="app">
        <Home onNavigate={navigateTo} />
        <footer style={{textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-muted)', fontSize: '0.9rem'}}>
          &copy; 2026 MedRisk Pro - Sistema de Soporte Clínico
        </footer>
      </div>
    )
  }

  if (view === 'login') {
    return (
      <div className="app">
        <Login 
          onLoginSuccess={handleLoginSuccess}
          onBack={() => navigateTo('home')}
        />
      </div>
    )
  }

  if (view === 'doctor_dashboard') {
    return (
      <div className="app">
        <DoctorDashboard 
          doctorData={doctorInfo}
          onLogout={() => navigateTo('home')}
        />
      </div>
    )
  }

  if (view === 'citizen_status') {
    return (
      <div className="app">
        <CitizenStatus onBack={() => navigateTo('home')} />
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <div style={{cursor: 'pointer'}} onClick={() => navigateTo('home')}>
          <h1>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              <path d="M12 5v14" />
              <path d="M5 12h14" />
            </svg>
            MedRisk <span style={{fontWeight: 300}}>Pro</span>
          </h1>
        </div>
        <p>Plataforma avanzada de análisis de riesgo clínico y soporte a la decisión médica basaba en IA.</p>
        <button 
          onClick={() => navigateTo('home')} 
          style={{marginTop: '1.5rem', background: 'rgba(255,255,255,0.1)', color: 'white', border: '1px solid rgba(255,255,255,0.2)', padding: '8px 16px'}}
        >
          &larr; Volver al Inicio
        </button>
      </header>

      <main className="main-content">
        <div className="mode-toggle">
          <button
            className={mode === 'chat' ? 'active' : ''}
            onClick={() => { setMode('chat'); setResult(null) }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21 15-3-3 3-3"/><path d="M15 12H3"/><path d="M10 18H3"/><path d="M10 6H3"/></svg>
            Análisis de Texto
          </button>
          <button
            className={mode === 'form' ? 'active' : ''}
            onClick={() => { setMode('form'); setResult(null) }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
            Cuestionario Técnico
          </button>
        </div>

        <div className="content-card">
          {mode === 'chat'
            ? <ChatInput onResult={handleResult} />
            : <FormInput onResult={handleResult} />
          }
        </div>

        {result && (
          <div id="result">
            <ResultPanel data={result} />
          </div>
        )}
      </main>
      
      <footer style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.9rem', borderTop: '1px solid var(--border)'}}>
        &copy; 2026 MedRisk Pro - Sistema de Soporte Clínico
      </footer>
    </div>
  )
}


