const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function predictFromForm(patientData) {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patientData),
  })
  if (!res.ok) throw new Error(`Error ${res.status}`)
  return res.json()
}

export async function predictFromText(text) {
  const res = await fetch(`${API_BASE}/api/predict-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!res.ok) throw new Error(`Error ${res.status}`)
  return res.json()
}
