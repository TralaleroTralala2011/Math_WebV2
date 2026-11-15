"""V68 release smoke test, isolated from the shipped account/history database.

Run from repository root:
 MATHWEB_DB_PATH=/tmp/v68-user-test.sqlite MATHWEB_AI_HISTORY_DB_PATH=/tmp/v68-ai-test.sqlite PYTHONPATH=backend python tools/test_v68_game_topics_and_choices.py
"""
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.ai.routes import router
from app.ai.engine.knowledge_service import KnowledgeService
from app.ai.engine.mcq_quality_v68 import improve_mcq
from app.ai.engine.validator import validate, options_equivalent

k=KnowledgeService()
games=[]
for path in (ROOT/'games').rglob('*.html'):
    raw=path.read_text('utf-8',errors='replace')
    found=re.search(r'window.MATH_GAME\s*=\s*(\{[^;]+\});',raw)
    if not found:continue
    game=json.loads(found.group(1))
    grade=int(game.get('grade') or 10)
    assert k.normalize_topics(grade,[str(game.get('topicId',''))]), (str(path),grade,game.get('topicId'))
    games.append(path)
print('OK: Valid topic IDs for',len(games),'game HTML pages')

app=FastAPI();app.include_router(router)
client=TestClient(app)
scenarios=[
    ('SEQUENCE',10,['Tìm quy luật','Điền số','Đường đua dãy số']),
    ('ALGEBRAIC_FRACTION',10,['Rút gọn','Tìm điều kiện','Phân thức tốc độ']),
    ('sequence',11,['Tìm quy luật','Điền số','Đường đua dãy số']),
]
for tid,grade,labels in scenarios:
    for stage,label in enumerate(labels,1):
        kwargs=dict(grade=grade,topics=[tid],count=8,
                    difficulty=('easy','medium','hard')[stage-1],
                    question_type='multiple_choice' if stage!=3 else 'mixed',
                    problem_mode=False,history=[],
                    game_id=f'{tid}_Dãy số • {label}_stage{stage}')
        response=client.post('/api/ai/practice/session',json=kwargs)
        assert response.status_code==200,(kwargs,response.status_code,response.text[:250])
        output=response.json(); qs=output['questions']
        assert len(qs)==8,(tid,grade,stage,len(qs))
        assert len({str(q['question']).strip().casefold() for q in qs})==len(qs)
        canonical=k.normalize_topics(grade,[tid])[0]
        assert all(q['topic']==canonical for q in qs)
        for q in qs:
            validate(q)
            if q['question_type']=='multiple_choice':
                assert sum(options_equivalent(q['answer'],v) for v in q['options'])==1,(tid,q['answer'],q['options'])
            if tid.upper()=='SEQUENCE' and grade==10:assert 'dãy' in q['question'].lower() or 'số hạng' in q['question'].lower() or 'đua' in q['question'].lower(),q['question']
            if tid=='ALGEBRAIC_FRACTION':assert 'phân thức' in q['question'].lower(),q['question']
        print('OK:',tid,grade,label,len(qs),'non-repeating, valid questions')

# Screenshot repro: only one choice uses a square-root denominator.
item={'question_type':'multiple_choice','question':'Viết sin của góc giữa PA và (α).',
      'answer':'7/√(113)', 'options':['7/8','8/√(113)','1','7/√(113)']}
improve_mcq(item)
assert item.get('distractors_refined')=='same_form_radical'
assert len(item['options'])==4
assert all('√' in option for option in item['options'])
assert sum(options_equivalent(item['answer'],v) for v in item['options'])==1
print('OK: Matched-form radical distractors, one correct answer')
