#!/usr/bin/env python3
"""AIOS guard. One policy for every harness.

Reads one JSON object on stdin: {"tool_name": ..., "tool_input": {...}, "cwd": ...}
(Claude Code's PreToolUse payload; the OpenCode plugin sends the same shape).
Exit 0 = allow. Exit 2 = block, with the reason on stderr.

Rules (see .aios/guard.json):
  1. No tool may read or write anything in private/.
  2. No tool may write outside the workspace folder.
  3. No tool may edit a core file, unless the person started the session with AIOS_UNLOCK=1.

Bash is checked by reading the command text. That catches the common cases and is NOT a sandbox:
a program the AI writes and runs (python, node, a script) can still do anything.
Covered: redirects and write commands, `bash -c '...'` and `eval` (the inner text is checked too),
recursive reads that start at the workspace root (grep -r, find, tar, ls -R, ...), and the output flags
of curl and wget, and PowerShell (Set-Content, Out-File, Remove-Item, Get-Content, `>`, ...). The tools' own search
(Grep, Glob) skips private/ through the .ignore file.
Paths are read the Windows way too: either slash, any letter case, `C:\\...`, Git Bash `/c/...`, and `NUL` or `/dev/null`
as a place to throw output away.
"""
import glob
import json
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.realpath(os.path.dirname(HERE))
POLICY = json.load(open(os.path.join(HERE, "guard.json")))

READ_TOOLS = {"read", "glob", "grep", "list", "notebookread"}
WRITE_TOOLS = {"write", "edit", "multiedit", "notebookedit", "apply_patch", "patch"}
WRITE_WORDS = {"rm", "mv", "cp", "tee", "touch", "mkdir", "rmdir", "ln", "chmod", "chown", "truncate",
               "dd", "install", "rsync", "unlink", "shred"}
