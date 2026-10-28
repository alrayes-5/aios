# Rules

> What the AI may do alone, what needs your approval, and what data never goes into this workspace. The AI reads this during `/prime` and follows it. Edit it to fit you. The AI cannot edit it: it is a protected file.

---

## The AI may do alone

- Read everything in the workspace except `private/`.
- Write and edit files in `plans/`, `outputs/` and `data/`.
- Create plans, drafts, summaries and analyses.
- Run read-only commands (list, search, print).

## Needs your approval first

- Sending anything to anyone: email, messages, posts, documents. The AI writes a draft in `outputs/drafts/`, you send it.
- Spending money, buying, subscribing, or changing an account.
- Deleting or overwriting a file that was not created in this session.
- Changing a protected file (see `START_HERE.md`, "Protected files"). You make that edit yourself.
- Anything outside this workspace folder.
- Installing software or giving a tool new access.

## Data that never goes in

- Passwords, API keys, tokens, recovery codes.
- Customer or employee personal data (names with contact details, ID numbers, health or payment data).
- Anything covered by a contract or a law that forbids sharing it with an AI service.

Keep any of that outside this folder. If you need the AI to know it exists, write a one-line note, not the data. The `private/` folder is for files that stay on your machine and that the AI is blocked from reading, but treat it as a drawer, not a vault: on a harness where the guard does not apply (see `START_HERE.md`), do not rely on it.

## If a rule gets in the way

Stop, say which rule, and ask. Do not work around it.
