import React from 'react'

export default function DoctorArea({ doctorData, onLogout }) {
  return (
    <div style={{maxWidth: '800px', margin: '4rem auto', padding: '2rem', background: 'white', borderRadius: '12px', boxShadow: 'var(--shadow-lg)'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
        <div>
          <h2 style={{margin: 0, color: 'var(--header-bg)'}}>Panel Médico Avanzado</h2>
          <p style={{margin: 0, color: 'var(--text-muted)'}}>{doctorData.message}</p>
        </div>
        <button 
          onClick={onLogout} 
          style={{background: 'var(--danger)', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer'}}
        >
          Cerrar Sesión
        </button>
      </div>

      <div style={{background: '#f8fafc', padding: '2rem', borderRadius: '8px', border: '1px solid var(--border)', textAlign: 'center'}}>
        <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{color: 'var(--primary)', marginBottom: '1rem'}}>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>
          <path d="m9 12 2 2 4-4"/>
        </svg>
        <h3>Acceso Concedido</h3>
        <p>Este panel le permite acceder a historiales clínicos compartidos y herramientas de monitoreo PCC/MACA en tiempo real.</p>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '2rem'}}>
            <div style={{background: 'white', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)'}}>
                <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--primary)'}}>12</div>
                <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Pacientes en Seguimiento</div>
            </div>
            <div style={{background: 'white', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)'}}>
                <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--warning)'}}>3</div>
                <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Alertas Pendientes</div>
            </div>
            <div style={{background: 'white', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)'}}>
                <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)'}}>JoanXXIII</div>
                <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Centro Médico</div>
            </div>
        </div>
      </div>
    </div>
  )
}
