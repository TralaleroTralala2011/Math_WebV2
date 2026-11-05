"""Read-only curriculum quality and prerequisite APIs. No existing routes modified."""
from pathlib import Path
import json
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='/api/curriculum', tags=['curriculum'])
ROOT = Path(__file__).resolve().parents[2]

def load():
    base = ROOT / 'learn-assets'
    topics = json.loads((base / 'topics.json').read_text(encoding='utf-8'))
    lessons = json.loads((base / 'verified-lessons.json').read_text(encoding='utf-8'))
    return topics, lessons

# Curated prerequisite edges, only applied if both IDs exist in the current catalog.
EDGES = {
    'ham_so_bac_hai': ['phuong_trinh_he'],
    'dao_ham': ['gioi_han', 'ham_so'],
    'tich_phan': ['nguyen_ham'],
    'phuong_trinh_logarit': ['ham_so_logarit'],
    'phuong_trinh_mu': ['ham_so_mu'],
}

def assessment(topic, lesson):
    required = ('summary', 'goals', 'formulas', 'examples', 'common_mistakes')
    missing = [k for k in required if not lesson.get(k)]
    return {'id': topic['id'], 'title': topic.get('title', ''),
            'grade': topic.get('grade'), 'has_lesson': bool(lesson),
            'missing_sections': missing,
            'publication_ready': not missing,
            'status': 'needs_review' if not missing else 'draft'}

@router.get('/quality')
def quality():
    topics, lessons = load()
    rows = [assessment(t, lessons.get(t['id'], {})) for t in topics]
    return {'total': len(rows), 'lessons_present': sum(r['has_lesson'] for r in rows),
            'structurally_complete_unverified': sum(r['publication_ready'] for r in rows),
            'published_by_this_feature': 0,
            'warning': 'Structural checks do not prove mathematical correctness; manual verification required.',
            'topics': rows}

@router.get('/graph')
def graph():
    topics, _ = load()
    ids = {t['id'] for t in topics}
    return {'nodes': [{'id': t['id'], 'title': t.get('title'), 'grade': t.get('grade')} for t in topics],
            'edges': [{'from': p, 'to': topic} for topic, pres in EDGES.items() if topic in ids for p in pres if p in ids],
            'coverage': 'curated_partial', 'note': 'Missing edges do not mean topics have no prerequisites.'}

@router.get('/topics/{topic_id}/readiness')
def readiness(topic_id: str):
    topics, lessons = load()
    topic = next((t for t in topics if t['id'] == topic_id), None)
    if topic is None:
        raise HTTPException(404, 'Unknown topic')
    return assessment(topic, lessons.get(topic_id, {}))
