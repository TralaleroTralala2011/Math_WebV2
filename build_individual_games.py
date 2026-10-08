import json, re, shutil, html
from pathlib import Path

ROOT=Path('/mnt/data/rework')
PRACT=ROOT/'js/practise.js'

# Parse the canonical 92 knowledge list from practise.js
text=PRACT.read_text(encoding='utf-8')
start=text.index('const knowledgeData = [')+len('const knowledgeData = ')
depth=0; instr=False; esc=False
for i,ch in enumerate(text[start:],start):
    if instr:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch=='"': instr=False
    else:
        if ch=='"': instr=True
        elif ch=='[': depth+=1
        elif ch==']':
            depth-=1
            if depth==0:
                knowledge=json.loads(text[start:i+1]); break
assert len(knowledge)==92, len(knowledge)

# Existing game pages are the visual/gameplay masters. We only clone them and
# retarget their topic metadata, API grade and links.
TEMPLATES={
 'probability':['games/probability/marble.html','games/probability/dice.html','games/probability/situation.html'],
 'counting':['games/combination/team.html','games/combination/choice.html','games/combination/hunt.html'],
 'permutation':['games/permutation/position.html','games/permutation/code.html','games/permutation/order.html'],
 'function':['games/function/point.html','games/function/intersection.html','games/function/graph.html'],
 'system':['games/system-equation/investigation.html','games/system-equation/value.html','games/system-equation/match.html'],
 'quadratic':['games/quadratic-equation/root.html','games/quadratic-equation/match.html','games/quadratic-equation/unlock.html'],
 'inequality':['games/inequality/safe-zone.html','games/inequality/interval.html','games/inequality/barrier.html'],
 'sequence':['games/sequence/rule.html','games/sequence/fill.html','games/sequence/race.html'],
 'divisibility':['games/divisibility/find.html','games/divisibility/select.html','games/divisibility/unlock.html'],
 'remainder':['games/remainder/draw.html','games/remainder/hunt.html','games/remainder/modulo.html'],
 'radical':['games/radical/hunt.html','games/radical/simplify.html','games/radical/unlock.html'],
 'identity':['games/identities/match.html','games/identities/break.html','games/identities/mystery.html'],
 'fraction':['games/algebraic-fraction/simplify.html','games/algebraic-fraction/condition.html','games/algebraic-fraction/speed.html'],
 'geometry':['games/geometry/angle.html','games/geometry/length.html','games/geometry/map.html'],
 'statistics':['games/statistics/chart.html','games/statistics/data.html','games/statistics/challenge.html'],
}

ids={str(k['id']).lower():k for k in knowledge}

def kind(k):
    s=(k['id']+' '+k['name']).lower()
    if any(x in s for x in ['xác suất','xac_suat','biến cố','ngẫu nhiên']): return 'probability'
    if any(x in s for x in ['tổ hợp','tổ hợp','quy tắc đếm','nhị thức newton','đếm']): return 'counting'
    if any(x in s for x in ['chỉnh hợp','hoán vị','sắp xếp']): return 'permutation'
    if any(x in s for x in ['thống kê','số đặc trưng','phân tán']): return 'statistics'
    if any(x in s for x in ['hình học','tam giác','đường tròn','mặt phẳng','mặt cầu','không gian','tọa độ trong không gian','góc và khoảng cách','thiết diện','song song','vuông góc','biến hình','tương giao']): return 'geometry'
    if any(x in s for x in ['hàm số','đơn điệu','cực trị','giá trị lớn nhất','giá trị nhỏ nhất','tiệm cận','khảo sát','tiếp tuyến','logarit','mũ','đạo hàm','nguyên hàm','tích phân']): return 'function'
    if any(x in s for x in ['bất phương trình','hệ bất phương trình']): return 'inequality'
    if any(x in s for x in ['phương trình bậc hai']): return 'quadratic'
    if any(x in s for x in ['hệ phương trình']): return 'system'
    if any(x in s for x in ['căn thức']): return 'radical'
    if any(x in s for x in ['hằng đẳng thức']): return 'identity'
    if any(x in s for x in ['phân thức']): return 'fraction'
    if 'chia dư' in s or 'modulo' in s: return 'remainder'
    if 'chia hết' in s: return 'divisibility'
    if any(x in s for x in ['dãy số','cấp số','quy nạp']): return 'sequence'
    # Algebraic/real-life/general topics use the function trio as the safest
    # old visual master. AI supplies the actual topic-specific questions.
    return 'function'

