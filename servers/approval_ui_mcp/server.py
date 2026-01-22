from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (replace with DB later)
PENDING = {}

class ApprovalItem(BaseModel):
    id: str
    merchant: str
    amount: float
    date: str
    status: str

class ApprovalRequest(BaseModel):
    items: List[ApprovalItem]

class ApprovalDecision(BaseModel):
    item_id: str
    approved: bool
    reason: Optional[str] = ""

@app.get('/.well-known/mcp-manifest')
def manifest():
    return {
        "name": "approval-ui-mcp-server",
        "tools": [{"name": "request_approval"}]
    }

# MCP tool — called by orchestrator
@app.post('/tools/request_approval')
def request_approval(req: ApprovalRequest):
    request_id = str(uuid.uuid4())
    PENDING[request_id] = {
        "created_at": time.time(),
        "items": {item.id: item.dict() | {"approved": None, "reason": ""} for item in req.items}
    }
    return {"request_id": request_id, "status": "pending"}

# UI polls this
@app.get('/pending')
def get_pending():
    return PENDING

# UI submits decisions
@app.post('/approve')
def approve(decisions: List[ApprovalDecision]):
    for decision in decisions:
        for req in PENDING.values():
            if decision.item_id in req["items"]:
                req["items"][decision.item_id]["approved"] = decision.approved
                req["items"][decision.item_id]["reason"] = decision.reason
    return {"status": "recorded"}
