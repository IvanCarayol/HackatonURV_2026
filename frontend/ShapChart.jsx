import React, { useState, useEffect } from 'react';
import './ShapChart.css';

/**
 * Componente Aislado para visualizar la Explicabilidad de la IA (SHAP Values)
 * Tu compañero de Frontend solo tiene que hacer:
 * <ShapChart shapData={tuArrayDeDatos} baseRisk={15.2} />
 */
export default function ShapChart({ shapData, baseRisk }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Animación fluida al cargar
    setTimeout(() => setMounted(true), 150);
  }, []);

  // Si no le pasan datos, usa un mock para que tu compañero vea cómo queda
  const data = shapData || [
    { feature: 'Pacient Crònic Complex (PCC)', impact: 0.82, type: 'positive' },
    { feature: 'Malaltia Sist. Nerviós (2)', impact: 0.45, type: 'positive' },
    { feature: 'Grup Edat (80-84 anys)', impact: 0.35, type: 'positive' },
    { feature: 'Fàrmacs Actius (8 totals)', impact: 0.22, type: 'positive' },
    { feature: 'Sexe (Dona)', impact: -0.15, type: 'negative' },
    { feature: 'Antiinfecciosos Prescrits (0)', impact: -0.18, type: 'negative' },
    { feature: 'Índex de Fragilitat (12)', impact: -0.25, type: 'negative' }
  ];

  // Buscamos el impacto máximo para escalar las barras (el 100% del ancho)
  const maxAbsImpact = Math.max(...data.map(d => Math.abs(d.impact)), 0.01);

  return (
    <div className="shap-container">
      <h3 className="shap-header">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{color: '#38bdf8', filter: 'drop-shadow(0 0 8px rgba(56,189,248,0.5))'}}><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        Radiografia de Risc Clínic Avançada
      </h3>
      
      <div className="shap-chart">
        <div className="shap-axis"></div>
        
        {data.map((item, index) => {
          // Calculamos el % de ancho respecto al impacto máximo (limitado a 100% por diseño)
          const targetWidth = Math.min((Math.abs(item.impact) / maxAbsImpact) * 100, 100);
          const currentWidth = mounted ? targetWidth : 0;
          
          return (
            <div key={index} className="shap-row" style={{ animationDelay: `${index * 0.08}s` }}>
              {/* Lado Izquierdo: Factores que BAJAN el riesgo (Azules) */}
              <div className="shap-side shap-side-left">
                {item.impact < 0 && (
                  <div className="shap-bar shap-bar-negative" style={{ width: `${currentWidth}%` }}>
                    <span className="shap-label shap-label-left">
                      {item.feature}
                    </span>
                    {item.impact.toFixed(2)}
                  </div>
                )}
              </div>

              {/* Lado Derecho: Factores que SUBEN el riesgo (Rojos) */}
              <div className="shap-side shap-side-right">
                {item.impact > 0 && (
                  <div className="shap-bar shap-bar-positive" style={{ width: `${currentWidth}%` }}>
                    <span className="shap-label shap-label-right">
                      {item.feature}
                    </span>
                    +{item.impact.toFixed(2)}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="shap-legend">
        <div className="shap-legend-item">
          <div className="shap-dot shap-dot-negative"></div>
          <span>Redueix el Risc</span>
        </div>
        {baseRisk !== undefined && (
          <div className="shap-legend-center">
            Risc Base (Tweedie): {baseRisk}%
          </div>
        )}
        <div className="shap-legend-item">
          <div className="shap-dot shap-dot-positive"></div>
          <span>Augmenta el Risc</span>
        </div>
      </div>
    </div>
  );
}
