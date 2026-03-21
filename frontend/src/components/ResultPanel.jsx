import './ResultPanel.css'

export default function ResultPanel({ data }) {
  // Manejo de la estructura de /analyze o la estructura directa de /predict
  const isFullAnalyze = !!data.predictive_analysis

  const risk_score = isFullAnalyze
    ? data.predictive_analysis.mortalidad_riesgo_anual
    : (data.mortalidad_riesgo_anual || data.risk_score_5y || 0)

  const narrative = isFullAnalyze ? data.narrative_report : data.analysis
  const medical_data = isFullAnalyze ? data.extracted_medical_data : null
  const predictions = isFullAnalyze ? data.predictive_analysis : data

  const level = risk_score < 10 ? 'low' : risk_score < 30 ? 'med' : 'high'
  const levelLabel = { low: 'Bajo', med: 'Moderado', high: 'Alto' }[level]

  const speakReport = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(narrative);
    utterance.lang = 'es-ES';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }

  return (
    <div className="result-panel">

      <div className="result-header">
        <div>
          <p className="result-label">Riesgo de Mortalidad (Anual)</p>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '15px' }}>
            <p className="result-score">{risk_score}%</p>
            <button
              onClick={speakReport}
              style={{ background: 'var(--secondary)', color: 'white', border: 'none', borderRadius: '50%', width: '36px', height: '36px', cursor: 'pointer' }}
              title="Escuchar análisis (Inclusión)"
            >
              🔊
            </button>
          </div>
        </div>
        <span className={`risk-badge risk-badge--${level}`}>{levelLabel}</span>
      </div>

      <div className="risk-bar-wrap">
        <div
          className={`risk-bar risk-bar--${level}`}
          style={{ width: `${Math.min(risk_score, 100)}%` }}
        />
      </div>

      {predictions.mortalidad_riesgo_anual !== undefined && (
        <>
          <p className="section-label">Predicciones Clínicas (Modelos ML)</p>
          <div className="timeline">
            <div className="timeline-node">
              <span className="timeline-pct">{predictions.visitas_urgencias_estimadas_mes}</span>
              <span className="timeline-yr">Urgencias / Mes</span>
              <div className={`timeline-bar timeline-bar--${predictions.visitas_urgencias_estimadas_mes > 0.15 ? 'med' : 'low'}`} />
            </div>
            <div className="timeline-node">
              <span className="timeline-pct">{predictions.probabilidad_perfil_pcc}%</span>
              <span className="timeline-yr">Perfil PCC</span>
              <div className={`timeline-bar timeline-bar--${predictions.probabilidad_perfil_pcc > 50 ? 'high' : 'low'}`} />
            </div>
          </div>
        </>
      )}

      {isFullAnalyze && medical_data && (
        <>
          <p className="section-label">Fisiopatología Detectada (Extracción LLM)</p>
          <div className="factors-grid">
            {Object.entries(medical_data).map(([key, value], i) => {
              // Solo mostrar campos con valor relevante
              if (value === 0 || value === 'No' || value === 'No indicado' || value === 'Desconocido') return null
              return (
                <div key={i} className="factor-card">
                  <span className="factor-name">{key.replace(/_/g, ' ')}</span>
                  <span className="factor-val">{value}</span>
                </div>
              )
            })}
          </div>
        </>
      )}

      {narrative && (
        <>
          <p className="section-label">Análisis Narrativo (Generado por IA)</p>
          <div className="analysis-box">
            {narrative.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </>
      )}

      {/* NUEVA SECCIÓN DE INCLUSIÓN Y GÉNERO */}
      <div className="inclusion-section" style={{
        marginTop: '25px',
        padding: '15px',
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(168, 85, 247, 0.05))',
        border: '1px solid rgba(139, 92, 246, 0.1)',
        borderRadius: '12px'
      }}>
        <p className="section-label" style={{ color: '#7c3aed', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
          Perspectiva de Inclusión y Equidad
        </p>
        <div style={{ fontSize: '0.9rem', color: '#4b5563', lineHeight: '1.5' }}>
          <p>
            <strong>Género:</strong> Este análisis integra variables de género para detectar sesgos clínicos habituales.
            {medical_data?.Sexo === 'Mujer' && " Se recomienda especial atención a síntomas atípicos en patología cardiovascular."}
          </p>
          <p style={{ marginTop: '10px' }}>
            <strong>Determinantes Sociales:</strong> La {risk_score > 30 ? 'alta' : 'moderada'} probabilidad de riesgo detectada sugiere
            la revisión del <strong>apoyo social</strong>. {risk_score > 50 ? "Se recomienda derivación proactiva a trabajador/a social para evaluar soledad no deseada o barreras de acceso." : "Mantener vigilancia sobre el entorno familiar del paciente."}
          </p>
        </div>
      </div>

    </div>
  )
}

