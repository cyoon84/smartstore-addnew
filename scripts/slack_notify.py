#!/usr/bin/env python3
"""Slack Incoming Webhook 으로 메시지 전송 (MCP 불필요 — 헤드리스/cron 안전).

Slack 은 표준 마크다운을 렌더하지 않으므로(#, **, |표| 가 raw 기호로 깨짐),
.md 입력은 Slack mrkdwn 으로 변환 후 보낸다 (--raw 로 끄기).

webhook URL 우선순위:
  1) 환경변수 SLACK_WEBHOOK_URL
  2) scripts/.slack_webhook 파일 (gitignore 됨, 첫 줄 = URL)

사용:
  python3 scripts/slack_notify.py --file output/foo_등록정보.md   # 변환 후 전송
  python3 scripts/slack_notify.py --text "메시지"                 # 그대로 전송
  python3 scripts/slack_notify.py --file x.md --raw               # 변환 없이
"""
import argparse, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBHOOK_FILE = os.path.join(ROOT, "scripts", ".slack_webhook")
LIMIT = 3500  # Slack section 한도 여유. 길면 분할 전송.


def get_url():
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if url:
        return url.strip()
    if os.path.exists(WEBHOOK_FILE):
        with open(WEBHOOK_FILE) as f:
            return f.readline().strip()
    sys.exit("Slack webhook URL 없음 — SLACK_WEBHOOK_URL 환경변수 또는 scripts/.slack_webhook 파일 설정 필요")


# ---------- 마크다운 → Slack mrkdwn ----------

def _inline(s):
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<\2|\1>", s)   # [t](u) -> <u|t>
    s = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", s)               # **b** -> *b*
    s = re.sub(r"(?<!\w)__([^_]+)__(?!\w)", r"*\1*", s)      # __b__ -> *b*
    return s


def _is_table_row(ln):
    return ln.strip().startswith("|") and ln.strip().endswith("|")


def _cells(ln):
    return [c.strip() for c in ln.strip().strip("|").split("|")]


def _is_sep(ln):
    return _is_table_row(ln) and all(re.fullmatch(r":?-{1,}:?", c or "-") for c in _cells(ln))


def _render_table(rows):
    """표 블록 → '• *첫칸* — 헤더2: 값2, 헤더3: 값3' 형식 (Slack 가독성)."""
    rows = [r for r in rows]
    sep_idx = next((i for i, r in enumerate(rows) if _is_sep(r)), None)
    header = _cells(rows[sep_idx - 1]) if sep_idx not in (None, 0) else None
    out = []
    for i, r in enumerate(rows):
        if _is_sep(r):
            continue
        if header is not None and i == sep_idx - 1:
            continue  # 헤더행은 라벨로만 쓰고 따로 출력 X
        cs = [_inline(c) for c in _cells(r)]
        lead = re.sub(r"\*+", "", cs[0]).strip() if cs else ""   # 이중 볼드 방지
        rest = cs[1:]
        if header is not None:
            labels = header[1:]
            pairs = [f"{(labels[j] if j < len(labels) else '').strip()}: {v}".lstrip(": ")
                     for j, v in enumerate(rest) if v]
            line = f"• *{lead}* — " + ", ".join(pairs) if pairs else f"• *{lead}*"
        else:
            line = "• " + " | ".join(c for c in cs if c)
        out.append(line)
    return out


def md_to_slack(text):
    lines = text.splitlines()
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if _is_table_row(ln):
            block = []
            while i < len(lines) and _is_table_row(lines[i]):
                block.append(lines[i]); i += 1
            out.extend(_render_table(block))
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if h:
            out.append("*" + _inline(h.group(2)).strip() + "*")
        elif re.fullmatch(r"\s*---+\s*", ln):
            out.append("───────────")
        else:
            ln = re.sub(r"^(\s*)[-*]\s+", r"\1• ", ln)   # 불릿
            out.append(_inline(ln))
        i += 1
    # 과도한 빈 줄 축약
    res, blank = [], 0
    for ln in out:
        if ln.strip() == "":
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        res.append(ln)
    return "\n".join(res)


# ---------- 전송 ----------

def post(url, text):
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


def chunks(text, n=LIMIT):
    buf = ""
    for ln in text.split("\n"):
        if len(buf) + len(ln) + 1 > n:
            if buf:
                yield buf
            buf = ln
        else:
            buf = buf + "\n" + ln if buf else ln
    if buf:
        yield buf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--raw", action="store_true", help="마크다운 변환 없이 그대로 전송")
    a = ap.parse_args()
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            text = f.read()
        convert = not a.raw and a.file.endswith(".md")
    elif a.text:
        text, convert = a.text, False
    else:
        text, convert = sys.stdin.read(), False
    if not text.strip():
        sys.exit("빈 메시지")
    if convert:
        text = md_to_slack(text)
    url = get_url()
    parts = list(chunks(text))
    for i, p in enumerate(parts, 1):
        prefix = f"({i}/{len(parts)})\n" if len(parts) > 1 else ""
        post(url, prefix + p)
    print(f"sent {len(parts)} message(s)")


if __name__ == "__main__":
    main()
