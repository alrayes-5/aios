"""Tests for scripts/kpi.py. Run: python3 -m unittest discover -s tests -v"""
import ast
import csv
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "kpi.py")
TODAY = "2026-10-28"


class KpiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        self.run_kpi("define", "Sign-ups", "people", "50", "up")
        self.run_kpi("define", "Churn", "%", "5", "down")

    def run_kpi(self, *args, **kw):
        env = dict(os.environ, AIOS_DATA_DIR=self.dir)
        return subprocess.run([sys.executable, "-I", SCRIPT, "--today", kw.get("today", TODAY)] + list(args),
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def readings(self):
        with open(os.path.join(self.dir, "kpis.csv"), newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_add_a_reading(self):
        done = self.run_kpi("add", "Sign-ups", "37", "--source", "dashboard", "--date", "2026-10-27")
        self.assertEqual(done.returncode, 0, done.stderr)
        rows = self.readings()
        self.assertEqual([(r["date"], r["metric"], r["value"], r["source"]) for r in rows],
                         [("2026-10-27", "Sign-ups", "37", "dashboard")])
        self.assertIn("Added Sign-ups = 37", done.stdout)
        self.assertIn("| Sign-ups | people | 37 | 2026-10-27 | 1d | 50 | -13 | - | behind |", done.stdout)

    def test_defaults_to_today(self):
        self.run_kpi("add", "Sign-ups", "40", "--source", "dashboard")
        self.assertEqual(self.readings()[0]["date"], TODAY)

    def test_gap_and_change(self):
        self.run_kpi("add", "Sign-ups", "30", "--source", "a", "--date", "2026-10-20")
        self.run_kpi("add", "Sign-ups", "55", "--source", "a", "--date", "2026-10-27")
        status = self.run_kpi("status").stdout
        self.assertIn("| Sign-ups | people | 55 | 2026-10-27 | 1d | 50 | +5 | +25 | on track |", status)

    def test_down_metric_direction(self):
        self.run_kpi("add", "Churn", "6.5", "--source", "a", "--date", "2026-10-27")
        self.assertIn("| Churn | % | 6.5 | 2026-10-27 | 1d | 5 | +1.5 | - | behind |", self.run_kpi("status").stdout)
        self.run_kpi("add", "Churn", "4", "--source", "a", "--date", "2026-10-28")
        self.assertIn("| 4 | 2026-10-28 | 0d | 5 | -1 | -2.5 | on track |", self.run_kpi("status").stdout)

    def test_no_data(self):
        self.assertIn("| Churn | % | - | - | - | 5 | - | - | no data |", self.run_kpi("status").stdout)

    def test_stale_marking(self):
        self.run_kpi("add", "Sign-ups", "60", "--source", "a", "--date", "2026-10-21")  # 7 days old: fresh
        self.run_kpi("add", "Churn", "3", "--source", "a", "--date", "2026-10-20")      # 8 days old: stale
        status = self.run_kpi("status").stdout
        self.assertIn("| 60 | 2026-10-21 | 7d | 50 | +10 | - | on track |", status)
        self.assertIn("| 3 | 2026-10-20 | 8d | 5 | -2 | - | on track, STALE |", status)

    def test_bad_values_are_refused(self):
        bad = [("abc", []), ("nan", []), ("inf", []), ("1e999", []), ("", []),
               ("5", ["--date", "2026-13-40"]), ("5", ["--date", "2026-11-30"]), ("5", ["--source", ""])]
        for value, extra in bad:
            args = ["add", "Sign-ups", value] + (extra if "--source" in extra else ["--source", "a"] + extra)
            done = self.run_kpi(*args)
            self.assertEqual(done.returncode, 2, (value, extra, done.stdout))
            self.assertTrue(done.stderr.startswith("kpi.py: "), done.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "kpis.csv")), "a refused value must not write anything")

    def test_unknown_metric_and_missing_source_refused(self):
        self.assertEqual(self.run_kpi("add", "Nope", "1", "--source", "a").returncode, 2)
        self.assertEqual(self.run_kpi("add", "Sign-ups", "1").returncode, 2)

    def test_far_value_needs_confirm(self):
        self.run_kpi("add", "Sign-ups", "40", "--source", "a", "--date", "2026-10-20")
        refused = self.run_kpi("add", "Sign-ups", "400", "--source", "a", "--date", "2026-10-21")
        self.assertEqual(refused.returncode, 2)
        self.assertIn("--confirm", refused.stderr)
        self.assertEqual(len(self.readings()), 1)
        self.assertEqual(self.run_kpi("add", "Sign-ups", "400", "--source", "a", "--date", "2026-10-21", "--confirm").returncode, 0)

    def test_same_day_reading_is_not_overwritten(self):
        self.run_kpi("add", "Sign-ups", "40", "--source", "a", "--date", "2026-10-20")
        self.assertEqual(self.run_kpi("add", "Sign-ups", "41", "--source", "a", "--date", "2026-10-20").returncode, 2)
        self.assertEqual([r["value"] for r in self.readings()], ["40"])

    def test_comma_and_quote_in_text_survive(self):
        self.run_kpi("add", "Sign-ups", "40", "--source", 'sheet "A", tab 2', "--note", "a, b")
        row = self.readings()[0]
        self.assertEqual((row["source"], row["note"]), ('sheet "A", tab 2', "a, b"))

    def test_define_twice_refused(self):
        self.assertEqual(self.run_kpi("define", "Sign-ups", "people", "60", "up").returncode, 2)
        self.assertEqual(self.run_kpi("define", "Other", "x", "1", "sideways").returncode, 2)

    def test_example_status_runs(self):
        env = dict(os.environ, AIOS_DATA_DIR=os.path.join(ROOT, "example", "data"))
        done = subprocess.run([sys.executable, "-I", SCRIPT, "--today", "2026-10-28", "status"], env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("| Loaves baked | count per week | 2380 | 2026-10-26 | 2d | 2400 | -20 | +50 | behind |", done.stdout)

    def test_script_is_python38_syntax(self):
        with open(SCRIPT, encoding="utf-8") as handle:
            ast.parse(handle.read(), feature_version=(3, 8))


if __name__ == "__main__":
    unittest.main()
