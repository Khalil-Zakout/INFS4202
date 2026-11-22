"""Minimal Portal HTTP client for verification probes: cookie session, login, CSRF-aware form posts."""
import re, html, urllib.request, urllib.parse, urllib.error, http.cookiejar, time
BASE = "http://127.0.0.1:8080"
PASSWORD = "Uniplace!2026"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None

class Portal:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), NoRedirect)
        self.token = None
    def _req(self, method, path, data=None, headers=None):
        url = path if path.startswith("http") else BASE + path
        body = None
        if data is not None:
            body = urllib.parse.urlencode(data, doseq=True).encode() if isinstance(data, (dict, list)) else data
        req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
        if body is not None and not (headers and "Content-Type" in headers):
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
        t = time.perf_counter()
        try:
            r = self.op.open(req, timeout=60)
            status, text, loc = r.status, r.read().decode("utf-8", "replace"), r.headers.get("Location")
        except urllib.error.HTTPError as e:
            status, text, loc = e.code, e.read().decode("utf-8", "replace"), e.headers.get("Location")
        self.ms = (time.perf_counter() - t) * 1000
        m = re.search(r'name="_csrf" value="([^"]+)"', text)
        if m: self.token = m.group(1)
        return status, text, loc
    def get(self, path, follow=True):
        s, t, loc = self._req("GET", path)
        hops = 0
        while follow and s in (301, 302, 303) and loc and hops < 5:
            s, t, loc = self._req("GET", loc); hops += 1
        return s, t, loc
    def post(self, path, data=None, csrf=True, follow=True):
        data = dict(data or {})
        if csrf:
            if not self.token: self.get("/dashboard")
            data["_csrf"] = self.token
        s, t, loc = self._req("POST", path, data)
        hops = 0
        while follow and s in (301, 302, 303) and loc and hops < 5:
            s, t, loc = self._req("GET", loc); hops += 1
        return s, t, loc
    def login(self, user, password=PASSWORD):
        self.get("/login")
        s, t, loc = self._req("POST", "/login", {"username": user, "password": password, "_csrf": self.token})
        if loc and "dashboard" in loc:
            self.get("/dashboard")  # the CSRF token changes at login: pick up the new one
        return loc
    def session_id(self):
        for c in self.jar:
            if c.name == "JSESSIONID": return c.value

def text(h):
    h = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))).strip()
def flash(h):
    m = re.findall(r'class="flash (ok|bad)"[^>]*>(.*?)</div>', h, flags=re.S)
    return [(k, text(v)) for k, v in m]
def login(user):
    p = Portal(); loc = p.login(user); assert loc and "dashboard" in loc, f"login failed for {user}: {loc}"; return p


def percentile(values, p):
    s = sorted(values)
    return s[min(len(s) - 1, int(len(s) * p / 100))]
