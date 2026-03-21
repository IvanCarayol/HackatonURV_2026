const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080'

export async function predictFromForm(patientData) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patientData),
  })
  if (!res.ok) throw new Error(`Error ${res.status}`)
  return res.json()
}

export async function analyzeFullCase(text) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!res.ok) throw new Error(`Error ${res.status}`)
  return res.json()
}

export async function predictFromText(text) {
  return analyzeFullCase(text)
}
