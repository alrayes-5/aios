# Start here

AIOS is a folder of plain files. You open an AI agent in that folder, and the agent reads the files first, so it knows who you are, what your business is and what matters now. Allow about 15 minutes.

## 1. Before you begin

- A folder on your own computer with this kit in it: `git clone https://github.com/alrayes-5/aios.git ~/aios` (or download the ZIP and unpack it to `~/aios`).
- Python 3.8 or newer, only for `/kpi` and `/daily-brief` (they run `scripts/kpi.py`). Check with `python3 --version`. On Windows install it from [python.org](https://www.python.org/downloads/) and tick "Add python.exe to PATH"; the commands then use `python` or `py`.
- One of: [Claude Code](https://code.claude.com/docs) (paid account), [OpenCode](https://opencode.ai) (free, works with free models), or your own AI tool (Path C).

## 2. Make the folder a git repository

Skip this if you cloned the kit (it already is one). If you downloaded the ZIP:

```bash
cd ~/aios
git init
git add -A
git commit -m "AIOS baseline"
```

`/prime` runs `git status` on the files that steer the AI (see "Protected files" in `AGENTS.md`) and tells you at the top of its answer if one of them changed. After you edit a protected file yourself, commit it, so the next check starts clean.

## 3. Set up `cs`

`cs` opens Claude Code in your workspace and runs `/prime`. In this mode Claude asks before it changes a file or runs a command.

**macOS and Linux:** add this to `~/.zshrc` or `~/.bashrc`, then `source ~/.zshrc`:

```bash
alias cs='claude "/prime"'
```

**Windows (PowerShell):** `notepad $PROFILE` (if it says the file does not exist, run `New-Item -Force $PROFILE` first), add this, save, and reload with `. $PROFILE`:

```powershell
function cs { claude "/prime" }
```

If PowerShell refuses to load the profile, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

From now on: `cd ~/aios` (on Windows `cd $HOME\aios`), then `cs`. OpenCode and other AI tools have no `cs`; see the paths below. A faster, riskier start exists, and is explained in [docs/advanced.md](docs/advanced.md). Do not use it yet.

## 4. Fill in your context

Open these five files and replace the text in `[brackets]` with your own words. Short is fine.

| File | What goes in |
| ---- | ------------ |
| `context/personal-info.md` | Who you are, your role, how you like to work |
| `context/business-info.md` | What the business is, what it sells, to whom |
| `context/strategy.md` | Your goals and priorities now |
| `context/current-data.md` | The current state: what is going on this month |
| `context/rules.md` | What the AI may do alone, what needs your approval, what data never goes in |

Or run `/prime` and say yes when it offers to ask you the questions: it writes an answer only after you confirm it. To see a finished version first, open `example/` (a made-up bakery cooperative).

Keep passwords, contracts and private files **outside** this folder. Nothing in the kit hides files from the AI.

## 5. Pick your path

### Path A: Claude Code

1. `cd ~/aios`, then `cs`. Claude Code asks you to trust the folder the first time, then runs `/prime`.
2. Run `/daily-brief`. It writes `outputs/drafts/daily-brief-<date>.md`.
3. Add a number with `/kpi define Weekly sign-ups people 50 up`, then `/kpi add "Weekly sign-ups" 37 "signup dashboard"`. Use `/plan` before a bigger change.

Claude Code will ask before it runs the KPI script. That is normal. The edit rules are in `.claude/settings.json`; `CLAUDE.md` points to `AGENTS.md`.

`.claude/settings.json` also turns on Claude Code's sandbox, which according to its documentation applies the same edit rules to shell commands. It works on macOS, Linux and WSL2; on Linux and WSL2 install `bubblewrap` and `socat` first (`sudo apt-get install bubblewrap socat`). On native Windows, or if those are missing, Claude Code says the sandbox is off and runs without it: the edit rules for its own file tools still hold, and shell commands still ask you. The sandbox was not run when this kit was tested: see [TESTING.md](TESTING.md).

### Path B: OpenCode (free)

1. Install OpenCode and pick a model. Free models work.
2. `cd ~/aios`, then `opencode`.
3. Type `/prime`, then `/daily-brief`.

OpenCode reads `AGENTS.md` itself, takes its commands from `.opencode/commands/` and its permission rules from `opencode.json`. To run one command without opening the screen: `opencode run --command prime ""`.

### Path C: your own AI (Claude Cowork, Codex, ChatGPT or any other)

For people who do not want a terminal. Give your AI the link `https://github.com/alrayes-5/aios` or the folder path (or upload the ZIP), and send this prompt:

```text
I want you to set up an AIOS workspace for me. AIOS is a folder of plain files that tells an AI agent who I am, what my business is and what matters now, so every session starts informed.

The kit is here: [paste the link https://github.com/alrayes-5/aios, or the folder path on my computer]

1. Read START_HERE.md, AGENTS.md, the files in context/ and the finished example in example/.
2. Ask me questions, a few at a time, about who I am, what my business is and who it serves, my goals right now, and what is going on this month. Wait for my answers. Do not guess.
3. Write my answers into the five files in context/ (personal-info.md, business-info.md, strategy.md, current-data.md, rules.md), in my own words. Show me each file before you save it, and change nothing until I say yes.
4. In rules.md, ask me what you may do alone, what needs my approval, and what must never go into this workspace. Keep the rules strict.
5. Do not put passwords, API keys or my customers' personal data in any file. Do not send or publish anything for me: you write drafts into outputs/drafts/ and I send them.
6. When you finish, run the steps in commands/prime.md and say back what you understood. If there is a step you cannot do in this tool, say so instead of pretending.
```

Review what the AI wrote before you rely on it. In these tools `AGENTS.md` and `context/rules.md` are instructions, not enforced rules.

## 6. Automation: a morning brief

`automation/morning-brief.sh` runs `/daily-brief` without opening a session. Try it once, then schedule it: see [automation/README.md](automation/README.md).

```bash
sh automation/morning-brief.sh claude     # or: opencode
```

## 7. Make it yours, and keep it current

- Edit `context/` as your business changes. Record numbers with `/kpi`. When you are done with `example/`, delete it.
- To add a command, write `commands/<name>.md` and copy the two small wrappers in `.claude/commands/` and `.opencode/commands/`. You do this yourself: the AI cannot edit those folders.
- Updating the kit never touches your files: see [UPDATING.md](UPDATING.md). What was tested, and what was not: [TESTING.md](TESTING.md).
