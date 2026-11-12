import zipfile,re,json,sys
from pathlib import Path
archive=Path(sys.argv[1])
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names=set(z.namelist())
    base='MATH_WEB_GITHUB_READY/'
    assert base+'geometry-studio.html' in names
    assert base+'js/practice-mathgeo-bridge.js' in names
    studio=z.read(base+'geometry-studio.html').decode('utf-8')
    bridge=z.read(base+'js/practice-mathgeo-bridge.js').decode('utf-8')
    for token in ('MATHWEB_PRACTICE_TO_MATHGEO','MATHWEB_MATHGEO_READY','CIRCLE_CENTER_','circleData.forEach','const valid=p=>'):
        assert token in studio, token
    assert 'MATHWEB_PRACTICE_TO_MATHGEO' in bridge
    assert 'if(!Object.keys(points).length)' in studio
    assert 'MATHGEO_INTERNAL_CENTER_' in studio
    bank=base+'backend/app/ai/verified_seed/verified_seed_bank.jsonl'
    count=0
    forms=set()
    for line in z.open(bank):
        r=json.loads(line)
        assert r.get('answer') and r.get('solution')
        forms.add((str(r.get('grade')),str(r.get('topic')),str(r.get('form_id'))))
        count+=1
    assert count==333780,(count,len(forms))
    assert len(forms)==33378,len(forms)
    print('PASS ZIP integrity, bridge markers, bank records',count,'forms',len(forms))
