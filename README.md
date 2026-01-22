# mcp-expense-agent-cd

Expense reconciliation agent composed of small MCP servers plus a React UI for approvals.

## Architecture
- Orchestrator drives the workflow (email → OCR → transactions → sheet → approvals → sheet updates).
- MCP servers provide narrow tools: Gmail fetch, OCR, credit-card transactions, Google Sheets I/O, and an approval UI backend.
- React frontend (Vite) renders pending approvals and posts decisions back to the approval server.

## Folder structure
- approval-ui/ — React frontend (Vite, React 18)
- orchestrator/ — Python script that stitches MCP tools together
- servers/
  - gmail_mcp/ — Gmail search + attachment download
  - receipt_ocr_mcp/ — OCR receipt extraction
  - creditcard_mcp/ — Card transaction fetch
  - sheets_mcp/ — Google Sheets create/append/update
  - approval_ui_mcp/ — Approval API that the UI talks to

## Agent flow (high level)
1) Orchestrator finds recent receipt emails via gmail_mcp.
2) Downloads attachments and sends to receipt_ocr_mcp for merchant/amount/date extraction.
3) Fetches card transactions from creditcard_mcp; marks receipts as matched/unmatched.
4) Creates a draft sheet in sheets_mcp and appends rows for each receipt.
5) Sends receipts to approval_ui_mcp `request_approval`; the React UI polls `/pending`.
6) User approves/rejects in the UI; UI POSTs decisions to `/approve`.
7) Orchestrator polls approval_ui_mcp until all items decided, then updates rows in sheets_mcp.

### Flow diagram
```
Gmail (emails+attachments)
   │
   ▼
gmail_mcp → receipt_ocr_mcp → receipts
   │                     
   └──→ creditcard_mcp (transactions)
	│
	▼
   match status
	│
	▼
   sheets_mcp (create sheet, append rows)
	│
	▼
approval_ui_mcp ⇄ approval-ui (React)
	│           │
	│     user approves/rejects
	▼           │
approvals returned to orchestrator
	│
	▼
   sheets_mcp updates rows
```

### Agent working diagram (alternate view)
```
┌──────────────┐
│  User (UI)   │
│ Web / Chat   │
└──────┬───────┘
	│ approve / add reason
	▼
┌──────────────────────────┐
│ Orchestrator Agent       │
│ (Planner + Memory)       │
└──────┬───────────┬───────┘
	│           │
	▼           ▼
┌──────────┐  ┌───────────────┐
│ Gmail    │  │ Credit Card   │
│ Agent    │  │ Agent         │
└────┬─────┘  └────┬──────────┘
     │              │
     ▼              ▼
┌────────────┐  ┌─────────────┐
│ Receipt    │  │ Reconciler  │
│ OCR Agent  │  │ Agent       │
└────┬───────┘  └────┬────────┘
     │               │
     ▼               ▼
┌──────────────────────────┐
│ Google Sheets Agent      │
│ (Expense Report)         │
└──────────────────────────┘
```

## Run (dev)
- Start MCP servers (each in its folder): `uvicorn server:app --port 3001|3002|3003|3004|3005`
- UI: `cd approval-ui && npm install && npm run dev`
- Orchestrator: `cd orchestrator && python3 orchestrator.py`
