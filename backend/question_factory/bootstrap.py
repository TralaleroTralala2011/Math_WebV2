"""Install the official 150-topic catalog in an isolated Question Factory database.

Importing this file does not create a database and does not touch existing
MATH_WEB users, battles, learning history, or verified seed banks.
"""
import os
from pathlib import Path
from database.data_paths import database_path as persistent_database_path
from . import storage
from .topic_import import import_topics

DEFAULT_DB = Path(__file__).resolve().parents[1] / 'database' / 'question_factory.sqlite3'
CATALOG = Path(__file__).with_name('catalog_150.json')


def database_path():
    configured = os.environ.get('QF_DB_PATH')
    return str(Path(configured).expanduser().resolve() if configured else persistent_database_path('question_factory.sqlite3').resolve())


def initialize_factory(path=None):
    path=path or database_path()
    storage.initialize(path)
    import_topics(path,CATALOG,expected_count=150)
    return path
