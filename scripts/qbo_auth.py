#!/usr/bin/env python3
"""QuickBooks Online OAuth2 인증 헬퍼 (stdlib only).

사용법:
  python3 scripts/qbo_auth.py            # 브라우저 인증 → 토큰 발급·저장 (localhost:8400 콜백)
  python3 scripts/qbo_auth.py --manual   # 콜백 서버 없이 — 인증 URL 출력, 리다이렉트된 URL을 붙여넣기
  python3 scripts/qbo_auth.py --refresh  # refresh_token 으로 access_token 갱신
  python3 scripts/qbo_auth.py --status   # 저장된 토큰 상태 확인

자격증명: config/qbo_credentials.json (gitignored)
토큰 저장: config/qbo_tokens.json (gitignored)

리다이렉트 URI (기본 http://localhost:8400/callback)는 Intuit 개발자 포털
(developer.intuit.com → 앱 → Keys & credentials → Redirect URIs)에 등록돼 있어야 한다.
포털이 localhost 를 거부하면(프로덕션 키) OAuth2 Playground URI 를 등록하고
--manual 모드로 리다이렉트 URL 을 붙여넣으면 된다.
"""
import argparse
import base64
import http.server
import json
import secrets
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_PATH = ROOT / "config" / "qbo_credentials.json"
TOKEN_PATH = ROOT / "config" / "qbo_tokens.json"

AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
SCOPE = "com.intuit.quickbooks.accounting"


def load_creds():
    if not CRED_PATH.exists():
        sys.exit(f"자격증명 파일 없음: {CRED_PATH}")
    return json.loads(CRED_PATH.read_text())


def save_tokens(data, realm_id):
    now = int(time.time())
    tokens = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "realm_id": realm_id,
        "expires_at": now + int(data.get("expires_in", 3600)),
        "refresh_expires_at": now + int(data.get("x_refresh_token_expires_in", 0)),
        "saved_at": now,
    }
    TOKEN_PATH.write_text(json.dumps(tokens, indent=2))
    TOKEN_PATH.chmod(0o600)
    print(f"토큰 저장됨 → {TOKEN_PATH}")
    print(f"  realm_id(회사 ID): {realm_id}")
    print(f"  access_token 만료: {time.ctime(tokens['expires_at'])}")
    if tokens["refresh_expires_at"]:
        print(f"  refresh_token 만료: {time.ctime(tokens['refresh_expires_at'])}")


def exchange(creds, grant: dict):
    basic = base64.b64encode(
        f"{creds['client_id']}:{creds['client_secret']}".encode()
    ).decode()
    body = urllib.parse.urlencode(grant).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"토큰 요청 실패 HTTP {e.code}: {e.read().decode()}")


def build_auth_url(creds, state):
    params = {
        "client_id": creds["client_id"],
        "response_type": "code",
        "scope": SCOPE,
        "redirect_uri": creds["redirect_uri"],
        "state": state,
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def parse_callback(url, expected_state=None):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    code = q.get("code", [None])[0]
    realm = q.get("realmId", [None])[0]
    state = q.get("state", [None])[0]
    if not code or not realm:
        sys.exit(f"콜백 URL에 code/realmId 없음: {url}")
    if expected_state and state != expected_state:
        sys.exit("state 불일치 — 다시 시도하세요.")
    return code, realm


def cmd_auth(creds, manual=False):
    state = secrets.token_urlsafe(16)
    url = build_auth_url(creds, state)

    if manual:
        print("아래 URL을 브라우저에서 열고 QuickBooks 로그인·승인 후,")
        print("리다이렉트된 전체 URL(주소창)을 여기에 붙여넣으세요.\n")
        print(url + "\n")
        redirected = input("리다이렉트 URL: ").strip()
        code, realm = parse_callback(redirected, state)
    else:
        parsed = urllib.parse.urlparse(creds["redirect_uri"])
        port = parsed.port or 80
        result = {}

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if not self.path.startswith(parsed.path):
                    self.send_response(404)
                    self.end_headers()
                    return
                result["url"] = f"http://localhost:{port}{self.path}"
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("<h2>연결 완료 — 터미널로 돌아가세요.</h2>".encode())

            def log_message(self, *a):
                pass

        server = http.server.HTTPServer(("localhost", port), Handler)
        print(f"콜백 대기 중 (localhost:{port}) — 브라우저에서 승인하세요…")
        webbrowser.open(url)
        print(f"\n브라우저가 안 열리면 직접 여세요:\n{url}\n")
        while "url" not in result:
            server.handle_request()
        server.server_close()
        code, realm = parse_callback(result["url"], state)

    data = exchange(
        creds,
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": creds["redirect_uri"],
        },
    )
    save_tokens(data, realm)


def cmd_refresh(creds):
    if not TOKEN_PATH.exists():
        sys.exit("토큰 파일 없음 — 먼저 인증하세요: python3 scripts/qbo_auth.py")
    tokens = json.loads(TOKEN_PATH.read_text())
    data = exchange(
        creds,
        {"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]},
    )
    save_tokens(data, tokens["realm_id"])


def cmd_status():
    if not TOKEN_PATH.exists():
        print("토큰 없음 — 인증 필요: python3 scripts/qbo_auth.py")
        return
    tokens = json.loads(TOKEN_PATH.read_text())
    now = time.time()
    print(f"realm_id: {tokens['realm_id']}")
    ok = now < tokens["expires_at"]
    print(f"access_token: {'유효' if ok else '만료'} (만료 {time.ctime(tokens['expires_at'])})")
    if tokens.get("refresh_expires_at"):
        rok = now < tokens["refresh_expires_at"]
        print(f"refresh_token: {'유효' if rok else '만료'} (만료 {time.ctime(tokens['refresh_expires_at'])})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual", action="store_true", help="콜백 서버 없이 수동 붙여넣기")
    ap.add_argument("--refresh", action="store_true", help="access_token 갱신")
    ap.add_argument("--status", action="store_true", help="토큰 상태 확인")
    args = ap.parse_args()

    if args.status:
        cmd_status()
        return
    creds = load_creds()
    if args.refresh:
        cmd_refresh(creds)
    else:
        cmd_auth(creds, manual=args.manual)


if __name__ == "__main__":
    main()
