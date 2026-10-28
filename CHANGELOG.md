# Changelog

## v1.1

Changes from an outside review: six independent reviews of v1 (one of them ours, five by outside AI models) found v1 unsafe to promote, and this version applies their ranked fixes.

- **`cr` is out of setup.** `START_HERE.md` sets up `cs` only. `cr` and its flag are in an appendix, [docs/advanced.md](docs/advanced.md), with the warning first.
- **Native permissions instead of a shell parser.** `.aios/guard.py`, its tests and the hook are gone. The files that steer the AI (`AGENTS.md`, `CLAUDE.md`, `context/rules.md`, `commands/`, `.claude/`, `.opencode/`, `opencode.json`, `scripts/`, `automation/`, `.github/`) are protected by `permissions.deny` in `.claude/settings.json` and by `edit` rules in `opencode.json`. Every shell command that the tool does not treat as read-only asks you. `/prime` runs `git status` on the protected files and reports any change.
- **`private/` is removed.** Keep private files outside the workspace folder.
- **KPIs by script.** `scripts/kpi.py` writes `data/kpis.csv` (date, metric, value, source), reads targets from `data/targets.csv`, computes the gap and the change, and marks readings older than 7 days as stale. `/kpi` and `/daily-brief` run it. `data/kpi-tracker.md` is gone.
- **Docs.** A short README that opens with a real daily brief; the test notes moved to `TESTING.md`; the five-layer table appears once (in `AGENTS.md`).
- **Updates.** Kit files and your files are kept apart, with exact steps in [UPDATING.md](UPDATING.md), this changelog and a `v1.1` tag.
- **Cuts.** `skill-creator` is removed. `/create-plan` and `/implement` became one short `/plan`.
- **Tests and CI.** `tests/` and a GitHub Actions workflow run on Linux, macOS and Windows.
- **Name.** The kit is called AIOS; "Operating System" is dropped from the tagline.

## v1.0

First public release: `AGENTS.md`, `context/`, `/prime`, `/create-plan`, `/implement`, `/kpi`, `/daily-brief`, a guard hook, a session-start hook, a scheduled morning brief, and a made-up example company.
