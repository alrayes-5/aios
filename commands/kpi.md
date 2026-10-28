# KPI

The numbers live in two files that a script reads and writes: `data/kpis.csv` (readings) and `data/targets.csv` (what each metric should reach). You run the script. You never edit either CSV by hand and never do the arithmetic yourself.

## Variables

request: $ARGUMENTS
- empty or `status`: show the status table
- `add <metric> <value> <source> [note]`: record a reading (the source is where the number came from)
- `define <metric> <unit> <target> <up|down>`: add a new metric

## Steps

Run the script with `python3` (if that command is not found, use `python`, then `py`).

1. Empty or `status`: run `python3 scripts/kpi.py status` and print its table as it is. Then say in one sentence which metric needs attention first.
2. `add`: run `python3 scripts/kpi.py add "<metric>" <value> --source "<source>"` (add `--note "<note>"` if I gave one). If I did not give a source, ask me for it. The script prints the new table.
3. `define`: run `python3 scripts/kpi.py define "<metric>" "<unit>" <target> <up|down>`.
4. If the script refuses (unknown metric, bad number, a value far from the last one, a duplicate date), show me its message and ask. Use `--confirm` only after I say the number is right.

## Rules

- Only record numbers I gave you. Never estimate or fill a gap.
- Never change or delete an earlier reading. To correct one, tell me; I edit the file myself.
- Aggregate figures only: no names, no personal data.
