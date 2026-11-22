"""System-level defect reproductions on the running Portal (fresh ./start.sh --reset).

Each check prints DEFECT (the specified behaviour is violated) or ok, and the
suite exits non-zero when any defect is present. Run after a fresh reset:

    cd tests/system && python3 reproduce.py

Covers issues D05, D48, D06, D07, D27, D28, D29, D39, D47, D35 (system view).
The offer/state and company issues (D02, D04, D21..D26, D31, D01) have JUnit
reproductions in portal/src/test/java/com/halcyon/uniplace/qa; D03 is seat_race.py.
"""
import sys, os, re, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
from portal_client import login, Portal, flash, text  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
defects = 0


def report(code, is_defect, detail):
    global defects
    defects += 1 if is_defect else 0
    print(f"[{code}] {'DEFECT' if is_defect else 'ok    '}  {detail}")


def d05_idor_application():
    h = login("student.omar").get("/applications/3")[1]
    report("D05", "Motivation letter" in h and "Software Support Intern" in h,
           "student.omar can open Amal's application /applications/3")


def d48_idor_document():
    s, h, _ = login("recruiter.gulfbank").get("/documents/1", follow=False)
    report("D48", s == 200 and h[:5] == "%PDF-", "recruiter.gulfbank downloaded Amal's CV /documents/1")


def d06_secrets():
    c = login("coordinator")
    c.post("/coordinator/settings", {"ai.apiKey": "sk-demo-SECRET-0001", "smtp.password": "Smtp-SECRET-0002"})
    log = open(os.path.join(REPO, "logs", "portal.log")).read()
    in_log = "sk-demo-SECRET-0001" in log or "Smtp-SECRET-0002" in log
    html = c.get("/coordinator/settings")[1]
    in_html = "sk-demo-SECRET-0001" in html or "Smtp-SECRET-0002" in html
    report("D06", in_log or in_html, f"secret in log={in_log}, in settings HTML value={in_html}")
    c.post("/coordinator/settings", {"ai.apiKey": "", "ai.apiKey.clear": "on",
                                      "smtp.password": "", "smtp.password.clear": "on"})


def d07_xss():
    r = login("recruiter.qtech")
    payload = "QTech <img src=x onerror=alert(1)>"
    r.post("/recruiter/company", {"name": payload, "sector": "Technology", "contactEmail": "careers@qtech.qa"})
    h = login("student.amal").get("/postings")[1]
    report("D07", "<img src=x onerror=alert(1)>" in h, "company name rendered unescaped on /postings")
    r.post("/recruiter/company", {"name": "QTech Solutions", "sector": "Technology", "contactEmail": "careers@qtech.qa"})


def d27_logout():
    p = login("student.khalid")
    sid = p.session_id()
    p.post("/account/logout", follow=False)
    s, h, _ = Portal()._req("GET", "/dashboard", headers={"Cookie": f"JSESSIONID={sid}"})
    report("D27", s == 200 and "Welcome" in h, "old session id still authenticated after /account/logout")


def d28_lockout():
    for _ in range(12):
        Portal().login("Student.Noor", "wrong-password")       # mixed case
    report("D28", bool(login("Student.Noor")) and "dashboard" in Portal().login("Student.Noor"),
           "12 mixed-case failures did not lock the account")


def d29_password_no_digit():
    p = login("student.hessa")
    p.post("/account/password", {"current": "Uniplace!2026", "next": "abcdefghijkl", "confirm": "abcdefghijkl"})
    ok_login = "dashboard" in Portal().login("student.hessa", "abcdefghijkl")
    report("D29", ok_login, "password changed to 12 letters with no digit")


def d39_generic_message():
    h = login("student.amal").post("/postings/10/apply", {"letter": "too short"})[1]
    msgs = [m for _, m in flash(h)]
    report("D39", any("Unable to submit" in m for m in msgs) and not any("between 100" in m for m in msgs),
           f"refused apply shows generic message: {msgs}")


def d47_withdraw_accepted():
    before = login("coordinator").get("/applications/116")[1]
    st_before = re.search(r'</a> ·\s*<span class="badge [^"]*">([^<]+)</span>', before).group(1)
    login("student.amna").post("/applications/116/withdraw")
    after = login("coordinator").get("/applications/116")[1]
    st_after = re.search(r'</a> ·\s*<span class="badge [^"]*">([^<]+)</span>', after).group(1)
    report("D47", st_before == "Accepted" and st_after == "Withdrawn",
           f"ACCEPTED application withdrawn via direct POST ({st_before} -> {st_after})")


def d35_outbox_unpaginated():
    h = login("coordinator").get("/coordinator/outbox")[1]
    rows = h.count("<td>") // 4
    report("D35", rows > 20 and 'class="pager"' not in h, f"outbox shows {rows} rows on one page, no pager")


def main():
    for check in (d05_idor_application, d48_idor_document, d06_secrets, d07_xss, d27_logout,
                  d28_lockout, d29_password_no_digit, d39_generic_message, d47_withdraw_accepted,
                  d35_outbox_unpaginated):
        try:
            check()
        except Exception as ex:  # noqa: BLE001
            print(f"[{check.__name__}] ERROR {ex}")
            global defects
            defects += 1
    print(f"\ndefects present: {defects}")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
