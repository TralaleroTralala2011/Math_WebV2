"""Build a small, independently verified seed bank; not a claim of 2,000 forms/topic."""
import json
from pathlib import Path
from fractions import Fraction

OUT = Path(__file__).resolve().parent / 'verified_seed_bank.jsonl'

def generate():
    for n in range(10):
        a=n+2; root=n-4; b=3*n-9; c=a*root+b
        yield dict(topic='Phương trình', grade=10, form_id='linear_isolate', form_signature='ax+b=c -> solve x', question=f'Giải phương trình {a}x + ({b}) = {c}.', answer=str(root), solution=f'Trừ {b} ở hai vế: {a}x={c-b}. Chia hai vế cho {a}: x={root}.', proof={'a':a,'b':b,'c':c,'x':root})
    for n in range(10):
        x=n+2; a=n+3; b=n-5; y=a*x+b
        yield dict(topic='Hàm số bậc nhất', grade=10, form_id='inverse_linear_model', form_signature='given output of affine function recover input', question=f'Một mô hình có y={a}x+({b}). Khi y={y}, hãy tìm x.', answer=str(x), solution=f'Thay y={y}: {a}x+({b})={y}, suy ra {a}x={y-b} và x={x}.', proof={'a':a,'b':b,'y':y,'x':x})
    for n in range(10):
        r=n-3; s=n+4; sm=r+s; prod=r*s
        yield dict(topic='Phương trình bậc hai', grade=10, form_id='quadratic_vieta_roots', form_signature='monic quadratic with two integer roots -> find roots', question=f'Tìm hai nghiệm của x² - ({sm})x + ({prod}) = 0.', answer=f'{r}; {s}', solution=f'Hai số {r} và {s} có tổng {sm} và tích {prod}. Vì thế x²-({sm})x+({prod})=(x-({r}))(x-({s})), suy ra x={r} hoặc x={s}.', proof={'r':r,'s':s,'sum':sm,'product':prod})

def validate(q):
    p=q['proof']; k=q['form_id']
    if k=='linear_isolate': return p['a']!=0 and p['a']*p['x']+p['b']==p['c'] and q['answer']==str(p['x'])
    if k=='inverse_linear_model': return p['a']!=0 and p['a']*p['x']+p['b']==p['y'] and q['answer']==str(p['x'])
    if k=='quadratic_vieta_roots': return p['r']!=p['s'] and p['r']+p['s']==p['sum'] and p['r']*p['s']==p['product'] and q['answer']==f"{p['r']}; {p['s']}"
    return False

def main():
    rows=list(generate())
    assert len(rows)==30 and len({r['question'] for r in rows})==30
    assert len({r['form_signature'] for r in rows})==3
    assert all(validate(r) and len(r['solution'])>20 for r in rows)
    with OUT.open('w',encoding='utf8') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    print('PASS: 30 verified questions across 3 task forms, 10 questions/form')
if __name__=='__main__': main()
