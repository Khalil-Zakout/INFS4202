#!/usr/bin/env python3
"""Render the defect reports from scripts/issues_data.py.

Outputs:
  docs/issues/<code>-<slug>.md      one committed Markdown body per defect
  docs/issues/INDEX.md              a summary table (also pasted into the report Q4)
  scripts/create_issues.sh          `gh issue create` calls, labels + assignee

Run:  python3 scripts/gen_issues.py
Then (once the GitHub repo exists and labels are created):
      bash scripts/create_issues.sh
"""
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
        with open(os.path.join(OUT, f"{it['code']}-{slug(it['title'])}.md"), "w") as f:
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
    with open(os.path.join(OUT, "INDEX.md"), "w") as f:
        f.write("\n".join(index) + "\n")

    # gh script — each member files their OWN issues (so GitHub records them as author, for R10)
    who_name = {"M1": "Khalil Zakout", "M2": "Monir Skaik", "M3": "Abdulaziz Debs"}
    sh = ["#!/usr/bin/env bash",
          "# Create this member's defect issues on GitHub, authored by whoever runs it.",
          "#",
          "# Each member runs ONLY their own block, signed in to gh as themselves:",
          "#   gh auth login                       # once, as yourself",
          "#   MEMBER=M1 bash scripts/create_issues.sh   # Khalil",
          "#   MEMBER=M2 bash scripts/create_issues.sh   # Monir",
          "#   MEMBER=M3 bash scripts/create_issues.sh   # Abdulaziz",
          "# Issues are created by you and assigned to you (@me). Run from the repo root.",
          "set -euo pipefail",
          'cd "$(dirname "$0")/.."',
          'repo="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"',
          'only="${MEMBER:?set MEMBER=M1 (Khalil), M2 (Monir) or M3 (Abdulaziz)}"',
          'echo "Creating $only issues in $repo as $(gh api user -q .login)"', ""]
    for it in ISSUES:
        md = f"docs/issues/{it['code']}-{slug(it['title'])}.md"
        labels = f"{it['cat']},severity:{it['sev']},priority:{it['prio']}"
        sh.append(
            f'if [ "$only" = "{it["who"]}" ]; then\n'
            f'  gh issue create --repo "$repo" --title {shq(title(it))} '
            f'--body-file "{md}" --label "{labels}" --assignee "@me"\n'
            f'fi\n')
    with open(os.path.join(HERE, "create_issues.sh"), "w") as f:
        f.write("\n".join(sh) + "\n")
    os.chmod(os.path.join(HERE, "create_issues.sh"), 0o755)

    print(f"{len(ISSUES)} issues rendered to docs/issues/")
    print("by severity:", dict(sev), "| weighted:", weight)


def shq(s):
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == "__main__":
    main()
