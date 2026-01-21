
import requests

def call(base, tool, payload):
    return requests.post(f"{base}/tools/{tool}", json=payload).json()

def main():
    gmail = "http://localhost:3001"
    ocr = "http://localhost:3002"
    cc = "http://localhost:3003"
    sheets = "http://localhost:3004"
    approval = "http://localhost:3005"

    emails = call(gmail, "search_emails", {"days":7,"query":"receipt"})["results"]
    receipts = []
    for e in emails:
        for a in e["attachments"]:
            file_url = call(gmail, "download_attachment", {"email_id":e["email_id"],"attachment_id":a["id"]})["file_url"]
            extracted = call(ocr, "extract_receipt", {"file_url":file_url})
            receipts.append(extracted)

    txns = call(cc, "get_transactions", {"from_date":"2026-01-14","to_date":"2026-01-21"})
    sheet = call(sheets, "create_sheet", {"title":"Expenses","columns":[]})

    for r in receipts:
        call(sheets, "append_row", {"sheet_id":sheet["sheet_id"],"row":r})

    approvals = call(approval, "request_approval", {"items":[{"id":"r1","merchant":"Uber","amount":42.75,"date":"2026-01-17","status":"Matched"}]})
    print("Approvals:", approvals)

if __name__ == "__main__":
    main()
