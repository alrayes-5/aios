# Shell Aliases

Two shell aliases start a Claude Code session in this workspace and run `/prime`. Set them up first, before anything else.

## Setup

Add these lines to your `~/.zshrc` (or `~/.bashrc`):

```bash
alias cs='claude "/prime"'
alias cr='claude --dangerously-skip-permissions "/prime"'
```

Then reload your shell: `source ~/.zshrc`

Run them from inside the AIOS folder: `cd ~/aios && cs`.

### Windows (PowerShell)

PowerShell has no `alias` with arguments, so use two functions. Open your profile with `notepad $PROFILE` (if the file does not exist, run `New-Item -Force $PROFILE` first) and add:

```powershell
function cs { claude "/prime" }
function cr { claude --dangerously-skip-permissions "/prime" }
```

Then reload: `. $PROFILE`. If PowerShell refuses to load the profile, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

Run them from inside the AIOS folder: `cd $HOME\aios; cs`.

## The aliases

### `cs`: Claude Safe

Starts Claude Code and runs `/prime` to load the workspace context. Claude asks for permission before running commands or changing files.

**Use when:** the task is new, sensitive, or you want to see and approve each action.

### `cr`: Claude Run

Starts Claude Code with permission prompts turned off, then runs `/prime`. Claude can run commands and change files without asking.

**Use when:** the task is familiar and constant approvals slow you down.

## Read this before using `cr`

With permission prompts off, nothing but the guard stands between the AI and your files. In this kit the guard hook (`.aios/guard.py`) is separate from the permission prompts, and `START_HERE.md` says what it blocks and what it does not. The guard is not a sandbox. Use `cr` only in this folder, and only for work you would be comfortable letting the AI do unsupervised.

## OpenCode

OpenCode has no `cs`/`cr` pair. Start it in the workspace folder with `opencode` and type `/prime`. Its permission rules live in `opencode.json`.
