#!/usr/bin/env python3
"""Render preview charts for Mini #9 (run: python3 src/render_previews.py).

matplotlib renders of the same numbers the Power BI page will show —
proof the model is right before Power BI opens, not the dashboard itself.
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "gym.db"
OUT = ROOT / "outputs"

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]


def bar(title, labels, values, path, ylabel, fmt="{:,.0f}"):
    plt.figure(figsize=(8, 4.5))
    bars = plt.bar(labels, values, color="#1F4E79")
    plt.title(title, fontsize=13, fontweight="bold")
    plt.ylabel(ylabel)
    plt.xticks(rotation=30, ha="right")
    for b, v in zip(bars, values):
        plt.text(b.get_x() + b.get_width() / 2, b.get_height(), fmt.format(v),
                 ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"wrote {path}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)

    months, rev = zip(*con.execute(
        "SELECT month, SUM(amount_pkr) FROM fact_payments "
        "WHERE status='paid' GROUP BY month ORDER BY month"))
    bar("Paid revenue by month (PKR) — IronWorks Gym, Jan–Jun 2026",
        list(months), list(rev), OUT / "preview_revenue_by_month.png",
        "PKR", fmt="PKR {:,.0f}")

    days = dict(con.execute(
        "SELECT weekday, COUNT(*) FROM fact_checkins GROUP BY weekday"))
    bar("Check-ins by weekday",
        WEEKDAYS, [days.get(d, 0) for d in WEEKDAYS],
        OUT / "preview_checkins_by_weekday.png", "Check-ins")

    plans, members = zip(*con.execute(
        "SELECT p.plan_name, COUNT(*) FROM dim_member m "
        "JOIN dim_plan p ON p.plan_id = m.plan_id "
        "WHERE m.status='active' GROUP BY p.plan_name ORDER BY COUNT(*) DESC"))
    bar("Active members by plan",
        list(plans), list(members), OUT / "preview_members_by_plan.png",
        "Active members")

    hours = dict(con.execute(
        "SELECT checkin_hour, COUNT(*) FROM fact_checkins GROUP BY checkin_hour"))
    xs = sorted(hours)
    bar("Check-ins by hour of day (the two peaks decide staffing)",
        [f"{h}:00" for h in xs], [hours[h] for h in xs],
        OUT / "preview_checkins_by_hour.png", "Check-ins")
    con.close()


if __name__ == "__main__":
    main()
