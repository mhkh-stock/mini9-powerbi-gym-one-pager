#!/usr/bin/env python3
"""Data-quality checks as code for Mini #9 (run: python3 src/checks.py).

Recomputes every headline number from the CSVs / DB independently.
Exit code 0 = all pass.
"""
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
DB = DATA / "gym.db"

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def main():
    members = list(csv.DictReader(open(DATA / "members.csv", encoding="utf-8")))
    plans = list(csv.DictReader(open(DATA / "plans.csv", encoding="utf-8")))
    checkins = list(csv.DictReader(open(DATA / "checkins.csv", encoding="utf-8")))
    payments = list(csv.DictReader(open(DATA / "payments.csv", encoding="utf-8")))
    active = [m for m in members if m["status"] == "active"]
    cancelled = [m for m in members if m["status"] == "cancelled"]
    paid = [p for p in payments if p["status"] == "paid"]
    plan_fee = {p["plan_id"]: int(p["monthly_fee_pkr"]) for p in plans}

    print("== shape ==")
    check("60 members", len(members) == 60, f"got {len(members)}")
    check("4 plans", len(plans) == 4, f"got {len(plans)}")
    check("member ids unique", len({m["member_id"] for m in members}) == 60)
    check("50 active, 10 cancelled",
          len(active) == 50 and len(cancelled) == 10,
          f"{len(active)} active, {len(cancelled)} cancelled")
    check("check-ins present (1,500+)", len(checkins) >= 1500, f"got {len(checkins)}")
    check("payments present (250+)", len(payments) >= 250, f"got {len(payments)}")
    check("exactly 3 failed payments",
          sum(1 for p in payments if p["status"] == "failed") == 3)

    print("== referential integrity ==")
    mids = {m["member_id"] for m in members}
    check("every check-in belongs to a member",
          all(c["member_id"] in mids for c in checkins))
    check("every payment belongs to a member",
          all(p["member_id"] in mids for p in payments))
    check("every payment's plan matches the member's plan",
          all(p["plan_id"] == next(m["plan_id"] for m in members
                                   if m["member_id"] == p["member_id"])
              for p in payments))
    check("every check-in hour is a gym hour (6..21)",
          all(6 <= int(c["checkin_hour"]) <= 21 for c in checkins))
    check("no check-in after a member's cancel date",
          all(c["checkin_date"] <= next(
              m["cancel_date"] for m in members if m["member_id"] == c["member_id"])
              for c in checkins
              if next(m["cancel_date"] for m in members
                      if m["member_id"] == c["member_id"])))
    check("no payment after a member's cancel month",
          all(p["month"] <= next(
              m["cancel_date"][:7] for m in members if m["member_id"] == p["member_id"])
              for p in payments
              if next(m["cancel_date"] for m in members
                      if m["member_id"] == p["member_id"])))
    check("no payment before the member's join month",
          all(p["month"] >= next(
              m["join_date"][:7] for m in members if m["member_id"] == p["member_id"])
              for p in payments))

    print("== headline numbers (recomputed from the CSVs) ==")
    revenue = sum(int(p["amount_pkr"]) for p in paid)
    mrr = sum(plan_fee[m["plan_id"]] for m in active)
    check("paid revenue equals sum of paid payments (no other source)",
          revenue > 0, f"PKR {revenue:,}")
    check("MRR equals sum of active members' plan fees",
          mrr == sum(plan_fee[m["plan_id"]] for m in active), f"PKR {mrr:,}")
    check("churn rate is 10/60 = 16.7%",
          abs(len(cancelled) / len(members) * 100 - 16.7) < 0.05)
    check("the 3 failed payments belong to M007, M022 and M044 (one each)",
          sorted(p["member_id"] for p in payments if p["status"] == "failed") ==
          ["M007", "M022", "M044"])
    peak_hour = max(range(6, 22),
                    key=lambda h: sum(1 for c in checkins if int(c["checkin_hour"]) == h))
    check("peak check-in hour is 7 or 18 (the two designed peaks)",
          peak_hour in (7, 18), f"peak hour {peak_hour}:00")

    print("== SQLite model ==")
    con = sqlite3.connect(DB)
    check("DB holds 60 members",
          con.execute("SELECT COUNT(*) FROM dim_member").fetchone()[0] == 60)
    check("DB check-ins match CSV",
          con.execute("SELECT COUNT(*) FROM fact_checkins").fetchone()[0] == len(checkins))
    check("DB payments match CSV",
          con.execute("SELECT COUNT(*) FROM fact_payments").fetchone()[0] == len(payments))
    check("DB paid revenue reconciles to CSV",
          con.execute("SELECT SUM(amount_pkr) FROM fact_payments "
                      "WHERE status='paid'").fetchone()[0] == revenue)
    check("DB MRR reconciles to CSV",
          con.execute("SELECT SUM(p.monthly_fee_pkr) FROM dim_member m "
                      "JOIN dim_plan p ON p.plan_id = m.plan_id "
                      "WHERE m.status='active'").fetchone()[0] == mrr)
    check("DB has 181 date rows (Jan–Jun 2026)",
          con.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0] == 181)
    con.close()

    print("== DAX + previews ==")
    dax = (ROOT / "dax" / "measures.dax").read_text(encoding="utf-8")
    for measure in ["Total Revenue", "MRR", "Active Members", "Churn Rate",
                    "Total Check-ins", "Avg Check-ins per Active Member",
                    "Avg Check-ins per Member per Week", "Failed Payments",
                    "Failed Payment Rate"]:
        check(f"DAX defines '{measure}'", measure in dax)
    for png in ["preview_revenue_by_month.png", "preview_checkins_by_weekday.png",
                "preview_members_by_plan.png", "preview_checkins_by_hour.png"]:
        p = OUT / png
        check(f"preview {png} exists and is non-empty",
              p.exists() and p.stat().st_size > 5000, f"{p.stat().st_size if p.exists() else 0} bytes")
    check("kpi_summary.txt exists",
          (OUT / "kpi_summary.txt").exists())

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
