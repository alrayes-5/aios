#!/usr/bin/env python3
"""Check that the guard blocks what it should. Run from anywhere: python3 scripts/test-guard.py

It feeds made-up tool calls to .aios/guard.py and prints PASS or FAIL for each. Nothing is read or written.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True   # loading guard.py for the path checks must not leave files in the kit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUARD = os.path.join(ROOT, ".aios", "guard.py")

# (expect, tool, input, label)   expect: "allow" or "block"
CASES = [
    ("allow", "Read", {"file_path": "context/strategy.md"}, "read a context file"),
    ("allow", "Write", {"file_path": "outputs/drafts/note.md", "content": "x"}, "write a draft"),
    ("allow", "Edit", {"file_path": "data/kpi-tracker.md"}, "edit the KPI tracker"),
    ("allow", "Write", {"file_path": "plans/2026-01-01-x.md", "content": "x"}, "write a plan"),
    ("allow", "Bash", {"command": "ls -la && cat AGENTS.md | head -5"}, "list and read"),
    ("allow", "Bash", {"command": "echo hi > outputs/drafts/a.md"}, "redirect into outputs/"),
    ("allow", "Bash", {"command": "git status"}, "git status"),
    ("allow", "Read", {"file_path": "/etc/hostname"}, "read outside the workspace"),
    ("allow", "Bash", {"command": "cat .aios/guard.json 2>/dev/null; ls $HOME 2>&1"}, "read a core file, discard errors"),
    ("allow", "Bash", {"command": "date +%F > outputs/drafts/today.txt 2>&1"}, "redirect with 2>&1"),
    ("block", "Bash", {"command": "echo x 2>&1 > private/a.txt"}, "redirect into private/ after 2>&1"),
    ("block", "Read", {"file_path": "private/notes.txt"}, "read private/"),
    ("block", "Write", {"file_path": "private/notes.txt", "content": "x"}, "write private/"),
    ("block", "Edit", {"file_path": "./private/../private/a.md"}, "edit private/ by a roundabout path"),
    ("block", "Glob", {"pattern": "private/*"}, "glob private/"),
    ("block", "Grep", {"pattern": "secret", "path": "private"}, "grep inside private/"),
    ("block", "Bash", {"command": "cat private/notes.txt"}, "cat private/"),
    ("block", "Bash", {"command": "cd private && ls"}, "cd into private/"),
    ("block", "Bash", {"command": "cat pri*/n*"}, "cat private/ by wildcard"),
    ("block", "Write", {"file_path": "AGENTS.md", "content": "x"}, "write AGENTS.md"),
    ("block", "Edit", {"file_path": "context/rules.md"}, "edit rules.md"),
    ("block", "Write", {"file_path": ".aios/guard.json", "content": "{}"}, "edit the guard policy"),
    ("block", "Write", {"file_path": ".claude/settings.json", "content": "{}"}, "edit Claude Code settings"),
    ("block", "Write", {"file_path": "opencode.json", "content": "{}"}, "edit OpenCode settings"),
    ("block", "Write", {"file_path": ".opencode/plugins/aios-guard.js", "content": ""}, "edit the OpenCode plugin"),
    ("block", "Bash", {"command": "sed -i 's/a/b/' AGENTS.md"}, "sed -i a core file"),
    ("block", "Bash", {"command": "echo x >> context/rules.md"}, "append to rules.md"),
    ("block", "Bash", {"command": "rm CLAUDE.md"}, "delete CLAUDE.md"),
    ("block", "Write", {"file_path": "/tmp/aios-outside.txt", "content": "x"}, "write outside the workspace"),
    ("block", "Write", {"file_path": "../outside.txt", "content": "x"}, "write above the workspace"),
    ("block", "Bash", {"command": "echo x > /tmp/aios-outside.txt"}, "redirect outside the workspace"),
    ("block", "Bash", {"command": "cp AGENTS.md ~/copy.md"}, "cp into the home folder"),
    ("block", "Bash", {"command": "touch ../x"}, "touch above the workspace"),
    ("block", "Bash", {"command": "rm -rf $HOME/x"}, "rm through a variable"),
    ("block", "apply_patch", {"patchText": "*** Begin Patch\n*** Update File: AGENTS.md\n@@\n-a\n+b\n*** End Patch"}, "patch AGENTS.md"),
    # round 2: recursive reads from the workspace root, shells that hide a command, git -C, curl/wget, case
    ("block", "Bash", {"command": "grep -rn secret ."}, "grep -r from the root"),
    ("block", "Bash", {"command": "grep -r secret"}, "grep -r with no folder"),
    ("block", "Bash", {"command": "grep -R secret ./"}, "grep -R ./"),
    ("block", "Bash", {"command": "grep --recursive secret ."}, "grep --recursive"),
    ("block", "Bash", {"command": "find . -type f -exec cat {} +"}, "find . then cat"),
    ("block", "Bash", {"command": "find . | xargs cat"}, "find . piped to xargs"),
    ("block", "Bash", {"command": "find . -path ./private"}, "find . -path ./private without prune"),
    ("block", "Bash", {"command": "find / -name secret.txt"}, "find from / reaches private/"),
    ("block", "Bash", {"command": "tar cf - ."}, "tar the root"),
    ("block", "Bash", {"command": "ls -R"}, "ls -R at the root"),
    ("block", "Bash", {"command": "cp -r . outputs/drafts/copy"}, "cp -r the root"),
    ("block", "Bash", {"command": "rg -u secret"}, "rg -u (ignores .ignore)"),
    ("block", "Bash", {"command": "grep -rn secret context && grep -r secret ."}, "second command of a pair reads the root"),
    ("allow", "Bash", {"command": "grep -rn secret context"}, "grep -r in context/"),
    ("allow", "Bash", {"command": "grep -rn secret . --exclude-dir=private"}, "grep -r excluding private/"),
    ("allow", "Bash", {"command": "grep -rn secret --exclude-dir private ."}, "grep -r excluding private/ (two words)"),
    ("allow", "Bash", {"command": "find . -name '*.md' -not -path './private/*'"}, "find excluding private/"),
    ("allow", "Bash", {"command": "find . -path ./private -prune -o -name '*.md' -print"}, "find pruning private/"),
    ("allow", "Bash", {"command": "find context -name '*.md'"}, "find in context/"),
    ("allow", "Bash", {"command": "ls -R context"}, "ls -R context/"),
    ("allow", "Bash", {"command": "rg secret"}, "rg (skips private/ through .ignore)"),
    ("block", "Bash", {"command": "bash -c 'cat private/secret.txt'"}, "bash -c reads private/"),
    ("block", "Bash", {"command": "sh -c \"echo hi > AGENTS.md\""}, "sh -c writes a core file"),
    ("block", "Bash", {"command": "zsh -c 'echo hi > /tmp/x'"}, "zsh -c writes outside"),
    ("block", "Bash", {"command": "eval 'cat private/secret.txt'"}, "eval reads private/"),
    ("block", "Bash", {"command": "env bash -lc 'grep -r x .'"}, "bash -lc with a recursive grep"),
    ("block", "Bash", {"command": "xargs sh -c 'cat private/x'"}, "xargs sh -c"),
    ("allow", "Bash", {"command": "bash -c 'ls context'"}, "bash -c on a harmless command"),
    ("block", "Bash", {"command": "python3 -c \"print(open('private/secret.txt').read())\""}, "inline python names private/"),
    ("block", "Bash", {"command": "node -e \"require('fs').readFileSync('private/x')\""}, "inline node names private/"),
    ("block", "Bash", {"command": "git -C . checkout AGENTS.md"}, "git -C . checkout a core file"),
    ("block", "Bash", {"command": "git -C . restore AGENTS.md"}, "git -C . restore a core file"),
    ("block", "Bash", {"command": "git -c core.x=1 checkout CLAUDE.md"}, "git -c checkout a core file"),
    ("allow", "Bash", {"command": "git -C . status"}, "git -C . status"),
    ("block", "Bash", {"command": "curl -o /tmp/x https://example.com"}, "curl -o outside"),
    ("block", "Bash", {"command": "curl --output=/tmp/x https://example.com"}, "curl --output= outside"),
    ("block", "Bash", {"command": "wget -O /tmp/x https://example.com"}, "wget -O outside"),
    ("block", "Bash", {"command": "wget -O AGENTS.md https://example.com"}, "wget -O a core file"),
    ("allow", "Bash", {"command": "curl -o outputs/drafts/page.html https://example.com"}, "curl -o into outputs/"),
    ("block", "Bash", {"command": "awk 'BEGIN{print \"x\" > \"/tmp/x\"}'"}, "awk writes a file"),
    ("allow", "Bash", {"command": "awk '{print $1}' data/kpi-tracker.md"}, "awk prints to the screen"),
    ("block", "Read", {"file_path": "PRIVATE/secret.txt"}, "read PRIVATE/ (case)"),
    ("block", "Bash", {"command": "cat Private/secret.txt"}, "cat Private/ (case)"),
    ("block", "Write", {"file_path": "agents.MD", "content": "x"}, "write agents.MD (case)"),
    # round 3: Windows paths, PowerShell, cmd, /dev/null and NUL. Windows-style paths are tried on every system.
    ("block", "Read", {"file_path": "private\\README.md"}, "read private\\ with a backslash"),
    ("block", "Read", {"file_path": ".\\PRIVATE\\README.md"}, "read .\\PRIVATE\\ (case, backslash)"),
    ("block", "Write", {"file_path": "context\\rules.md", "content": "x"}, "write context\\rules.md with a backslash"),
    ("block", "Edit", {"file_path": ".claude\\settings.json"}, "edit .claude\\settings.json with a backslash"),
    ("block", "Write", {"file_path": ".opencode\\plugins\\aios-guard.js", "content": ""}, "edit the plugin with backslashes"),
    ("block", "Write", {"file_path": "C:\\Users\\Public\\x.txt", "content": "x"}, "write to C:\\Users\\Public"),
    ("block", "Write", {"file_path": "Agents.md", "content": "x"}, "write Agents.md (case)"),
    ("allow", "Write", {"file_path": "outputs\\drafts\\a.md", "content": "x"}, "write a draft with backslashes"),
    ("allow", "Bash", {"command": "echo hi 2>/dev/null"}, "discard errors into /dev/null"),
    ("block", "PowerShell", {"command": "Get-Content private/README.md"}, "PowerShell: read private/"),
    ("block", "PowerShell", {"command": "Get-Content .\\PRIVATE\\README.md"}, "PowerShell: read .\\PRIVATE\\"),
    ("block", "PowerShell", {"command": "Get-Content pri*\\*"}, "PowerShell: wildcard into private\\"),
    ("block", "PowerShell", {"command": "Get-Content (Join-Path private x)"}, "PowerShell: Join-Path into private"),
    ("block", "PowerShell", {"command": "Set-Location private; ls"}, "PowerShell: Set-Location private"),
    ("block", "PowerShell", {"command": "[System.IO.File]::ReadAllText('private/a')"}, "PowerShell: .NET read of private/"),
    ("block", "PowerShell", {"command": "Set-Content AGENTS.md x"}, "PowerShell: Set-Content AGENTS.md"),
    ("block", "PowerShell", {"command": "Set-Content -Value x -Path AGENTS.md"}, "PowerShell: Set-Content -Value first"),
    ("block", "PowerShell", {"command": "Set-Content -Path:AGENTS.md -Value x"}, "PowerShell: -Path:value form"),
    ("block", "PowerShell", {"command": "Add-Content context\\rules.md 'x'"}, "PowerShell: Add-Content rules.md"),
    ("block", "PowerShell", {"command": "'x' | Out-File .claude\\settings.json"}, "PowerShell: Out-File settings.json"),
    ("block", "PowerShell", {"command": "echo x > AGENTS.md"}, "PowerShell: redirect into AGENTS.md"),
    ("block", "PowerShell", {"command": "'x' >> .opencode\\plugins\\aios-guard.js"}, "PowerShell: append to the plugin"),
    ("block", "PowerShell", {"command": "Remove-Item CLAUDE.md"}, "PowerShell: Remove-Item CLAUDE.md"),
    ("block", "PowerShell", {"command": "del AGENTS.md"}, "PowerShell: del AGENTS.md"),
    ("block", "PowerShell", {"command": "Copy-Item a.md AGENTS.md"}, "PowerShell: Copy-Item onto AGENTS.md"),
    ("block", "PowerShell", {"command": "Copy-Item -Path a.md -Destination AGENTS.md"}, "PowerShell: Copy-Item -Destination AGENTS.md"),
    ("block", "PowerShell", {"command": "Move-Item AGENTS.md outputs\\x.md"}, "PowerShell: Move-Item out of AGENTS.md"),
    ("block", "PowerShell", {"command": "New-Item AGENTS.md -Force"}, "PowerShell: New-Item AGENTS.md"),
    ("block", "PowerShell", {"command": "[System.IO.File]::WriteAllText('AGENTS.md','x')"}, "PowerShell: .NET write to AGENTS.md"),
    ("block", "PowerShell", {"command": "Get-ChildItem | ForEach-Object { Set-Content AGENTS.md x }"}, "PowerShell: Set-Content inside a script block"),
    ("block", "PowerShell", {"command": "Set-Content C:\\Users\\Public\\x.txt hi"}, "PowerShell: write to C:\\Users\\Public"),
    ("block", "PowerShell", {"command": "Set-Content ..\\x.txt hi"}, "PowerShell: write above the workspace"),
    ("block", "PowerShell", {"command": "Set-Content $env:USERPROFILE\\x hi"}, "PowerShell: write through a variable"),
    ("block", "PowerShell", {"command": "Get-Content \"$pwd\\private\\x\""}, "PowerShell: private path built from $pwd"),
    ("block", "PowerShell", {"command": "Invoke-WebRequest http://x -OutFile C:\\Temp\\a"}, "PowerShell: download outside the workspace"),
    ("block", "PowerShell", {"command": "iwr http://x -OutFile:AGENTS.md"}, "PowerShell: download over AGENTS.md"),
    ("block", "PowerShell", {"command": "Get-ChildItem -Recurse"}, "PowerShell: Get-ChildItem -Recurse from the root"),
    ("block", "PowerShell", {"command": "gci -r ."}, "PowerShell: gci -r ."),
    ("block", "PowerShell", {"command": "dir /s"}, "PowerShell: dir /s from the root"),
    ("block", "PowerShell", {"command": "Compress-Archive -Path . -DestinationPath outputs\\a.zip"}, "PowerShell: zip the root"),
    ("block", "PowerShell", {"command": "powershell -Command \"Get-Content private/x\""}, "PowerShell: nested powershell reads private/"),
    ("block", "PowerShell", {"command": "cmd /c \"type private\\x\""}, "PowerShell: cmd /c type private\\"),
    ("block", "PowerShell", {"command": "cmd /c echo x > AGENTS.md"}, "PowerShell: cmd /c redirect into AGENTS.md"),
    ("block", "PowerShell", {"command": "bash -c 'cat private/x'"}, "PowerShell: bash -c reads private/"),
    ("block", "PowerShell", {"command": "iex $cmd"}, "PowerShell: Invoke-Expression of a variable"),
    ("block", "PowerShell", {"command": "powershell -enc AAAA"}, "PowerShell: encoded command"),
    ("block", "PowerShell", {"command": ".\\private\\run.ps1"}, "PowerShell: run a script in private\\"),
    ("block", "Bash", {"command": "powershell -Command \"Set-Content AGENTS.md x\""}, "Bash: powershell -Command writes AGENTS.md"),
    ("block", "Bash", {"command": "cmd /c \"type private\\x\""}, "Bash: cmd /c type private\\"),
    ("block", "PowerShell", {"command": "Set-Content (Join-Path . AGENTS.md) x"}, "PowerShell: Set-Content through Join-Path"),
    ("block", "PowerShell", {"command": "Out-File -FilePath:AGENTS.md -InputObject x"}, "PowerShell: Out-File -FilePath:AGENTS.md"),
    ("block", "PowerShell", {"command": "Set-Content \"C:\\Program Files\\x.txt\" hi"}, "PowerShell: write to a path with a space outside"),
    ("allow", "PowerShell", {"command": "Get-Content context\\strategy.md"}, "PowerShell: read a context file"),
    ("allow", "PowerShell", {"command": "Set-Content notes.md 'see https://x.com/a/b and more'"}, "PowerShell: text with a URL and spaces"),
    ("allow", "PowerShell", {"command": "Get-Content AGENTS.md"}, "PowerShell: read AGENTS.md"),
    ("allow", "PowerShell", {"command": "Get-Content AGENTS.md | Set-Content outputs\\drafts\\a.md"}, "PowerShell: copy AGENTS.md into a draft"),
    ("allow", "PowerShell", {"command": "Copy-Item AGENTS.md outputs\\drafts\\agents-copy.md"}, "PowerShell: Copy-Item out of AGENTS.md"),
    ("allow", "PowerShell", {"command": "Set-Content outputs\\drafts\\a.md 'hi'"}, "PowerShell: write a draft"),
    ("allow", "PowerShell", {"command": "Set-Content -Path outputs/drafts/a.md -Value 'see https://x.com/a/b'"}, "PowerShell: text with slashes"),
    ("allow", "PowerShell", {"command": "Add-Content notes.md \"today $(Get-Date)\""}, "PowerShell: text with an expression"),
    ("allow", "PowerShell", {"command": "Get-Date > outputs\\drafts\\d.txt"}, "PowerShell: redirect into outputs\\"),
    ("allow", "PowerShell", {"command": "Get-Content a.md 2>$null"}, "PowerShell: 2>$null"),
    ("allow", "PowerShell", {"command": "Get-Content a.md 2>&1"}, "PowerShell: 2>&1"),
    ("allow", "PowerShell", {"command": "ls 2>NUL"}, "PowerShell: 2>NUL"),
    ("allow", "PowerShell", {"command": "cmd /c dir 2>nul"}, "PowerShell: cmd /c dir 2>nul"),
    ("allow", "PowerShell", {"command": "Get-ChildItem -Force"}, "PowerShell: list, not recursive"),
    ("allow", "PowerShell", {"command": "Get-ChildItem -Recurse context"}, "PowerShell: recurse into context\\"),
    ("allow", "PowerShell", {"command": "dir /s outputs"}, "PowerShell: dir /s outputs"),
    ("allow", "PowerShell", {"command": "Get-ChildItem | Where-Object { $_.Name -like '*.md' }"}, "PowerShell: filter a listing"),
    ("allow", "PowerShell", {"command": "Invoke-WebRequest https://example.com -OutFile outputs\\drafts\\x.html"}, "PowerShell: download into outputs\\drafts"),
    ("allow", "PowerShell", {"command": "Remove-Item outputs\\drafts\\old.md"}, "PowerShell: delete a draft"),
    ("allow", "PowerShell", {"command": "New-Item -ItemType File -Path outputs\\drafts\\n.md"}, "PowerShell: New-Item a draft"),
    ("allow", "PowerShell", {"command": "git status"}, "PowerShell: git status"),
]


def load_guard():
    spec = importlib.util.spec_from_file_location("aios_guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def path_checks():
    """How the guard reads Windows paths. These run on any system, so they test the text rules, not a real Windows machine."""
    g = load_guard()
    return [
        ("Git Bash path /c/Users/me/x becomes C:/Users/me/x", g.native("/c/Users/me/x", windows=True) == "C:/Users/me/x"),
        ("Git Bash path /cygdrive/d/work becomes D:/work", g.native("/cygdrive/d/work", windows=True) == "D:/work"),
        ("a backslash is a separator", g.native("private\\README.md", windows=False) == "private/README.md"),
        ("a trailing dot or space is dropped on Windows (private. and private are the same folder)", g.native("private. /a", windows=True) == "private/a"),
        ("a name that looks like a drive letter on Linux is left alone", g.native("/c", windows=False) == "/c"),
        ("/dev/null, NUL and $null are safe places to discard output", all(n in g.NULL_NAMES for n in ("/dev/null", "nul", "$null"))),
        ("PRIVATE/ is private/ (case)", g.in_private(os.path.join(g.ROOT, "PRIVATE", "x"))),
    ]


def hook_checks():
    """The exact hook command in .claude/settings.json, run with different Pythons on the PATH. Needs `sh`."""
    sh = shutil.which("sh")
    if not sh or os.name == "nt":
        return None
    cmd = json.load(open(os.path.join(ROOT, ".claude", "settings.json")))["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        only_python, nothing, store_stub = (os.path.join(tmp, n) for n in ("only-python", "nothing", "store-stub"))
        for d in (only_python, nothing, store_stub):
            os.mkdir(d)
        os.symlink(sys.executable, os.path.join(only_python, "python"))
        os.symlink(sys.executable, os.path.join(store_stub, "python"))
        with open(os.path.join(store_stub, "python3"), "w") as f:   # like the Windows Store shortcut: exists, does not run
            f.write("#!/bin/sh\nexit 9\n")
        os.chmod(os.path.join(store_stub, "python3"), 0o755)

        def run(path, payload):
            env = {"PATH": path, "CLAUDE_PROJECT_DIR": ROOT}
            return subprocess.run([sh, "-c", cmd], input=json.dumps(payload), capture_output=True, text=True, env=env).returncode
        read = {"tool_name": "Read", "tool_input": {"file_path": "README.md"}, "cwd": ROOT}
        write = {"tool_name": "Write", "tool_input": {"file_path": "AGENTS.md", "content": "x"}, "cwd": ROOT}
        ps = {"tool_name": "PowerShell", "tool_input": {"command": "Set-Content AGENTS.md x"}, "cwd": ROOT}
        out += [("hook: only `python` on the PATH, a read is allowed", run(only_python, read) == 0),
                ("hook: only `python` on the PATH, a write to AGENTS.md is blocked", run(only_python, write) == 2),
                ("hook: a `python3` that does not run (Store shortcut) is skipped, `python` is used", run(store_stub, read) == 0),
                ("hook: no Python at all, every action is blocked", run(nothing, read) == 2),
                ("hook: the PowerShell tool is checked", run(only_python, ps) == 2)]
    matcher = json.load(open(os.path.join(ROOT, ".claude", "settings.json")))["hooks"]["PreToolUse"][0]["matcher"]
    out.append(("hook matcher names PowerShell", "PowerShell" in matcher.split("|")))
    return out


def run(tool, args, env=None):
    payload = json.dumps({"tool_name": tool, "tool_input": args, "cwd": ROOT})
    e = dict(os.environ)
    e.pop("AIOS_UNLOCK", None)
    e.update(env or {})
    r = subprocess.run([sys.executable, GUARD], input=payload, capture_output=True, text=True, env=e)
    return r.returncode, r.stderr.strip()


def main():
    bad = 0
    for expect, tool, args, label in CASES:
        code, err = run(tool, args)
        got = "allow" if code == 0 else "block" if code == 2 else "error(%d)" % code
        ok = got == expect
        bad += not ok
        print("%s  %-5s  %-11s %s%s" % ("PASS" if ok else "FAIL", expect, tool, label, "" if ok else "   -> " + got + " " + err))
    # the unlock switch: core files open for the person's maintenance session, private/ stays closed
    code, _ = run("Edit", {"file_path": "AGENTS.md"}, {"AIOS_UNLOCK": "1"})
    ok = code == 0
    bad += not ok
    print("%s  allow  Edit        AGENTS.md with AIOS_UNLOCK=1" % ("PASS" if ok else "FAIL"))
    code, _ = run("Read", {"file_path": "private/a.txt"}, {"AIOS_UNLOCK": "1"})
    ok = code == 2
    bad += not ok
    print("%s  block  Read        private/ stays closed with AIOS_UNLOCK=1" % ("PASS" if ok else "FAIL"))
    total = len(CASES) + 2
    hooks = hook_checks()
    for label, ok in path_checks() + (hooks or []):
        total += 1
        bad += not ok
        print("%s  %s" % ("PASS" if ok else "FAIL", label))
    if hooks is None:
        print("SKIP  hook command checks (need `sh`; not run on Windows)")
    print("\n%d checks, %d failed" % (total, bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
