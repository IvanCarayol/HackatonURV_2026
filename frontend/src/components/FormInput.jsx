import { useState } from 'react'
import { predictFromForm } from '../services/api'
import './FormInput.css';

const initialForm = {
  // Datos básicos
  sexo: 'M',
  edad: '',
  
  // Cronicidad
  es_cronico: 'no_se',
  tipo_cronico: 'ninguno',
  
  // Diagnósticos
  total_diagnosticos: '',
  problemas_agudos: '',
  problemas_cronicos: '',
  neoplasia_maligna: '',
  
  // Visitas
  visitas_primaria: '',
  visitas_urgencias: '',
  hospitalizaciones: '',
  
  // Fármacos generales
  total_farmacos: '',
  
  // Fármacos específicos
  toma_cardio_digestivo: 'no_se',
  toma_nervios_musculo: 'no_se',
  toma_infecciosos: 'no_se',
  toma_quimio_sangre: 'no_se',
  
  // Fármacos específicos (Cantidades)
  farmacos_cardiovascular: '',
  farmacos_digestivo: '',
  farmacos_musculoesqueletic: '',
  farmacos_nervios: '',
  farmacos_antiinfecciosos: '',
  farmacos_quimio: '',
  farmacos_sangre: '',
  farmacos_respiratori: '',
  farmacos_sentits: ''
}

