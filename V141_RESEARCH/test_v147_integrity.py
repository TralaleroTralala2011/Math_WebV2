import json
from pathlib import Path
from batch_integrity import inspect_batch, template

ROOT=Path(__file__).parent

def load(name):
    return [json.loads(s) for s in (ROOT/name).read_text(encoding='utf8').splitlines() if s.strip()]

def test_real_batch():
    result=inspect_batch(load('V141_CANDIDATE_METHODS.jsonl'),load('V141_VERIFIED_QUESTIONS.jsonl'))
    assert result['issues']==[]
    assert result['certified_new_methods']==0

def test_duplicate_stem_across_methods():
    ms=[{'method_id':'a'},{'method_id':'b'}]
    qs=[{'id':f'a{i}','method_id':'a','question':f'Tính {i}'} for i in range(10)]
    qs += [{'id':f'b{i}','method_id':'b','question':f'Tính {i+10}'} for i in range(10)]
    qs[-1]['question']=qs[0]['question']
    assert 'duplicate_stem' in [p['kind'] for p in inspect_batch(ms,qs)['issues']]

def test_duplicate_ids_and_orphan():
    qs=[{'id':'same','method_id':'unknown','question':'A'}, {'id':'same','method_id':'unknown','question':'B'}]
    kinds={p['kind'] for p in inspect_batch([],qs)['issues']}
    assert {'duplicate_question_id','orphan_question'}<=kinds

def test_numeric_variants_same_template():
    assert template('Tính 3 + 4')==template('Tính 5 + 6')
