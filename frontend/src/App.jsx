import { useState, useEffect } from 'react'
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

  // ESTADO DE ACCESIBILIDAD UNIVERSAL
  const [contrast, setContrast] = useState(false)
  const [largeText, setLargeText] = useState(false)
  const [dyslexic, setDyslexic] = useState(false)

  useEffect(() => {
    // Sincronizar clases globales para accesibilidad plena
    document.body.className = ''
    if (contrast) document.body.classList.add('high-contrast')
    if (largeText) document.body.classList.add('large-text')
    if (dyslexic) document.body.classList.add('dyslexic-font')
  }, [contrast, largeText, dyslexic])

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

  const renderAccessibilityPanel = () => (
    <div className="accessibility-center" style={{
      position: 'fixed', bottom: '25px', left: '25px', zIndex: 9999,
      background: 'var(--card-bg)', border: '2px solid var(--primary)',
      borderRadius: '16px', padding: '10px', boxShadow: 'var(--shadow-lg)',
      display: 'flex', flexDirection: 'column', gap: '8px'
    }}>
      <button onClick={() => setContrast(!contrast)} title="Alto Contraste" style={{ padding: '10px', borderRadius: '10px', border: 'none', background: '#000', color: '#fff', cursor: 'pointer', fontSize: '1.2rem' }}>🌓</button>
      <button onClick={() => setLargeText(!largeText)} title="Texto Grande" style={{ padding: '10px', borderRadius: '10px', border: 'none', background: '#f0f0f0', color: '#000', cursor: 'pointer', fontSize: '1.2rem', fontWeight: 'bold' }}>A+</button>
      <button onClick={() => setDyslexic(!dyslexic)} title="Fuente Lectura Fácil" style={{ padding: '10px', borderRadius: '10px', border: 'none', background: '#3498db', color: '#fff', cursor: 'pointer', fontSize: '1.2rem' }}>📖</button>
    </div>
  );

  const renderContent = () => {
    if (view === 'home') {
      return (
        <>
          <Home onNavigate={navigateTo} />
          <footer style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            &copy; 2026 MedRisk Pro - Sistema de Soporte Clínico
          </footer>
        </>
      )
    }

    if (view === 'login') {
      return (
        <Login
          onLoginSuccess={handleLoginSuccess}
          onBack={() => navigateTo('home')}
        />
      )
    }

    if (view === 'doctor_dashboard') {
      return (
        <DoctorDashboard
          doctorData={doctorInfo}
          onLogout={() => navigateTo('home')}
        />
      )
    }

    if (view === 'citizen_status') {
      return <CitizenStatus onBack={() => navigateTo('home')} />
    }

    // Default view (Predictor)
    return (
      <>
        <header className="app-header">
          <div style={{ cursor: 'pointer' }} onClick={() => navigateTo('home')}>
            <h1>
              MedRisk <span style={{ fontWeight: 300 }}>Pro</span>
            </h1>
          </div>
          <p>Plataforma avanzada de análisis de riesgo clínico y soporte a la decisión médica basada en IA.</p>
          <button
            onClick={() => navigateTo('home')}
            style={{ marginTop: '1.5rem', background: 'rgba(255,255,255,0.1)', color: 'white', border: '1px solid rgba(255,255,255,0.2)', padding: '8px 16px' }}
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
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21 15-3-3 3-3" /><path d="M15 12H3" /><path d="M10 18H3" /><path d="M10 6H3" /></svg>
              Análisis de Texto
            </button>
            <button
              className={mode === 'form' ? 'active' : ''}
              onClick={() => { setMode('form'); setResult(null) }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" /><rect x="8" y="2" width="8" height="4" rx="1" ry="1" /></svg>
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

        <footer style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.9rem', borderTop: '1px solid var(--border)' }}>
          &copy; 2026 MedRisk Pro - Sistema de Soporte Clínico
        </footer>
      </>
    )
  }

  return (
    <div className="app">
      {renderContent()}
      {renderAccessibilityPanel()}
    </div>
  )
}


