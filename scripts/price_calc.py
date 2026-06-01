#!/usr/bin/env python3
"""
price_calc.py — finchmart_ca 스마트스토어 가격 산정 결정론적 엔진

LEARNED_RULES.md 의 가격 산식(§1, §3, §5, §6, §7, §11)을 코드로 고정한 것.
LLM 이 손으로 계산할 때 생기는 오차를 없애기 위함. CLAUDE.md 워크플로에서
가격을 낼 때는 항상 이 스크립트를 거친다.

공통 상수
  NAVER_FEE = 0.066   # 네이버 스마트스토어 수수료 (gross-up 기준)

지원 모드 (--mode)
  std        §1/§3  원가 + 마진 + (세금) → 수수료 gross-up → 환산        [ceil_10]
  hst_incl   §5     원가에 HST 이미 포함 → 마진 + gross-up → 환산         [round_100]
  target_krw §6-2   KRW 목표가 그대로 listed price (수수료 차감 실수령 참고)
  target_cad §6-3   CAD 목표가 → gross-up → 환산                          [round_100]
  reverse    §6-4   KRW 목표가 + 원가 → 실 마진 역산 (기록·검산용)
  pct_net    §11-1  "수수료 감안 N%" 순마진 → 판매가 = 원가KRW/(0.934-N/100) [round_100]
  shipping   §7     배송비 수량당 단순 곱셈 (묶음 없음)

사용 예
  python price_calc.py std        --cost 12.99 --markup 5   --fx 1083 --tax 0
  python price_calc.py hst_incl   --cost 16.99 --markup 3   --fx 1070 --tax 13
  python price_calc.py target_krw --target 8000  --fx 1070
  python price_calc.py target_cad --target 8     --fx 1070
  python price_calc.py reverse    --target 29900 --cost 16.99 --tax 13 --fx 1090
  python price_calc.py pct_net    --cost 6.97  --pct 30    --fx 1100 --tax 0
  python price_calc.py shipping   --unit 5000  --qty 3

  --json 을 붙이면 product_info.json 의 pricing 블록에 그대로 넣을 dict 를 출력.
"""
import argparse
import json
import math
import sys

NAVER_FEE = 0.066
FEE_KEEP = 1 - NAVER_FEE  # 0.934


def ceil_10(x: float) -> int:
    """10원 단위 올림 (§1)."""
    return int(math.ceil(x / 10.0) * 10)


def round_100(x: float) -> int:
    """100원 단위 반올림 (§5/§6/§11)."""
    return int(round(x / 100.0) * 100)


def _round(x: float, mode: str) -> int:
    return ceil_10(x) if mode == "ceil_10" else round_100(x)


def _tax_rate(tax) -> float:
    """13 또는 0.13 어느 쪽으로 줘도 비율로 정규화."""
    t = float(tax)
    return t / 100.0 if t > 1 else t


# ---------------------------------------------------------------- modes

def mode_std(cost, markup, fx, tax, rounding="ceil_10"):
    """§1 + §3: 세전 원가 + (세금) + 마진 → 수수료 gross-up → KRW."""
    tr = _tax_rate(tax)
    cost_with_tax = cost * (1 + tr)
    sell_pre_fee = cost_with_tax + markup
    sell_original = sell_pre_fee / FEE_KEEP
    sell_krw = _round(sell_original * fx, rounding)
    # 검산: 실수령 - 원가(세포함) = 마진
    realized_margin = (sell_krw * FEE_KEEP) / fx - cost_with_tax
    return {
        "pricing_mode": "cost_plus",
        "cost_original": round(cost, 4),
        "tax_rate": tr,
        "cost_with_tax": round(cost_with_tax, 4),
        "markup": round(markup, 4),
        "markup_currency": "CAD",
        "sell_pre_fee": round(sell_pre_fee, 4),
        "platform_fee_rate": NAVER_FEE,
        "sell_original": round(sell_original, 4),
        "exchange_rate": fx,
        "sell_krw": sell_krw,
        "rounding": rounding,
        "verification": {"realized_margin_cad": round(realized_margin, 4)},
    }


