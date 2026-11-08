-- Mini #9 — Power BI One-Pager (Gym): star schema
-- SQLite. Rebuild any time: python3 src/build_model.py
-- The .db file is NOT uploaded to GitHub (rebuildable from the CSVs).

DROP TABLE IF EXISTS fact_checkins;
DROP TABLE IF EXISTS fact_payments;
DROP TABLE IF EXISTS dim_member;
DROP TABLE IF EXISTS dim_plan;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_plan (
    plan_id TEXT PRIMARY KEY,
    plan_name TEXT NOT NULL,
    monthly_fee_pkr INTEGER NOT NULL CHECK (monthly_fee_pkr > 0),
    includes TEXT
);

CREATE TABLE dim_member (
    member_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('M', 'F')),
    join_date TEXT NOT NULL,
    plan_id TEXT NOT NULL REFERENCES dim_plan (plan_id),
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled')),
    cancel_date TEXT
);

CREATE TABLE dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_label TEXT NOT NULL,
    weekday TEXT NOT NULL,
    is_weekend INTEGER NOT NULL CHECK (is_weekend IN (0, 1))
);

CREATE TABLE fact_checkins (
    checkin_id TEXT PRIMARY KEY,
    member_id TEXT NOT NULL REFERENCES dim_member (member_id),
    checkin_date TEXT NOT NULL REFERENCES dim_date (date),
    checkin_hour INTEGER NOT NULL CHECK (checkin_hour BETWEEN 0 AND 23),
    weekday TEXT NOT NULL
);

CREATE TABLE fact_payments (
    payment_id TEXT PRIMARY KEY,
    member_id TEXT NOT NULL REFERENCES dim_member (member_id),
    plan_id TEXT NOT NULL REFERENCES dim_plan (plan_id),
    month TEXT NOT NULL,
    amount_pkr INTEGER NOT NULL CHECK (amount_pkr > 0),
    status TEXT NOT NULL CHECK (status IN ('paid', 'failed')),
    paid_on TEXT
);

CREATE INDEX idx_checkins_member ON fact_checkins (member_id);
CREATE INDEX idx_checkins_date ON fact_checkins (checkin_date);
CREATE INDEX idx_payments_member ON fact_payments (member_id);
CREATE INDEX idx_payments_month ON fact_payments (month);
