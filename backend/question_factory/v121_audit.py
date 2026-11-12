"""Reproducible V121 corpus audit. Similarity warnings are NOT certification."""
from __future__ import annotations
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from hashlib import sha256
from pathlib import Path
import csv, json, re, unicodedata
from .v121_research import METHODS, SPEC_BY_FAMILY, export, numeric_value
from .v117_audit import all_candidate_records
from .v118_research import METHODS as V118
from .v119_research import METHODS as V119
from .v120_research import METHODS as V120


def normalize(t):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(t)).casefold()).strip()

def key(t):return sha256(normalize(t).encode('utf8')).hexdigest()


def run(root:Path, out:Path):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    stats=export(out)
    old_methods=all_candidate_records()
    old_methods += [(m.family,m.topic,m.title,m.signature,m.difficulty,'V118') for m in V118]
    old_methods += [(m.family,m.topic,m.title,m.signature,m.difficulty,'V119') for m in V119]
    old_methods += [(m.family,m.topic,m.title,m.signature,m.difficulty,'V120') for m in V120]
    if len(old_methods)!=470:raise ValueError(f'expected 470 previous candidates; got {len(old_methods)}')
    by_topic=defaultdict(list)
    for old in old_methods:by_topic[old[1]].append(old)
    alerts=[]
    for m in METHODS:
        stems=[]
        for f,topic,title,signature,diff,source in by_topic[m.topic]:
            score=max(SequenceMatcher(None,normalize(m.title),normalize(title)).ratio(),
                      SequenceMatcher(None,normalize(m.skill),normalize(signature)).ratio())
            if score>=0.57: stems.append((round(score,3),f,source,title))
        for score,f,source,title in sorted(stems,reverse=True)[:5]:
            alerts.append({'family':m.family,'topic_id':m.topic,'existing_family':f,
                           'existing_version':source,'score':score,'existing_title':title})
    # Audit all old question strings that can be verified from current extracted source tree.
    inputs=[
      root/'backend/app/ai/verified_seed/verified_seed_bank.jsonl',
      root/'V114_AUDIT/V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl',
      root/'V116_RESEARCH/V116_NEW_QUESTIONS_10_EACH.jsonl',
      root/'V117_AUDIT/V117_NEW_QUESTIONS.jsonl',
      root/'V118_AUDIT/V118_NEW_QUESTIONS.jsonl',
      root/'V119_RESEARCH/V119_NEW_QUESTIONS.jsonl',
      root/'V120_RESEARCH/V120_1500_NEW_QUESTIONS.jsonl',
    ]
    legacy_stems=set();sources=[];bad_lines=[]
    for p in inputs:
        count=0
        if p.exists():
            with p.open(encoding='utf8') as stream:
                for lineno,line in enumerate(stream,1):
                    if not line.strip():continue
                    try:data=json.loads(line)
                    except Exception:
                        bad_lines.append({'source':str(p.relative_to(root)),'line':lineno});continue
                    value=data.get('stem') or data.get('question')
                    if isinstance(value,str) and value.strip():legacy_stems.add(key(value))
                    count+=1
        sources.append({'filename':str(p.relative_to(root)),'parsed_rows':count,'missing':not p.exists()})
    collisions=[];new_stems=set();by_topic_count=Counter();by_family_count=Counter();format_count=Counter()
    with (out/'V121_3000_NEW_QUESTIONS.jsonl').open(encoding='utf8') as stream:
        for line in stream:
            row=json.loads(line)
            digest=key(row['stem'])
            if digest in legacy_stems:collisions.append([row['family'],row['ordinal']])
            if digest in new_stems:raise ValueError('duplicate within V121')
            new_stems.add(digest)
            by_topic_count[row['topic_id']]+=1;by_family_count[row['family']]+=1;format_count[row['question_type']]+=1
    formula_groups=defaultdict(list)
    for m in METHODS:
        # Reused formulas across unrelated topics should be reviewed for topical specificity.
        f=SPEC_BY_FAMILY[m.family][1]
        formula_groups[re.sub(r'\s+','',f)].append(m.family)
    formula_collisions=[list(group) for group in formula_groups.values() if len(group)>1]
    topics=json.loads((root/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
    with (out/'V121_TOPIC_PROGRESS_150.csv').open('w',encoding='utf8',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=['topic_id','grade','topic_name','new_candidate_forms','new_questions_checked','total_candidate_forms_v113_to_v121','independent_forms_certified'])
        w.writeheader()
        older=Counter(old[1] for old in old_methods)
        for t in topics:
            w.writerow(dict(topic_id=t['id'],grade=t['grade'],topic_name=t['name'],new_candidate_forms=by_topic_count[t['id']]//10,
                    new_questions_checked=by_topic_count[t['id']],total_candidate_forms_v113_to_v121=older[t['id']]+by_topic_count[t['id']]//10,
                    independent_forms_certified=0))
    report={**stats,'total_candidates_v113_to_v121':len(old_methods)+len(METHODS),
            'previous_candidate_forms':len(old_methods),
            'legacy_question_sources':sources,'bad_json_rows_old':bad_lines[:50],
            'legacy_question_hashes_available':len(legacy_stems),
            'exact_legacy_stem_collisions':len(collisions),'legacy_collisions':collisions,
            'candidate_title_similarity_alerts':len(alerts),
            'repeated_formula_groups_across_topics':len(formula_collisions),
            'warning':'Neither the existence of an original title nor a numerical difference establishes independent methods. Expert review pending.',
            'production_bank_unmodified':True}
    (out/'V121_AUDIT_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'V121_POTENTIAL_METHOD_OVERLAPS.json').write_text(json.dumps({'title_similarity':alerts,'formula_groups':formula_collisions},ensure_ascii=False,indent=2),encoding='utf8')
    if collisions or bad_lines or set(by_topic_count.values())!={20} or set(by_family_count.values())!={10}:
        raise ValueError(f'V121 audit failed: {len(collisions)} old duplicates, {len(bad_lines)} malformed old rows')
    return report
