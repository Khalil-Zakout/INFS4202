"""OFF-04 concurrency reproduction (issue D03).

Two students accept offers for the only seat of "Sustainability Reporting Intern"
at the same instant. The specification allows exactly one to succeed; the defect
lets both succeed and drives seatsTaken above the number of seats.

Run (fresh data): ./start.sh --reset  then  cd tests/system && python3 seat_race.py
Exits 0 when the race is reproduced (both ACCEPTED), 1 otherwise.
"""
import sys, os, threading, re, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
from portal_client import login, Portal  # noqa: E402

OFFER_IBRAHIM, OFFER_MUBARAK = 2, 3   # pending offers on the 1-seat posting (fresh start)
APPS = (7, 8, 9)
POSTING = 8


def accept_in_parallel():
    ib, mu = login("student.ibrahim"), login("student.mubarak")
    for p in (ib, mu):
        p.get("/dashboard")  # fresh CSRF token
    barrier = threading.Barrier(2)

    def go(p, offer_id):
        data = urllib.parse.urlencode({"_csrf": p.token}).encode()
        barrier.wait()
        p._req("POST", f"/offers/{offer_id}/accept", data)

    threads = [threading.Thread(target=go, args=(ib, OFFER_IBRAHIM)),
               threading.Thread(target=go, args=(mu, OFFER_MUBARAK))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    c = login("coordinator")
    accept_in_parallel()
    states = {}
    for aid in APPS:
        _, h, _ = c.get(f"/applications/{aid}")
        states[aid] = re.search(r'</a> ·\s*<span class="badge [^"]*">([^<]+)</span>', h).group(1)
    _, h, _ = c.get(f"/postings/{POSTING}")
    seats = re.search(r"Seats</th><td>([^<]+)<", h).group(1)
    status = re.search(r'<span class="badge [^"]*">([^<]+)</span>', h).group(1)
    print("application states:", states)
    print(f"posting {POSTING}: seats = {seats}, status = {status}")
    both = states[7] == "Accepted" and states[8] == "Accepted"
    print("\nDEFECT reproduced: both acceptances succeeded for one seat." if both
          else "Not reproduced on this run (the race is timing-dependent; retry on a fresh --reset).")
    return 0 if both else 1


if __name__ == "__main__":
    sys.exit(main())