GIT_WRITES = {"checkout", "reset", "clean", "rm", "mv", "restore", "stash", "apply", "rebase", "merge", "pull", "switch"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", ">&"}


def deny(msg):
    sys.stderr.write("AIOS guard: " + msg + "\n")
    sys.exit(2)


IS_WINDOWS = os.name == "nt"
# Windows and macOS folders ignore letter case: PRIVATE/x is private/x there. Where the filesystem is case-blind, compare that way.
CASE_BLIND = IS_WINDOWS or sys.platform == "darwin"
NULL_NAMES = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty", "nul", "$null"}


def native(path, windows=None):
    """Turn a path as the AI wrote it into one this machine understands.
    Either slash works, `C:\\x` stays a drive path, and on Windows a Git Bash path (`/c/x`, `/cygdrive/c/x`) becomes `C:/x`."""
    windows = IS_WINDOWS if windows is None else windows
    path = os.path.expanduser(path).replace("\\", "/")
    m = re.match(r"^(?:/cygdrive)?/([A-Za-z])(?:/|$)", path)
    if windows and m:
        path = m.group(1).upper() + ":/" + path[m.end():]
    if windows:
        # Windows drops a trailing dot or space from every name: `private.` and `private ` are private
        drive, rest = re.match(r"^([A-Za-z]:)?(.*)$", path, re.S).groups()
        path = (drive or "") + "/".join(seg if seg in ("", ".", "..") else (seg.rstrip(" .") or seg) for seg in rest.split("/"))
    return path


def real(path, cwd):
    path = native(path)
    if not IS_WINDOWS and re.match(r"^[A-Za-z]:/", path):
        # a Windows drive path means nothing on this machine: it is somewhere outside the workspace
        return "/__windows_drive__/" + path[0].lower() + path[2:]
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    return os.path.realpath(path)


def norm(path):
    path = os.path.normpath(path)
    return os.path.normcase(path).casefold() if CASE_BLIND else path


def inside(path, base):
    path, base = norm(path), norm(base)
    return path == base or path.startswith(base.rstrip(os.sep) + os.sep)


def inside_ci(path, base):
    # private/ and the core files are compared without regard to case on every system: fail closed
    return inside(path.casefold(), base.casefold())


def in_private(path):
    return any(inside_ci(path, os.path.join(ROOT, p)) for p in POLICY["private"])


def is_core(path):
    return any(inside_ci(path, os.path.join(ROOT, p)) for p in POLICY["core"])


def unlocked():
    return os.environ.get(POLICY["unlock_env"]) == "1"


def check_path(path, cwd, writing):
    p = real(path, cwd)
    if in_private(p):
        deny("private/ is closed to the AI (read and write). Open the file yourself and paste only what the AI needs.")
    if writing:
        if not inside(p, ROOT):
            deny("writes outside the workspace are blocked: " + p)
        if is_core(p) and not unlocked():
            deny("core file, edits are blocked: " + os.path.relpath(p, ROOT) +
                 ". Write the proposed change to plans/ and ask the person to apply it, "
                 "or have them start a session with AIOS_UNLOCK=1.")


def patch_paths(text):
    out = []
    for line in text.splitlines():
        for tag in ("*** Update File:", "*** Add File:", "*** Delete File:", "*** Move to:"):
            if line.startswith(tag):
                out.append(line[len(tag):].strip())
    return out


def check_target(t, cwd, writing):
    """One token that names a path. `writing` says the command changes it."""
    if not t or t.casefold() in NULL_NAMES:
        return
    if t.startswith("$") or "`" in t:
        if writing:
            deny("this command writes and uses a shell variable or substitution; the guard cannot tell where it writes: " + t)
        return
    cands = [t]
    if any(c in t for c in "*?["):
        # a wildcard that could match private/ (even an empty one) is refused
        parts = os.path.expanduser(t).split("/")
        for i in range(1, len(parts) + 1):
            for m in glob.glob(os.path.join(cwd, "/".join(parts[:i]))):
                if in_private(os.path.realpath(m)):
                    deny("private/ is closed to the AI (this wildcard would reach it): " + t)
        cands = glob.glob(os.path.join(cwd, os.path.expanduser(t))) or [t]
    for c in cands:
        p = real(c, cwd)
        if in_private(p):
            deny("private/ is closed to the AI (read and write): " + t)
        if writing:
            core_names = {norm(os.path.join(ROOT, x)) for x in POLICY["core"]}
            names_a_path = "/" in t or "\\" in t or t.startswith((".", "~")) or re.match(r"^[A-Za-z]:", t) or norm(p) in core_names
            if names_a_path and not inside(p, ROOT):
                deny("this command writes, and it names a path outside the workspace: " + t)
            if is_core(p) and not unlocked():
                deny("this command writes, and it names a core file: " + t)


SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "ash", "fish"}
INLINE_CODE = {"python": {"-c"}, "python3": {"-c"}, "node": {"-e", "-p", "--eval", "--print"}, "perl": {"-e", "-E"},
               "ruby": {"-e"}, "php": {"-r"}, "deno": {"eval"}, "bun": {"-e", "--eval"}}
SEPARATORS = {"&&", "||", ";", "|", "&", "(", ")"}
# Commands that read a whole tree. `implicit` = reads the current folder when no path is named.
ALWAYS_RECURSIVE = {"find": True, "fd": True, "tree": True, "du": True, "ack": True, "rgrep": True,
                    "tar": False, "bsdtar": False, "gtar": False, "zip": False, "7z": False, "7za": False, "rsync": False, "scp": False}
# Skip private/ by themselves (through .ignore) unless told not to.
IGNORE_AWARE = {"rg": {"-u", "-uu", "-uuu", "--unrestricted", "--no-ignore", "--no-ignore-dot", "--no-ignore-vcs"},
                "ag": {"-u", "--unrestricted", "-U", "--skip-vcs-ignores"}}
