import React from 'react'
import './Home.css'

export default function Home({ onNavigate }) {
  return (
    <div className="home-container">
      <section className="hero-section">
        <h1>MedRisk <span style={{fontWeight: 300}}>Pro</span></h1>
        <p>
          Sistema avanzado de soporte a la decisión clínica. Nuestra plataforma utiliza algoritmos 
          de inteligencia artificial para la detección precoz del riesgo de mortalidad y gestión de cronicidad compleja.
        </p>
      </section>

      <section className="cards-grid">
        <div className="home-card">
          <div className="card-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <h2>Área Médica Profesional</h2>
          <p>
            Herramientas exclusivas para facultativos. Registre diagnósticos persistentes, realice seguimiento de pacientes crónicos (PCC/MACA) y gestione historiales clínicos compartidos.
          </p>
          <button onClick={() => onNavigate('login')}>
            Registrarse como Médico
          </button>
        </div>

        <div className="home-card">
          <div className="card-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
          </div>
          <h2>Análisis Clínico Libre</h2>
          <p>
            Realice una estimación de riesgo instantánea utilizando lenguaje natural o nuestro cuestionario técnico optimizado para la atención primaria y urgencias.
          </p>
          <button onClick={() => onNavigate('predictor')}>
            Empezar Consulta
          </button>
        </div>

        <div className="home-card">
          <div className="card-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
              <path d="M9 12h6"/>
              <path d="M9 16h6"/>
              <path d="M12 8h.01"/>
            </svg>
          </div>
          <h2>Consulta d'Estat (Ticket)</h2>
          <p>
            Vegi l'estat de les seves peticions generades. Introduint el seu identificador de ticket, podrà comprovar si la nostra IA i els metges han revisat el seu cas.
          </p>
          <button onClick={() => onNavigate('citizen_status')}>
            Comprovar Estat
          </button>
        </div>
      </section>

      <section className="info-section">
        <div className="info-text">
          <h3>Soporte Clínico Inteligente</h3>
          <p>
            Utilizamos modelos de IA avanzados para monitorizar la cronicidad avanzada (MACA) y pacientes crónicos complejos (PCC). Ayudamos a optimizar recursos en atención primaria.
          </p>
          <ul className="feature-list">
            <li>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
              Predicción de Riesgo de Mortalidad a 5 años
            </li>
            <li>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
              Extracción Inteligente desde Historia Clínica
            </li>
            <li>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
              Soporte para Pacientes PCC y MACA
            </li>
          </ul>
        </div>
        <div className="info-visual">
          <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v20M2 12h20M7 7l10 10M17 7L7 17"/>
          </svg>
        </div>
      </section>
    </div>
  )
}
