"""V127: independent brute-force oracle for integer-divisibility scenarios.
No use of the generation formula, stored intermediate answers or solution text.
"""
import json,re,statistics
from fractions import Fraction
from pathlib import Path
PAT=re.compile(r'([A-D])\. Trong các số nguyên từ 1 đến (\d+), có bao nhiêu số chia hết cho (\d+) nhưng không chia hết cho (\d+)\?')

def verify(record):
    if record.get('topic_id')!='menh_de_tap_hop':
        return {'status':'unsupported-topic'}
    found=PAT.findall(record['stem'])
    if len(found)<2 or len(found)!=len(set(x[0] for x in found)):
        return {'status':'unparsed-scenarios'}
    vals={label:sum(n%int(a)==0 and n%int(b)!=0 for n in range(1,int(hi)+1)) for label,hi,a,b in found}
    family=record['family'].split('_')[1]
    a,b,c,d=(vals.get(k) for k in 'ABCD')
    if family=='delta': result=b-a
    elif family=='total': result=a+b+c
    elif family=='maximum': result=max(a,b,c)
    elif family=='median': result=sorted((a,b,c))[1]
    elif family=='curvature': result=c-2*b+a
    elif family=='threshold': result=sum(x>a for x in (b,c,d))
    elif family=='variance':
        mean=Fraction(a+b+c,3)
        result=sum((Fraction(x)-mean)**2 for x in (a,b,c))/3
    else: return {'status':'unsupported-family'}
    try: expected=Fraction(str(record['numeric_result']))
    except (ValueError,ZeroDivisionError): return {'status':'invalid-numeric-result'}
    return {'status':'pass' if result==expected else 'mismatch','computed':str(result),'stored':str(expected),'scenario_count':len(vals)}

def audit(path):
    counts={};bad=[];n=0
    with open(path,encoding='utf-8') as f:
        for line in f:
            q=json.loads(line)
            if q.get('topic_id')!='menh_de_tap_hop':continue
            n+=1; r=verify(q);counts[r['status']]=counts.get(r['status'],0)+1
            if r['status']!='pass':bad.append({'family':q.get('family'),'ordinal':q.get('ordinal'),'result':r})
    return {'checked':n,'by_status':counts,'failures':bad,'method':'brute-force enumeration independent of stored generator formula','independence_certified_new':0}
if __name__=='__main__':
    import sys
    print(json.dumps(audit(sys.argv[1]),ensure_ascii=False,indent=2))
