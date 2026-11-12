#!/usr/bin/env python3
"""Export honest per-topic question-count deficits, never infer certified type count."""
import json,csv,sqlite3,collections
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]; OUT=BASE/'bank_updates'
catalog=json.loads((BASE/'backend/app/ai/knowledge/index.json').read_text())
with sqlite3.connect(BASE/'backend/database/mathweb.db') as db:
 total=collections.Counter({(int(g),t):n for g,t,n in db.execute('SELECT grade,topic,count(*) FROM admin_question_bank GROUP BY grade,topic')})
 newer=collections.Counter({(int(g),t):n for g,t,n in db.execute("SELECT grade,topic,count(*) FROM admin_question_bank WHERE source IN ('V198 QA-gated','V199 QA-gated','V200 QA-gated','V201 QA-gated','V202 QA-gated','V203 QA-gated') GROUP BY grade,topic")})
fields=['grade','topic','topic_name','bundled_total_questions','new_questions_v198_v203','questions_missing_to_20000_count_only','certified_distinct_type_count','certified_types_remaining']
rows=[]
for grade,topics in catalog.items():
 for item in topics:
  g=int(grade);t=item['id'];count=total[(g,t)]
  rows.append(dict(grade=g,topic=t,topic_name=item['name'],bundled_total_questions=count,new_questions_v198_v203=newer[(g,t)],questions_missing_to_20000_count_only=max(0,20000-count),certified_distinct_type_count='unverified',certified_types_remaining='unverified'))
assert len(rows)==150
with (OUT/'V203_COVERAGE_150.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
priority=sorted(rows,key=lambda x:(x['bundled_total_questions'],x['new_questions_v198_v203'],x['grade'],x['topic']))
(OUT/'V203_TOPIC_PRIORITY.json').write_text(json.dumps({'version':'V203','order_rule':'fewest bundled questions first; count-only priority, not a measure of certified independent mathematical types','topic_count':150,'priority_order':priority},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'topics':150,'fewest_topic_questions':priority[0]['bundled_total_questions'],'highest_priority_topic':priority[0]['topic'],'missing_questions_total_count_only':sum(r['questions_missing_to_20000_count_only'] for r in rows),'unverified_method_count':'not inventable'},ensure_ascii=False))