EXCLUDE_FLAGS = {"grep": {"--exclude-dir"}, "rg": {"-g", "--glob"}, "ag": {"--ignore"}, "find": {"-path", "-ipath", "-wholename", "-name", "-iname"},
                 "tar": {"--exclude"}, "du": {"--exclude"}, "ls": {"-I", "--ignore"}, "zip": {"-x", "--exclude"}, "fd": {"-E", "--exclude"},
                 "tree": {"-I"}, "rsync": {"--exclude"}, "7z": {"-x"}}


def cluster_has(args, chars):
    """True if a short-flag cluster such as -rn or -lR holds one of `chars`."""
    return any(a.startswith("-") and not a.startswith("--") and len(a) > 1 and any(c in chars for c in a[1:]) for a in args)


def recursive_reader(base, args):
    """Return (is_recursive, implicit): does this command read a folder tree, and does it default to the current folder."""
    if base in {"grep", "egrep", "fgrep", "zgrep", "zegrep", "zfgrep"}:
        rec = (cluster_has(args, "rR") or "--recursive" in args or "--dereference-recursive" in args
               or "recurse" in args or "--directories=recurse" in args)
        return rec, True
    if base in IGNORE_AWARE:
        return any(a in IGNORE_AWARE[base] or (a.startswith("-u") and set(a[1:]) == {"u"}) for a in args), True
    if base == "ls":
        return cluster_has(args, "R") or "--recursive" in args, True
    if base in {"cp"}:
        return cluster_has(args, "rRa") or "--recursive" in args or "--archive" in args, False
    if base in ALWAYS_RECURSIVE:
        return True, ALWAYS_RECURSIVE[base]
    return False, False


def exclusion_marks(base, args):
    """Indexes in args that exclude private/ from a recursive read (such as --exclude-dir=private)."""
    flags = EXCLUDE_FLAGS.get(base, set())
    marks = set()

    def names_private(v):
        v = v.lstrip("!").replace("\\", "/")
        while v.startswith("./"):
            v = v[2:]
        v = v.lstrip("/")
        for suffix in ("/**", "/*", "/"):
            if v.endswith(suffix):
                v = v[: -len(suffix)]
        return v.casefold() == "private"

    for i, a in enumerate(args):
        value = None
        if a in flags and i + 1 < len(args):
            value, idx = args[i + 1], i + 1
        elif "=" in a and a.split("=", 1)[0] in flags:
            value, idx = a.split("=", 1)[1], i
        if value is not None and names_private(value):
            # find needs the pattern to prune or negate the path, otherwise -path private/ selects it
            if base == "find" and not (args[i + 2:i + 3] == ["-prune"] or (i > 0 and args[i - 1] in {"!", "-not"})):
                continue
            marks.add(idx)
            marks.add(i)
    return marks


def refuse_if_walks_private(base, args, implicit, cwd):
    """A tree walk is refused when a folder it names holds private/, or when it names none and starts in a folder that holds it."""
    private_dir = os.path.join(ROOT, POLICY["private"][0])
    named = False
    for a in args:
        if a.startswith("-") or any(c in a for c in "*?["):
            continue
        p = real(a, cwd)
        if os.path.exists(p):
            named = True
            if inside_ci(private_dir, p):
                deny("`%s` would read through private/, which is closed to the AI. Name a folder (for example context/ or outputs/) "
                     "or exclude private/ (for example --exclude-dir=private): %s" % (base, a))
    if implicit and not named and inside_ci(private_dir, cwd):
        deny("`%s` with no folder named would read through private/, which is closed to the AI. Name a folder "
             "(for example context/) or exclude private/." % base)


def check_recursive(tokens, cwd):
    """A read that walks a folder tree must not start at the workspace root or above private/ unless it excludes private/."""
    segs, cur = [], []
    for t in tokens:
        if t in SEPARATORS:
            segs.append(cur)
            cur = []
        else:
            cur.append(t)
    segs.append(cur)
    for seg in segs:
        for i, t in enumerate(seg):
            base = os.path.basename(t)
            args = seg[i + 1:]
            rec, implicit = recursive_reader(base, args)
            if not rec:
                continue
            if exclusion_marks(base, args):
                continue
            refuse_if_walks_private(base, args, implicit, cwd)


