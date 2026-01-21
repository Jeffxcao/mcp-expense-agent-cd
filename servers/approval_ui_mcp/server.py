
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    id: str
    merchant: str
    amount: float
    date: str
    status: str

class ApprovalRequest(BaseModel):
    items: List[Item]

@app.get('/.well-known/mcp-manifest')
def manifest():
    return {
        "name": "approval-ui-mcp-server",
        "tools": [{"name": "request_approval"}]
    }

@app.post('/tools/request_approval')
def request_approval(req: ApprovalRequest):
    return {
        "approvals": [
            {"item_id": item.id, "approved": True, "reason": "Business expense"}
            for item in req.items
        ]
    }
