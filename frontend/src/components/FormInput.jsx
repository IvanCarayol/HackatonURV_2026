import { useState } from 'react'
import { predictFromForm } from '../services/api'
import './FormInput.css';

const initialForm = {
  age: '',
  sex: 'M',
  bmi: '',
  diagnosis: 'heart_failure',
  systolic_bp: '',
  creatinine: '',
  hemoglobin: '',
  fasting_glucose: '',
  comorbidities: '0',
  smoker: 'no',
  horizon_years: '5',
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
      const result = await predictFromForm({
        ...form,
        age: parseInt(form.age),
        bmi: parseFloat(form.bmi),
        systolic_bp: parseInt(form.systolic_bp),
        creatinine: parseFloat(form.creatinine),
        hemoglobin: parseFloat(form.hemoglobin),
        fasting_glucose: parseInt(form.fasting_glucose),
        comorbidities: parseInt(form.comorbidities),
        horizon_years: parseInt(form.horizon_years),
      })
      onResult(result)
    } catch (err) {
      setError('No se pudo conectar con la API. Comprueba que el servidor está activo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="form-panel" onSubmit={handleSubmit}>

      <div className="form-section">
        <h3>Datos del paciente</h3>
        <div className="form-row">
          <div className="field">
            <label>Edad</label>
            <input
              type="number" name="age" min="0" max="120"
              placeholder="65" value={form.age}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Sexo</label>
            <select name="sex" value={form.sex} onChange={handleChange}>
              <option value="M">Masculino</option>
              <option value="F">Femenino</option>
            </select>
          </div>
          <div className="field">
            <label>IMC (kg/m²)</label>
            <input
              type="number" name="bmi" step="0.1" min="10" max="70"
              placeholder="27.5" value={form.bmi}
              onChange={handleChange} required
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Diagnóstico</h3>
        <div className="form-row">
          <div className="field field--wide">
            <label>Diagnóstico principal</label>
            <select name="diagnosis" value={form.diagnosis} onChange={handleChange}>
              <option value="heart_failure">Insuficiencia cardíaca</option>
              <option value="copd">EPOC</option>
              <option value="diabetes_t2">Diabetes tipo 2</option>
              <option value="ckd">Enfermedad renal crónica</option>
              <option value="cancer">Neoplasia maligna</option>
              <option value="other">Otro</option>
            </select>
          </div>
          <div className="field">
            <label>Comorbilidades</label>
            <select name="comorbidities" value={form.comorbidities} onChange={handleChange}>
              <option value="0">Ninguna</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3 o más</option>
            </select>
          </div>
          <div className="field">
            <label>Fumador</label>
            <select name="smoker" value={form.smoker} onChange={handleChange}>
              <option value="no">No</option>
              <option value="ex">Ex-fumador</option>
              <option value="yes">Sí</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Parámetros clínicos</h3>
        <div className="form-row">
          <div className="field">
            <label>Presión sistólica (mmHg)</label>
            <input
              type="number" name="systolic_bp"
              placeholder="120" value={form.systolic_bp}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Creatinina (mg/dL)</label>
            <input
              type="number" name="creatinine" step="0.1"
              placeholder="1.0" value={form.creatinine}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Hemoglobina (g/dL)</label>
            <input
              type="number" name="hemoglobin" step="0.1"
              placeholder="13.5" value={form.hemoglobin}
              onChange={handleChange} required
            />
          </div>
          <div className="field">
            <label>Glucosa en ayunas (mg/dL)</label>
            <input
              type="number" name="fasting_glucose"
              placeholder="100" value={form.fasting_glucose}
              onChange={handleChange} required
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Horizonte de predicción</h3>
        <div className="form-row">
          <div className="field">
            <label>Años vista</label>
            <select name="horizon_years" value={form.horizon_years} onChange={handleChange}>
              <option value="1">1 año</option>
              <option value="2">2 años</option>
              <option value="3">3 años</option>
              <option value="5">5 años</option>
              <option value="10">10 años</option>
            </select>
          </div>
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? 'Analizando...' : 'Calcular riesgo'}
      </button>

    </form>
  )
}
