#!/usr/bin/env python3
"""Build an exact, reviewable Todoist task draft from parse.py JSON output."""

import json
import sys
from pathlib import Path


def item_content(item):
    name = item["kor_name"]
    option = item.get("option", "")
    qty = item["qty"]
    if option:
        return f"{name} ({option}) × {qty}"
    return f"{name} × {qty}"


def main():
    if len(sys.argv) != 3:
        print("usage: build_draft.py <parsed.json> <draft.json>", file=sys.stderr)
        return 2

    parsed_path = Path(sys.argv[1])
    draft_path = Path(sys.argv[2])
    parsed = json.loads(parsed_path.read_text(encoding="utf-8"))

    if "error" in parsed:
        raise ValueError(f"parse output contains an error: {parsed['error']}")

    shopping = [
        {
            "content": item_content(item),
            "product_id": item["product_id"],
            "kor_name": item["kor_name"],
            "option": item.get("option", ""),
            "qty": item["qty"],
        }
        for item in parsed["shopping"]
    ]

    recipients = [
        {
            "name": recipient["name"],
            "items": [
                {
                    "content": item_content(item),
                    "product_id": item["product_id"],
                    "kor_name": item["kor_name"],
                    "option": item.get("option", ""),
                    "qty": item["qty"],
                }
                for item in recipient["items"]
            ],
        }
        for recipient in parsed["recipients"]
    ]

    draft = {
        "shopping_parent": "사야할 제품들",
        "recipient_parent": "수취인별 주문",
        "shopping": shopping,
        "recipients": recipients,
        "buyer_count": parsed["buyer_count"],
        "shopping_line_count": parsed["shopping_line_count"],
        "verbatim_policy": True,
        "due_policy": "parents_only",
    }

    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(draft_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
