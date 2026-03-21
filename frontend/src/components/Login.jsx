import React, { useState } from 'react'
import './Login.css'

export default function Login({ onLoginSuccess, onBack }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    center: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8080'

  function handleChange(e) {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const submissionData = {
      username: formData.username.trim(),
      password: formData.password.trim(),
      center: formData.center.trim()
    }

    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submissionData)
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error en la autenticación')

      // Redirigir a vista.html al tener éxito
      window.location.href = '/vista.html'
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-header">
        <h2>Área de Facultativos</h2>
        <p>Valide su identidad profesional para acceder al panel avanzado.</p>
      </div>

      {error && <div className="login-error">⚠️ {error}</div>}

      <form className="login-form" onSubmit={handleSubmit}>
        <div className="field">
          <label>Nombre del Médico</label>
          <input
            type="text" name="username" placeholder="F. Apellido"
            value={formData.username} onChange={handleChange} required
          />
        </div>

        <div className="field">
          <label>Contraseña</label>
          <input
            type="password" name="password" placeholder="••••••••"
            value={formData.password} onChange={handleChange} required
          />
        </div>

        <div className="field">
          <label>Centro Médico</label>
          <input
            type="text" name="center" placeholder=" HOSPITAL JOAN XXIII"
            value={formData.center} onChange={handleChange} required
          />
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Validando...' : 'Acceder al Panel'}
        </button>
      </form>

      <div className="login-footer">
        <span className="back-link" onClick={onBack}>
          &larr; Volver a Selección de Área
        </span>
      </div>
    </div>
  )
}
