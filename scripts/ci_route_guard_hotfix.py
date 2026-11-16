"""Patch only the unsafe route.path comprehension in local CI preflight scripts.

This tool retains every other release gate as-is. It supports both v34 and v54
without replacing newer preflight rules. It should be run only when updating
an existing checkout that still has the unsafe comprehension.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
old = "routes={route.path for route in app.routes}"
new = "routes={p for route in app.routes if isinstance((p := getattr(route, 'path', None)), str)}"
for filename in ("v34_preflight.py", "v54_preflight.py"):
    path = root / "scripts" / filename
    if not path.exists():
        continue
    contents = path.read_text(encoding="utf-8")
    if old in contents:
        path.write_text(contents.replace(old, new), encoding="utf-8")
        print(f"Patched {path.relative_to(root)}")
    elif new in contents:
        print(f"Already patched {path.relative_to(root)}")
    else:
        print(f"Review manually: {path.relative_to(root)} has a different route check")
