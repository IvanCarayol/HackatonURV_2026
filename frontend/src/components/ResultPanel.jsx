export default function ResultPanel({ data }) {
  const { risk_score_5y, timeline, risk_factors, analysis } = data

  const level = risk_score_5y < 20 ? 'low' : risk_score_5y < 50 ? 'med' : 'high'
  const levelLabel = { low: 'Bajo', med: 'Moderado', high: 'Alto' }[level]

  return (
    <div className="result-panel">

      <div className="result-header">
        <div>
          <p className="result-label">Riesgo de mortalidad a 5 años</p>
          <p className="result-score">{risk_score_5y}%</p>
        </div>
        <span className={`risk-badge risk-badge--${level}`}>{levelLabel}</span>
      </div>

      <div className="risk-bar-wrap">
        <div
          className={`risk-bar risk-bar--${level}`}
          style={{ width: `${risk_score_5y}%` }}
        />
      </div>

      {timeline && (
        <>
          <p className="section-label">Evolución temporal</p>
          <div className="timeline">
            {timeline.map(t => {
              const l = t.pct < 20 ? 'low' : t.pct < 50 ? 'med' : 'high'
              return (
                <div key={t.year} className="timeline-node">
                  <span className="timeline-pct">{t.pct}%</span>
                  <span className="timeline-yr">{t.year} año{t.year > 1 ? 's' : ''}</span>
                  <div className={`timeline-bar timeline-bar--${l}`} />
                </div>
              )
            })}
          </div>
        </>
      )}

      {risk_factors && (
        <>
          <p className="section-label">Factores detectados</p>
          <div className="factors-grid">
            {risk_factors.map((f, i) => (
              <div key={i} className="factor-card">
                <span className="factor-name">{f.name}</span>
                <span className={`factor-val factor-val--${f.level}`}>{f.value}</span>
              </div>
            ))}
          </div>
        </>
      )}

      {analysis && (
        <>
          <p className="section-label">Análisis del modelo</p>
          <div className="analysis-box">
            {analysis.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </>
      )}

    </div>
  )
}