export default function FormInput({ onResult }) {
  const [form, setForm] = useState(initialForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function handleChange(e) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  // Función de ayuda para enviar null si el campo está vacío, en lugar de 0
  const parseNumber = (value) => value === '' ? null : parseInt(value);

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    
    try {
      const payload = {
        sexo: form.sexo,
        edad: parseNumber(form.edad),
        
        // Enviamos el string literal ('si', 'no', 'no_se') para que el árbol de decisión lo procese
        es_cronico: form.es_cronico,
        tipo_cronico: form.tipo_cronico,
        
        total_diagnosticos: parseNumber(form.total_diagnosticos),
        problemas_agudos: parseNumber(form.problemas_agudos),
        problemas_cronicos: parseNumber(form.problemas_cronicos),
        neoplasia_maligna: parseNumber(form.neoplasia_maligna),
        
        visitas_primaria: parseNumber(form.visitas_primaria),
        visitas_urgencias: parseNumber(form.visitas_urgencias),
        hospitalizaciones: parseNumber(form.hospitalizaciones),
        
        total_farmacos: parseNumber(form.total_farmacos),
        
        farmacos_cardiovascular: parseNumber(form.farmacos_cardiovascular),
        farmacos_digestivo: parseNumber(form.farmacos_digestivo),
        farmacos_musculoesqueletic: parseNumber(form.farmacos_musculoesqueletic),
        farmacos_nervios: parseNumber(form.farmacos_nervios),
        farmacos_antiinfecciosos: parseNumber(form.farmacos_antiinfecciosos),
        farmacos_quimio: parseNumber(form.farmacos_quimio),
        farmacos_sangre: parseNumber(form.farmacos_sangre),
        farmacos_respiratori: parseNumber(form.farmacos_respiratori),
        farmacos_sentits: parseNumber(form.farmacos_sentits)
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

      <div className="form-section">
        <h3>Datos Personales e Inclusión</h3>
        <div className="form-row">
          <div className="field">
            <label>Sexo Biológico / Identidad</label>
            <select name="sexo" value={form.sexo} onChange={handleChange}>
              <option value="M">Hombre</option>
              <option value="F">Mujer</option>
              <option value="NB">No Binario / Otros</option>
              <option value="NS">Prefiero no decir</option>
            </select>
          </div>
          <div className="field">
            <label>Edad</label>
            <input
              type="number" name="edad" min="0" max="120"
              placeholder="Edad (Obligatorio)" value={form.edad}
              onChange={handleChange} required
            />
          </div>
          <div className="field field--wide">
            <label>Situación Social (Inclusión)</label>
            <select name="apoyo_social" value={form.apoyo_social || 'si'} onChange={handleChange}>
              <option value="si">Cuenta con apoyo familiar/social</option>
              <option value="vulnerable">Vive solo / Riesgo de aislamiento</option>
              <option value="dependiente">Dependencia grado II o III</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Cronicidad y Seguimiento</h3>
        <div className="form-row">
          <div className="field field--wide">
            <label>¿Tiene usted alguna enfermedad crónica que requiera control continuo, o recibe visitas de enfermería en su domicilio?</label>
            <select name="es_cronico" value={form.es_cronico} onChange={handleChange}>
              <option value="no_se">No lo sé / No estoy seguro</option>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
          
          {form.es_cronico === 'si' && (
            <div className="field field--wide">
              <label>En el caso de que sea Paciente Crónico de que tipo es:</label>
              <select name="tipo_cronico" value={form.tipo_cronico} onChange={handleChange}>
                <option value="ninguno">No lo sé</option>
                <option value="PCC">PCC (Paciente Crónico Complejo)</option>
                <option value="MACA">MACA (Atención a la Cronicidad Avanzada)</option>
              </select>
            </div>
          )}
        </div>
      </div>

      <div className="form-section">
        <h3>Historial de Diagnósticos</h3>
        <p className="form-hint">Deje en blanco los campos si no conoce la respuesta exacta.</p>
        <div className="form-row">
          <div className="field field--wide">
            <label>¿Cuántos problemas de salud o enfermedades distintas le ha diagnosticado su médico? (Ej. diabetes, artrosis, asma...)</label>
            <input
              type="number" name="total_diagnosticos" min="0"
              placeholder="Total (deje en blanco si no sabe)" value={form.total_diagnosticos}
              onChange={handleChange} 
            />
          </div>
          <div className="field">
            <label>Problemas agudos</label>
            <input
              type="number" name="problemas_agudos" min="0"
              placeholder="Nº diagnósticos" value={form.problemas_agudos}
              onChange={handleChange}
            />
          </div>
          <div className="field">
            <label>Problemas crónicos</label>
            <input
              type="number" name="problemas_cronicos" min="0"
              placeholder="Nº diagnósticos" value={form.problemas_cronicos}
              onChange={handleChange}
            />
          </div>
          <div className="field">
            <label>Neoplasia maligna (Cáncer)</label>
            <input
              type="number" name="neoplasia_maligna" min="0"
              placeholder="Nº diagnósticos" value={form.neoplasia_maligna}
              onChange={handleChange}
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Visitas y Hospitalizaciones (Último año)</h3>
        <div className="form-row">
          <div className="field field--wide">
            <label>¿Aproximadamente, cuántas veces ha ido a su ambulatorio (médico de cabecera o enfermera) en el último año?</label>
            <input
              type="number" name="visitas_primaria" min="0"
              placeholder="Nº de visitas (deje en blanco si no sabe)" value={form.visitas_primaria}
              onChange={handleChange} 
            />
          </div>
          <div className="field field--wide">
            <label>¿Ha tenido que ir a Urgencias en los últimos 12 meses? ¿Cuántas veces?</label>
            <input
              type="number" name="visitas_urgencias" min="0"
              placeholder="Nº de visitas a urgencias" value={form.visitas_urgencias}
              onChange={handleChange} 
            />
          </div>
          <div className="field field--wide">
            <label>¿Ha estado ingresado en el hospital pasando al menos una noche este último año? (Indique cuántas veces)</label>
            <input
              type="number" name="hospitalizaciones" min="0"
              placeholder="Nº de ingresos" value={form.hospitalizaciones}
              onChange={handleChange} 
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Medicación</h3>
        <div className="form-row">
          <div className="field field--wide">
            <label>¿Cuántas pastillas o medicamentos diferentes toma al día de forma habitual?</label>
            <input
              type="number" name="total_farmacos" min="0"
              placeholder="Total de medicamentos (deje en blanco si no sabe)" value={form.total_farmacos}
              onChange={handleChange} 
            />
          </div>

          <div className="field field--wide">
            <label>¿Toma pastillas para la tensión, el corazón, el colesterol, el azúcar (diabetes) o protectores de estómago?</label>
            <select name="toma_cardio_digestivo" value={form.toma_cardio_digestivo} onChange={handleChange}>
              <option value="no_se">No lo sé / No estoy seguro</option>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
          {form.toma_cardio_digestivo === 'si' && (
            <>
              <div className="field">
                <label>Nº Fármacos Sist. Cardiovascular</label>
                <input type="number" name="farmacos_cardiovascular" min="0" placeholder="Opcional" value={form.farmacos_cardiovascular} onChange={handleChange} />
              </div>
              <div className="field">
                <label>Nº Fármacos Sist. Digestivo</label>
                <input type="number" name="farmacos_digestivo" min="0" placeholder="Opcional" value={form.farmacos_digestivo} onChange={handleChange} />
              </div>
            </>
          )}

          <div className="field field--wide">
            <label>¿Toma medicación para dolores fuertes, artrosis, relajantes musculares, ansiedad o para dormir?</label>
            <select name="toma_nervios_musculo" value={form.toma_nervios_musculo} onChange={handleChange}>
              <option value="no_se">No lo sé / No estoy seguro</option>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
          {form.toma_nervios_musculo === 'si' && (
            <>
              <div className="field">
                <label>Nº Fármacos Sist. Musculoesquelético</label>
                <input type="number" name="farmacos_musculoesqueletic" min="0" placeholder="Opcional" value={form.farmacos_musculoesqueletic} onChange={handleChange} />
              </div>
              <div className="field">
                <label>Nº Fármacos Sist. Nervioso</label>
                <input type="number" name="farmacos_nervios" min="0" placeholder="Opcional" value={form.farmacos_nervios} onChange={handleChange} />
              </div>
            </>
          )}

          <div className="field field--wide">
            <label>¿Le han recetado algún antibiótico en las últimas semanas?</label>
            <select name="toma_infecciosos" value={form.toma_infecciosos} onChange={handleChange}>
              <option value="no_se">No lo sé / No estoy seguro</option>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
          {form.toma_infecciosos === 'si' && (
            <div className="field">
              <label>Nº Fármacos Antiinfecciosos</label>
              <input type="number" name="farmacos_antiinfecciosos" min="0" placeholder="Opcional" value={form.farmacos_antiinfecciosos} onChange={handleChange} />
            </div>
          )}

          <div className="field field--wide">
            <label>¿Está recibiendo tratamiento de quimioterapia, para problemas graves de la sangre o de defensas?</label>
            <select name="toma_quimio_sangre" value={form.toma_quimio_sangre} onChange={handleChange}>
              <option value="no_se">No lo sé / No estoy seguro</option>
              <option value="no">No</option>
              <option value="si">Sí</option>
            </select>
          </div>
          {form.toma_quimio_sangre === 'si' && (
            <>
              <div className="field">
                <label>Nº Fármacos Quimioterapia</label>
                <input type="number" name="farmacos_quimio" min="0" placeholder="Opcional" value={form.farmacos_quimio} onChange={handleChange} />
              </div>
              <div className="field">
                <label>Nº Fármacos Sangre/Hematopoyéticos</label>
                <input type="number" name="farmacos_sangre" min="0" placeholder="Opcional" value={form.farmacos_sangre} onChange={handleChange} />
              </div>
            </>
          )}

          <div className="field field--wide">
            <label>Otros tratamientos (Opcional)</label>
          </div>
          <div className="field">
            <label>Nº Fármacos Sist. Respiratorio</label>
            <input type="number" name="farmacos_respiratori" min="0" placeholder="Opcional" value={form.farmacos_respiratori} onChange={handleChange} />
          </div>
          <div className="field">
            <label>Nº Fármacos Órganos de los Sentidos</label>
            <input type="number" name="farmacos_sentits" min="0" placeholder="Opcional" value={form.farmacos_sentits} onChange={handleChange} />
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