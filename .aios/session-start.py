#!/usr/bin/env python3
"""AIOS SessionStart hook: print a few facts so every session starts informed.

Claude Code adds this script's output to the session context. It only reads; it never writes.
Prints today's date (so the AI does not guess it), which context files are still templates,
and the newest daily brief.
"""
import datetime
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
today = datetime.date.today()
print("AIOS session start. Today is %s (%s)." % (today.isoformat(), today.strftime("%A")))

templates = []
for path in sorted(glob.glob(os.path.join(ROOT, "context", "*.md"))):
    text = open(path, encoding="utf-8").read()
    if re.search(r"^\[[^\]]+\]\s*$", text, re.M):
        templates.append(os.path.basename(path))
if templates:
    print("Context files still containing template text: %s. Offer to fill them in during /prime." % ", ".join(templates))
else:
    print("Context files are filled in.")

briefs = sorted(glob.glob(os.path.join(ROOT, "outputs", "drafts", "daily-brief-*.md")))
if briefs:
    name = os.path.basename(briefs[-1])
    print("Newest daily brief: outputs/drafts/%s" % name)
else:
    print("No daily brief yet. /daily-brief writes one.")
print("Run /prime to load the full context.")