def check_nested(tokens, cwd):
    """`bash -c '...'`, `eval ...` and inline interpreter code hide a command inside one token: check the inside too."""
    for i, t in enumerate(tokens):
        base = os.path.basename(t)
        rest = tokens[i + 1:]
        if base in SHELLS:
            for j, a in enumerate(rest):
                if a.startswith("-") and not a.startswith("--") and "c" in a[1:] and j + 1 < len(rest):
                    check_bash(rest[j + 1], cwd)
                    break
        elif base == "eval" and rest:
            check_bash(" ".join(rest), cwd)
        elif exe_less(base) in {"powershell", "pwsh", "cmd"}:
            inner = [a for a in rest if not a.startswith(("-", "/")) or " " in a]
            if inner:
                check_powershell(" ".join(inner), cwd)
        elif re.match(r"^python[0-9.]*$", base) or base in INLINE_CODE:
            flags = INLINE_CODE.get(base) or INLINE_CODE["python3"]
            for j, a in enumerate(rest):
                if a in flags and j + 1 < len(rest) and "private" in rest[j + 1].casefold():
                    deny("inline %s code that names private/ is refused; private/ is closed to the AI" % base)


def output_flag_targets(tokens):
    """curl and wget write where their output flags say. Return the indexes of tokens that are write targets (and rewrite attached forms)."""
    marks = set()
    spec = {"curl": ({"-o", "--output", "--output-dir", "-D", "--dump-header", "-c", "--cookie-jar", "--stderr", "--trace", "--trace-ascii"}, ("-o", "-D", "-c")),
            "wget": ({"-O", "--output-document", "-P", "--directory-prefix", "-o", "--output-file", "-a", "--append-output"}, ("-O", "-P", "-o", "-a"))}
    prog = None
    for i, t in enumerate(tokens):
        b = os.path.basename(t)
        if b in spec:
            prog = b
            continue
        if prog is None:
            continue
        flags, short = spec[prog]
        if t in flags and i + 1 < len(tokens):
            marks.add(i + 1)
        elif "=" in t and t.split("=", 1)[0] in flags:
            tokens[i] = t.split("=", 1)[1]
            marks.add(i)
        elif t.startswith(short) and not t.startswith("--") and len(t) > 2:
            tokens[i] = t[2:]
            marks.add(i)
    return marks


AWK_WRITES = re.compile(r"\b(print|printf)\b[^;}]*>|\bsystem\s*\(|\|\s*\"|\bgetline\b[^;}]*<|\|&")


def check_awk(tokens):
    for i, t in enumerate(tokens):
        if os.path.basename(t) in {"awk", "gawk", "mawk", "nawk"}:
            for a in tokens[i + 1:]:
                if AWK_WRITES.search(a):
                    deny("an awk program that writes to a file or runs a command cannot be checked; use a redirect on the command instead")


def git_subcommand(tokens):
    """The git subcommand, skipping options that take an argument (-C path, -c key=value)."""
    i = tokens.index("git") + 1
    while i < len(tokens):
        t = tokens[i]
        if t in {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}:
            i += 2
            continue
        if t.startswith("-"):
            i += 1
            continue
        return t
    return ""


# ---------------------------------------------------------------------------------------------------------
# PowerShell (and cmd). Claude Code on Windows has a PowerShell tool next to Bash: same policy, different text.
# A backslash is part of a path here, so this reads the command with its own small tokenizer.

