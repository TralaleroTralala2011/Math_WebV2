"""Read-only normalized exact-text audit over historical JSONL, without certifying semantics."""
import json,re,unicodedata,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).parent

def norm(value):
 return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(value)).casefold()).strip()

def run():
 fresh=[json.loads(x) for x in (HERE/'V158_VERIFIED_ANSWERS_PENDING_REVIEW.jsonl').read_text(encoding='utf8').splitlines()]
 methods=[json.loads(x) for x in (HERE/'V158_CANDIDATE_METHODS.jsonl').read_text(encoding='utf8').splitlines()]
 new_questions={norm(o['question'].split(' Nhận định:')[0]) for o in fresh}
 new_names={norm(o['title']) for o in methods}
 seen_q=set();seen_names=set(); q_count=0;m_count=0; matched_q=[];matched_methods=[];bad_lines=0
 paths=[]
 for p in ROOT.rglob('*.jsonl'):
  if HERE in p.parents or '/.git/' in str(p):continue
  # Avoid opaque large arbitrary external corpora, count each record present.
  paths.append(p)
 for p in paths:
  with p.open('r',encoding='utf8',errors='replace') as fh:
   for line in fh:
    try: o=json.loads(line)
    except json.JSONDecodeError:bad_lines+=1;continue
    if not isinstance(o,dict):continue
    question=o.get('question') or o.get('stem') or o.get('question_text')
    if isinstance(question,str) and question.strip():
     q_count+=1
     key=norm(question)
     if key in new_questions:matched_q.append({'file':p.relative_to(ROOT).as_posix(),'question':question[:180]})
    name=o.get('title') or o.get('method_title')
    if isinstance(name,str) and name.strip():
     m_count+=1
     if norm(name) in new_names:matched_methods.append({'file':p.relative_to(ROOT).as_posix(),'title':name})
 out=dict(files_scanned=len(paths),historical_question_records=q_count,historical_title_records=m_count,unparseable_lines=bad_lines,exact_question_collisions=matched_q[:40],exact_title_collisions=matched_methods[:40],new_questions=60,new_candidate_methods=6,semantic_independence_certified=False,limitation='Exact Unicode-normalized text/title comparison ONLY, not semantic/method proof')
 (HERE/'V158_HISTORICAL_AUDIT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in out.items() if k not in ('exact_question_collisions','exact_title_collisions')},ensure_ascii=False))
 return out
if __name__=='__main__':run()
