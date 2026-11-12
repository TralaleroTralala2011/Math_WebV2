"""Independent batch-level structural safeguards; does not certify mathematical novelty."""
from collections import Counter, defaultdict
import re
import unicodedata


def normalize(s):
    return ' '.join(unicodedata.normalize('NFKC', str(s or '')).casefold().split())


def template(s):
    """Conservative heuristic: mask numeric literals to identify reparameterized stems."""
    s=normalize(s)
    return re.sub(r'(?<![\w])[-+]?\d+(?:[.,]\d+)?(?![\w])', '<number>', s)


def inspect_batch(methods, questions):
    problems=[]
    method_ids=[m.get('method_id') for m in methods]
    if len(set(method_ids))!=len(method_ids):
        problems.append({'kind':'duplicate_method_id'})
    ids=[q.get('id') for q in questions]
    if len(set(ids))!=len(ids):
        problems.append({'kind':'duplicate_question_id'})
    by_method=defaultdict(list)
    exact=defaultdict(list)
    for q in questions:
        mid=q.get('method_id')
        by_method[mid].append(q)
        stem=normalize(q.get('question'))
        if not stem:
            problems.append({'kind':'empty_stem','id':q.get('id')})
        else:
            exact[stem].append(q.get('id'))
        if mid not in method_ids:
            problems.append({'kind':'orphan_question','id':q.get('id')})
    for stem, qids in exact.items():
        if len(qids)>1:
            problems.append({'kind':'duplicate_stem','ids':qids})
    for mid in method_ids:
        if len(by_method[mid])!=10:
            problems.append({'kind':'incorrect_question_count','method_id':mid,'actual':len(by_method[mid])})
    # Repeated templates within a method are EXPECTED, not additional methods.
    # This diagnostic must never increase certified method totals.
    templates={mid:len(set(template(q.get('question')) for q in by_method[mid])) for mid in method_ids}
    return {'issues':problems,'template_counts_by_method':templates,
            'certified_new_methods':0,'certified_new_questions':0}


def inspect_review_risks(methods, questions):
    """Non-certifying review queue: quality gaps and cross-method numeric clones.

    These findings are warnings, not mathematical novelty judgments.
    """
    warnings=[]
    by_template=defaultdict(lambda: defaultdict(list))
    known={m.get('method_id') for m in methods}
    for q in questions:
        qid=q.get('id')
        mid=q.get('method_id')
        if mid not in known:
            continue  # inspect_batch already reports orphans
        stem=normalize(q.get('question'))
        if stem:
            by_template[template(stem)][mid].append(qid)
        if not normalize(q.get('solution')):
            warnings.append({'kind':'missing_solution','id':qid})
        if not normalize(q.get('canonical_answer',q.get('answer'))):
            warnings.append({'kind':'missing_answer','id':qid})
        if q.get('answer_oracle_match') is False:
            warnings.append({'kind':'oracle_mismatch','id':qid})
        if q.get('format')=='trac_nghiem':
            options=q.get('options')
            if not isinstance(options,dict) or set(options)!={'A','B','C','D'}:
                warnings.append({'kind':'invalid_mcq_options','id':qid})
            else:
                if len({normalize(v) for v in options.values()})!=4:
                    warnings.append({'kind':'repeated_mcq_options','id':qid})
                if q.get('correct_option',q.get('answer')) not in options:
                    warnings.append({'kind':'invalid_mcq_answer','id':qid})
    for fingerprint, mids in by_template.items():
        if len(mids)>1:
            warnings.append({'kind':'cross_method_numeric_template',
                             'method_ids':sorted(mids),
                             'sample_question_ids':{mid:ids[:2] for mid,ids in mids.items()},
                             'template':fingerprint[:240]})
    return {'warnings':warnings,'warning_count':len(warnings),
            'certified_new_methods':0,'certified_new_questions':0}
