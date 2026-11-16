"""Local Chromium regression checks; uses set_content because localhost navigation is blocked."""
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]

def build_markup(page_name):
    soup=BeautifulSoup((root/page_name).read_text(encoding='utf8'), 'html.parser')
    for item in soup.find_all('script',src=True): item.decompose()
    for item in soup.find_all('link',href=True): item.decompose()
    if page_name=='geometry-studio.html':
        css='''*{box-sizing:border-box}.hidden{display:none!important}.flex{display:flex}.flex-col{flex-direction:column}.flex-1{flex:1 1 0%}.overflow-hidden{overflow:hidden}.overflow-y-auto{overflow-y:auto}.h-screen{height:100vh}.grid{display:grid}.w-full{width:100%}body{margin:0;background:#0f172a;color:#e2e8f0;font-family:system-ui}header{flex-shrink:0}#geo-studio-workspace{display:flex;flex:1 1 0%;min-height:0}#geo-studio-workspace main{flex:1 1 0%;display:flex;flex-direction:column}#geo-canvas{display:block;flex:1 1 0%}#geo-studio-sidebar{width:410px;flex:none}'''
        for path in ('css/unified-navbar-v55.css','css/geometry-mobile-v21.css','css/geometry-mobile-v33.css'):
            css += (root/path).read_text(encoding='utf8')
        style=soup.new_tag('style');style.string=css;soup.head.append(style)
    return str(soup)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    nav_js=(root/'js/unified-navbar-v55.js').read_text(encoding='utf8')
    total=0
    for name in ['learning-path.html','geometry-lab.html','battle.html','learn.html','geometry-studio.html']:
        page=browser.new_page(viewport={'width':1280,'height':900});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(build_markup(name),wait_until='domcontentloaded')
        before=page.evaluate('''() => ({title:document.body.querySelector('header h1')?.textContent, battle:!!document.querySelector('.battle-header'), toolbar:!!document.querySelector('#view-mode-3d')})''')
        page.add_script_tag(content=nav_js)
        after=page.evaluate('''() => ({title:document.body.querySelector('header:not(.mw-v55-unified) h1')?.textContent,battle:!!document.querySelector('.battle-header'),toolbar:!!document.querySelector('#view-mode-3d'),navbar:document.querySelectorAll('#mathwebUnifiedNavbar').length})''')
        assert after['navbar']==1,(name,after)
        if before['title']: assert after['title']==before['title'],(name,before,after)
        if before['battle']: assert after['battle'], (name,after)
        if before['toolbar']: assert after['toolbar'],(name,after)
        # Injecting the same script again must not add a second navbar.
        page.add_script_tag(content=nav_js)
        assert page.locator('#mathwebUnifiedNavbar').count()==1,name
        if name=='geometry-studio.html':
            for js in ['js/geometry-mobile-v21.js','js/geometry-mobile-v33.js']:
                page.add_script_tag(content=(root/js).read_text(encoding='utf8'))
            assert page.locator('.draw-3d-btn').count()==13
            for i in range(13):
                page.locator('.draw-3d-btn').nth(i).evaluate('(b)=>b.click()')
                n=page.evaluate('Object.keys(mode3D.nodes).length')
                assert n>=4,(i,n)
                total+=1
            page.locator('#tab-ai-btn').evaluate('(b)=>b.click()')
            page.locator('#ai-input-text').fill('Cho tam giác ABC vuông tại A, có AB=6 cm và AC=4 cm.')
            page.locator('#btn-ai-parse').evaluate('(b)=>b.click()')
            m=page.evaluate('''() => {const a=points.A,b=points.B,c=points.C;return {dot:(b.x-a.x)*(c.x-a.x)+(b.y-a.y)*(c.y-a.y),sign:rightAngleSigns[0]?.vertex,mode:currentMode}}''')
            assert abs(m['dot'])<1e-8 and m['sign']=='A' and m['mode']=='2D',m
            total+=1
            page.locator('#ai-input-text').fill('Cho hình chữ nhật ABCD có góc vuông tại A, AB=6 cm.')
            page.locator('#btn-ai-parse').evaluate('(b)=>b.click()')
            dims=page.evaluate('''() => ({w:Math.hypot(points.B.x-points.A.x,points.B.y-points.A.y),h:Math.hypot(points.D.x-points.A.x,points.D.y-points.A.y)})''')
            assert abs(dims['w']-dims['h'])>1,dims
            total+=1
            page.locator('#ai-input-text').fill('Trong không gian Oxyz, đường thẳng đi qua M(3;-3;4) có vectơ chỉ phương u=(-3;3;-3).')
            page.locator('#btn-ai-parse').evaluate('(b)=>b.click()')
            model=page.evaluate('''() => ({mode:currentMode,nodeCount:Object.keys(mode3D.nodes).length,edges:mode3D.edges.length})''')
            assert model['mode']=='3D' and model['nodeCount']>=3 and model['edges']>=1,model
            total+=1
        assert not errors,(name,errors[:5])
        print('PASS',name,after)
        total+=1
        page.close()
    for width in [393,768]:
        page=browser.new_page(viewport={'width':width,'height':852});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(build_markup('geometry-studio.html'),wait_until='domcontentloaded')
        page.add_script_tag(content=nav_js)
        for js in ['js/geometry-mobile-v21.js','js/geometry-mobile-v33.js']: page.add_script_tag(content=(root/js).read_text(encoding='utf8'))
        page.locator('#geo-mobile-more').click()
        page.locator('.draw-3d-btn[data-shape="cube"]').evaluate('(b)=>b.click()')
        assert page.evaluate('Object.keys(mode3D.nodes).length')==8
        assert not page.locator('#geo-studio-sidebar').evaluate('(e)=>e.classList.contains("geo-panel-open")'), 'drawer not closed'
        assert not errors,errors[:5]
        print('PASS mobile',width)
        total+=1
        page.close()
    browser.close()
print(f'PASS: {total} focused browser checks')
