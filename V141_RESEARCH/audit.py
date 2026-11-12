"""V141 batch QA; only structural/exact duplicates, NOT semantic certification."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import unicodedata

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def norm(text):
    value=unicodedata.normalize('NFKC',str(text or '')).casefold().strip()
    return ' '.join(value.split())

def lines(path):
    with path.open(encoding='utf-8') as f:
        for n,line in enumerate(f,1):
            if not line.strip(): continue
            try: yield n,json.loads(line)
            except json.JSONDecodeError as e: raise RuntimeError(f'{path} line {n}: {e}')

def method_reference_data():
    data=[]
    for path in sorted(ROOT.glob('V*_RESEARCH/*CANDIDATE_METHODS.jsonl'))+[ROOT/'V114_AUDIT/V114_CANDIDATE_METHODS.jsonl']:
        if not path.is_file() or path.parent==HERE: continue
        for line,d in lines(path):
            topic=d.get('topic') or d.get('topic_id')
            title=d.get('title') or d.get('name')
            if not topic or not title: continue
            data.append({'topic':topic,'title':title,'id':d.get('method_id',d.get('family')),'source':str(path.relative_to(ROOT))})
    return data

def audit():
    from build import oracle, same, pretty, distractors, METHODS
    methods=[d for _,d in lines(HERE/'V141_CANDIDATE_METHODS.jsonl')]
    questions=[d for _,d in lines(HERE/'V141_VERIFIED_QUESTIONS.jsonl')]
    prior=method_reference_data()
    issues=[]; warnings=[]
    method_by_id={m['method_id']:m for m in methods}
    by_method=defaultdict(list)
    for q in questions:
        by_method[q['method_id']].append(q)
        if q['method_id'] not in method_by_id:
            issues.append({'type':'unknown_method','id':q['id']}); continue
        m=method_by_id[q['method_id']]
        if q['topic']!=m['topic'] or q['grade']!=m['grade']:
            issues.append({'type':'topic_grade_mismatch','id':q['id']})
        if not q['solution'] or len(q['solution'])<75:
            issues.append({'type':'weak_solution','id':q['id']})
        if q['published'] or q['independence_certified']:
            issues.append({'type':'unsafe_publication','id':q['id']})
    total_math=0
    for i,m in enumerate(methods):
        mid=m['method_id']; items=by_method[mid]
        if m['published'] or m['independence_certified']:
            issues.append({'type':'unsafe_method_publication','id':mid})
        if len(items)!=10 or len({norm(q['question']) for q in items})!=10:
            issues.append({'type':'missing_or_duplicate_questions','id':mid})
        if [q['id'] for q in items]!=[f'{mid}_{j:02d}' for j in range(10)]:
            issues.append({'type':'id_sequence_mismatch','id':mid})
        if Counter(q['format'] for q in items)!={'trac_nghiem':7,'tra_loi_ngan':2,'dung_sai':1}:
            issues.append({'type':'question_format_ratio','id':mid})
        for j,q in enumerate(items):
            stem,v,oracle_answer,_=oracle(i,j)
            total_math+=1
            if not same(v,oracle_answer):
                issues.append({'type':'independent_math_oracle_mismatch','id':q['id']})
            if q['canonical_answer']!=pretty(v):
                issues.append({'type':'answer_changed','id':q['id']})
            if j<7:
                if not q.get('correct_option') or q['answer']!=q['correct_option']:
                    issues.append({'type':'answer_key_mismatch','id':q['id']})
                if len(q.get('options',{}))!=4:
                    issues.append({'type':'missing_choices','id':q['id']})
                else:
                    # Choice texts must be EXACTLY the expected four symbolic outcomes;
                    # this checks one and only one correct choice independent of its label.
                    rendered=[pretty(v)]+[pretty(d) for d in distractors(v)]
                    if sorted(q['options'].values())!=sorted(rendered):
                        issues.append({'type':'choice_distractors_mismatch','id':q['id']})
                    matches=[key for key,val in q['options'].items() if val==pretty(v)]
                    if matches!=[q['correct_option']]:
                        issues.append({'type':'not_exactly_one_correct_option','id':q['id']})
            elif j<9:
                if q['answer']!=pretty(v) or q['independent_check']!=pretty(oracle_answer):
                    issues.append({'type':'short_answer_mismatch','id':q['id']})
            else:
                val=v if i%2==0 else distractors(v)[0]
                expected='Đúng' if same(val,v) else 'Sai'
                if q['answer']!=expected or q['assertion']!=pretty(val):
                    issues.append({'type':'true_false_mismatch','id':q['id']})
        for p in prior:
            if p['topic']!=m['topic']:continue
            ratio=SequenceMatcher(None,norm(p['title']),norm(m['title'])).ratio()
            if ratio>=0.70:
                warnings.append({'method_id':mid,'old_id':p['id'],'similarity':round(ratio,3),'old_title':p['title'],'source':p['source'],'note':'Potential overlap for human semantic review; similarity is not proof.'})
    seen={}; duplicates=[]; count=0; files=0
    # Scan historical JSONL questions, including original expansion banks.
    for path in sorted(ROOT.rglob('*.jsonl')):
        if path==HERE/'V141_VERIFIED_QUESTIONS.jsonl' or 'CANDIDATE_METHODS' in path.name:continue
        if path.stat().st_size>200_000_000: continue
        files+=1
        for line,d in lines(path):
            # Honor only known question-bearing fields. Some banks use 'stem'.
            statement=d.get('question') or d.get('stem') or d.get('text')
            if not isinstance(statement,str) or not statement.strip(): continue
            count+=1
            key=norm(statement)
            seen.setdefault(key,{'file':str(path.relative_to(ROOT)),'line':line})
    for q in questions:
        if norm(q['question']) in seen:
            duplicates.append({'id':q['id'],'old':seen[norm(q['question'])]})
    if duplicates:
        issues.extend({'type':'historical_exact_duplicate',**d} for d in duplicates)
    report={'version':'V141','method_candidates':len(methods),'questions_generated':len(questions),
            'formats':dict(Counter(q['format'] for q in questions)),
            'topics_covered':sorted({m['topic'] for m in methods}),
            'math_oracle_checks':total_math,
            'historical_question_records_scanned':count,'historical_jsonl_files_scanned':files,
            'historical_literal_duplicates':duplicates,
            'possible_semantic_method_overlap':warnings,
            'failures':issues,
            'independent_methods_certified':0,'published_into_production':0,
            'notes':['No numeric reparameterization is counted as an independent new mathematical method.',
                     'Mathematical novelty across all existing method catalogs remains unverified.',
                     'Only static question files were produced, not published in the application.',
                     'Independent oracles check computational answers, not prose completeness or curricular certification.']}
    (HERE/'V141_RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['method_candidates','questions_generated','math_oracle_checks','historical_question_records_scanned','historical_jsonl_files_scanned','independent_methods_certified']},ensure_ascii=False))
    print('FAILED:',len(issues),'WARNED:',len(warnings),'HISTORY DUPLICATES:',len(duplicates))
    if issues: raise SystemExit(1)
    return report

if __name__=='__main__': audit()
