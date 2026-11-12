#!/usr/bin/env python3
"""Independent answer checks for five V73 math-method families (25,000 records).
Run: python V77_CHECK_ANSWERS.py [path/to/verified_seed_bank.jsonl]
"""
import collections, json, math, pathlib, re, sys
from fractions import Fraction
P={
'v73_method_03':r'^Có (\d+) loại áo và (\d+) loại quần\. Chọn 1 áo và 1 quần được bao nhiêu cách\?$',
'v73_method_04':r'^Cho u=\(([-\d]+);([-\d]+)\) và v=\(([-\d]+);([-\d]+)\)\. Tính u·v\.$',
'v73_method_07':r'^Hộp có (\d+) bi đỏ và (\d+) bi xanh\. Rút ngẫu nhiên một viên, xác suất bi đỏ\?$',
'v73_method_16':r'^Tìm tiệm cận đứng của y=(\d+)/\(x-\((\d+)\)\)\.$',
'v73_method_19':r'^Trong Oxyz, A\(([-\d]+);([-\d]+);([-\d]+)\), B\(([-\d]+);([-\d]+);([-\d]+)\)\. Tính AB\.$'
}
P={k:re.compile(v) for k,v in P.items()}
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(__file__).parent/'backend/app/ai/verified_seed/verified_seed_bank.jsonl'
stats=collections.Counter();errors=[]
with path.open(encoding='utf-8') as f:
 for line in f:
  r=json.loads(line);fam=r.get('method_family')
  if fam not in P:continue
  stats['target']+=1;m=P[fam].fullmatch(r['question'])
  if not m:errors.append((r['form_id'],'unparsed'));continue
  n=list(map(int,m.groups()))
  if fam=='v73_method_03':answer=str(n[0]*n[1])
  elif fam=='v73_method_04':answer=str(n[0]*n[2]+n[1]*n[3])
  elif fam=='v73_method_07':answer=str(Fraction(n[0],n[0]+n[1]))
  elif fam=='v73_method_16':answer='x='+str(n[1])
  else:
   d=sum((n[i+3]-n[i])**2 for i in range(3));root=math.isqrt(d)
   answer=str(root) if root*root==d else f'sqrt({d})'
  if r.get('answer')!=answer:errors.append((r['form_id'],'wrong answer',answer,r.get('answer')))
  else:stats['passed']+=1
print(json.dumps({'checked':stats['target'],'passed':stats['passed'],'errors':errors[:30],'error_count':len(errors)},ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
