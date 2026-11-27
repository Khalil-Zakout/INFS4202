#!/usr/bin/env python3
"""Render the defect reports from scripts/issues_data.py.

Outputs:
  docs/issues/<code>-<slug>.md      one committed Markdown body per defect
  docs/issues/INDEX.md              a summary table (also pasted into the report Q4)
  docs/issues/manifest.json         code, title, labels and owner, read by scripts/file_issues.py

Run:  python3 scripts/gen_issues.py
Then each member, signed in to gh as themselves:  python scripts/file_issues.py M1|M2|M3
"""
import json
import os
import re
from collections import Counter

from issues_data import ISSUES, PASSWORD, NAMES

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "issues")
SEV_WEIGHT = {"critical": 3, "major": 2, "minor": 1, "enhancement": 0.5}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50]


def body(it):
    steps = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(it["steps"]))
    return f"""**Requirement violated:** {it['req']}

**Description:**
{it['desc']}

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `{PASSWORD}`):
{steps}

**Expected result:** {it['expected']}

**Actual result:** {it['actual']}

**Severity:** {it['sev'].capitalize()}
**Priority:** {it['prio'].upper()}
**Category:** {it['cat']}
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** {it['evidence']}
**Discovered by:** {NAMES[it['who']]}
**Technique that found it:** {it['tech']}
"""


def title(it):
    return f"[{it['code']}] {it['title']}"


def main():
    os.makedirs(OUT, exist_ok=True)
    codes = [it["code"] for it in ISSUES]
    assert len(codes) == len(set(codes)), "duplicate issue codes"

    index = ["# Defect reports — index", "",
             "| Code | Title | Category | Severity | Priority | Requirement | Discovered by |",
             "|------|-------|----------|----------|----------|-------------|----------------|"]
    for it in ISSUES:
        with open(os.path.join(OUT, f"{it['code']}-{slug(it['title'])}.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# {title(it)}\n\n{body(it)}")
        index.append(f"| {it['code']} | {it['title']} | {it['cat']} | {it['sev']} | {it['prio']} "
                     f"| {it['req']} | {NAMES[it['who']]} |")

    sev = Counter(it["sev"] for it in ISSUES)
    cat = Counter(it["cat"] for it in ISSUES)
    weight = sum(SEV_WEIGHT[it["sev"]] for it in ISSUES)
    index += ["", "## Totals", "",
              f"- Issues: **{len(ISSUES)}**",
              "- By severity: " + ", ".join(f"{k} {sev[k]}" for k in ("critical", "major", "minor", "enhancement") if sev[k]),
              "- By category: " + ", ".join(f"{k} {cat[k]}" for k in sorted(cat)),
              f"- Severity-weighted (C3/Maj2/Min1/Enh0.5): **{weight:g}**", ""]
    with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(index) + "\n")

    # Manifest read by scripts/file_issues.py (each member files their OWN issues, for R10).
    manifest = [{"code": it["code"], "title": title(it), "member": it["who"], "discoverer": NAMES[it["who"]],
                 "file": f"docs/issues/{it['code']}-{slug(it['title'])}.md",
                 "labels": f"{it['cat']},severity:{it['sev']},priority:{it['prio']}"} for it in ISSUES]
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"{len(ISSUES)} issues rendered to docs/issues/")
    print("by severity:", dict(sev), "| weighted:", weight)


if __name__ == "__main__":
    main()
