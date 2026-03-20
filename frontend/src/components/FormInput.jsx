import { useState } from 'react'
import { predictFromForm } from '../services/api' // Asegúrate de que esta ruta es correcta
import './FormInput.css';

const initialForm = {
  sexo: 'M',
  edad: '',
  es_cronico: 'no',
  es_pcc: 'no',
  es_maca: 'no',
  diagnosticos: '',
  problemas_agudos: '',
  total_farmacos: '',
  visitas_urgencias: '',
  hospitalizaciones: '',
  visitas_primaria: '',
}

export default function FormInput({ onResult }) {
  const [form, setForm] = useState(initialForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function handleChange(e) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    
    try {
      // Convertimos los valores a números donde sea necesario para el árbol de decisión
      const payload = {
        ...form,
        edad: parseInt(form.edad),
        total_farmacos: parseInt(form.total_farmacos || 0),
        visitas_urgencias: parseInt(form.visitas_urgencias || 0),
        hospitalizaciones: parseInt(form.hospitalizaciones || 0),
        visitas_primaria: parseInt(form.visitas_primaria || 0),
        // Convertimos los 'si'/'no' a booleanos por si tu compañero lo prefiere así en Python
        es_cronico: form.es_cronico === 'si',
        es_pcc: form.es_pcc === 'si',
        es_maca: form.es_maca === 'si'
      }

      const result = await predictFromForm(payload)
      onResult(result)
    } catch (err) {
      setError('No se pudo conectar con la API. Comprueba que el servidor está activo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="form-panel" onSubmit={handleSubmit}>

      {/* SECCIÓN 1: Datos Demográficos */}
      <div className="form-section">
        <h3>Datos Demográficos</h3>
        <div className="form-row">
          <div className="field">
            <label>Edad</label>
            <input
              type="number" name="edad" min="0" max="120"
              placeholder="Ej: 65" value={form.edad}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Sexo</label>
            <select name="sexo" value={form.sexo} onChange={handleChange}>
              <option value="M">Hombre</option>
              <option value="F">Mujer</option>
            </select>
          </div>
        </div>
      </div>

      {/* SECCIÓN 2: Perfil de Cronicidad */}
      <div className="form-section">
        <h3>Perfil de Cronicidad</h3>
        <div className="form-row">
          <div className="field">
            <label>¿Paciente Crónico?</label>
            <select name="es_cronico" value={form.es_cronico} onChange={handleChange}>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
          <div className="field">
            <label>Paciente PCC (Complejo)</label>
            <select name="es_pcc" value={form.es_pcc} onChange={handleChange}>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
          <div className="field">
            <label>Paciente MACA (Avanzado)</label>
            <select name="es_maca" value={form.es_maca} onChange={handleChange}>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
        </div>
      </div>

      {/* SECCIÓN 3: Historial Médico */}
      <div className="form-section">
        <h3>Historial Médico</h3>
        <div className="form-row">
          <div className="field field--wide">
            <label>Diagnósticos realizados (separados por coma)</label>
            <input
              type="text" name="diagnosticos"
              placeholder="Ej: Hipertensión, Diabetes Tipo 2..." 
              value={form.diagnosticos}
              onChange={handleChange} required
            />
          </div>
          <div className="field field--wide">
            <label>Problemas de salud agudos recientes</label>
            <input
              type="text" name="problemas_agudos"
              placeholder="Ej: Neumonía, Fractura de cadera..." 
              value={form.problemas_agudos}
              onChange={handleChange}
            />
          </div>
        </div>
      </div>

      {/* SECCIÓN 4: Uso de Recursos Asistenciales */}
      <div className="form-section">
        <h3>Uso de Recursos Asistenciales (Último año)</h3>
        <div className="form-row">
          <div className="field">
            <label>Fármacos recetados (Total)</label>
            <input
              type="number" name="total_farmacos" min="0"
              placeholder="Ej: 5" value={form.total_farmacos}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Visitas a Urgencias</label>
            <input
              type="number" name="visitas_urgencias" min="0"
              placeholder="Ej: 2" value={form.visitas_urgencias}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Hospitalizaciones</label>
            <input
              type="number" name="hospitalizaciones" min="0"
              placeholder="Ej: 1" value={form.hospitalizaciones}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Visitas Atención Primaria</label>
            <input
              type="number" name="visitas_primaria" min="0"
              placeholder="Ej: 6" value={form.visitas_primaria}
              onChange={handleChange} required
            />
          </div>
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? 'Procesando Árbol de Decisión...' : 'Calcular Riesgo de Mortalidad'}
      </button>

    </form>
  )
}