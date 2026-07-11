#!/usr/bin/env python3
"""QuickBooks Online 영수증 업로드 — Purchase(지출) 생성 + 영수증 파일 첨부 (stdlib only).

사용법:
  python3 scripts/qbo_receipt.py --list-accounts              # 계정과목 목록 (지출·결제 계정 확인)
  python3 scripts/qbo_receipt.py --list-vendors               # 거래처 목록
  python3 scripts/qbo_receipt.py <영수증파일> --amount 45.67 \
      --vendor "Costco" --date 2026-07-07 \
      --payment-account "Checking" --expense-account "Supplies" \
      [--memo "7/10 출고 COGS"] [--payment-type Cash|CreditCard|Check]

동작: ① 거래처 이름 조회(없으면 생성) → ② Purchase 생성 → ③ 영수증 파일을
Attachable 로 multipart 업로드하며 Purchase 에 링크.

자격증명/토큰: config/qbo_credentials.json · config/qbo_tokens.json (qbo_auth.py 로 발급).
access_token 만료 시 자동 refresh.
"""
import argparse
import base64
import json
import mimetypes
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_PATH = ROOT / "config" / "qbo_credentials.json"
TOKEN_PATH = ROOT / "config" / "qbo_tokens.json"

BASES = {
    "production": "https://quickbooks.api.intuit.com",
    "sandbox": "https://sandbox-quickbooks.api.intuit.com",
}
MINOR = "75"


def load_json(p):
    if not p.exists():
        sys.exit(f"파일 없음: {p} — 먼저 qbo_auth.py 로 인증하세요.")
    return json.loads(p.read_text())


def ensure_token():
    """유효한 access_token 반환 (만료면 자동 refresh)."""
    tokens = load_json(TOKEN_PATH)
    if time.time() < tokens["expires_at"] - 60:
        return tokens
    creds = load_json(CRED_PATH)
    basic = base64.b64encode(
        f"{creds['client_id']}:{creds['client_secret']}".encode()
    ).decode()
    body = urllib.parse.urlencode(
        {"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]}
    ).encode()
    req = urllib.request.Request(
        "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    now = int(time.time())
    tokens.update(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=now + int(data.get("expires_in", 3600)),
        refresh_expires_at=now + int(data.get("x_refresh_token_expires_in", 0)),
        saved_at=now,
    )
    TOKEN_PATH.write_text(json.dumps(tokens, indent=2))
    return tokens


def api(method, path, tokens, body=None, headers=None, raw_body=None, query=None):
    creds = load_json(CRED_PATH)
    base = BASES[creds.get("environment", "production")]
    url = f"{base}/v3/company/{tokens['realm_id']}/{path}"
    q = {"minorversion": MINOR}
    if query:
        q.update(query)
    url += "?" + urllib.parse.urlencode(q)
    h = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Accept": "application/json",
    }
    if headers:
        h.update(headers)
    data = raw_body
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"QBO API 오류 HTTP {e.code} ({path}): {e.read().decode()}")


def qbo_query(tokens, q):
    return api("GET", "query", tokens, query={"query": q}).get("QueryResponse", {})


# ---------------- 조회 ----------------

def list_accounts(tokens):
    rows = qbo_query(
        tokens,
        "select Id, Name, AccountType, AccountSubType from Account "
        "where Active = true maxresults 1000",
    ).get("Account", [])
    pay_types = {"Bank", "Credit Card"}
    print("== 결제 계정 (--payment-account 후보) ==")
    for a in rows:
        if a["AccountType"] in pay_types:
            print(f"  [{a['Id']}] {a['Name']}  ({a['AccountType']})")
    print("\n== 지출 계정 (--expense-account 후보) ==")
    for a in rows:
        if a["AccountType"] in {"Expense", "Cost of Goods Sold", "Other Expense"}:
            print(f"  [{a['Id']}] {a['Name']}  ({a['AccountType']}/{a['AccountSubType']})")


def list_vendors(tokens):
    rows = qbo_query(
        tokens, "select Id, DisplayName from Vendor where Active = true maxresults 1000"
    ).get("Vendor", [])
    for v in rows:
        print(f"  [{v['Id']}] {v['DisplayName']}")


def find_account(tokens, name):
    esc = name.replace("'", "\\'")
    rows = qbo_query(
        tokens, f"select Id, Name, AccountType from Account where Name = '{esc}'"
    ).get("Account", [])
    if not rows:
        sys.exit(f"계정 '{name}' 없음 — --list-accounts 로 확인하세요.")
    return rows[0]


