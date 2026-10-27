"""Validate the individual-game catalogue without regenerating or overwriting pages.

The game's visual pages are intentionally kept as authored files so running this
script cannot accidentally reset the locked UI or geometry-renderer fixes.
"""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest_path = ROOT / "games" / "individual-games-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
counts = Counter(item["knowledge_id"] for item in manifest)
missing = [item["path"] for item in manifest if not (ROOT / item["path"]).is_file()]
duplicate_paths = len({item["path"] for item in manifest}) != len(manifest)
duplicate_names = len({item["game"] for item in manifest}) != len(manifest)
problems = []
if len(manifest) != 441:
    problems.append(f"Expected 441 game pages, found {len(manifest)}")
if len(counts) != 147:
    problems.append(f"Expected 147 knowledge topics, found {len(counts)}")
if any(count != 3 for count in counts.values()):
    problems.append("Each knowledge topic must have exactly 3 games")
if missing:
    problems.append(f"Missing game files: {missing[:10]}")
if duplicate_paths:
    problems.append("Duplicate game paths detected")
if duplicate_names:
    problems.append("Duplicate game names detected")
if problems:
    print("MATH_WEB game catalogue validation FAILED")
    print("\n".join(f"- {item}" for item in problems))
    raise SystemExit(1)
print("MATH_WEB game catalogue validation PASSED")
print(f"- {len(counts)} knowledge topics")
print(f"- {len(manifest)} game pages")
print("- 3 games per topic")
print("- all paths and game names are unique")
