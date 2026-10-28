# Advanced: `cr`, Claude Code without permission prompts

**Read this before you add `cr`. It is not for first use, and it is not part of setting AIOS up.**

`cs` (in `START_HERE.md`) is the normal way to start: Claude asks before it runs a command or changes a file. `cr` is the same start with Claude Code's permission prompts turned off, using the flag `--dangerously-skip-permissions`. With it:

- Claude runs every shell command and writes every file **without asking you**.
- The flag belongs to the alias, so it applies in **every folder you start it in**, not only in this one. Anything your user account can do, the AI can do.
- The edit rules in `.claude/settings.json` still hold, but a shell command is not stopped by them: a script the AI writes and runs can change any file, and `curl` can reach any address. In the run recorded in [TESTING.md](../TESTING.md), a one-line Python command rewrote `commands/prime.md` and a shell redirect wrote a file outside the folder, with the flag on.
- If a web page or a document the AI reads tells it to do something, nothing asks you first.

Use it only when you would be comfortable leaving the AI alone with your whole account, for a task you know well. The `git status` check in `/prime` will show you if a protected file changed, after the fact.

If you still want it, add it next to `cs`:

```bash
alias cr='claude --dangerously-skip-permissions "/prime"'
```

On Windows PowerShell, in the same profile file as `cs`:

```powershell
function cr { claude --dangerously-skip-permissions "/prime" }
```

To undo it, delete that line and reload your shell (`source ~/.zshrc`, or `. $PROFILE` in PowerShell).
