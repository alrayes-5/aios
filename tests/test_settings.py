"""Settings check: the protected paths are denied in both tools, and nothing widens permissions."""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTECTED = ["AGENTS.md", "CLAUDE.md", "context/rules.md", "commands/**", ".claude/**", ".opencode/**", "opencode.json", "scripts/**", "automation/**", ".github/**"]
# OpenCode's edit rules use plain globs: a folder is written "commands/*".
PROTECTED_OC = ["AGENTS.md", "CLAUDE.md", "context/rules.md", "commands/*", ".claude/*", ".opencode/*", "opencode.json", "scripts/*", "automation/*", ".github/*"]


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as handle:
        return json.load(handle)


class SettingsTest(unittest.TestCase):
    def test_claude_code_denies_edits_to_protected_paths(self):
        deny = load(".claude/settings.json")["permissions"]["deny"]
        for path in PROTECTED:
            self.assertIn("Edit(./%s)" % path, deny)

    def test_opencode_denies_edits_to_protected_paths(self):
        edit = load("opencode.json")["permission"]["edit"]
        for path in PROTECTED_OC:
            self.assertEqual(edit.get(path), "deny", path)
        self.assertEqual(edit.get("*"), "allow", "the catch-all must come first so the deny rules win (last match wins)")
        self.assertEqual(list(edit)[0], "*")

    def test_claude_code_sandbox_on_and_still_asks_for_shell(self):
        sandbox = load(".claude/settings.json")["sandbox"]
        self.assertIs(sandbox.get("enabled"), True)
        self.assertIs(sandbox.get("autoAllowBashIfSandboxed"), False, "a sandboxed shell command must still ask")

    def test_opencode_asks_for_shell_and_web(self):
        permission = load("opencode.json")["permission"]
        self.assertEqual(permission.get("bash"), "ask")
        self.assertEqual(permission.get("webfetch"), "ask")

    def test_no_bypass_mode_anywhere(self):
        for name in (".claude/settings.json", "opencode.json"):
            with open(os.path.join(ROOT, name), encoding="utf-8") as handle:
                text = handle.read()
            self.assertNotIn("bypassPermissions", text)
            self.assertNotIn("dangerously", text)
        claude = load(".claude/settings.json")
        self.assertIn(claude.get("permissions", {}).get("defaultMode", "default"), ("default",))

    def test_no_broad_bash_allow(self):
        claude = load(".claude/settings.json")
        for rule in claude.get("permissions", {}).get("allow", []):
            self.assertFalse(rule == "Bash" or rule.startswith("Bash(*") or rule.startswith("Bash(:"), rule)
        self.assertNotIn("hooks", claude, "the kit ships no hooks")
        self.assertNotEqual(load("opencode.json")["permission"].get("bash"), "allow")
        bash = load("opencode.json")["permission"]["bash"]
        if isinstance(bash, dict):
            self.assertNotEqual(bash.get("*"), "allow")

    def test_every_command_has_both_wrappers(self):
        names = [f[:-3] for f in os.listdir(os.path.join(ROOT, "commands")) if f.endswith(".md")]
        self.assertEqual(sorted(names), ["daily-brief", "kpi", "plan", "prime"])
        for name in names:
            for folder in (".claude/commands", ".opencode/commands"):
                path = os.path.join(ROOT, folder, name + ".md")
                self.assertTrue(os.path.exists(path), path)
                with open(path, encoding="utf-8") as handle:
                    self.assertIn("`commands/%s.md`" % name, handle.read())


if __name__ == "__main__":
    unittest.main()
