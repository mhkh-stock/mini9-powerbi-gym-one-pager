#!/usr/bin/env python3
"""Build data/gym.db from the CSVs (run: python3 src/build_model.py).

Also writes outputs/kpi_summary.txt — the headline numbers the README
and the build guide cite (recomputed here, asserted in src/checks.py).
"""
import csv
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "gym.db"
SCHEMA = ROOT / "model" / "schema.sql"


def main():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    for table, path in [("dim_plan", "plans.csv"), ("dim_member", "members.csv"),
                        ("fact_checkins", "checkins.csv"),
                        ("fact_payments", "payments.csv")]:
        rows = list(csv.DictReader(open(ROOT / "data" / path, encoding="utf-8")))
        cols = rows[0].keys()
        con.executemany(
            f"INSERT INTO {table} ({','.join(cols)}) "
            f"VALUES ({','.join('?' * len(cols))})",
            [[r[c] for c in cols] for r in rows])
    # Date dimension: every day Jan–Jun 2026.
    d = date(2026, 1, 1)
    while d <= date(2026, 6, 30):
        con.execute(
            "INSERT INTO dim_date VALUES (?,?,?,?,?,?)",
            (d.isoformat(), d.year, d.month, d.strftime("%Y-%m"),
             d.strftime("%A"), 1 if d.weekday() >= 5 else 0))
        d += timedelta(days=1)
    con.commit()
    n = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
         for t in ("dim_member", "dim_plan", "fact_checkins", "fact_payments")}
    rev = con.execute("SELECT SUM(amount_pkr) FROM fact_payments "
                      "WHERE status='paid'").fetchone()[0]
    mrr = con.execute(
        "SELECT SUM(p.monthly_fee_pkr) FROM dim_member m "
        "JOIN dim_plan p ON p.plan_id = m.plan_id WHERE m.status='active'"
    ).fetchone()[0]
    churn = con.execute("SELECT COUNT(*) FROM dim_member "
                        "WHERE status='cancelled'").fetchone()[0]
    peak = con.execute(
        "SELECT checkin_hour, COUNT(*) c FROM fact_checkins "
        "GROUP BY checkin_hour ORDER BY c DESC LIMIT 1").fetchone()
    (ROOT / "outputs" / "kpi_summary.txt").write_text(
        f"members: {n['dim_member']}\n"
        f"active members: {n['dim_member'] - churn}\n"
        f"cancelled members: {churn}\n"
        f"check-ins: {n['fact_checkins']}\n"
        f"payments: {n['fact_payments']}\n"
        f"paid revenue Jan-Jun 2026: PKR {rev:,}\n"
        f"MRR (active members x plan fee): PKR {mrr:,}\n"
        f"churn rate: {churn / n['dim_member'] * 100:.1f}%\n"
        f"peak check-in hour: {peak[0]}:00 ({peak[1]} check-ins)\n",
        encoding="utf-8")
    print(f"loaded gym.db: {n}")
    print(f"paid revenue PKR {rev:,} | MRR PKR {mrr:,} | peak hour {peak[0]}:00")
    con.close()


if __name__ == "__main__":
    main()
