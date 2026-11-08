# Data dictionary — Mini #9 (IronWorks Gym, SAMPLE)

Fictional Lahore gym, Jan–Jun 2026. 60 members, 4 plans, 2,387
check-ins, 255 payments. Generated deterministically
(`src/generate_data.py`, seed 9) — re-running reproduces the identical
files. No real person, gym or payment is involved.

## Files

| File | What it is |
|---|---|
| `plans.csv` | 4 membership plans with monthly fees |
| `members.csv` | 60 members: join date, plan, status, cancel date |
| `checkins.csv` | 2,387 visits: member, date, hour, weekday |
| `payments.csv` | 255 monthly payments: member, plan, month, amount, status |
| `gym.db` | SQLite star-schema load (`model/schema.sql`); rebuild with `python3 src/build_model.py`; NOT uploaded (rebuildable from the CSVs) |

## Columns

**plans.csv** — `plan_id` (P1–P4) · `plan_name` (Basic / Standard /
Premium / Family) · `monthly_fee_pkr` (3,000 / 5,000 / 8,000 / 12,000)
· `includes` (what the plan covers).

**members.csv** — `member_id` (M001–M060) · `name` · `gender` (M/F) ·
`join_date` (2026-01-01–2026-05-30) · `plan_id` · `status`
(active/cancelled) · `cancel_date` (blank unless cancelled; 10 members
cancelled Mar–Jun 2026).

**checkins.csv** — `checkin_id` · `member_id` · `checkin_date`
(2026-01-01–2026-06-30) · `checkin_hour` (6–21) · `weekday`.
One row per visit; never after the member's cancel date. Visit
probability follows the designed pattern: mornings (7–8) and evenings
(18–19) heaviest, Friday lighter, Sunday lightest.

**payments.csv** — `payment_id` · `member_id` · `plan_id` · `month`
(YYYY-MM) · `amount_pkr` (= the plan's monthly fee) · `status`
(paid/failed) · `paid_on` (blank when failed). One row per member per
active month. Exactly 3 failed payments (one each for M007, M022,
M044) — the failed-payment rate is 1.2%.

## Design notes (what the data was built to show)

- Plan mix is Standard-led on members (23 active) but Premium-led on
  value (PKR 120,000 of the PKR 307,000 MRR) — the upsell finding.
- Revenue grows monthly Jan–May, then dips in June when 4 members
  cancel — the churn finding.
- Check-ins have twin peaks (7:00 and 18:00) and a Friday/Sunday dip —
  the staffing finding.
