# Power BI build guide — IronWorks Gym one-pager (15 minutes)

**Goal:** one page that answers "is the gym healthy?" — members, money,
usage, and the two peak hours that decide staffing. No `.pbix` is
bundled: Power BI Desktop authors it from this model (a `.pbix` is a
binary only Power BI can write — shipping one would be faking it).

## 0. Files you need

- `data/members.csv`, `data/plans.csv`, `data/checkins.csv`,
  `data/payments.csv` (SAMPLE data — fictional Lahore gym, Jan–Jun 2026)
- `model/schema.sql` (the star schema; the CSVs already match it)
- `dax/measures.dax` (9 measures — copy-paste, one at a time)

## 1. Load the data (3 min)

1. Power BI Desktop → **Get Data → Text/CSV** → load the 4 CSVs.
2. Rename the queries to `dim_member`, `dim_plan`, `fact_checkins`,
   `fact_payments` (the names the DAX measures expect).
3. Set types: `join_date` / `checkin_date` / `paid_on` → Date;
   `checkin_hour` → Whole Number; `amount_pkr` / `monthly_fee_pkr` →
   Whole Number; `month` → Text.

## 2. Build the model (3 min)

Model view → drag these relationships (single direction, one-to-many):

| From | To |
|---|---|
| `dim_plan[plan_id]` | `dim_member[plan_id]` |
| `dim_plan[plan_id]` | `fact_payments[plan_id]` |
| `dim_member[member_id]` | `fact_checkins[member_id]` |
| `dim_member[member_id]` | `fact_payments[member_id]` |

Star schema: `dim_member` and `dim_plan` are the dimensions,
`fact_checkins` and `fact_payments` the facts. No relationship is
needed between the two fact tables — they join through the member.

## 3. Add the measures (3 min)

Modeling → **New measure** → paste each block from `dax/measures.dax`:
`Total Revenue`, `MRR`, `Active Members`, `Churn Rate`,
`Total Check-ins`, `Avg Check-ins per Active Member`,
`Avg Check-ins per Member per Week`, `Failed Payments`,
`Failed Payment Rate`. Format: revenue/MRR as whole-number currency
(PKR), churn/failed rates as percentages (1 decimal).

## 4. Build the page (5 min)

One page, 6 visuals, top to bottom:

| # | Visual | Fields | What it proves |
|---|---|---|---|
| 1 | 4 KPI cards (row) | `Active Members`, `MRR`, `Total Revenue`, `Churn Rate` | The gym's health at a glance |
| 2 | Clustered column | Axis: `fact_payments[month]` · Values: `Total Revenue` | Revenue trend Jan–Jun |
| 3 | Clustered column | Axis: `dim_plan[plan_name]` · Values: `Active Members` + `Total Revenue` | Which plan brings members vs money |
| 4 | Clustered column | Axis: `fact_checkins[weekday]` · Values: `Total Check-ins` | Which days are busy (sort Mon–Sun with a sort column) |
| 5 | Clustered column | Axis: `fact_checkins[checkin_hour]` · Values: `Total Check-ins` | The two peak hours that decide staffing |
| 6 | Table | `dim_member[name]`, `plan_name`, `join_date`, `status` + `Total Check-ins` | Who trains, who went quiet |

Weekday sort: add a `weekday_num` column (`WEEKDAY([checkin_date], 2)`)
and sort `weekday` by it, or Monday sorts after Sunday.

## 5. Check it (1 min)

- `Active Members` = 50, `Churn Rate` = 16.7%, `Total Revenue` =
  the paid-payments sum in `outputs/kpi_summary.txt`. If any card
  disagrees, the model relationships are wrong — not the measure.
- `Total Check-ins` and the peak-hour column must match the same file.
- Slicer (optional): `dim_member[status]` — "active only" answers
  the retention question without rebuilding the page.

## What the preview PNGs are

`outputs/preview_*.png` are matplotlib renders of the same numbers —
proof the model is right before Power BI opens, not the dashboard
itself. The real one-pager is the `.pbix` you build in the 15 minutes
above.
