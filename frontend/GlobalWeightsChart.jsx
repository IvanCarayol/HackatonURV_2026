// GlobalWeightsChart.jsx
import React, { useState, useEffect } from 'react';
import './GlobalWeightsChart.css';
import './ShapChart.css';

export default function GlobalWeightsChart({ weightsData }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Animación de entrada
    setTimeout(() => setMounted(true), 150);
  }, []);

  const data = weightsData || [
    { feature: 'cronic', importance: 15.71 },
    { feature: 'grup_edat', importance: 12.43 },
    { feature: 'indice_fragilidad', importance: 8.90 },
    { feature: 'sexe', importance: 4.80 },
    { feature: 'altres', importance: 4.25 },
    { feature: 'diags_totals', importance: 4.18 },
    { feature: 'antiinfecciosos_per_a_us_sistemic', importance: 4.17 },
    { feature: 'organs_dels_sentits', importance: 3.81 }
  ];

  // El máximo impacto determina el 100% del ancho de la barra
  const maxImpact = Math.max(...data.map(d => d.importance), 0.01);

  return (
    <div className="shap-container">
      <h3 className="shap-header" style={{ marginBottom: '1.5rem' }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{filter: 'drop-shadow(0 0 8px rgba(168,85,247,0.5))'}}><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
        Impacte Global de les Variables
      </h3>
      
      <div className="gw-chart">
        {data.map((item, index) => {
          const targetWidth = Math.min((item.importance / maxImpact) * 100, 100);
          const currentWidth = mounted ? targetWidth : 0;
          
          return (
            <div key={index} className="gw-row" style={{ animationDelay: `${index * 0.06}s` }}>
              <div className="gw-label" title={item.feature}>
                {item.feature}
              </div>
              <div className="gw-bar-container">
                <div className="gw-bar" style={{ width: `${currentWidth}%` }}>
                  {item.importance.toFixed(2)}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
