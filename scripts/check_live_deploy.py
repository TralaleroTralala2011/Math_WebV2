"""Non-mutating smoke test for an already deployed GitHub Pages + Render pair.

Run after updating BOTH services. Uses only stdlib, no credentials or user data.
    python scripts/check_live_deploy.py
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import json,sys
API='https://math-webv2.onrender.com'
PAGE='https://tralalerotralala2011.github.io/Math_WebV2/'

def check(url, method='GET', headers=None, expect=(200,)):
    try:
        with urlopen(Request(url,method=method,headers=headers or {}),timeout=25) as r:
            data=r.read(120000)
            if r.status not in expect:raise ValueError('HTTP '+str(r.status))
            return r.status,dict(r.headers),data
    except HTTPError as e:
        if e.code in expect:return e.code,dict(e.headers),e.read(500)
        raise

def main():
    checks=[('GitHub Pages',PAGE+'index.html',(200,)),
            ('API health',API+'/health',(200,)),
            ('Feature endpoint',API+'/api/roadmap-v2/status/10',(401,403,)),
            ('Game heatmap',API+'/api/games/activity-heatmap',(401,403,)),
            ('Account guard',API+'/api/auth/me',(401,))]
    errors=0
    for label,url,expected in checks:
        try:
            status,headers,data=check(url,expect=expected)
            print('PASS',label,status)
            if label=='API health':
                features=json.loads(data).get('features',{})
                if not all(features.get(n) for n in ('roadmap_v2','activity_heatmap','tutor_recommendations')):
                    print('FAIL: backend not updated to matching frontend');errors+=1
        except Exception as e:
            print('FAIL',label,type(e).__name__,str(e)[:140]);errors+=1
    try:
        status,h,_=check(API+'/api/auth/login','OPTIONS',{
             'Origin':'https://tralalerotralala2011.github.io',
             'Access-Control-Request-Method':'POST',
             'Access-Control-Request-Headers':'content-type'},(200,))
        assert h.get('Access-Control-Allow-Origin')=='https://tralalerotralala2011.github.io'
        print('PASS CORS from GitHub Pages')
    except Exception as e:
        print('FAIL CORS',str(e)[:150]);errors+=1
    print('Errors:',errors,'NOTE: no accounts, user persistence or browser E2E exercised.')
    return 1 if errors else 0

if __name__=='__main__':sys.exit(main())
