# Daily brief

Turn the context and the numbers into judgment: what matters, what slipped, what to do. Read-only except for one draft file.

## Variables

focus: $ARGUMENTS (optional: a project, a person or a topic to weigh more heavily)

## Steps

1. Read `context/strategy.md`, `context/current-data.md`, `context/personal-info.md` and `context/rules.md`.
2. Run `python3 scripts/kpi.py status` (if `python3` is not found, use `python`, then `py`). Use its table as it is: do not recompute a gap or a change. Its first line gives today's date; use that date everywhere. Any row marked STALE is a reading older than 7 days: say it is stale, do not treat it as current.
3. List `plans/` and `outputs/drafts/`. Note plans whose status is still `Draft` and drafts that have not been sent.
4. Decide, using only what is in those files and the table:
   - **Matters:** at most three items, tied to a strategic priority.
   - **Slipped:** anything past its date, behind its target, stale, or with no update for more than two weeks. Name the file or metric the evidence comes from.
   - **Do:** at most three actions, each with an owner (me or you) and one line on why. Mark anything that needs my approval under `context/rules.md`.
5. Never invent a number, a date or a name. If the files do not say, write "not in the files" and add it to **Gaps**.
6. Save the brief as `outputs/drafts/daily-brief-YYYY-MM-DD.md` with the headings: Matters, Slipped, Do, Gaps. If the file exists, overwrite it.

## Report

Print the brief in the chat, then the path of the saved file. Keep it under 250 words. A person reads it and sends it on; you do not send anything.