def mode_hst_incl(cost, markup, fx, tax, rounding="round_100"):
    """§5: 원가에 HST 포함 → 가산 스킵, 마진 + gross-up."""
    tr = _tax_rate(tax)
    cost_with_tax = cost  # 가산 X
    sell_pre_fee = cost_with_tax + markup
    sell_original = sell_pre_fee / FEE_KEEP
    sell_krw = _round(sell_original * fx, rounding)
    realized_margin = (sell_krw * FEE_KEEP) / fx - cost_with_tax
    return {
        "pricing_mode": "cost_plus_hst_included",
        "cost_original": round(cost, 4),
        "tax_label": f"HST {int(tr*100)}% (included in cost)",
        "tax_added_to_cost": False,
        "cost_with_tax": round(cost_with_tax, 4),
        "markup": round(markup, 4),
        "markup_currency": "CAD",
        "sell_pre_fee": round(sell_pre_fee, 4),
        "platform_fee_rate": NAVER_FEE,
        "sell_original": round(sell_original, 4),
        "exchange_rate": fx,
        "sell_krw": sell_krw,
        "rounding": rounding,
        "verification": {"realized_margin_cad": round(realized_margin, 4)},
    }


def mode_target_krw(target, fx):
    """§6-2: KRW 목표가 그대로. 실수령/CAD 환산은 참고용."""
    after_fee = target * FEE_KEEP
    after_fee_cad = after_fee / fx
    return {
        "pricing_mode": "target_match",
        "target_currency": "KRW",
        "target_value": target,
        "sell_krw": int(target),
        "platform_fee_rate": NAVER_FEE,
        "exchange_rate": fx,
        "verification": {
            "after_fee_krw": round(after_fee, 2),
            "after_fee_cad": round(after_fee_cad, 4),
        },
    }


def mode_target_cad(target, fx, rounding="round_100"):
    """§6-3: CAD 목표가 → gross-up → 환산."""
    sell_original = target / FEE_KEEP
    sell_krw = _round(sell_original * fx, rounding)
    return {
        "pricing_mode": "target_match",
        "target_currency": "CAD",
        "target_value": target,
        "platform_fee_rate": NAVER_FEE,
        "sell_original": round(sell_original, 4),
        "exchange_rate": fx,
        "sell_krw": sell_krw,
        "rounding": rounding,
    }


def mode_reverse(target, cost, fx, tax):
    """§6-4: KRW 목표가 + 원가 → 실 마진 역산."""
    tr = _tax_rate(tax)
    after_fee_krw = target * FEE_KEEP
    realized_cad = after_fee_krw / fx
    cost_with_tax = cost * (1 + tr)
    margin_cad = realized_cad - cost_with_tax
    margin_rate = margin_cad / realized_cad if realized_cad else 0.0
    # 마진 합리성 코멘트 (LEARNED_RULES §6-4)
    if margin_cad <= 5:
        comment = "일반 유통 정상 범위 ($2~5)"
    else:
        comment = "$5 초과 — 품목 특성(미출시·한정·콜라보·굿즈)이면 합리적, 아니면 재검토 권장"
    return {
        "pricing_mode": "target_match",
        "target_currency": "KRW",
        "target_value": target,
        "sell_krw": int(target),
        "cost_original": round(cost, 4),
        "tax_rate": tr,
        "cost_with_tax": round(cost_with_tax, 4),
        "platform_fee_rate": NAVER_FEE,
        "exchange_rate": fx,
        "markup": round(margin_cad, 4),
        "markup_note": "역산",
        "verification": {
            "method": "reverse_margin",
            "after_fee_krw": round(after_fee_krw, 2),
            "realized_cad": round(realized_cad, 4),
            "margin_cad": round(margin_cad, 4),
            "margin_rate": round(margin_rate, 4),
            "margin_comment": comment,
        },
    }


