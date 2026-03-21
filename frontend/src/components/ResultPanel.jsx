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

  return (
    <div className="result-panel">

      <div className="result-header">
        <div>
          <p className="result-label">Riesgo de Mortalidad (Anual)</p>
          <p className="result-score">{risk_score}%</p>
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
          <p className="section-label">Predicciones Proyectadas (Motor Árboles)</p>
          <div className="timeline">
             <div className="timeline-node">
                <span className="timeline-pct">{predictions.visitas_urgencias_estimadas_mes}</span>
                <span className="timeline-yr">Urgencias/Mes</span>
                <div className={`timeline-bar timeline-bar--${predictions.visitas_urgencias_estimadas_mes > 0.15 ? 'med' : 'low'}`} />
             </div>
             <div className="timeline-node">
                <span className="timeline-pct">{predictions.probabilidad_perfil_pcc}%</span>
                <span className="timeline-yr">Probabilidad PCC</span>
                <div className={`timeline-bar timeline-bar--${predictions.probabilidad_perfil_pcc > 50 ? 'high' : 'low'}`} />
             </div>
          </div>
        </>
      )}

      {isFullAnalyze && medical_data && (
        <>
          <p className="section-label">Fisiopatología Detectada (LLM Extraction)</p>
          <div className="factors-grid">
            {Object.entries(medical_data).map(([key, value], i) => {
              // Solo mostrar campos con valor relevante
              if (value === 0 || value === 'No' || value === 'No indicado') return null
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
          <p className="section-label">Evaluación Médica (IA Summarizer)</p>
          <div className="analysis-box">
            {narrative.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </>
      )}

    </div>
  )
}

