#!/usr/bin/env python3
"""Deterministically verify a Todoist draft against parse.py JSON."""

import json
import sys
from pathlib import Path

from build_draft import item_content


def expected_draft(parsed):
    return {
        "shopping_parent": "사야할 제품들",
        "recipient_parent": "수취인별 주문",
        "shopping": [
            {**item, "content": item_content(item)}
            for item in parsed["shopping"]
        ],
        "recipients": [
            {
                "name": recipient["name"],
                "items": [
                    {**item, "content": item_content(item)}
                    for item in recipient["items"]
                ],
            }
            for recipient in parsed["recipients"]
        ],
        "buyer_count": parsed["buyer_count"],
        "shopping_line_count": parsed["shopping_line_count"],
        "verbatim_policy": True,
        "due_policy": "parents_only",
    }


def first_difference(expected, actual, path="$"):
    if type(expected) is not type(actual):
        return f"{path}: type {type(expected).__name__} != {type(actual).__name__}"
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            return f"{path}: keys {list(expected)} != {list(actual)}"
        for key in expected:
            difference = first_difference(expected[key], actual[key], f"{path}.{key}")
            if difference:
                return difference
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            return f"{path}: length {len(expected)} != {len(actual)}"
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            difference = first_difference(
                expected_item, actual_item, f"{path}[{index}]"
            )
            if difference:
                return difference
    elif expected != actual:
        return f"{path}: {expected!r} != {actual!r}"
    return None


def main():
    if len(sys.argv) != 3:
        print("usage: verify_draft.py <parsed.json> <draft.json>", file=sys.stderr)
        return 2

    parsed = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    actual = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    difference = first_difference(expected_draft(parsed), actual)
    if difference:
        print(f"DETERMINISTIC_VERDICT: FAIL\n{difference}")
        return 1

    print("DETERMINISTIC_VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
