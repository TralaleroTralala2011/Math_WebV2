"""Wait for both local MATH_WEB servers, then open the website."""
from __future__ import annotations
import sys
import time
import urllib.request
import webbrowser

SERVICES = (
    "http://127.0.0.1:8000/openapi.json",
    "http://127.0.0.1:5500/index.html",
)

def ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

def main() -> int:
    for _ in range(45):
        if all(ready(url) for url in SERVICES):
            webbrowser.open("http://127.0.0.1:5500/index.html")
            print("MATH_WEB is ready. Admin and all APIs share the backend process.")
            return 0
        time.sleep(1)
    print("Servers did not become ready within 45 seconds.", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
