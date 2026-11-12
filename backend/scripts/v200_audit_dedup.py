#!/usr/bin/env python3
"""Exact and heuristic method similarities. Similarity is NOT independence proof."""
import sqlite3,json,re,difflib,collections
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
SPECS=json.loads((BASE/'bank_updates/V200_FAMILY_SPECS.json').read_text())
OLD=[]
for name in ('V191_FAMILY_SPECS.json','V192_FAMILY_SPECS.json','V194_FAMILY_SPECS.json','V198_FAMILY_SPECS.json','V199_FAMILY_SPECS.json'):
    p=BASE/'bank_updates'/name
    if p.exists():
        x=json.loads(p.read_text());
        for y in x:
            OLD.append({'source':name,'name':str(y.get('name') or y.get('concept') or ''),'method':str(y.get('method') or y.get('math_method') or ''),'grade':y.get('grade'),'topic':y.get('topic')})

def normalize(s):
    s=str(s).lower().strip();s=re.sub(r'\d+(?:[.,/]\d+)?','#',s);return re.sub(r'\s+',' ',s)

with sqlite3.connect(BASE/'backend/database/mathweb.db') as db:
    oldprompts={normalize(q) for (q,) in db.execute("select question from admin_question_bank where source not like 'V200%'")}
    fresh=db.execute("select question from admin_question_bank where source like 'V200%'").fetchall()
    duplicate_prompts=sum(normalize(q) in oldprompts for (q,) in fresh)
    unmatched=db.execute("select count(*) from admin_question_bank where grade=10 and topic='chia_het'").fetchone()[0]
flagged=[]
for spec in SPECS:
    comparisons=[]
    for other in OLD:
        if spec['grade']!=other['grade']:continue
        similarity=difflib.SequenceMatcher(None,normalize(spec['name']+' '+spec['method']), normalize(other['name']+' '+other['method'])).ratio()
        comparisons.append((similarity,other))
    score,candidate=max(comparisons,key=lambda t:t[0])
    if score>=0.56:flagged.append({'form':spec['form_id'],'score':round(score,3),'possible_prior':candidate})
result={'verified_new_count':len(fresh),'duplicate_normalized_question_count':duplicate_prompts,'family_candidates':len(SPECS),'flagged_for_manual_semantic_review':flagged,'method_independence_certified':0,'remaining_invalid_topic_rows':unmatched,'warning':'heuristic similarity is not proof of mathematical independence'}
(BASE/'bank_updates/V200_DEDUP_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in result.items()},ensure_ascii=False))