def slug(s):
    import unicodedata
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s or 'topic'

def level_name(k):
    return {'foundation':'easy','medium':'medium','advanced':'hard'}.get(k['level_key'],'medium')

def replace_once(t,a,b):
    if a not in t: return t
    return t.replace(a,b,1)

# Remove old generated individual folder if rerun
out=ROOT/'games'/'knowledge'
if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True)

manifest=[]
for k in knowledge:
    family=kind(k); srcs=TEMPLATES[family]
    d=out/slug(k['id'])
    d.mkdir(parents=True,exist_ok=True)
    for idx,src_rel in enumerate(srcs,1):
        src=ROOT/src_rel
        t=src.read_text(encoding='utf-8')
        # Pull source GAME metadata and visible title/icon where possible.
        m=re.search(r'window\.MATH_GAME=(\{.*?\});</script>',t)
        cfg=json.loads(m.group(1)) if m else {}
        game_title=cfg.get('title', src.stem.replace('-',' ').title())
        icon='🎮'
        mi=re.search(r'<div class="icon">(.*?)</div>',t,re.S)
        if mi: icon=mi.group(1).strip()
        # Preserve the exact CSS/markup structure. Only retarget text/meta.
        t=t.replace(f'<title>{html.escape(game_title)} | MATH WEB</title>', f'<title>{html.escape(game_title)} • {html.escape(k["name"])} | MATH WEB</title>')
        # Some titles may use | instead of escaped dot; broad replacement is safer.
        t=t.replace(f'<title>{game_title} | MATH WEB</title>', f'<title>{game_title} • {html.escape(k["name"])} | MATH WEB</title>')
        t=t.replace(f'<h1 class="title">{game_title}</h1>', f'<h1 class="title">{html.escape(k["name"])}</h1>')
        t=t.replace(f'<div class="kicker">{cfg.get("topic", "TOÁN")}</div>', f'<div class="kicker">TOÁN {k["grade"]} • {"NỀN TẢNG" if k["level_key"]=="foundation" else "TRUNG CẤP" if k["level_key"]=="medium" else "NÂNG CAO"}</div>')
        # Keep the same icon box and game UI, but identify the knowledge.
        mi2=re.search(r'<div class="icon">(.*?)</div>',t,re.S)
        if mi2:
            t=t[:mi2.start()] + f'<div class="icon">{icon}</div>' + t[mi2.end():]
        # Retarget description only, not layout.
        t=re.sub(r'<p class="desc">.*?</p>', f'<p class="desc">Game <b>{html.escape(game_title)}</b> theo kiến thức <b>{html.escape(k["name"])}</b>, giữ nguyên giao diện và cơ chế của game gốc.</p>', t, count=1, flags=re.S)
        # Fix relative links for depth games/knowledge/<slug>/file.html
        t=t.replace('src="../../js/api-config.js"','src="../../../js/api-config.js"')
        t=t.replace('href="../../practice.html"','href="../../../practise.html"')
        # Replace GAME metadata exactly. Re-find the marker after all prior text/path edits.
        engine=cfg.get('engine', family)
        newcfg={'title':game_title,'topic':k['name'],'topicId':k['id'],'grade':k['grade'],'difficulty':level_name(k),'engine':engine,'sourceTemplate':src_rel,'knowledgeId':k['id']}
        m2=re.search(r'window\.MATH_GAME=(\{.*?\});</script>',t)
        if m2:
            t=t[:m2.start()] + 'window.MATH_GAME='+json.dumps(newcfg,ensure_ascii=False,separators=(',',':'))+';</script>' + t[m2.end():]
        else:
            raise RuntimeError(f'No GAME config in {src}')
        # Existing game scripts hardcode grade 12 in their AI request. Patch to metadata.
        t=t.replace("{grade:12,topics:[GAME.topicId]", "{grade:GAME.grade,topics:[GAME.topicId]")
        # Ensure game_id is unique and descriptive while keeping the old game logic.
        t=t.replace("game_id:GAME.title", "game_id:`legacy_${GAME.knowledgeId}_${GAME.engine}`")
        # Make level buttons initialize from the knowledge difficulty where source permits.
        t=t.replace("level:'medium'", f"level:'{level_name(k)}'",1)
        filename=f'{idx}-{slug(game_title)}.html'
        target=d/filename
        target.write_text(t,encoding='utf-8')
        manifest.append({'grade':k['grade'],'level':k['level_key'],'knowledge_id':k['id'],'knowledge':k['name'],'game':game_title,'icon':icon,'path':str(target.relative_to(ROOT)).replace('\\','/'),'source_template':src_rel})

