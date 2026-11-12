"""Exact question/method duplicate scan. Does NOT certify mathematical independence."""
from pathlib import Path
from importlib import util
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent

def norm(s):
    return ' '.join(re.findall(r'\w+',unicodedata.normalize('NFKC',str(s or '')).casefold()))

def audit():
    methods=[json.loads(x) for x in (HERE/'V154_CANDIDATE_METHODS.jsonl').read_text(encoding='utf8').splitlines()]
    qs=[json.loads(x) for x in (HERE/'V154_VERIFIED_ANSWERS_PENDING_REVIEW.jsonl').read_text(encoding='utf8').splitlines()]
    corpus=sorted(p for p in ROOT.rglob('*.jsonl') if p.parent!=HERE and '.venv' not in p.parts)
    ms={(norm(m['topic']),norm(m['solving_method'])) for m in methods}
    qtexts={norm(q['question']) for q in qs}
    collisions_q=[];collisions_m=[];n=0
    for path in corpus:
        with path.open(encoding='utf8',errors='replace') as f:
            for line_no,line in enumerate(f,1):
                n+=1
                try:record=json.loads(line)
                except (json.JSONDecodeError,UnicodeError):continue
                if not isinstance(record,dict):continue
                txt=record.get('question') or record.get('prompt') or record.get('text') or record.get('statement') or record.get('problem')
                if txt and norm(txt) in qtexts:
                    collisions_q.append({'file':str(path.relative_to(ROOT)),'line':line_no})
                topic=record.get('topic') or record.get('topic_id')
                meth=record.get('solving_method') or record.get('method') or record.get('method_description')
                if (norm(topic),norm(meth)) in ms:
                    collisions_m.append({'file':str(path.relative_to(ROOT)),'line':line_no})
    result={'candidate_methods':len(methods),'candidate_questions':len(qs),'corpus_files':len(corpus),'corpus_lines':n,
            'exact_question_collisions':len(collisions_q),'exact_topic_method_collisions':len(collisions_m),
            'question_examples':collisions_q[:12],'method_examples':collisions_m[:12],
            'independent_certified_types':0,
            'scope':'Exact normalized wording only; no semantic or mathematical independence proof.'}
    (HERE/'V154_DUPLICATE_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':audit()