PS_WRITE = {"set-content", "add-content", "out-file", "remove-item", "copy-item", "move-item", "new-item", "rename-item", "clear-content",
            "set-item", "tee-object", "export-csv", "export-clixml", "set-itemproperty", "new-itemproperty", "remove-itemproperty",
            "expand-archive", "compress-archive", "set-acl", "robocopy", "xcopy", "icacls", "takeown", "attrib", "mklink",
            "sc", "ac", "ri", "rm", "rmdir", "rd", "del", "erase", "cp", "cpi", "copy", "mv", "mi", "move", "rni", "ren", "rename",
            "mkdir", "md", "ni", "tee", "clc", "si", "ln", "touch", "dd", "truncate"}
PS_WEB = {"invoke-webrequest", "iwr", "invoke-restmethod", "irm", "curl", "wget", "start-bitstransfer"}
PS_WEB_OUT = {"-outfile", "-destination"}              # the only flags that make a web cmdlet write a file
PS_TEXT_PARAMS = {"-value", "-inputobject", "-encoding", "-itemtype", "-stream", "-newname"}   # the next word is text, not a place
PS_COPY = {"copy-item", "cpi", "cp", "copy", "xcopy", "robocopy"}
PS_LIST = {"get-childitem", "gci", "ls", "dir", "copy-item", "cpi", "cp", "copy", "get-item", "gi", "findstr"}
PS_WALKERS = {"robocopy", "xcopy", "compress-archive", "tar", "bsdtar", "7z", "zip"}
PS_RECURSE_FLAG = re.compile(r"^(-r(e(c(u(r(s(e)?)?)?)?)?)?|/s|/e)$", re.I)
PS_DOTNET_WRITE = re.compile(r"::\s*(write|append|delete|copy|move|create|open|replace|set)", re.I)
PS_RUNNERS = {"powershell", "pwsh", "cmd", "invoke-expression", "iex"}
PS_BASH = {"bash", "sh", "zsh", "wsl"}


def ps_lex(cmd):
    """Split PowerShell text into statements. A statement is a list of (kind, text, expands): kind "w" is a word,
    ">" is a file that a redirect writes. `expands` is True when the word holds a variable or expression."""
    stmts, cur = [], []
    word, quoted, expands, redirect_next = [], False, False, False
    i, n = 0, len(cmd)

    def flush():
        nonlocal word, quoted, expands, redirect_next
        if word or quoted:
            cur.append((">" if redirect_next else "w", "".join(word), expands))
            redirect_next = False
        word, quoted, expands = [], False, False

    def end():
        nonlocal cur
        flush()
        if cur:
            stmts.append(cur)
        cur = []

    while i < n:
        c = cmd[i]
        if c == "`" and i + 1 < n:
            word.append(cmd[i + 1])
            i += 2
        elif c in "'\"":
            quoted = True
            i += 1
            while i < n:
                ch = cmd[i]
                if ch == c:
                    if cmd[i + 1:i + 2] == c:      # a doubled quote inside a string is one quote
                        word.append(c)
                        i += 2
                        continue
                    break
                if c == '"' and ch == "`" and i + 1 < n:
                    word.append(cmd[i + 1])
                    i += 2
                    continue
                if c == '"' and ch == "$":
                    expands = True
                word.append(ch)
                i += 1
            i += 1
        elif c in " \t\r,(){}":
            flush()
            i += 1
        elif c in "\n;|":
            end()
            i += 1
        elif c == "&":
            end()
            i += 2 if cmd[i + 1:i + 2] == "&" else 1
        elif c == ">" or (c in "0123456789*" and not word and re.match(r"[0-9*]>", cmd[i:i + 2])):
            flush()
            j = i
            while j < n and cmd[j] in "0123456789*":
                j += 1
            while j < n and cmd[j] == ">":
                j += 1
            if cmd[j:j + 1] == "&":      # 2>&1 copies a stream; it writes no file
                j += 1
                while j < n and cmd[j] in "0123456789-":
                    j += 1
            else:
                redirect_next = True
            i = j
        else:
            if c == "$":
                expands = True
            word.append(c)
            i += 1
    end()
    return stmts


