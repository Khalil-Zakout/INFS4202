#!/usr/bin/env python3
"""File (or update) YOUR defect issues on GitHub. Safe to run more than once.

Each member runs it from the repository folder, signed in to the GitHub CLI as THEMSELVES:

    gh auth login
    python scripts/file_issues.py M1      # Khalil
    python scripts/file_issues.py M2      # Monir
    python scripts/file_issues.py M3      # Abdulaziz

    python scripts/file_issues.py --status    # anyone: who filed what, what is missing

What it does (only the standard library and the gh command are used):
  1. checks gh, who you are, and that you have write access to the repository;
  2. creates any missing labels from .github/labels.json;
  3. for each of YOUR defects in docs/issues/manifest.json:
       - no issue with that code ([D01] ...) yet  -> creates it with its labels, assigned to you;
       - already exists                           -> updates its text from docs/issues/, adds the
                                                     labels and you as assignee (never a duplicate);
  4. prints a summary and the link to your issues.
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMBERS = {"M1": "Khalil Zakout", "M2": "Monir Skaik", "M3": "Abdulaziz Debs"}


class GhError(Exception):
    pass


def gh(*args):
    """Run gh and return its standard output; raise GhError with gh's message on failure."""
    p = subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        raise GhError((p.stderr or p.stdout).strip() or f"gh {' '.join(args)} failed")
    return p.stdout.strip()


def stop(msg):
    print(f"\nSTOPPED: {msg}")
    sys.exit(1)


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def existing_issues(repo):
    """{code: issue} for every issue whose title starts with [Dnn], open or closed."""
    found = {}
    for it in json.loads(gh("issue", "list", "--repo", repo, "--state", "all", "--limit", "500",
                            "--json", "number,title,author,assignees,labels,state")):
        m = re.match(r"\[(D\d+)\]", it["title"])
        if m and m.group(1) not in found:
            found[m.group(1)] = it
    return found


def preflight():
    if not shutil.which("gh"):
        stop("GitHub CLI not found. Install it (Windows: winget install --id GitHub.cli), "
             "close and reopen the terminal, then run: gh auth login")
    try:
        login = gh("api", "user", "-q", ".login")
    except GhError:
        stop("you are not signed in to GitHub CLI. Run: gh auth login")
    try:
        repo = os.environ.get("REPO") or gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
    except GhError:
        stop("run this from inside your clone of the team repository (the INFS4202 folder).")
    return login, repo


def status(repo):
    manifest = load("docs/issues/manifest.json")
    have = existing_issues(repo)
    print(f"{'code':5} {'#':>5}  {'filed by':18} {'assignees':28} {'labels':3}  should be")
    missing = []
    for m in manifest:
        it = have.get(m["code"])
        if not it:
            missing.append(m["code"])
            print(f"{m['code']:5} {'-':>5}  {'MISSING':18} {'':28} {'':3}  {m['discoverer']}")
            continue
        assignees = ",".join(a["login"] for a in it["assignees"]) or "-"
        print(f"{m['code']:5} {it['number']:>5}  {it['author']['login']:18} {assignees:28} "
              f"{len(it['labels']):>3}  {m['discoverer']}")
    print(f"\n{len(manifest) - len(missing)} of {len(manifest)} defects are on GitHub."
          + (f" Missing: {', '.join(missing)}" if missing else ""))


def file_member(member, login, repo):
    try:
        push = gh("api", f"repos/{repo}", "-q", ".permissions.push")
    except GhError as ex:
        stop(f"cannot read {repo}: {ex}")
    if push != "true":
        stop(f"{login} has no write access to {repo}. Accept the collaborator invitation "
             "(github.com -> your notifications or e-mail), or ask Khalil to add you with Write access.")
    print(f"Repository: {repo}   Signed in as: {login}   Member: {member} ({MEMBERS[member]})\n")

    have_labels = {lab["name"] for lab in
                   json.loads(gh("label", "list", "--repo", repo, "--limit", "200", "--json", "name"))}
    for lab in load(".github/labels.json"):
        if lab["name"] not in have_labels:
            gh("label", "create", lab["name"], "--color", lab["color"], "--description", lab["description"],
               "--repo", repo)
            print(f"  label created: {lab['name']}")

    have = existing_issues(repo)
    mine = [m for m in load("docs/issues/manifest.json") if m["member"] == member]
    created, updated, failed = 0, 0, []
    for m in mine:
        body = os.path.join(ROOT, m["file"])
        try:
            if m["code"] in have:
                n = str(have[m["code"]]["number"])
                gh("issue", "edit", n, "--repo", repo, "--body-file", body,
                   "--add-label", m["labels"], "--add-assignee", "@me")
                updated += 1
                print(f"  updated #{n:<4} {m['title']}")
            else:
                url = gh("issue", "create", "--repo", repo, "--title", m["title"], "--body-file", body,
                         "--label", m["labels"], "--assignee", "@me")
                created += 1
                print(f"  created {url}  {m['title']}")
        except GhError as ex:
            failed.append(m["code"])
            print(f"  FAILED  {m['code']}: {ex}")

    print(f"\nDone for {member} ({login}): {created} created, {updated} updated, "
          f"{len(failed)} failed, of {len(mine)}.")
    if failed:
        print(f"Failed: {', '.join(failed)}. Run the same command again; it skips what already worked.")
        sys.exit(1)
    print(f"Your issues: https://github.com/{repo}/issues?q=is%3Aissue+assignee%3A{login}")


def main(argv):
    if len(argv) != 1 or argv[0] not in (*MEMBERS, "--status"):
        print(__doc__)
        return 2
    login, repo = preflight()
    if argv[0] == "--status":
        status(repo)
    else:
        file_member(argv[0], login, repo)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
