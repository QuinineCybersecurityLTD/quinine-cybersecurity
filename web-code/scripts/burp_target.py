"""Tiny deliberately-vulnerable web app (stdlib only) for the Burp 'intercept & modify' demo.

Vulnerability (by design): GET /account?id=<n> returns that account with NO ownership check,
so changing the id value in an intercepted request exposes another user's data (IDOR / BOLA).
This stands in for the OWASP Juice Shop basket IDOR when Juice Shop cannot be built locally.

Run: python web-code/scripts/burp_target.py [port]   (binds 127.0.0.1 only)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Seeded synthetic accounts. The logged-in demo user "owns" only 1001.
ACCOUNTS = {
    "1001": {"owner": "demo-user", "name": "Demo User", "balance": 42.00},
    "1002": {"owner": "alice", "name": "Alice Admin", "balance": 98230.55},
    "1003": {"owner": "bob", "name": "Bob CFO", "balance": 1500000.00},
}
SESSION_USER = "demo-user"  # the "logged in" account owns 1001 only


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            return self._json(200, {"hint": "GET /account?id=1001  (you are demo-user, owning 1001)"})
        if u.path == "/account":
            acc_id = (parse_qs(u.query).get("id") or [""])[0]
            acc = ACCOUNTS.get(acc_id)
            if acc is None:
                return self._json(404, {"error": "no such account"})
            # VULNERABILITY: no check that acc["owner"] == SESSION_USER (IDOR / BOLA)
            return self._json(200, {"id": acc_id, **acc})
        return self._json(404, {"error": "not found"})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8020
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
