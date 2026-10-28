# KPI

Keep the numbers in one place: `data/kpi-tracker.md`.

## Variables

request: $ARGUMENTS
- empty: show the status table
- `add <metric> <value> [note]`: record a new reading
- `define <metric> <unit> <target> <up|down>`: add a new metric

## Steps

1. Read `data/kpi-tracker.md`. It has a **Metrics** table (what to measure, unit, target, which direction is good) and a **Readings** log (date, metric, value, note).
2. If `request` is empty: for every metric print the latest reading, the target, the gap, and the change since the previous reading. Mark each one `on track`, `behind` or `no data`. Then say in one sentence which metric needs attention first.
3. If `request` starts with `add`: get today's date from the system. Append one row to **Readings**. The metric must already exist in **Metrics**; if it does not, stop and tell me to `define` it first. Never change or delete an earlier reading.
4. If `request` starts with `define`: append one row to **Metrics**. Do not create duplicates.
5. After any change, print the status table again.

## Rules

- Only write numbers I gave you. Never estimate or fill a gap.
- If a value looks wrong (10x the last reading, a negative count), ask before writing it.
- Do not put personal or customer data in this file. Aggregate figures only.
