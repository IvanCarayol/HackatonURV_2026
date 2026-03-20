import { useState } from 'react'
import { predictFromText } from '../services/api'
import './Chatinput.css';

const EXAMPLES = [
  'Mujer de 72 años con insuficiencia cardíaca, diabetes tipo 2 y presión arterial de 160/90. Creatinina 1.8 mg/dL.',
  'Hombre de 58 años, fumador, diagnosticado de EPOC hace 3 años. IMC 31, hemoglobina 11 g/dL.',
  'Paciente de 80 años con enfermedad renal crónica estadio 3 y dos comorbilidades adicionales.',
]

export default function ChatInput({ onResult }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim()) return
    setError(null)
    setLoading(true)
    try {
      const result = await predictFromText(text)
      onResult(result)
    } catch (err) {
      setError('No se pudo conectar con la API. Comprueba que el servidor está activo.')
    } finally {
      setLoading(false)
    }
  }

  function useExample(example) {
    setText(example)
  }

  return (
    <div className="chat-panel">

      <p className="chat-hint">
        Describe el caso clínico en lenguaje natural. El modelo extraerá los datos relevantes y calculará el riesgo.
      </p>

      <div className="examples">
        <span className="examples-label">Ejemplos:</span>
        {EXAMPLES.map((ex, i) => (
          <button
            key={i}
            className="example-chip"
            onClick={() => useExample(ex)}
            type="button"
          >
            {ex.slice(0, 48)}…
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="chat-input-wrap">
          <textarea
            className="chat-textarea"
            placeholder="Ej: Mujer de 68 años con insuficiencia cardíaca y diabetes tipo 2, presión arterial 150/90..."
            value={text}
            onChange={e => setText(e.target.value)}
            rows={5}
            required
          />
          <div className="chat-footer">
            <span className="char-count">{text.length} caracteres</span>
            <button
              type="submit"
              className="submit-btn submit-btn--inline"
              disabled={loading || !text.trim()}
            >
              {loading ? 'Analizando...' : 'Analizar →'}
            </button>
          </div>
        </div>
      </form>

      {error && <p className="form-error">{error}</p>}

      <div className="chat-info">
        <strong>¿Cómo funciona?</strong> El texto se envía al LLM, que extrae edad, diagnósticos,
        parámetros clínicos y comorbilidades de forma automática antes de calcular el riesgo.
        Cuanta más información incluyas, más precisa será la predicción.
      </div>

    </div>
  )
}
