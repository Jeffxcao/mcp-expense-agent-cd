
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
SHEET = []

class CreateSheet(BaseModel):
    title: str
    columns: list

class AppendRow(BaseModel):
    sheet_id: str
    row: dict

class UpdateRow(BaseModel):
    sheet_id: str
    row_id: str
    updates: dict

@app.get('/.well-known/mcp-manifest')
def manifest():
    return {
        "name": "sheets-mcp-server",
        "tools": [
            {"name": "create_sheet"},
            {"name": "append_row"},
            {"name": "update_row"}
        ]
    }

@app.post('/tools/create_sheet')
def create_sheet(args: CreateSheet):
    return {"sheet_id": "sheet1"}

@app.post('/tools/append_row')
def append_row(args: AppendRow):
    SHEET.append(args.row)
    return {"row_id": str(len(SHEET))}

@app.post('/tools/update_row')
def update_row(args: UpdateRow):
    return {"status": "updated"}
