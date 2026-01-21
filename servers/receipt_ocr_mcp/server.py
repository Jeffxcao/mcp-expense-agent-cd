
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ExtractArgs(BaseModel):
    file_url: str

@app.get('/.well-known/mcp-manifest')
def manifest():
    return {
        "name": "receipt-ocr-mcp-server",
        "tools": [{"name": "extract_receipt", "input": {"file_url": "string"}}]
    }

@app.post('/tools/extract_receipt')
def extract_receipt(args: ExtractArgs):
    return {
        "merchant": "Uber",
        "date": "2026-01-17",
        "amount": 42.75,
        "currency": "USD",
        "card_hint": "1234",
        "tax": 3.25
    }