def find_or_create_vendor(tokens, name):
    esc = name.replace("'", "\\'")
    rows = qbo_query(
        tokens, f"select Id, DisplayName from Vendor where DisplayName = '{esc}'"
    ).get("Vendor", [])
    if rows:
        return rows[0]
    created = api("POST", "vendor", tokens, body={"DisplayName": name})["Vendor"]
    print(f"거래처 신규 생성: {name} (Id {created['Id']})")
    return created


# ---------------- 생성 ----------------

def create_purchase(tokens, args, pay_acct, exp_acct, vendor):
    payment_type = args.payment_type
    if payment_type is None:
        payment_type = "CreditCard" if pay_acct["AccountType"] == "Credit Card" else "Cash"
    body = {
        "PaymentType": payment_type,
        "AccountRef": {"value": pay_acct["Id"], "name": pay_acct["Name"]},
        "TxnDate": args.date,
        "Line": [
            {
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": args.amount,
                "Description": args.memo or "",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {"value": exp_acct["Id"], "name": exp_acct["Name"]}
                },
            }
        ],
    }
    if vendor:
        body["EntityRef"] = {"value": vendor["Id"], "name": vendor["DisplayName"], "type": "Vendor"}
    if args.memo:
        body["PrivateNote"] = args.memo
    return api("POST", "purchase", tokens, body=body)["Purchase"]


def upload_attachment(tokens, file_path: Path, purchase_id):
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    meta = {
        "FileName": file_path.name,
        "ContentType": mime,
        "AttachableRef": [
            {"EntityRef": {"type": "Purchase", "value": str(purchase_id)}, "IncludeOnSend": False}
        ],
    }
    boundary = f"----qbo{uuid.uuid4().hex}"
    parts = []
    parts.append(
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file_metadata_01"; filename="attachment.json"\r\n'
        "Content-Type: application/json; charset=UTF-8\r\n"
        "Content-Transfer-Encoding: 8bit\r\n\r\n"
        f"{json.dumps(meta)}\r\n"
    )
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file_content_01"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime}\r\n"
        "Content-Transfer-Encoding: base64\r\n\r\n"
        f"{base64.b64encode(file_path.read_bytes()).decode()}\r\n"
    )
    body = ("".join(parts) + f"--{boundary}--\r\n").encode()
    resp = api(
        "POST",
        "upload",
        tokens,
        raw_body=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    entries = resp.get("AttachableResponse", [])
    if not entries or "Attachable" not in entries[0]:
        sys.exit(f"첨부 업로드 실패: {json.dumps(resp, ensure_ascii=False)}")
    return entries[0]["Attachable"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt", nargs="?", help="영수증 파일 (pdf/jpg/png)")
    ap.add_argument("--amount", type=float, help="총액 (CAD/USD — QBO 회사 통화)")
    ap.add_argument("--date", help="거래일 YYYY-MM-DD")
    ap.add_argument("--vendor", help="거래처 이름 (없으면 자동 생성)")
    ap.add_argument("--memo", help="메모")
    ap.add_argument("--payment-account", help="결제 계정 이름 (Bank/Credit Card)")
    ap.add_argument("--expense-account", help="지출 계정 이름 (Expense/COGS)")
    ap.add_argument("--payment-type", choices=["Cash", "CreditCard", "Check"])
    ap.add_argument("--list-accounts", action="store_true")
    ap.add_argument("--list-vendors", action="store_true")
    args = ap.parse_args()

    tokens = ensure_token()

    if args.list_accounts:
        list_accounts(tokens)
        return
    if args.list_vendors:
        list_vendors(tokens)
        return

    missing = [k for k in ("receipt", "amount", "date", "payment_account", "expense_account")
               if not getattr(args, k)]
    if missing:
        ap.error("필수: 영수증파일 --amount --date --payment-account --expense-account")

    file_path = Path(args.receipt)
    if not file_path.exists():
        sys.exit(f"파일 없음: {file_path}")

    pay_acct = find_account(tokens, args.payment_account)
    exp_acct = find_account(tokens, args.expense_account)
    vendor = find_or_create_vendor(tokens, args.vendor) if args.vendor else None

    purchase = create_purchase(tokens, args, pay_acct, exp_acct, vendor)
    print(f"Purchase 생성됨 — Id {purchase['Id']}, 금액 {purchase['TotalAmt']}, 날짜 {purchase['TxnDate']}")

    att = upload_attachment(tokens, file_path, purchase["Id"])
    print(f"영수증 첨부됨 — Attachable Id {att['Id']} ({att.get('FileName')})")
    print("완료 ✅")


if __name__ == "__main__":
    main()
