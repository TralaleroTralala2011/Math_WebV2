#!/usr/bin/env python3
"""MATH_WEB batch pipeline. Only genuinely different reviewed task specifications get new IDs.
Usage: python tools/type_pipeline.py audit [bank.jsonl]
       python tools/type_pipeline.py build specs.jsonl output.jsonl
A specification must have: grade, topic, type_key, mathematical_task, method,
knowledge, reasoning_steps, questions (exactly 10 entries with question,answer,solution).
The script does not certify mathematical independence; human review is required.
"""
import collections, hashlib, json, pathlib, sys

def normalize(v): return ' '.join(str(v).casefold().split())
def signature(r):
    # Detect identical mathematical tasks even if IDs differ; this is a first-line gate.
    return tuple(normalize(r.get(k,'')) for k in ('grade','topic','mathematical_task','method','knowledge','reasoning_steps'))

def audit(path):
    ids=collections.defaultdict(list); tasks=collections.defaultdict(set); bad=[]
    with open(path,encoding='utf-8') as f:
        for n,line in enumerate(f,1):
            try: r=json.loads(line)
            except Exception as e: bad.append((n,'invalid JSON'));continue
            key=(str(r.get('grade')),str(r.get('topic')),str(r.get('form_id')))
            ids[key].append(r)
            tasks[(key[0],key[1],str(r.get('method_family','')))].add(key[2])
    under=sum(len(v)!=10 for v in ids.values())
    dup=sum(len({normalize(q.get('question')) for q in v})!=len(v) for v in ids.values())
    shared=sum(len(tasks[(k[0],k[1],str(v[0].get('method_family','')))])>1 for k,v in ids.items())
    return {'form_ids':len(ids),'questions':sum(map(len,ids.values())),'forms_not_exactly_10':under,'forms_with_duplicate_question_text':dup,'form_ids_sharing_method_family':shared,'malformed_lines':len(bad),'certified_independent_types':0}

def build(spec_path,out_path):
    seen_signatures=set();seen_ids=set();out=[];rejected=[]
    for n,line in enumerate(open(spec_path,encoding='utf-8'),1):
        try: s=json.loads(line)
        except Exception: rejected.append((n,'invalid JSON'));continue
        required=['grade','topic','type_key','mathematical_task','method','knowledge','reasoning_steps','questions']
        if any(not s.get(k) for k in required):rejected.append((n,'missing fields'));continue
        sig=signature(s)
        if sig in seen_signatures:rejected.append((n,'duplicate mathematical task signature'));continue
        questions=s['questions']
        if not isinstance(questions,list) or len(questions)!=10:rejected.append((n,'not exactly 10 questions'));continue
        if any(not all(q.get(k) for k in ('question','answer','solution')) for q in questions):rejected.append((n,'missing question/answer/solution'));continue
        if len({normalize(q['question']) for q in questions})!=10:rejected.append((n,'duplicate questions'));continue
        fid='mw_'+hashlib.sha256('|'.join(sig).encode()).hexdigest()[:20]
        if fid in seen_ids:rejected.append((n,'ID collision'));continue
        seen_ids.add(fid);seen_signatures.add(sig)
        for q in questions:
            out.append({'grade':s['grade'],'topic':s['topic'],'form_id':fid,'form_signature':s['mathematical_task'],'method_family':s['method'],'question':q['question'],'answer':q['answer'],'solution':q['solution'],'independently_verified_type':False,'review_status':'needs_independent_math_and_pedagogy_review','source':'type_pipeline'})
    with open(out_path,'w',encoding='utf-8') as f:
        for r in out:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    print(json.dumps({'accepted_type_specs':len(seen_ids),'generated_questions':len(out),'rejected':len(rejected),'rejection_examples':rejected[:20]},ensure_ascii=False,indent=2))
    return 1 if rejected else 0

if __name__=='__main__':
    if len(sys.argv)<3:sys.exit(__doc__)
    if sys.argv[1]=='audit':print(json.dumps(audit(sys.argv[2]),ensure_ascii=False,indent=2))
    elif sys.argv[1]=='build' and len(sys.argv)==4:sys.exit(build(sys.argv[2],sys.argv[3]))
    else:sys.exit(__doc__)
