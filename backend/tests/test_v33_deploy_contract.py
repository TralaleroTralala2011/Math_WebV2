"""Regression checks for public GitHub Pages + Render API feature agreement."""
from fastapi.testclient import TestClient
from app.main import app

def test_health_advertises_optional_apis():
    # Lifespan not required for a read-only health check.
    c = TestClient(app)
    d = c.get('/health').json()
    assert d['features']['roadmap_v2'] is True
    assert d['features']['activity_heatmap'] is True
    assert d['features']['tutor_recommendations'] is True
    paths = {r.path for r in app.routes}
    assert '/api/roadmap-v2/status/{grade}' in paths
    assert '/api/roadmap-v2/tutor/{grade}' in paths
    assert '/api/games/activity-heatmap' in paths
