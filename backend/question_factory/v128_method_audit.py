"""Read-only V128 audit of V123 candidate method reuse and publication safeguards."""
import json,collections,sys,zipfile
from pathlib import Path
FORMS='MATH_WEB_GITHUB_READY/V123_RESEARCH/V123_1050_CANDIDATE_OBJECTIVES.jsonl'
QUESTIONS='MATH_WEB_GITHUB_READY/V123_RESEARCH/V123_10500_WORKED_QUESTIONS.jsonl'
def analyze(z):
    """Accept the original V127 ZIP or a later project with the same V123 files.

    Shipping a current ZIP without embedding the historical ZIP should not
    make six read-only regression tests fail when the original V123 evidence
    itself is present and can be audited directly.
    """
    path=Path(z)
    if path.is_dir():
        def content(member):
            relative=Path(member).relative_to('MATH_WEB_GITHUB_READY')
            return (path/relative).read_text(encoding='utf-8')
        forms=[json.loads(x) for x in content(FORMS).splitlines() if x.strip()]
        questions=[json.loads(x) for x in content(QUESTIONS).splitlines() if x.strip()]
    else:
        with zipfile.ZipFile(path) as f:
            forms=[json.loads(x) for x in f.read(FORMS).decode().splitlines() if x.strip()]
            questions=[json.loads(x) for x in f.read(QUESTIONS).decode().splitlines() if x.strip()]
    by_topic=collections.Counter(x['topic'] for x in forms)
    by_family=collections.Counter(x['family'] for x in questions)
    by_source=collections.defaultdict(set)
    for x in forms:by_source[x['source_family']].add(x['operator'])
    flags=collections.Counter()
    for x in forms:
        if x.get('published') is not False:flags['form_not_explicitly_unpublished']+=1
        if x.get('independence_certified') is not False:flags['form_incorrect_certification']+=1
        if x.get('review_status')!='pending-expert-review':flags['form_unexpected_review_state']+=1
    for x in questions:
        if x.get('independence_certified') is not False:flags['question_incorrect_certification']+=1
        if x.get('method_review_status')!='pending-expert-review':flags['question_unexpected_review_state']+=1
        if x.get('family') not in by_family:flags['missing_family']+=1
    families={x['family'] for x in forms}
    missing=sorted(families-set(by_family))
    excess=sorted(set(by_family)-families)
    inconsistent=[k for k,v in by_family.items() if v!=10]
    return {'forms':len(forms),'questions':len(questions),'topics':len(by_topic),'min_forms_per_topic':min(by_topic.values()),'max_forms_per_topic':max(by_topic.values()),'source_methods':len(by_source),'source_reuse_distribution':dict(sorted(collections.Counter(len(v) for v in by_source.values()).items())),'distinct_operators':sorted(set(x['operator'] for x in forms)),'forms_with_shared_core':sum(x.get('shared_core_method') is True for x in forms),'certified_independent_forms':sum(x.get('independence_certified') is True for x in forms),'publication_and_review_flags':dict(flags),'missing_question_families':missing,'extra_question_families':excess,'families_not_ten_questions':inconsistent,'status':'PASS' if not flags and not missing and not excess and not inconsistent and len(forms)==1050 and len(questions)==10500 else 'REVIEW_REQUIRED','note':'Structural and method-reuse audit only. No mathematical independence or solution correctness certification.'}
if __name__=='__main__':print(json.dumps(analyze(sys.argv[1]),ensure_ascii=False,indent=2))