def mode_pct_net(cost, pct, fx, tax, rounding="round_100"):
    """§11-1: "수수료 감안 N%" 순마진. 판매가 = 원가KRW / (0.934 - N/100)."""
    tr = _tax_rate(tax)
    cost_with_tax = cost * (1 + tr)
    cost_krw = cost_with_tax * fx
    denom = FEE_KEEP - pct / 100.0
    if denom <= 0:
        raise ValueError(f"N%={pct} 가 너무 커서 분모(0.934 - N/100)가 0 이하입니다.")
    sell = cost_krw / denom
    sell_krw = _round(sell, rounding)
    net_profit = sell_krw * FEE_KEEP - cost_krw
    realized_rate = net_profit / sell_krw if sell_krw else 0.0
    return {
        "pricing_mode": "percent_net_margin",
        "cost_original": round(cost, 4),
        "tax_rate": tr,
        "cost_with_tax": round(cost_with_tax, 4),
        "cost_krw": round(cost_krw, 2),
        "target_net_margin_pct": pct,
        "platform_fee_rate": NAVER_FEE,
        "exchange_rate": fx,
        "sell_krw": sell_krw,
        "rounding": rounding,
        "verification": {
            "net_profit_krw": round(net_profit, 2),
            "realized_margin_pct": round(realized_rate * 100, 2),
        },
    }


def mode_shipping(unit, qty):
    """§7: 배송비 수량당 단순 곱셈 (묶음 없음)."""
    return {
        "shipping_rule": f"수량당 {int(unit):,}원 (묶음 없음)",
        "unit": int(unit),
        "qty": int(qty),
        "shipping_total": int(unit) * int(qty),
    }


# ---------------------------------------------------------------- cli

def _fmt(result) -> str:
    lines = []
    for k, v in result.items():
        if isinstance(v, dict):
            lines.append(f"{k}:")
            for kk, vv in v.items():
                lines.append(f"    {kk}: {vv}")
        else:
            if k == "sell_krw":
                lines.append(f"{k}: ₩{int(v):,}")
            else:
                lines.append(f"{k}: {v}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="finchmart_ca 가격 산정 엔진")
    p.add_argument("mode", choices=[
        "std", "hst_incl", "target_krw", "target_cad", "reverse", "pct_net", "shipping"])
    p.add_argument("--cost", type=float, help="원가 (CAD, 세전 또는 HST포함)")
    p.add_argument("--markup", type=float, default=0.0, help="마진 (CAD)")
    p.add_argument("--fx", type=float, help="CAD→KRW 환율")
    p.add_argument("--tax", type=float, default=0.0, help="세율 (13 또는 0.13)")
    p.add_argument("--target", type=float, help="목표 판매가 (KRW 또는 CAD)")
    p.add_argument("--pct", type=float, help="순마진 %% (수수료 감안)")
    p.add_argument("--unit", type=float, help="배송비 수량당 단가 (KRW)")
    p.add_argument("--qty", type=int, default=1, help="수량")
    p.add_argument("--rounding", choices=["ceil_10", "round_100"], help="반올림 방식 override")
    p.add_argument("--json", action="store_true", help="JSON 으로 출력")
    a = p.parse_args(argv)

    try:
        if a.mode == "std":
            _need(a, ["cost", "fx"])
            r = mode_std(a.cost, a.markup, a.fx, a.tax, a.rounding or "ceil_10")
        elif a.mode == "hst_incl":
            _need(a, ["cost", "fx"])
            r = mode_hst_incl(a.cost, a.markup, a.fx, a.tax, a.rounding or "round_100")
        elif a.mode == "target_krw":
            _need(a, ["target", "fx"])
            r = mode_target_krw(a.target, a.fx)
        elif a.mode == "target_cad":
            _need(a, ["target", "fx"])
            r = mode_target_cad(a.target, a.fx, a.rounding or "round_100")
        elif a.mode == "reverse":
            _need(a, ["target", "cost", "fx"])
            r = mode_reverse(a.target, a.cost, a.fx, a.tax)
        elif a.mode == "pct_net":
            _need(a, ["cost", "pct", "fx"])
            r = mode_pct_net(a.cost, a.pct, a.fx, a.tax, a.rounding or "round_100")
        elif a.mode == "shipping":
            _need(a, ["unit"])
            r = mode_shipping(a.unit, a.qty)
    except ValueError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1

    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else _fmt(r))
    return 0


def _need(a, fields):
    missing = [f for f in fields if getattr(a, f) is None]
    if missing:
        raise ValueError(f"--{', --'.join(missing)} 인자가 필요합니다 (mode={a.mode}).")


if __name__ == "__main__":
    sys.exit(main())
