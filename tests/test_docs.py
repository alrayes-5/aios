"""Docs check: the skip-permissions flag only in the appendix, no em or en dashes, no removed things."""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAG = "--dangerously-" + "skip-permissions"
APPENDIX = "docs/advanced.md"
SKIP_DIRS = {".git", "__pycache__", ".opencode/node_modules"}


def text_files():
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(folder, name)
            if name == "LICENSE" or name.endswith((".pyc", ".png", ".jpg")):
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                yield os.path.relpath(path, ROOT).replace(os.sep, "/"), handle.read()


class DocsTest(unittest.TestCase):
    def test_skip_flag_only_in_the_appendix(self):
        hits = [p for p, t in text_files() if FLAG in t and not p.startswith("tests/")]
        self.assertEqual(hits, [APPENDIX])

    def test_warning_comes_before_the_alias(self):
        with open(os.path.join(ROOT, APPENDIX), encoding="utf-8") as handle:
            text = handle.read()
        self.assertLess(text.index("Read this before"), text.index("alias cr="))
        self.assertLess(text.index("every folder"), text.index("alias cr="))

    def test_cs_only_in_start_here(self):
        with open(os.path.join(ROOT, "START_HERE.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("alias cs=", text)
        self.assertNotIn("alias cr=", text)
        self.assertNotIn("function cr", text)

    def test_no_em_or_en_dashes(self):
        bad = [p for p, t in text_files() if "\u2014" in t or "\u2013" in t]
        self.assertEqual(bad, [])

    def test_removed_things_are_gone(self):
        for path in (".aios", "private", ".claude/skills", "commands/create-plan.md", "commands/implement.md", "scripts/test-guard.py"):
            self.assertFalse(os.path.exists(os.path.join(ROOT, path)), path)
        words = ("guard.py", "skill-creator", "Operating System", "/create-plan", "/implement", "AIOS_UNLOCK")
        hits = [(p, w) for p, t in text_files() if not p.startswith("tests/") and p != "CHANGELOG.md" and p != "UPDATING.md"
                for w in words if w in t]
        self.assertEqual(hits, [])

    def test_layer_table_appears_once(self):
        marker = "| 1. Context |"
        self.assertEqual([p for p, t in text_files() if marker in t and not p.startswith("tests/")], ["AGENTS.md"])

    def test_readme_is_short_and_opens_with_a_brief(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        self.assertLessEqual(len([l for l in lines if l.strip()]), 28)
        self.assertIn("Matters", "\n".join(lines[:12]))

    def test_no_company_or_secret_words(self):
        words = ["flow" + "layers", "ke" + "met", "paper" + "clip", "od" + "oo", "flex" + "tock", "api_key=", "sk-" + "ant-", "gh" + "p_", "github_" + "pat_"]
        hits = [(p, w) for p, t in text_files() if not p.startswith("tests/") for w in words if w in t.lower()]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
