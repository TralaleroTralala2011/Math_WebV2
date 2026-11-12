import json
from pathlib import Path
from batch_integrity import inspect_review_risks

ROOT=Path(__file__).parent

def test_actual_batch_review():
    methods=[json.loads(x) for x in (ROOT/'V141_CANDIDATE_METHODS.jsonl').read_text().splitlines() if x.strip()]
    questions=[json.loads(x) for x in (ROOT/'V141_VERIFIED_QUESTIONS.jsonl').read_text().splitlines() if x.strip()]
    audit=inspect_review_risks(methods,questions)
    assert audit['certified_new_methods']==0
    assert isinstance(audit['warnings'],list)

def test_cross_method_number_variants_flagged():
    ms=[{'method_id':'a'},{'method_id':'b'}]
    qs=[{'id':'1','method_id':'a','question':'Tính 3 + 4','answer':'7','solution':'Cộng'},
        {'id':'2','method_id':'b','question':'Tính 5 + 6','answer':'11','solution':'Cộng'}]
    assert 'cross_method_numeric_template' in {x['kind'] for x in inspect_review_risks(ms,qs)['warnings']}

def test_bad_mcq_and_missing_solution():
    q={'id':'x','method_id':'a','question':'Tính 1','format':'trac_nghiem',
       'options':{'A':'1','B':'1','C':'3','D':'4'},'correct_option':'Z','answer':'Z'}
    kinds={x['kind'] for x in inspect_review_risks([{'method_id':'a'}],[q])['warnings']}
    assert {'missing_solution','repeated_mcq_options','invalid_mcq_answer'}<=kinds
