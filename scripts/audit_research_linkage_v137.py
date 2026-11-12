"""Cross-check research candidates and question files. No novelty certification."""
import json, re, unicodedata, argparse
from pathlib import Path
from collections import Counter, defaultdict
from sympy import sympify, simplify

def norm(x):
    return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC',str(x or '')).casefold()))

def answer_equivalent(a,b):
    """Check scalar symbolic equality; return None if parsing unsupported."""
    if str(a).strip()==str(b).strip(): return True
    try:
        return bool(simplify(sympify(str(a))-sympify(str(b)))==0)
    except (ValueError, TypeError, SyntaxError, AttributeError):
        return None

def audit(root):
    methods={}; questions=defaultdict(list); ids=set(); texts={}; errors=[]; counts=Counter()
    for f in sorted(root.glob('V*_RESEARCH/V*_CANDIDATE_METHODS.jsonl')):
        counts['method_files']+=1
        for n,line in enumerate(f.read_text(encoding='utf8').splitlines(),1):
            try: d=json.loads(line)
            except Exception: errors.append([f.name,n,'bad method JSON']);continue
            mid=d.get('method_id');counts['candidates']+=1
            if not mid or mid in methods: errors.append([f.name,n,'missing or duplicate method ID',mid])
            else: methods[mid]=d
            if d.get('published') is True or d.get('independence_certified') is True: errors.append([f.name,n,'unsafe candidate status',mid])
    for f in sorted(root.glob('V*_RESEARCH/V*_VERIFIED_QUESTIONS.jsonl')):
        counts['question_files']+=1
        for n,line in enumerate(f.read_text(encoding='utf8').splitlines(),1):
            try: d=json.loads(line)
            except Exception: errors.append([f.name,n,'bad question JSON']);continue
            qid=d.get('id');mid=d.get('method_id');counts['questions']+=1
            if not qid or qid in ids: errors.append([f.name,n,'missing or duplicate question ID',qid])
            ids.add(qid)
            if mid not in methods: errors.append([f.name,n,'orphan method',mid])
            elif d.get('topic')!=methods[mid].get('topic') or d.get('grade')!=methods[mid].get('grade'):
                errors.append([f.name,n,'topic or grade mismatch',qid])
            if d.get('published') is True or d.get('independence_certified') is True: errors.append([f.name,n,'unsafe question status',qid])
            if not all(str(d.get(k,'')).strip() for k in ('question','answer','solution')): errors.append([f.name,n,'missing question answer or solution',qid])
            if 'independent_check' in d:
                verdict=answer_equivalent(d.get('answer'),d['independent_check'])
                if verdict is False:
                    counts['stored_check_mismatches']+=1
                    errors.append([f.name,n,'mathematically unequal stored check',qid])
                elif verdict is None:
                    counts['unparsed_stored_checks']+=1
            key=''.join(unicodedata.normalize('NFKC',str(d.get('question',''))).casefold().split())
            if key in texts: errors.append([f.name,n,'duplicate normalized question',qid,texts[key]])
            else: texts[key]=qid
            questions[mid].append(d)
    for mid,d in methods.items():
        qs=questions[mid]
        if len(qs)!=d.get('questions_expected',10): errors.append([mid,'question count',len(qs),d.get('questions_expected',10)])
        if qs and len({str(q.get('answer')) for q in qs})==1: counts['constant_answer_methods']+=1
    counts['linked_methods']=sum(bool(questions[mid]) for mid in methods)
    return {'counts':dict(counts),'issues':errors,'limitation':'Structural checks and literal normalized text only; stored checks are not independent mathematical proofs; zero forms certified.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path);a=p.parse_args();r=audit(a.root)
    if a.output:a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'counts':r['counts'],'issue_count':len(r['issues'])},ensure_ascii=False))
    if r['issues']:raise SystemExit(1)
