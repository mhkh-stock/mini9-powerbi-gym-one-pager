#!/usr/bin/env python3
"""Generate SAMPLE gym data for Mini #9 (deterministic, seed 9).

Fictional Lahore gym "IronWorks Gym": 4 plans, 60 members, Jan–Jun 2026.
Writes data/members.csv, data/plans.csv, data/checkins.csv,
data/payments.csv. Re-running reproduces the identical files.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 9
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

PLANS = [
    ("P1", "Basic", 3000, "Gym floor access, off-peak hours"),
    ("P2", "Standard", 5000, "Full access + 2 group classes / week"),
    ("P3", "Premium", 8000, "Full access + unlimited classes + sauna"),
    ("P4", "Family", 12000, "2 adults + 2 children, full access"),
]

FIRST = ["Ahmed", "Ayesha", "Bilal", "Fatima", "Hassan", "Hina", "Usman",
         "Zainab", "Omar", "Maryam", "Ali", "Sana", "Danish", "Nida",
         "Kamran", "Rabia", "Faisal", "Mehwish", "Tariq", "Sadia"]
LAST = ["Khan", "Ahmed", "Ali", "Malik", "Hussain", "Raza", "Butt",
        "Sheikh", "Chaudhry", "Iqbal", "Akhtar", "Nawaz"]

# Peak-hour weights: early morning + evening dominate a real gym day.
HOUR_WEIGHTS = {6: 9, 7: 12, 8: 10, 9: 5, 10: 4, 11: 3, 12: 3, 13: 2,
                14: 2, 15: 3, 16: 4, 17: 8, 18: 12, 19: 11, 20: 8, 21: 4}
# Weekday weights (Mon=0): Mon/Wed/Fri heavier, Fri lighter (Jummah), Sun lightest.
WEEKDAY_WEIGHTS = [14, 12, 14, 12, 9, 13, 6]


def _pick(rng, weights):
    items = list(weights.items())
    total = sum(w for _, w in items)
    x = rng.uniform(0, total)
    for k, w in items:
        x -= w
        if x <= 0:
            return k
    return items[-1][0]


def main():
    rng = random.Random(SEED)
    DATA.mkdir(parents=True, exist_ok=True)

    with open(DATA / "plans.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["plan_id", "plan_name", "monthly_fee_pkr", "includes"])
        w.writerows(PLANS)
    plan_fee = {p[0]: p[2] for p in PLANS}
    # Plan mix: Standard is the volume plan, Premium the revenue plan.
    plan_pick = ["P1"] * 12 + ["P2"] * 26 + ["P3"] * 16 + ["P4"] * 6

    members, checkins, payments = [], [], []
    start = date(2026, 1, 1)
    end = date(2026, 6, 30)
    names = set()
    for i in range(1, 61):
        while True:
            name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            if name not in names:
                names.add(name)
                break
        join = start + timedelta(days=rng.randrange(0, 150))
        plan = plan_pick[i - 1] if i <= len(plan_pick) else rng.choice(plan_pick)
        rng.shuffle(plan_pick)
        status, cancel = "active", ""
        # 10 members churn (cancel) during the window, spread Feb–Jun.
        if i in (5, 11, 18, 23, 29, 34, 41, 47, 53, 58):
            cancel = join + timedelta(days=rng.randrange(30, 120))
            if cancel > end:
                cancel = end
            status = "cancelled"
        members.append({
            "member_id": f"M{i:03d}", "name": name,
            "gender": rng.choice(["M", "F"]),
            "join_date": join.isoformat(), "plan_id": plan,
            "status": status,
            "cancel_date": cancel.isoformat() if cancel else "",
        })

    for m in members:
        join = date.fromisoformat(m["join_date"])
        last = date.fromisoformat(m["cancel_date"]) if m["cancel_date"] else end
        # Payments: one per active month (join month .. last active month).
        month = date(join.year, join.month, 1)
        while month <= date(last.year, last.month, 1):
            payments.append({
                "payment_id": f"PAY-{m['member_id']}-{month.strftime('%Y%m')}",
                "member_id": m["member_id"], "plan_id": m["plan_id"],
                "month": month.strftime("%Y-%m"),
                "amount_pkr": plan_fee[m["plan_id"]],
                "status": "paid",
                "paid_on": (month + timedelta(days=rng.randrange(1, 5))).isoformat(),
            })
            month = date(month.year + (1 if month.month == 12 else 0),
                         month.month % 12 + 1, 1)
        # Check-ins: one row per visit, only while the membership is live.
        # Base rate by plan (Premium trains most, Basic least) + noise.
        base = {"P1": 7, "P2": 10, "P3": 13, "P4": 11}[m["plan_id"]]
        day = join
        cid = 0
        while day <= last:
            if rng.random() < (base / 30) * (WEEKDAY_WEIGHTS[day.weekday()] / 11.4):
                hour = _pick(rng, HOUR_WEIGHTS)
                checkins.append({
                    "checkin_id": f"CHK-{m['member_id']}-{day.strftime('%Y%m%d')}-{cid}",
                    "member_id": m["member_id"],
                    "checkin_date": day.isoformat(),
                    "checkin_hour": hour,
                    "weekday": day.strftime("%A"),
                })
                cid += 1
            day += timedelta(days=1)

    # 3 failed payments, by design: one each for M007 (Mar), M022 (Apr),
    # M044 (Mar). A member only has a row for months they were active, so
    # fall back to that member's earliest payment if the target month
    # is outside their active window — exactly 3 failed rows either way.
    for mid, target_month in [("M007", "2026-03"), ("M022", "2026-04"),
                              ("M044", "2026-03")]:
        mine = [p for p in payments if p["member_id"] == mid]
        row = next((p for p in mine if p["month"] == target_month), mine[0])
        row["status"] = "failed"
        row["paid_on"] = ""

    for name, rows, fields in [
        ("members.csv", members, ["member_id", "name", "gender", "join_date",
                                  "plan_id", "status", "cancel_date"]),
        ("checkins.csv", checkins, ["checkin_id", "member_id", "checkin_date",
                                    "checkin_hour", "weekday"]),
        ("payments.csv", payments, ["payment_id", "member_id", "plan_id",
                                    "month", "amount_pkr", "status", "paid_on"]),
    ]:
        with open(DATA / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    print(f"members: {len(members)} (active "
          f"{sum(1 for m in members if m['status'] == 'active')}, "
          f"cancelled {sum(1 for m in members if m['status'] == 'cancelled')})")
    print(f"check-ins: {len(checkins)}")
    print(f"payments: {len(payments)} "
          f"(paid {sum(1 for p in payments if p['status'] == 'paid')}, "
          f"failed {sum(1 for p in payments if p['status'] == 'failed')})")
    print(f"paid revenue: PKR "
          f"{sum(p['amount_pkr'] for p in payments if p['status'] == 'paid'):,}")


if __name__ == "__main__":
    main()
