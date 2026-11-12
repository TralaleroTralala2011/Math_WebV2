import json
from app import roadmap_v2_routes as roadmap


def _row(choices, answer='1/2', difficulty='nền tảng'):
    return {'id':123, 'question':'Tính giá trị biểu thức đã cho',
            'question_type':'multiple_choice','difficulty':difficulty,
            'choices_json':json.dumps(choices), 'correct_answer':answer,
            'explanation':'Giải theo quy tắc phân số.',
            'tags_json':json.dumps(['form:1'])}


def test_approved_question_with_equivalent_correct_options_is_rejected(monkeypatch):
    monkeypatch.setattr(roadmap, '_data', lambda: ([], {}))
    topic={'id':'demo','title':'Phân số','grade':10}
    bank={'demo':[_row(['1/2','0.5','1/3','2/3'])]}
    assert roadmap.pool(topic, approved_bank=bank, lesson_reviews={}) == []


def test_approved_question_with_four_distinct_options_is_eligible(monkeypatch):
    monkeypatch.setattr(roadmap, '_data', lambda: ([], {}))
    topic={'id':'demo','title':'Phân số','grade':10}
    bank={'demo':[_row(['1/2','1/4','1/3','2/3'])]}
    qs=roadmap.pool(topic, approved_bank=bank, lesson_reviews={})
    assert len(qs)==1 and qs[0]['correct']==0


def test_unlabeled_approved_question_cannot_enter_tier_exam(monkeypatch):
    monkeypatch.setattr(roadmap, '_data', lambda: ([], {}))
    topic={'id':'demo','title':'Phân số','grade':10}
    bank={'demo':[_row(['1/2','1/4','1/3','2/3'], difficulty='unknown')]}
    assert roadmap.pool(topic, approved_bank=bank, lesson_reviews={}) == []
