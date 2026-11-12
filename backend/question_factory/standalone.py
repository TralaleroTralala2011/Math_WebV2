"""Optional standalone Question Factory API, for uvicorn question_factory.standalone:app."""
from .api import create_app
from .bootstrap import initialize_factory
app=create_app(db_path=initialize_factory())