def exe_less(t):
    """A command name in lower case without `.exe`: `Robocopy.EXE` and `robocopy` are the same command."""
    t = t.casefold()
    return t[:-4] if t.endswith(".exe") else t


def looks_like_text(t):
    """A word with spaces, or a URL, that does not start like a path: text to write, not a place."""
    return bool(re.search(r"\s|://", t)) and not re.match(r"^([A-Za-z]:|[/\\.~])", t)


def ps_param(t):
    """('-path', 'value') for -Path:value, ('-path', '') for -Path, None for a plain word."""
    m = re.match(r"^-([A-Za-z]+)(?::(.*))?$", t, re.S)
    return ("-" + m.group(1).casefold(), m.group(2) or "") if m else None


def ps_check_runners(words, names, cwd):
    """A shell or interpreter inside the command: read the text it will run."""
    for j, nm in enumerate(names):
        tail = [w for w, _ in words[j + 1:]]
        if nm in PS_BASH:
            if nm == "wsl":
                check_bash(" ".join(tail), cwd)
            for k, a in enumerate(tail):
                if a.startswith("-") and not a.startswith("--") and "c" in a[1:] and k + 1 < len(tail):
                    check_bash(tail[k + 1], cwd)
        elif nm in PS_RUNNERS:
            if any(re.match(r"^-e(nc\w*)?$", a, re.I) for a in tail):
                deny("an encoded PowerShell command cannot be read; write the command out in full")
            inner = [(w, e) for w, e in words[j + 1:] if not (w.startswith(("-", "/")) and " " not in w)]
            if any(e for _, e in inner):
                deny("this runs text held in a variable; the guard cannot tell what it does. Write the command out in full.")
            if inner:
                check_powershell(" ".join(w for w, _ in inner), cwd)


def ps_check_walks(names, words, cwd):
    """Get-ChildItem -Recurse, dir /s, Compress-Archive, robocopy and friends must name a folder, or start where private/ is not below them."""
    for j, nm in enumerate(names):
        args = []
        for w, _ in words[j + 1:]:
            p = ps_param(w)
            args.append(p[1] if p and p[1] else w)
        flagged = any(PS_RECURSE_FLAG.match(a) for a in args)
        if (nm in PS_LIST and flagged) or nm in PS_WALKERS:
            refuse_if_walks_private(nm, [native(a) for a in args], nm in PS_LIST, cwd)


def check_powershell(cmd, cwd):
    """The same policy as check_bash, for PowerShell and cmd text."""
    for st in ps_lex(cmd):
        words = [(t, e) for k, t, e in st if k == "w"]
        names = [exe_less(t) for t, _ in words]
        ps_check_runners(words, names, cwd)
        ps_check_walks(names, words, cwd)
        web = bool(set(names) & PS_WEB)
        writing = (bool(set(names) & PS_WRITE) or any(PS_DOTNET_WRITE.search(t) for t, _ in words)) and not web
        copying = bool(set(names) & PS_COPY)
        plain = [x for x, (k, t, _) in enumerate(st) if k == "w" and x > 0 and ps_param(t) is None and exe_less(t) not in PS_WRITE | PS_WEB]
        skip_next = out_next = False
        for idx, (kind, t, e) in enumerate(st):
            if skip_next:
                skip_next = False
                continue
            is_write = kind == ">" or out_next
            out_next = False
            text = False
            if kind == "w" and idx > 0:           # the first word is the command (or a value being piped); the rest are its arguments
                if exe_less(t) in PS_WRITE | PS_WEB:
                    continue                      # the name of another command inside a script block
                if re.match(r"^/[A-Za-z?]$", t):
                    continue                      # a cmd switch such as /c or /s
                pr = ps_param(t)
                if pr:
                    p, v = pr
                    if p in PS_TEXT_PARAMS:
                        skip_next = not v
                        continue
                    if web and p in PS_WEB_OUT:
                        if not v:
                            out_next = True
                            continue
                        t, is_write = v, True
                    elif v:
                        t, is_write = v, writing
                    else:
                        continue
                elif writing:
                    is_write = not copying or idx == plain[-1]    # Copy-Item source dest: only the last word is written
                    if looks_like_text(t):
                        text, is_write = True, False              # the text that Set-Content and friends write is not a place
            if t.casefold() in NULL_NAMES:
                continue
            if e and not text and (is_write or "private" in t.casefold()):
                deny("this PowerShell command builds a path from a variable or expression (%s); the guard cannot tell where it points. "
                     "Write the path out in full." % t)
            if text and "private" not in t.casefold():
                continue
            check_target(native(t), cwd, is_write)


