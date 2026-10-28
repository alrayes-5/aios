# Example: Kestrel Bakery Cooperative (made up)

Kestrel Bakery Cooperative does not exist. The company, the people and every number in this folder are invented to show what a filled-in AIOS workspace looks like when it is set up for a company instead of one person.

## What is different in a company setup

- `personal-info.md` describes the role of whoever runs the workspace, and who else uses it.
- `rules.md` names who approves what, because more than one person depends on the output.
- `context/team.md` is one extra file: who is on the team and who decides what.
- `data/kpis.csv` and `data/targets.csv` hold the figures the whole team agrees on.
- Drafts in `outputs/drafts/` are reviewed by a named person before anything leaves.

## Try it

Do this in a fresh copy of the kit, because it replaces the template files in `context/` and `data/`:

```bash
cp -r example/context/. context/
cp example/data/kpis.csv data/kpis.csv
cp example/data/targets.csv data/targets.csv
```

Then open your agent in that folder, run `/prime`, then `/daily-brief`. You get a brief built from the made-up numbers, saved in `outputs/drafts/`.

When you set up your own, copy the structure, write your own words, and delete this `example/` folder.
