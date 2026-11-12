#!/usr/bin/env python3
"""Conservative structural quality gate for MATH_WEB question banks.
This DOES NOT certify mathematical or pedagogical independence.
Usage: python validate_mathweb_types.py <zip> [--output report.json]
"""
import argparse, collections, json, zipfile, pathlib

def validate(path):
    forms=collections.defaultdict(lambda:{'count':0,'questions':set(),'missing':0,'families':set(),'signatures':set()})
    families=collections.defaultdict(set)
    malformed=[]; total=0
    with zipfile.ZipFile(path) as z:
        bank=next((x for x in z.namelist() if x.endswith('verified_seed_bank.jsonl')),None)
        if bank is None: raise ValueError('No verified_seed_bank.jsonl found')
        for line_no,line in enumerate(z.open(bank),1):
            try: r=json.loads(line)
            except (ValueError,UnicodeError):
                malformed.append(line_no);continue
            total+=1
            key=(str(r.get('grade','')),str(r.get('topic','')),str(r.get('form_id','')))
            form=forms[key];form['count']+=1
            q=str(r.get('question','')).strip();form['questions'].add(q)
            if not q or not str(r.get('answer','')).strip() or not str(r.get('solution','')).strip(): form['missing']+=1
            family=str(r.get('method_family') or r.get('form_signature') or 'UNLABELED')
            form['families'].add(family)
            form['signatures'].add(str(r.get('form_signature','')))
            families[key[:2]+(family,)].add(key[2])
    shared=set()
    for ids in families.values():
        if len(ids)>1: shared.update(ids)
    problems=[]
    for key,form in forms.items():
        if form['count']!=10 or len(form['questions'])!=10 or form['missing']:
            problems.append({'grade':key[0],'topic':key[1],'form_id':key[2], 'count':form['count'], 'unique_questions':len(form['questions']),'missing_fields':form['missing']})
    topic_counts=collections.Counter((grade,topic) for grade,topic,fid in forms)
    return {'total_records':total,'form_ids':len(forms),'grade_topic_pairs':len(topic_counts),
        'form_ids_not_exactly_10_valid_unique_questions':len(problems),
        'examples_of_failing_forms':problems[:50],
        'method_family_clusters':len(families),
        'form_ids_in_shared_method_families':sum(any(len(families[key[:2]+(f,)])>1 for f in form['families']) for key,form in forms.items()),
        'topics_with_at_least_2000_form_ids':sum(n>=2000 for n in topic_counts.values()),
        'missing_topics_vs_target_147':max(0,147-len(topic_counts)),
        'malformed_json_lines':malformed[:100],
        'independent_types_certified':0,
        'certification_note':'Structural validation only. Different IDs, family names or question texts do NOT establish distinct mathematical problem types. Independent mathematical and pedagogical review is still required.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('zip');p.add_argument('--output');args=p.parse_args()
    report=validate(args.zip)
    out=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output:pathlib.Path(args.output).write_text(out,encoding='utf-8')
    print(out)
