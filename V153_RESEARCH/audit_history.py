"""Conservative read-only exact text/method scan against historical JSONL files."""
from pathlib import Path
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=Path(__file__).resolve().parent


def norm(s):
    return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC',str(s or '')).casefold()))


def audit():
    new_methods=[json.loads(x) for x in (RESEARCH/'V153_CANDIDATE_METHODS.jsonl').read_text(encoding='utf-8').splitlines()]
    new_q=[json.loads(x) for x in (RESEARCH/'V153_REVIEW_QUESTIONS.jsonl').read_text(encoding='utf-8').splitlines()]
    methods={(norm(m['topic']),norm(m['solving_method'])) for m in new_methods}
    questions={norm(q['question']) for q in new_q}
    historical_files=sorted(p for p in ROOT.rglob('*.jsonl') if p.parent!=RESEARCH and
                            '.venv' not in p.parts and 'node_modules' not in p.parts)
    count_lines=0; parsed=0; matches_question=[]; matches_method=[]
    for f in historical_files:
        with f.open(encoding='utf8',errors='replace') as stream:
            for lineno,line in enumerate(stream,1):
                count_lines+=1
                try: data=json.loads(line)
                except (json.JSONDecodeError,UnicodeError):continue
                if not isinstance(data,dict):continue
                parsed+=1
                value=data.get('question') or data.get('prompt') or data.get('text') or data.get('statement') or data.get('problem')
                if value and norm(value) in questions:
                    matches_question.append({'file':str(f.relative_to(ROOT)),'line':lineno})
                method=data.get('solving_method') or data.get('method') or data.get('method_description')
                topic=data.get('topic') or data.get('topic_id')
                if (norm(topic),norm(method)) in methods:
                    matches_method.append({'file':str(f.relative_to(ROOT)),'line':lineno})
    result={'historical_jsonl_files_scanned':len(historical_files),'historical_lines_scanned':count_lines,
            'historical_json_dict_records':parsed,'candidate_methods':len(new_methods),
            'candidate_questions':len(new_q),'exact_normalized_question_collisions':len(matches_question),
            'exact_normalized_topic_method_collisions':len(matches_method),
            'question_collision_examples':matches_question[:20],'method_collision_examples':matches_method[:20],
            'limitations':'Exact textual equality after normalization only; semantic duplication and independent mathematical novelty NOT certified.'}
    (RESEARCH/'V153_HISTORICAL_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':audit()
