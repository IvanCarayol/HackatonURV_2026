import { useState } from 'react'
import FormInput from './components/FormInput'
import ChatInput from './components/ChatInput'
import ResultPanel from './components/ResultPanel'
import './App.css'

export default function App() {
  const [mode, setMode] = useState('chat')
  const [result, setResult] = useState(null)

  function handleResult(data) {
    setResult(data)
    // scroll suave al resultado
    setTimeout(() => {
      document.getElementById('result')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>MedRisk Predictor</h1>
        <p>Introduce los datos del paciente para estimar el riesgo de mortalidad.</p>
      </header>

      <div className="mode-toggle">
        <button
          className={mode === 'chat' ? 'active' : ''}
          onClick={() => { setMode('chat'); setResult(null) }}
        >
          Texto libre
        </button>
        <button
          className={mode === 'form' ? 'active' : ''}
          onClick={() => { setMode('form'); setResult(null) }}
        >
          Formulario técnico
        </button>
      </div>

      {mode === 'chat'
        ? <ChatInput onResult={handleResult} />
        : <FormInput onResult={handleResult} />
      }

      {result && (
        <div id="result">
          <ResultPanel data={result} />
        </div>
      )}
    </div>
  )
}