# Build mapping function replacement in practise.js
old_start=text.find('    function ensureKnowledgeGames(knowledge) {')
old_end=text.find('\n    /* =====================================================\n       RENDER GAMES', old_start)
assert old_start>=0 and old_end>old_start
new_func='''    function ensureKnowledgeGames(knowledge) {\n        // Each knowledge topic owns three separate HTML game pages.\n        // The pages are cloned from the existing legacy game templates so their\n        // original visual/gameplay interfaces remain the baseline.\n        const gameMap = {\n'''
for k in knowledge:
    family=kind(k); srcs=TEMPLATES[family]
    paths=[]; names=[]; icons=[]
    for src_rel in srcs:
        src=ROOT/src_rel; st=src.read_text(encoding='utf8')
        mm=re.search(r'window\.MATH_GAME=(\{.*?\});</script>',st)
        cfg=json.loads(mm.group(1))
        paths.append(f"games/knowledge/{slug(k['id'])}/{srcs.index(src_rel)+1}-{slug(cfg['title'])}.html")
        names.append(cfg['title']);
        mi=re.search(r'<div class="icon">(.*?)</div>',st,re.S); icons.append(mi.group(1).strip() if mi else '🎮')
    new_func += '            '+json.dumps(k['id'],ensure_ascii=False)+': [' + ', '.join('{name:'+json.dumps(n,ensure_ascii=False)+',icon:'+json.dumps(ic,ensure_ascii=False)+',path:'+json.dumps(p,ensure_ascii=False)+'}' for n,ic,p in zip(names,icons,paths)) + '],\n'
new_func += '''        };\n        const key = String(knowledge?.id || knowledge?.code || '').trim();\n        const games = gameMap[key] || [];\n        return games.map(function (game) {\n            return { name: game.name, icon: game.icon, path: game.path };\n        });\n    }\n'''
newtext=text[:old_start]+new_func+text[old_end:]
PRACT.write_text(newtext,encoding='utf8')

# Keep universal as legacy reference, but explicitly document it is no longer used by practise.
(ROOT/'INDIVIDUAL_GAME_SYSTEM.md').write_text('''# MATH WEB • Individual HTML Game System\n\nEvery one of the 92 knowledge topics now owns 3 separate HTML game pages (276 pages total).\nPractise routes directly to those pages. Each page is cloned from an existing legacy game template, preserving its original HTML/CSS/game UI as the baseline.\nThe Universal Game remains in `games/universal/` as a reference and is not used by the knowledge game buttons.\n''',encoding='utf8')

json.dump(manifest,(ROOT/'games'/'individual-games-manifest.json').open('w',encoding='utf8'),ensure_ascii=False,indent=2)
print('knowledge',len(knowledge),'pages',len(manifest))
print('unique',len({m['path'] for m in manifest}))