def check_bash(cmd, cwd):
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        deny("could not read this shell command safely; run it yourself or simplify it")
    check_nested(tokens, cwd)
    check_recursive(tokens, cwd)
    check_awk(tokens)
    write_marks = output_flag_targets(tokens)
    # tokens that only exclude private/ from a search are not "reading" it
    skip_idx = set()
    for i, t in enumerate(tokens):
        base = os.path.basename(t)
        if base in EXCLUDE_FLAGS:
            end = next((k for k in range(i + 1, len(tokens)) if tokens[k] in SEPARATORS), len(tokens))
            skip_idx |= {i + 1 + m for m in exclusion_marks(base, tokens[i + 1:end])}
    base_words = {os.path.basename(t) for t in tokens}
    writing = bool(base_words & WRITE_WORDS)
    if base_words & {"sed", "perl"} and any(t == "--in-place" or (t.startswith("-i") and not t.startswith("--")) for t in tokens):
        writing = True
    if "git" in base_words:
        writing = writing or git_subcommand(tokens) in GIT_WRITES
    skip = {"&&", "||", ";", "|", "&", "(", ")", "<", "<<", "<<<"}
    after_redirect = False
    for i, t in enumerate(tokens):
        if t in REDIRECTS:
            # `2>&1` and `>&2` duplicate a file descriptor; anything else after a redirect is a file that gets written
            nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
            after_redirect = not (t == ">&" and (nxt.isdigit() or nxt == "-"))
            continue
        if t in skip:
            after_redirect = False
            continue
        if i in skip_idx:
            continue
        if t.startswith("-") and "/" not in t and "=" not in t and i not in write_marks:
            continue
        if "=" in t and not t.startswith(("/", ".", "~", "$")) and i not in write_marks:
            t = t.split("=", 1)[1]
        check_target(t, cwd, writing or after_redirect or i in write_marks)
        after_redirect = False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        deny("no readable tool payload; blocking to be safe")
    tool = (data.get("tool_name") or "").lower()
    args = data.get("tool_input") or {}
    cwd = os.path.realpath(data.get("cwd") or os.getcwd())
    if tool == "bash":
        check_bash(args.get("command") or "", cwd)
    elif tool == "powershell":
        check_powershell(args.get("command") or "", cwd)
    elif tool in READ_TOOLS or tool in WRITE_TOOLS:
        writing = tool in WRITE_TOOLS
        paths = [args.get(k) for k in ("file_path", "filePath", "path", "notebook_path") if args.get(k)]
        if tool in {"apply_patch", "patch"}:
            paths += patch_paths(args.get("patchText") or args.get("patch") or "")
        for p in paths:
            check_path(p, cwd, writing)
        # A search rooted at the workspace can walk into private/. The harness deny rules cover that,
        # and private/ is gitignored, so ripgrep skips it. Here we only refuse patterns that name it.
        for k in ("pattern", "glob", "include"):
            v = args.get(k)
            if isinstance(v, str) and any(part == "private" for part in v.replace("\\", "/").split("/")):
                deny("private/ is closed to the AI (the search pattern names it): " + v)
    sys.exit(0)


if __name__ == "__main__":
    main()
