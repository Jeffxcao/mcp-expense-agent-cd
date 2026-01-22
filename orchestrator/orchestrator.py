import time
import requests
from datetime import datetime, timedelta

# MCP server base URLs
GMAIL_MCP = "http://localhost:3001"
OCR_MCP = "http://localhost:3002"
CARD_MCP = "http://localhost:3003"
SHEETS_MCP = "http://localhost:3004"
APPROVAL_MCP = "http://localhost:3005"


# ---------- Helper ----------
def call_mcp(base_url, tool, payload):
    url = f"{base_url}/tools/{tool}"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()


# ---------- Approval Wait ----------
def wait_for_approval(poll_interval=3):
    """
    Blocks until all approval items are approved/rejected
    """
    print("⏳ Waiting for user approval...")
    while True:
        pending = requests.get(f"{APPROVAL_MCP}/pending").json()

        if not pending:
            time.sleep(poll_interval)
            continue

        all_done = True
        for req in pending.values():
            for item in req["items"].values():
                if item["approved"] is None:
                    all_done = False
                    break

        if all_done:
            print("✅ All approvals completed")
            return pending

        time.sleep(poll_interval)


# ---------- Main Orchestration ----------
def main():
    print("🚀 Starting expense reconciliation run")

    # Date window
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=7)

    # 1️⃣ Find receipt emails
    emails = call_mcp(
        GMAIL_MCP,
        "search_emails",
        {"days": 7, "query": "receipt OR invoice"}
    )["results"]

    print(f"📧 Found {len(emails)} receipt emails")

    # 2️⃣ OCR receipts
    receipts = []
    for email in emails:
        for attachment in email.get("attachments", []):
            file_url = call_mcp(
                GMAIL_MCP,
                "download_attachment",
                {
                    "email_id": email["email_id"],
                    "attachment_id": attachment["id"]
                }
            )["file_url"]

            extracted = call_mcp(
                OCR_MCP,
                "extract_receipt",
                {"file_url": file_url}
            )

            receipts.append({
                "id": f"r{len(receipts)+1}",
                "merchant": extracted["merchant"],
                "amount": extracted["amount"],
                "date": extracted["date"],
                "status": "Unmatched"
            })

    print(f"🧾 Extracted {len(receipts)} receipts")

    # 3️⃣ Get credit card transactions
    transactions = call_mcp(
        CARD_MCP,
        "get_transactions",
        {
            "from_date": str(from_date),
            "to_date": str(to_date)
        }
    )

    # 4️⃣ Simple reconciliation
    for r in receipts:
        for t in transactions:
            if abs(t["amount"] - r["amount"]) < 0.5:
                r["status"] = "Matched"
                break

    # 5️⃣ Create Google Sheet (draft)
    sheet = call_mcp(
        SHEETS_MCP,
        "create_sheet",
        {
            "title": f"Expenses {from_date} → {to_date}",
            "columns": [
                "Date",
                "Merchant",
                "Amount",
                "Status",
                "Approved",
                "Reason"
            ]
        }
    )

    sheet_id = sheet["sheet_id"]

    for r in receipts:
        call_mcp(
            SHEETS_MCP,
            "append_row",
            {
                "sheet_id": sheet_id,
                "row": {
                    "date": r["date"],
                    "merchant": r["merchant"],
                    "amount": r["amount"],
                    "status": r["status"],
                    "approved": False,
                    "reason": ""
                }
            }
        )

    print(f"📊 Draft expense sheet created: {sheet_id}")

    # 6️⃣ Request approval (MCP tool)
    approval_request = call_mcp(
        APPROVAL_MCP,
        "request_approval",
        {"items": receipts}
    )

    print(f"🛑 Approval request created: {approval_request['request_id']}")

    # 7️⃣ Wait for UI approval
    approvals = wait_for_approval()

    # 8️⃣ Apply approvals to sheet
    for req in approvals.values():
        for item in req["items"].values():
            call_mcp(
                SHEETS_MCP,
                "update_row",
                {
                    "sheet_id": sheet_id,
                    "row_id": item["id"],
                    "updates": {
                        "approved": item["approved"],
                        "reason": item["reason"]
                    }
                }
            )

    print("🎉 Expense reconciliation complete")


if __name__ == "__main__":
    main()
