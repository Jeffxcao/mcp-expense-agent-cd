import { useEffect, useState } from 'react'

const API = 'http://localhost:3005'

export default function App() {
  const [pending, setPending] = useState({})
  const [decisions, setDecisions] = useState({})

  useEffect(() => {
    fetch(`${API}/pending`)
      .then(r => r.json())
      .then(setPending)
  }, [])

  const setDecision = (itemId, approved) => {
    setDecisions(d => ({ ...d, [itemId]: { approved, reason: '' } }))
  }

  const setReason = (itemId, reason) => {
    setDecisions(d => ({ ...d, [itemId]: { ...d[itemId], reason } }))
  }

  const submit = async () => {
    const payload = Object.entries(decisions).map(([item_id, v]) => ({
      item_id,
      approved: v.approved,
      reason: v.reason
    }))

    await fetch(`${API}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    alert('Submitted!')
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Expense Approvals</h2>

      {Object.entries(pending).map(([reqId, req]) => (
        <div key={reqId}>
          <h3>Request {reqId.slice(0, 8)}</h3>

          {Object.entries(req.items).map(([itemId, item]) => (
            <div key={itemId} style={{ borderBottom: '1px solid #ccc', padding: 8 }}>
              <strong>{item.merchant}</strong> — ${item.amount} ({item.date})
              <div>
                <button onClick={() => setDecision(itemId, true)}>Approve</button>
                <button onClick={() => setDecision(itemId, false)}>Reject</button>
              </div>
              <input
                placeholder="Reason"
                onChange={e => setReason(itemId, e.target.value)}
              />
            </div>
          ))}
        </div>
      ))}

      <button onClick={submit} style={{ marginTop: 20 }}>
        Submit Decisions
      </button>
    </div>
  )
}
