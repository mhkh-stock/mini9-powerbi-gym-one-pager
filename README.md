# Mini #9 — Power BI One-Pager: Gym Membership Dashboard

**SAMPLE / DEMO data only.** Fictional Lahore gym "IronWorks Gym",
fictional members, fictional payments. Never claimed as real client
or real business data.

The Power BI half of the portfolio, after Mini #8's SQL date pack:
a star-schema model, 9 DAX measures, and a 15-minute build guide that
ends in a one-page dashboard — with preview renders proving the model
first. No `.pbix` is bundled: Power BI Desktop authors it from this
model (a `.pbix` is a binary only Power BI can write — shipping one
would be faking it).

## Demo dataset

Fictional gym, Jan–Jun 2026: 60 members (50 active, 10 cancelled) ·
4 plans · 2,387 check-ins · 255 payments (252 paid, 3 failed) · paid
revenue PKR 1,562,000 · MRR PKR 307,000. Schema: `model/schema.sql` ·
CSVs: `data/*.csv` (generated deterministically, seed 9) · Dictionary:
`data/README.md` · Built database: `data/gym.db` (rebuild any time
with `python3 src/build_model.py`).

## How to run (3 steps)

1. `cd mini9-powerbi-gym-one-pager`
2. `python3 src/generate_data.py` — regenerates `data/*.csv`
   (deterministic, seed 9)
3. `python3 src/build_model.py` — builds `data/gym.db` + writes
   `outputs/kpi_summary.txt`
4. `python3 src/render_previews.py` — renders the 4 preview PNGs
5. `python3 src/checks.py` — 39 checks, all passing

Requires Python 3.10+ and SQLite (standard library) + matplotlib
for the previews. Verified on Python 3.12.3, SQLite 3.45.1.

## The model

Star schema: `dim_member` + `dim_plan` (dimensions) →
`fact_checkins` + `fact_payments` (facts), joined on member and plan.
`dim_date` covers every day Jan–Jun 2026 (181 rows). Relationships
for Power BI are listed in `powerbi/build-guide.md`.

## DAX measures (`dax/measures.dax`)

| Measure | What it answers | Verified value |
|---|---|---|
| `Total Revenue` | What did the gym actually collect? | PKR 1,562,000 (paid only) |
| `MRR` | What does the active base pay every month? | PKR 307,000 |
| `Active Members` | How many members are live right now? | 50 |
| `Churn Rate` | What share cancelled? | 16.7% (10 of 60) |
| `Total Check-ins` | How much is the gym used? | 2,387 |
| `Avg Check-ins per Active Member` | Usage per member over the window | 47.7 |
| `Avg Check-ins per Member per Week` | The comparable usage rate | 1.84 |
| `Failed Payments` | How many payments bounced? | 3 |
| `Failed Payment Rate` | Bounce rate | 1.2% (3 of 255) |

## Key findings (from the verified run)

- **Premium nearly matches Standard on revenue with 8 fewer members:**
  Standard brings 23 active members and PKR 595,000 of paid revenue;
  Premium brings 15 members and PKR 592,000. *So what:* one Premium
  member is worth ~1.5 Standard members — the upsell conversation
  pays more than the acquisition conversation.
- **The gym has two peaks, not one:** 18:00 (302 check-ins) and 7:00
  (299) together are a quarter of all visits; 19:00 adds 261 more.
  *So what:* staffing and class slots belong at 7–8 AM and 6–7 PM,
  and the midday floor (12:00–15:00) is the quiet window for
  maintenance, not for classes.
- **Friday dips, Sunday collapses:** Wednesday is the busiest day
  (421 check-ins), Friday drops to 258 and Sunday to 187 — the
  Jummah + weekend pattern is in the data, not assumed. *So what:*
  Friday-evening and Sunday programming should be lighter, and
  Sunday is the day for the deep clean, not a launch.
- **Revenue grows with the member base, then flattens:** paid revenue
  climbs every month from PKR 150,000 (Jan) to PKR 331,000 (May),
  then slips to PKR 323,000 in June — the month 4 members cancelled.
  *So what:* June's churn (4 of the 10) is the first number the owner
  should watch, because it already cost the gym its growth month.

## Preview renders (`outputs/`)

| File | Shows |
|---|---|
| `preview_revenue_by_month.png` | Paid revenue Jan–Jun: 150k → 331k → 323k |
| `preview_checkins_by_weekday.png` | Wed busiest (421), Sun quietest (187) |
| `preview_members_by_plan.png` | Active members: Standard 23, Premium 15, Basic 8, Family 4 |
| `preview_checkins_by_hour.png` | Twin peaks 7:00 (299) and 18:00 (302) |
| `kpi_summary.txt` | Headline KPIs, recomputed from the DB |

## Limits — what this mini does not do

- **One gym, six months, demo data.** Jan–Jun 2026 only, PKR only,
  60 members. A real gym replaces the four CSVs (same columns) and
  re-runs the pipeline.
- **No `.pbix` in the repo.** The 15-minute guide builds it in Power
  BI Desktop; the preview PNGs are matplotlib renders of the same
  numbers, not the dashboard itself.
- **Churn is a snapshot, not a cohort study.** 10 cancellations over
  6 months is a rate, not a retention curve — Flagship 1 does cohorts
  properly on real data.
