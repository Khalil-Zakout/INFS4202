# UniPlace QA project — read me first

This is your whole INFS4202 project, finished. This page tells you, in plain words,
what it is, what is already done, and exactly what each of the three of you does next.

Team: **Khalil Zakout (60314057)**, **Monir Skaik (60314058)**, **Abdulaziz Debs (60309913)**.
Repo: https://github.com/Khalil-Zakout/INFS4202

---

## 1. What the project is (30 seconds)

You are a QA team hired to test **UniPlace**, an internship portal, and report as many
real bugs as you can. It has two parts: the **Portal** (you have the Java source — you
test it "white-box", seeing the code) and the **Engine** (you only have the program —
you test it "black-box", through its API). There is also an **AI feature** that gives
students feedback on their application letter.

## 2. What is already done

- We explored the system, read the requirements, and read the code.
- We **found and proved 48 real defects** (10 critical, 28 major, 10 minor) — each one
  reproducible on the running system.
- We wrote the full paperwork: **test strategy**, **test cases** (3 modules), **48 defect
  reports**, the **final report** (Word + PDF), the **slides**, an **AI usage log**, and a
  template for each person's **individual statement**.
- We wrote **automated tests** at four levels (Java + Python) that run with one command.

Nothing about the testing is left to invent. What is left is **admin**: put it on
GitHub, file the issues from each of your accounts, fill a few names, and prepare to
present. That is what the rest of this page covers.

## 3. What is in this folder

| Folder / file | What it is |
|---|---|
| `docs/final-report.docx` / `.pdf` | The final report — **edit the Word file** if you want, then export a fresh PDF |
| `docs/presentation.pptx` | The slide deck (title + team part + one slide each) |
| `docs/test-strategy.md`, `docs/test-cases.md`, `docs/ai-usage-log.md` | The required documents |
| `docs/issues/` | All 48 defect reports (one file each) + `INDEX.md` |
| `docs/individual-statement-template.docx` | Each of you fills one and submits it privately on D2L |
| `tests/` | The automated tests (`README.md` explains every command) |
| `scripts/push_all.sh` | Puts the project on GitHub with a commit from each of you |
| `scripts/create_issues.sh` | Each of you runs it to file your own issues |
| `start.sh`, `portal/`, `engine/`, `bin/` | The UniPlace system itself (from the kit) |

## 4. Step by step — who does what

> You need **Git**, a **JDK 17+**, **Python 3**, and the GitHub CLI **`gh`**
> (https://cli.github.com) installed. Do the steps in order.

### Step A — Khalil only: put the project on GitHub (~5 min)

```bash
# 1. unzip the project and go into it
cd uniplace

# 2. open scripts/push_all.sh and replace the three REPLACE_..._email lines
#    with each member's GitHub e-mail (Settings -> Emails on github.com).

# 3. connect it to your empty repo and push (this makes one commit per member)
git remote add origin https://github.com/Khalil-Zakout/INFS4202.git
bash scripts/push_all.sh
```

Then, on github.com, create the issue labels once (**do this before Step B** — the
issue command needs the labels to exist):
**your repo -> Actions -> "Create labels" -> Run workflow.**
Wait for it to finish (green tick). The "Tests" workflow also runs automatically on
your push and will show failing tests — that is expected, those failures are your
defect evidence.

Check `vanilson` is a collaborator (Settings -> Collaborators) — you said the invites
are sent, so this is just a check.

### Step B — each of the three of you: file your own issues (~2 min each)

This is the step that records **you** on GitHub, which is graded individually. On your
own computer, after Khalil's push:

```bash
git clone https://github.com/Khalil-Zakout/INFS4202.git   # or 'git pull' if you already have it
cd INFS4202
gh auth login                     # sign in as YOURSELF
MEMBER=M1 bash scripts/create_issues.sh    # Khalil     (16 issues)
# MEMBER=M2 bash scripts/create_issues.sh  # Monir      (17 issues)
# MEMBER=M3 bash scripts/create_issues.sh  # Abdulaziz  (15 issues)
```

Run only **your** line (M1 Khalil, M2 Monir, M3 Abdulaziz). The issues are created
under your name and assigned to you. If `gh` is a hassle for anyone, that person can
instead open each of their `docs/issues/*.md` files and paste them as new issues on the
website — slower, but the same result.

### Step C — each of you: finish your personal parts

1. **Know your defects.** Open `docs/issues/INDEX.md` and read the reports with your
   name. You must be able to explain and **demo one live** at the presentation
   (each person's live demo is on their slide).
2. **Fill your individual statement.** Open `docs/individual-statement-template.docx`,
   fill your part and the private peer-evaluation, and submit it to **your own** D2L
   individual folder.
3. **Practise your slide** (slides 8-10 are Khalil, Monir, Abdulaziz in order).

### Step D — before the deadline (Week 15)

- One of you submits `docs/final-report.pdf` on D2L.
- Register the team name on D2L if not done (the report says "UniPlace QA Team" —
  change it to whatever you registered).
- When everything is in, tag the repo so the instructor grades the right version:
  ```bash
  git tag final && git push origin final
  ```

## 5. Running the system (for your live demos)

Open a terminal in the project folder and run:

```bash
./start.sh            # starts the Engine (port 8081) and the Portal (port 8080)
```

Then open **http://localhost:8080** in a browser. Log in with any seeded account —
usernames are listed on the coordinator's Users page; the password for all of them is
`Uniplace!2026`. Add **`--reset`** (`./start.sh --reset`) to wipe the database and
reload fresh demo data — do this before a demo so the IDs in the issue steps match.
Stop it with Ctrl-C.

To run the automated tests while it is up, see `tests/README.md` (for example
`cd tests/api && python3 -m unittest` for the Engine suite). The Java tests need
internet the first time to download Maven libraries: `cd portal && ./mvnw test`.

## 6. Two optional extras (for a few more marks)

- **Coverage number** for the report: `cd portal && ./mvnw test -Dmaven.test.failure.ignore=true`
  then open `portal/target/site/jacoco/index.html` and put the service-layer line-% into
  the report's Q3 (where it says *[fill in from your run]*).
- **AI prompt experiment:** needs a free model key — steps are in `tests/README.md`.
  Put the result into the report's "Use of AI" section.

That's everything. If a command fails, send me the error and I'll sort it.
