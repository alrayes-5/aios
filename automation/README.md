# Automation

Layer 4: work that happens without a session.

## Already in this kit

| What | Where | When it runs |
| ---- | ----- | ------------ |
| Morning brief | `automation/morning-brief.sh` | When you schedule it (below) |

The brief runs `/daily-brief`, which runs `scripts/kpi.py status`. The script is the only shell command it is allowed to run.

## Schedule the morning brief

Run it once by hand first, to see it work:

```bash
sh automation/morning-brief.sh claude      # or: opencode
```

It writes `outputs/drafts/daily-brief-YYYY-MM-DD.md`. To run it every weekday at 07:30, add one line with `crontab -e`. Use full paths: cron has a short PATH and does not know your aliases.

```
30 7 * * 1-5 AIOS_BIN=/full/path/to/claude /full/path/to/your-workspace/automation/morning-brief.sh claude >> /full/path/to/your-workspace/automation/morning-brief.log 2>&1
```

Find the full path of the agent with `command -v claude` (or `command -v opencode`).

### On Windows: Task Scheduler

`morning-brief.sh` is a shell script; on Windows, Task Scheduler can start the agent directly. Find its full path first: in PowerShell, `(Get-Command claude).Source` (or `opencode`). Then open Task Scheduler, choose **Create Task**, and set:

- **Triggers:** New, Weekly, Monday to Friday, 07:30.
- **Actions:** New, Start a program.
  - Program/script: the full path from above (for example `C:\Users\you\AppData\Roaming\npm\claude.cmd`).
  - Add arguments: `-p "/daily-brief" --allowedTools Read Glob Grep "Edit(outputs/drafts/**)" "Bash(python scripts/kpi.py status)"`. For OpenCode use `run --command daily-brief ""` instead.
  - Start in: the full path of your AIOS folder (for example `C:\Users\you\aios`). This one matters: the agent reads the workspace from where it starts.
- **Conditions:** untick "Start the task only if the computer is on AC power" if you use a laptop.

Run the task once from Task Scheduler (right-click, Run) and check that `outputs/drafts/daily-brief-<date>.md` appears. This was not run when the kit was tested: see [TESTING.md](../TESTING.md).

## Next steps (not in the kit)

Add your own triggers the same way: a script in `automation/` that runs one command, and a schedule or a file watcher that calls it. Keep each one small, keep drafts in `outputs/drafts/`, and keep a person as the one who sends.
