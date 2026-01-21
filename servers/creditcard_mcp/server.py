
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TxnArgs(BaseModel):
    from_date: str
    to_date: str

@app.get('/.well-known/mcp-manifest')
def manifest():
    return {
        "name": "creditcard-mcp-server",
        "tools": [{"name": "get_transactions", "input": {"from_date": "string", "to_date": "string"}}]
    }

@app.post('/tools/get_transactions')
def get_transactions(args: TxnArgs):
    return [
        {"id": "txn1", "merchant": "UBER *TRIP", "amount": 42.75, "date": "2026-01-17"}
    ]
