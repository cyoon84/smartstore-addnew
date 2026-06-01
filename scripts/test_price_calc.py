#!/usr/bin/env python3
"""price_calc.py 회귀 테스트 — LEARNED_RULES 의 실제 케이스로 검증.

  python3 scripts/test_price_calc.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import price_calc as pc

CASES = []


def check(name, got, want, tol=0):
    ok = abs(got - want) <= tol
    CASES.append((name, ok, got, want))
    return ok


# §1 Chosen Foods Avocado Mayo: 12.99 + $5, fx1083, tax0 → ₩20,860, 마진 $5
r = pc.mode_std(12.99, 5, 1083, 0)
check("§1 std Chosen Foods sell_krw", r["sell_krw"], 20860)
check("§1 std 마진 검산", round(r["verification"]["realized_margin_cad"]), 5)

# §5 Aveeno Baby Lotion HST-incl: 16.99 + $3, fx1070, tax13 → ₩22,900, 마진 ~3.0
r = pc.mode_hst_incl(16.99, 3, 1070, 13)
check("§5 hst_incl Aveeno sell_krw", r["sell_krw"], 22900)
check("§5 hst_incl 마진 검산", round(r["verification"]["realized_margin_cad"], 1), 3.0, 0.05)

# §6-2 Kellogg target KRW 8000, fx1070 → 8000, 실수령 7472
r = pc.mode_target_krw(8000, 1070)
check("§6-2 target_krw sell_krw", r["sell_krw"], 8000)
check("§6-2 target_krw 실수령", round(r["verification"]["after_fee_krw"]), 7472)

# §6-3 CAD target 8, fx1070 → gross-up
r = pc.mode_target_cad(8, 1070)
check("§6-3 target_cad sell_krw 양수", 1 if r["sell_krw"] > 8000 else 0, 1)

# §6-4 ACE 팀빗: target 29900, cost16.99, tax13, fx1090 → 마진 ~6.42, 25%
r = pc.mode_reverse(29900, 16.99, 1090, 13)
check("§6-4 reverse 마진 CAD", round(r["verification"]["margin_cad"], 2), 6.42, 0.01)
check("§6-4 reverse 마진율", round(r["verification"]["margin_rate"], 2), 0.25, 0.01)

# §11-1 Kinder Kinderini: cost6.97, pct30, fx1100, tax0 → ₩12,100, ~30%
r = pc.mode_pct_net(6.97, 30, 1100, 0)
check("§11-1 pct_net sell_krw", r["sell_krw"], 12100)
check("§11-1 pct_net 실현 마진율", round(r["verification"]["realized_margin_pct"]), 30, 1)

# §7 shipping 5000 x 3 → 15000
r = pc.mode_shipping(5000, 3)
check("§7 shipping_total", r["shipping_total"], 15000)


def main():
    passed = sum(1 for _, ok, *_ in CASES if ok)
    for name, ok, got, want in CASES:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}: got={got} want={want}")
    print(f"\n{passed}/{len(CASES)} passed")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
