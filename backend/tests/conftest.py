
# V50: The deployment restores the packaged read-only bank before startup.
# Do the same for test sessions, otherwise Battle incorrectly appears empty.
import subprocess
import sys
from pathlib import Path

def pytest_sessionstart(session):
    root = Path(__file__).resolve().parents[2]
    restore = root / "scripts" / "restore_v254_bank.py"
    if restore.is_file():
        subprocess.run([sys.executable, str(restore)], cwd=root, check=True, capture_output=True, text=True)
