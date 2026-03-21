import React, { useState } from 'react'
import './Login.css' // Reutilizamos estilos de login para consistencia

export default function CitizenStatus({ onBack }) {
  const [ticketId, setTicketId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [statusData, setStatusData] = useState(null)

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080'

  async function handleSearch(e) {
    e.preventDefault()
    if (!ticketId.trim()) return
    
    setLoading(true)
    setError(null)
    setStatusData(null)

    try {
      const res = await fetch(`${API_BASE}/patient/${ticketId.trim()}`)
      if (!res.ok) {
          throw new Error("No se ha encontrado ninguna petición con este ID.")
      }
      const data = await res.json()
      setStatusData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container" style={{maxWidth: '500px'}}>
      <div className="login-header">
        <h2>Consulta de Estado del Ticket</h2>
        <p>Introduzca el identificador de su consulta para ver si ha sido revisada por un facultativo.</p>
      </div>

      <form className="login-form" onSubmit={handleSearch}>
        <div className="field">
          <label>Identificador del Ticket (ID)</label>
          <input
            type="text" 
            placeholder="Ex: 1, 2, 3..."
            value={ticketId} 
            onChange={(e) => setTicketId(e.target.value)} 
            required
          />
        </div>
        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Consultando...' : 'Consultar Estado'}
        </button>
      </form>

      {error && <div className="login-error" style={{marginTop: '20px'}}>⚠️ {error}</div>}

      {statusData && (
        <div style={{marginTop: '30px', padding: '20px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)'}}>
          <h3 style={{marginTop: 0, color: 'var(--primary)'}}>Resumen de la Consulta</h3>
          <p><strong>Código:</strong> #{statusData.id}</p>
          
          <div style={{display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px'}}>
            <StatusItem 
                label="Auditoría de Cronicidad" 
                val={statusData.tratado_auditor} 
            />
            <StatusItem 
                label="Previsión de Urgencias" 
                val={statusData.tratado_previsor} 
            />
            <StatusItem 
                label="Análisis de Riesgo" 
                val={statusData.tratado_risc} 
            />
          </div>
        </div>
      )}

      <div className="login-footer">
        <span className="back-link" onClick={onBack}>
          &larr; Volver al Inicio
        </span>
      </div>
    </div>
  )
}

function StatusItem({ label, val }) {
    let statusText = "Pendiente de revisión";
    let color = "#718096";
    let icon = "⏳";

    if (val === 1) {
        statusText = "Validado por facultativo";
        color = "#48bb78";
        icon = "✅";
    } else if (val === -1) {
        statusText = "Revisado (Previsión Rechazada)";
        color = "#f56565";
        icon = "🩺";
    }

    return (
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px'}}>
            <span style={{fontSize: '0.9rem'}}>{label}</span>
            <span style={{color, fontWeight: 'bold', fontSize: '0.85rem'}}>{icon} {statusText}</span>
        </div>
    )
}
