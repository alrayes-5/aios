#!/usr/bin/env python3
"""AIOS KPI tracker: readings in data/kpis.csv, targets in data/targets.csv.

    python3 scripts/kpi.py status                     print the Markdown status table (default)
    python3 scripts/kpi.py define NAME UNIT TARGET up|down
    python3 scripts/kpi.py add NAME VALUE --source TEXT [--date YYYY-MM-DD] [--note TEXT] [--confirm]

Python 3.8+, standard library only. The AI runs this script; it never edits the CSV files by hand.
Gap is the latest value minus the target. Set AIOS_DATA_DIR to use another folder, and
--today YYYY-MM-DD (before the command) to fix "today", for tests.
"""
import argparse
import csv
import datetime
import math
import os
import sys

STALE_DAYS = 7
JUMP = 10  # a reading 10x above or below the last one is refused unless --confirm is given
READING_COLS = ["date", "metric", "value", "source", "note"]
TARGET_COLS = ["metric", "unit", "target", "direction"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class KpiError(Exception):
    pass


def data_dir():
    return os.environ.get("AIOS_DATA_DIR") or os.path.join(ROOT, "data")


def parse_number(text, what):
    try:
        number = float(str(text).strip())
    except ValueError:
        raise KpiError("%s %r is not a number." % (what, text))
    if math.isnan(number) or math.isinf(number):
        raise KpiError("%s %r is not a finite number." % (what, text))
    return number


def parse_date(text):
    try:
        return datetime.datetime.strptime(str(text).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise KpiError("Date %r is not YYYY-MM-DD." % (text,))


def clean_text(text, what):
    text = str(text).strip()
    if "\n" in text or "\r" in text:
        raise KpiError("%s must be one line." % what)
    return text


def read_rows(name, cols):
    path = os.path.join(data_dir(), name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in cols[:4] if c not in (reader.fieldnames or [])]
        if missing:
            raise KpiError("%s is missing the column(s): %s." % (name, ", ".join(missing)))
        return list(reader)


def append_row(name, cols, row):
    path = os.path.join(data_dir(), name)
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    if not os.path.isdir(data_dir()):
        raise KpiError("Data folder %s does not exist." % data_dir())
    with open(path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        if new_file:
            writer.writerow(cols)
        writer.writerow([row.get(c, "") for c in cols])


def fmt(number):
    return ("%.2f" % number).rstrip("0").rstrip(".") if number is not None else "-"


def signed(number):
    return ("+" if number > 0 else "") + fmt(number) if number is not None else "-"


def targets():
    out = {}
    for row in read_rows("targets.csv", TARGET_COLS):
        out[row["metric"]] = row
    return out


def cmd_define(args):
    name = clean_text(args.name, "Metric name")
    if not name:
        raise KpiError("Metric name is empty.")
    if name in targets():
        raise KpiError("Metric %r is already defined. Edit data/targets.csv yourself to change its target." % name)
    if args.direction not in ("up", "down"):
        raise KpiError("Direction must be up or down.")
    target = parse_number(args.target, "Target")
    append_row("targets.csv", TARGET_COLS, {"metric": name, "unit": clean_text(args.unit, "Unit"),
                                            "target": fmt(target), "direction": args.direction})
    print("Defined %s: target %s %s, good direction %s." % (name, fmt(target), args.unit, args.direction))


def cmd_add(args, today):
    name = clean_text(args.name, "Metric name")
    if name not in targets():
        raise KpiError("Metric %r is not defined. Run: python3 scripts/kpi.py define NAME UNIT TARGET up|down" % name)
    value = parse_number(args.value, "Value")
    when = parse_date(args.date) if args.date else today
    if when > today:
        raise KpiError("Date %s is in the future." % when)
    source = clean_text(args.source or "", "Source")
    if not source:
        raise KpiError("A source is required (--source \"where this number came from\").")
    previous = [r for r in read_rows("kpis.csv", READING_COLS) if r["metric"] == name]
    if any(r["date"] == when.isoformat() for r in previous):
        raise KpiError("%s already has a reading for %s. Earlier readings are never changed." % (name, when))
    if previous and not args.confirm:
        last = parse_number(previous[-1]["value"], "Last value")
        if last != 0 and (abs(value) >= abs(last) * JUMP or (value != 0 and abs(value) <= abs(last) / JUMP)):
            raise KpiError("%s is far from the last reading (%s). If it is right, repeat with --confirm." % (fmt(value), fmt(last)))
    append_row("kpis.csv", READING_COLS, {"date": when.isoformat(), "metric": name, "value": fmt(value),
                                          "source": source, "note": clean_text(args.note or "", "Note")})
    print("Added %s = %s (%s)." % (name, fmt(value), when))


def build_status(today):
    defined = targets()
    readings = {}
    for row in read_rows("kpis.csv", READING_COLS):
        readings.setdefault(row["metric"], []).append(row)
    lines = ["KPI status as of %s. Readings older than %d days are marked STALE." % (today, STALE_DAYS), "",
             "| Metric | Unit | Latest | Date | Age | Target | Gap | Change | Status |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    if not defined:
        lines.append("| (no metrics yet) | | | | | | | | run define |")
    for name, spec in defined.items():
        target = parse_number(spec["target"], "Target for " + name)
        rows = sorted(readings.get(name, []), key=lambda r: r["date"])
        if not rows:
            lines.append("| %s | %s | - | - | - | %s | - | - | no data |" % (name, spec["unit"], fmt(target)))
            continue
        value = parse_number(rows[-1]["value"], "Value for " + name)
        age = (today - parse_date(rows[-1]["date"])).days
        change = value - parse_number(rows[-2]["value"], "Value for " + name) if len(rows) > 1 else None
        gap = value - target
        good = value >= target if spec["direction"] == "up" else value <= target
        status = "on track" if good else "behind"
        if age > STALE_DAYS:
            status += ", STALE"
        lines.append("| %s | %s | %s | %s | %dd | %s | %s | %s | %s |" % (
            name, spec["unit"], fmt(value), rows[-1]["date"], age, fmt(target), signed(gap), signed(change), status))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="AIOS KPI tracker")
    parser.add_argument("--today", help="YYYY-MM-DD, for tests")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status")
    p = sub.add_parser("define")
    for arg in ("name", "unit", "target", "direction"):
        p.add_argument(arg)
    p = sub.add_parser("add")
    p.add_argument("name")
    p.add_argument("value")
    for opt in ("--source", "--date", "--note"):
        p.add_argument(opt)
    p.add_argument("--confirm", action="store_true")
    args = parser.parse_args(argv)
    try:
        today = parse_date(args.today) if args.today else datetime.date.today()
        if args.command == "define":
            cmd_define(args)
        elif args.command == "add":
            cmd_add(args, today)
            print()
            print(build_status(today))
        else:
            print(build_status(today))
    except KpiError as error:
        print("kpi.py: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
