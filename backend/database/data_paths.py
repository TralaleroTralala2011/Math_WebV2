"""Optional external persistent SQLite directory; defaults preserve legacy paths."""
import os
from pathlib import Path

LEGACY_DIR = Path(__file__).resolve().parent


def database_path(filename: str) -> Path:
    if Path(filename).name != filename or filename in ('', '.', '..'):
        raise ValueError('SQLite filename must be a simple basename')
    external = os.environ.get('MATHWEB_DATA_DIR', '').strip()
    directory = Path(external).expanduser().resolve() if external else LEGACY_DIR
    return directory / filename
