
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SearchArgs(BaseModel):
    days: int
    query: str

class DownloadArgs(BaseModel):
    email_id: str
    attachment_id: str

@app.get('/.well-known/mcp-manifest')
def manifest():
    return {
        "name": "gmail-mcp-server",
        "tools": [
            {"name": "search_emails", "input": {"days": "number", "query": "string"}},
            {"name": "download_attachment", "input": {"email_id": "string", "attachment_id": "string"}}
        ]
    }

@app.post('/tools/search_emails')
def search_emails(args: SearchArgs):
    return {
        "results": [
            {
                "email_id": "e1",
                "from": "receipts@uber.com",
                "date": "2026-01-17",
                "attachments": [{"id": "a1", "filename": "receipt.pdf", "url": "https://example.com/receipt.pdf"}]
            }
        ]
    }

@app.post('/tools/download_attachment')
def download_attachment(args: DownloadArgs):
    return {"file_url": "https://example.com/receipt.pdf"}
