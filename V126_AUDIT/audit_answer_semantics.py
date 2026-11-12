"""V126: type-aware checks; not a proof of mathematical correctness."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'V123_RESEARCH' / 'V123_10500_WORKED_QUESTIONS.jsonl'

def audit(records):
    stats=Counter(); problems=[]; by_topic=Counter()
    for index, d in enumerate(records,1):
        stats['total']+=1
        kind=d.get('question_type'); by_topic[d.get('topic_id')]+=1
        result=str(d.get('numeric_result','')).strip()
        answer=str(d.get('answer','')).strip()
        if kind=='dung_sai':
            stats['true_false']+=1
            expected='Đúng' if d.get('truth') is True else 'Sai' if d.get('truth') is False else None
            if answer != expected: problems.append([index,'truth_answer_inconsistent'])
            if str(d.get('assertion_value','')).strip()==result and d.get('truth') is False: problems.append([index,'false_assertion_equals_result'])
            if str(d.get('assertion_value','')).strip()!=result and d.get('truth') is True: problems.append([index,'true_assertion_differs_from_result'])
            if answer!=result:stats['expected_display_numeric_difference']+=1
        elif kind=='trac_nghiem':
            stats['multiple_choice']+=1
            opts=[str(x).strip() for x in d.get('options',[])]
            correct=d.get('correct_index')
            if len(opts)!=4 or len(set(opts))!=4: problems.append([index,'invalid_options'])
            if not isinstance(correct,int) or not 0<=correct<len(opts) or opts[correct]!=result or opts.count(result)!=1: problems.append([index,'mcq_answer_invalid'])
            if answer!=result: problems.append([index,'mcq_display_mismatch'])
        else:
            stats['direct_answer']+=1
            if answer!=result:problems.append([index,'direct_answer_mismatch'])
        if d.get('independence_certified') is True: stats['self_declared_certified']+=1
    return {'counts':dict(stats),'topics':len(by_topic),'topic_min':min(by_topic.values(),default=0),'topic_max':max(by_topic.values(),default=0),'issues_count':len(problems),'issues_sample':problems[:30],'new_independent_types_certified':0,'scope':'type-aware display/metadata consistency only; mathematical truth and novelty not certified'}

if __name__=='__main__':
    with DATA.open(encoding='utf-8') as f:
        report=audit(json.loads(line) for line in f if line.strip())
    output=Path(__file__).with_name('V126_RESULTS.json')
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
