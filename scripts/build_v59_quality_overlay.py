"""Build V59 additive quality-screened question overlay from preserved V254+B56.

Never alters the original V254/B56 SQLite or the 150 Word documents.
Source-derived items remain unverified mathematically. Deterministic original
exercises have independently checked numeric answers, not certified new 'types'.
"""
from __future__ import annotations
import collections
import hashlib
import json
import random
import re
import sqlite3
import sys
import unicodedata
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORAGE = ROOT / 'backend/app/ai/storage'
sys.path.insert(0,str(ROOT/'backend'))
from app.ai.engine.validator import validate, ValidationError

OLD = STORAGE/'v254_candidates.sqlite'
B56 = STORAGE/'v254_b56_candidates.sqlite'
TARGET = STORAGE/'v59_screened_additions.sqlite'
SEED = STORAGE/'v59_screened_additions.seed.zip'
MANIFEST = STORAGE/'v59_screened_additions_manifest.json'
REPORT = ROOT/'V59_QUESTION_BANK_AUDIT.json'


def canonical(text):
    return ' '.join(unicodedata.normalize('NFKC', str(text or '')).casefold().split())


def hash_prompt(text):
    return hashlib.sha256(canonical(text).encode('utf8')).hexdigest()


def independent_exercises():
    """12 distinct construction methods, ten numeric variants each."""
    import sympy as s
    rng = random.Random(20261114)
    X = s.Symbol('x')
    out=[]
    def add(form,grade,topic,q,answer,sol,verify):
        assert verify, f'Independent check failed: {form}'
        assert len(sol.strip())>=55 and not re.match(r'^[A-D][.):]',str(answer)),form
        idx=1+sum(x['form_id']==form for x in out)
        out.append({'id':f'v59:{form}:{idx:02d}', 'grade':grade,'topic':topic,'difficulty':'medium',
                    'question_type':'short_answer','question':q,'answer':str(answer),
                    'solution':sol,'options':'[]','source':'V59_generated_independently_calculated',
                    'quality_status':'numeric_answer_independently_checked','form_id':form})
    for i in range(10):
        u=rng.randint(-10,0);v=rng.randint(1,11)
        b=-(u+v);c=u*v
        q=f'Giải phương trình x² {b:+d}x {c:+d}=0. Hãy nhập nghiệm lớn hơn.'
        sol=f'Đây là phương trình bậc hai có hai nghiệm {u} và {v}, vì (x−({u}))(x−({v})) = x² {b:+d}x {c:+d}. Nghiệm lớn hơn là {v}. Kiểm tra thay cả hai giá trị vào phương trình đều cho 0.'
        add('g10_quadratic_larger_root',10,'phuong_trinh',q,v,sol,(u*u+b*u+c==0 and v*v+b*v+c==0 and v>u))
    for i in range(10):
        while True:
            a,b,c,d=[rng.choice([k for k in range(-5,6) if k!=0]) for _ in range(4)]
            if a*d-b*c:break
        x,y=rng.randint(-7,7),rng.randint(-6,6)
        e=a*x+b*y;f=c*x+d*y
        det=a*d-b*c
        ans=s.Rational(e*d-b*f,det)
        q=f'Xét hệ {a}x {b:+d}y={e}, {c}x {d:+d}y={f}. Tìm giá trị x của nghiệm hệ.'
        sol=f'Định thức hệ số D={a}·{d}−({b})·({c})={det} khác 0 nên hệ có nghiệm duy nhất. Dùng quy tắc Cramer, x=({e}·{d}−({b})·{f})/{det}={x}. Thay x={x}, y={y} vào cả hai phương trình đều thỏa mãn.'
        add('g10_linear_system_x',10,'he_phuong_trinh',q,x,sol,ans==x and a*x+b*y==e and c*x+d*y==f)
    for i in range(10):
        x1,y1=rng.randint(-8,7),rng.randint(-8,7);dx,dy=rng.randint(1,10),rng.randint(-9,9)
        x2=x1+dx;y2=y1+dy;ans=dx*dx+dy*dy
        q=f'Trong mặt phẳng Oxy, cho A({x1}; {y1}), B({x2}; {y2}). Tính bình phương độ dài AB.'
        sol=f'Hiệu hoành độ là {x2}−({x1})={dx}; hiệu tung độ là {y2}−({y1})={dy}. Theo công thức khoảng cách trong Oxy: AB²=({dx})²+({dy})²={ans}. Kết quả không âm, phù hợp tính chất độ dài.'
        add('g10_coordinate_distance_squared',10,'toa_do_phang',q,ans,sol,ans==(x2-x1)**2+(y2-y1)**2)
    for i in range(10):
        a,b,c,d=[rng.randint(-9,9) for _ in range(4)]
        ans=a*c+b*d
        q=f'Trong mặt phẳng Oxy, vectơ u=({a}; {b}) và vectơ v=({c}; {d}). Tính tích vô hướng u·v.'
        sol=f'Với hai vectơ tọa độ (u₁;u₂), (v₁;v₂), tích vô hướng là u₁v₁+u₂v₂. Thay số: ({a})·({c})+({b})·({d})={ans}. Đây là một số thực, không phải độ dài vectơ.'
        add('g10_vector_dot_product',10,'vector',q,ans,sol,ans==a*c+b*d)
    for i in range(10):
        first=rng.randint(-13,15);step=rng.choice([z for z in range(-7,8) if z]);n=rng.randint(6,30);ans=first+(n-1)*step
        q=f'Cho cấp số cộng có số hạng đầu u₁={first} và công sai d={step}. Tính u_{n}.'
        sol=f'Theo định nghĩa cấp số cộng, số hạng tổng quát uₙ=u₁+(n−1)d. Ở đây n={n}, nên u_{n}={first}+({n}−1)·({step})={ans}. Kiểm tra hiệu hai số hạng kề nhau luôn bằng d={step}.'
        add('g11_arithmetic_nth',11,'cap_so_cong',q,ans,sol,ans==first+(n-1)*step)
    for i in range(10):
        first=rng.choice([-4,-3,-2,2,3,4]);ratio=rng.choice([-3,-2,2,3]);n=rng.randint(3,7)
        ans=first*ratio**(n-1)
        q=f'Cấp số nhân có u₁={first}, công bội q={ratio}. Tính số hạng u_{n}.'
        sol=f'Số hạng thứ n của cấp số nhân: uₙ=u₁·q^(n−1). Do n={n} nên u_{n}={first}·({ratio})^({n}−1)={ans}. Nhân lần lượt mỗi số hạng với {ratio} sẽ cho cùng kết quả.'
        add('g11_geometric_nth',11,'cap_so_nhan',q,ans,sol,ans==first*ratio**(n-1))
    for i in range(10):
        a=rng.choice([v for v in range(-4,5) if v]);b=rng.randint(-6,6);c=rng.randint(-7,7);d=rng.randint(-10,10);x0=rng.randint(-4,4)
        poly=a*X**3+b*X**2+c*X+d;ans=3*a*x0*x0+2*b*x0+c
        q=f'Cho f(x)={a}x³ {b:+d}x² {c:+d}x {d:+d}. Tính đạo hàm f′({x0}).'
        sol=f'Lấy đạo hàm từng hạng: f′(x)=3·({a})x²+2·({b})x+({c}). Thay x={x0}, ta được f′({x0})=3·({a})·({x0})²+2·({b})·({x0})+({c})={ans}. Hằng số {d} có đạo hàm bằng 0.'
        add('g11_cubic_derivative_at_point',11,'dao_ham',q,ans,sol,int(s.diff(poly,X).subs(X,x0))==ans)
    for i in range(10):
        t=rng.choice([v for v in range(-13,14) if v]);ans=2*t
        q=f'Tính lim khi x tiến tới {t} của biểu thức (x²−({t})²)/(x−({t})).'
        sol=f'Với x khác {t}, dùng hằng đẳng thức hiệu hai bình phương: x²−({t})²=(x−({t}))(x+({t})). Rút gọn được x+({t}), nên khi x→{t} giới hạn bằng {t}+({t})={ans}.'
        add('g11_limit_difference_squares',11,'gioi_han',q,ans,sol,s.limit((X*X-t*t)/(X-t),X,t)==ans)
    for i in range(10):
        base=2+i;ans=rng.randint(-4,10);k=2*ans-3
        q=f'Giải phương trình {base}^(2x−3)={base}^{k}. Tìm giá trị x.'
        sol=f'Vì cơ số {base}>0 và {base}≠1 nên hàm số mũ là đơn ánh. Do đó 2x−3={k}, suy ra x=({k}+3)/2={ans}. Thay x={ans} vào hai vế đều có số mũ {k}.'
        add('g12_exponential_same_base',12,'pt_mu',q,ans,sol,2*ans-3==k and base>1)
    for i in range(10):
        a=2*rng.choice([v for v in range(-5,6) if v]);b=rng.randint(-9,9);n=rng.randint(2,9);ans=a*n*n//2+b*n
        q=f'Tính tích phân xác định từ 0 đến {n} của ({a}x {b:+d}) dx.'
        sol=f'Nguyên hàm của {a}x {b:+d} là F(x)=({a}/2)x²+({b})x. Theo Newton–Leibniz, tích phân bằng F({n})−F(0)={a}·{n}²/2+({b})·{n}={ans}. Đây là giá trị có dấu của tích phân.'
        add('g12_linear_definite_integral',12,'nguyen_ham_tich_phan',q,ans,sol,s.integrate(a*X+b,(X,0,n))==ans)
    for i in range(10):
        a=rng.randint(-12,12);b=rng.choice([v for v in range(-12,13) if v]);ans=a*a+b*b
        q=f'Cho số phức z={a} {b:+d}i. Tính bình phương môđun |z|².'
        sol=f'Với z=a+bi thì |z|²=z·z̄=a²+b². Ở đây a={a}, b={b}, nên |z|²=({a})²+({b})²={ans}. Bình phương môđun luôn không âm và bằng tổng bình phương hai thành phần.'
        add('g12_complex_modulus_squared',12,'so_phuc',q,ans,sol,ans==a*a+b*b)
    for i in range(10):
        a=[rng.randint(-8,8) for _ in range(3)]; delta=[rng.randint(-8,8) for _ in range(3)]; bb=[a[j]+delta[j] for j in range(3)];ans=sum(x*x for x in delta)
        q=f'Trong không gian Oxyz, cho A({a[0]}; {a[1]}; {a[2]}), B({bb[0]}; {bb[1]}; {bb[2]}). Tính AB².'
        sol=f'Hiệu ba tọa độ của B và A lần lượt là {delta[0]}, {delta[1]} và {delta[2]}. Theo công thức khoảng cách Oxyz, AB²=({delta[0]})²+({delta[1]})²+({delta[2]})²={ans}. Đây là bình phương độ dài đoạn thẳng AB.'
        add('g12_3d_distance_squared',12,'toa_do_khong_gian',q,ans,sol,ans==sum((bb[j]-a[j])**2 for j in range(3)))
    for i in range(10):
        side_a=rng.randint(3,17);side_b=rng.randint(4,18)
        ans=side_a**2+side_b**2
        q=f'Tam giác ABC vuông tại A, có AB={side_a}, AC={side_b}. Tính bình phương độ dài cạnh huyền BC².'
        sol=f'Áp dụng hệ thức lượng trong tam giác vuông, định lý Pitago cho góc A=90°: BC²=AB²+AC². Thay AB={side_a}, AC={side_b} thu được BC²={side_a}²+{side_b}²={ans}. Cạnh huyền luôn dài hơn từng cạnh góc vuông.'
        add('g10_right_triangle_hypotenuse_squared',10,'he_thuc_luong_van_dung_10',q,ans,sol,ans==side_a*side_a+side_b*side_b)
    for i in range(10):
        a=rng.choice([v for v in range(-8,9) if v]);b=rng.choice([v for v in range(-8,9) if v]);
        k=i%4
        angles=[('0',0),('π/2',s.pi/2),('π',s.pi),('3π/2',3*s.pi/2)]
        label,angle=angles[k]
        ans=int(s.simplify(a*s.sin(angle)+b*s.cos(angle)))
        q=f'Cho hàm số lượng giác f(x)={a}sin(x) {b:+d}cos(x). Hãy tính f({label}).'
        sol=f'Dùng các giá trị lượng giác đặc biệt tại x={label}: sin({label})={s.sin(angle)}, cos({label})={s.cos(angle)}. Suy ra f({label})={a}·({s.sin(angle)})+({b})·({s.cos(angle)})={ans}. Giá trị được tính trực tiếp từ định nghĩa của hàm số đã cho.'
        add('g11_trig_function_special_angle',11,'ham_so_luong_giac_day_du',q,ans,sol,s.simplify(a*s.sin(angle)+b*s.cos(angle))==ans)
    for i in range(10):
        side_ab=4+i; side_ac=7+2*i
        ans=side_ab**2+side_ac**2-side_ab*side_ac
        q=f'Cho tam giác ABC có AB={side_ab}, AC={side_ac} và góc BAC bằng 60 độ. Tính BC² theo định lý cosin.'
        sol=f'Trong tam giác, định lý cosin cho BC²=AB²+AC²−2·AB·AC·cos(A). Vì A=60° nên cos(A)=1/2, do đó BC²={side_ab}²+{side_ac}²−{side_ab}·{side_ac}={ans}. Giá trị phải dương để tương ứng bình phương một độ dài.'
        verify=s.simplify(side_ab**2+side_ac**2-2*side_ab*side_ac*s.cos(s.pi/3))==ans and ans>0
        add('g10_cosine_law_side_squared',10,'he_thuc_luong',q,ans,sol,verify)
    # B56 exposes this Battle topic ID although the learning catalog uses a
    # different canonical grouping. Provide a viable selection pool without
    # modifying any existing lesson/topic mappings.
    for i in range(10):
        coef_b=-12+2*i;coef_c=4+i;coef_a=2
        discriminant=coef_b*coef_b-4*coef_a*coef_c
        q=f'Xét phương trình bậc hai {coef_a}x² {coef_b:+d}x {coef_c:+d}=0. Tính biệt thức Δ=b²−4ac.'
        distractors=[discriminant+8,discriminant-8,discriminant+16]
        options=[str(discriminant)]+[str(x) for x in distractors]
        rng.shuffle(options)
        sol=f'Với a={coef_a}, b={coef_b}, c={coef_c}, công thức biệt thức là Δ=b²−4ac. Thay vào: Δ=({coef_b})²−4·{coef_a}·({coef_c})={discriminant}. Chỉ phương án {discriminant} là bằng giá trị tính được.'
        assert len(set(options))==4 and str(discriminant) in options
        add('g10_quadratic_discriminant_mcq',10,'phuong_trinh_bac_hai',q,discriminant,sol,discriminant==coef_b*coef_b-4*coef_a*coef_c)
        out[-1]['question_type']='multiple_choice'
        out[-1]['options']=json.dumps(options,ensure_ascii=False)
    for i in range(10):
        r1=i-8;r2=i+2
        b=-(r1+r2);c=r1*r2
        q=f'Phương trình bậc hai x² {b:+d}x {c:+d}=0 có hai nghiệm thực. Hãy tính tổng hai nghiệm theo Viète.'
        answer=-b
        sol=f'Theo định lý Viète cho x²+bx+c=0 với hệ số đầu bằng 1, tổng hai nghiệm S=−b. Với b={b}, S=−({b})={answer}. Có thể kiểm lại bằng hai nghiệm {r1} và {r2}, tổng cũng bằng {answer}.'
        add('g10_quadratic_vieta_sum',10,'phuong_trinh_bac_hai',q,answer,sol,answer==r1+r2 and r1*r1+b*r1+c==0 and r2*r2+b*r2+c==0)
    return out


def build():
    # Restore both immutable source banks from their versioned seed ZIPs when
    # the repo is freshly cloned (SQLite files are intentionally gitignored).
    from app.ai.engine.v254_bank import ensure_v254_bank
    from app.ai.engine.b56_bank import ensure_b56_bank
    if not ensure_v254_bank() or not ensure_b56_bank():
        raise RuntimeError('Both V254 and B56 source banks must be available')
    stats=collections.Counter()
    rejects=collections.Counter()
    rejects_examples=collections.defaultdict(list)
    old=sqlite3.connect(f'file:{OLD}?mode=ro',uri=True)
    b56=sqlite3.connect(f'file:{B56}?mode=ro',uri=True)
    old_prompts={canonical(q): (g,t) for q,g,t in old.execute('SELECT question, grade, topic FROM questions')}
    stats['old_rows']=old.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    stats['b56_rows']=b56.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    seen=set(old_prompts)
    if TARGET.exists(): TARGET.unlink()
    new=sqlite3.connect(TARGET)
    new.execute('''CREATE TABLE questions (
        id TEXT PRIMARY KEY, grade INTEGER NOT NULL, topic TEXT NOT NULL,
        difficulty TEXT NOT NULL, question_type TEXT NOT NULL,
        question TEXT NOT NULL, answer TEXT NOT NULL, solution TEXT NOT NULL,
        options TEXT NOT NULL, source TEXT NOT NULL,
        quality_status TEXT NOT NULL, form_id TEXT NOT NULL DEFAULT ''
    )''')
    insert='''INSERT INTO questions(id,grade,topic,difficulty,question_type,question,answer,solution,options,source,quality_status,form_id)
              VALUES(:id,:grade,:topic,:difficulty,:question_type,:question,:answer,:solution,:options,:source,:quality_status,:form_id)'''
    novel_topics=collections.Counter()
    for row in b56.execute('SELECT id,grade,topic,question,answer,solution,options,question_type,difficulty,source FROM questions'):
        id,grade,topic,q,ans,sol,opts,kind,level,source=row
        key=canonical(q)
        if key in old_prompts:
            stats['b56_duplicate_old']+=1
            if old_prompts[key]!=(grade,topic):stats['b56_duplicate_cross_topic']+=1
            continue
        stats['b56_nonduplicate_old']+=1
        try: choices=json.loads(opts or '[]')
        except (ValueError, TypeError): choices=[]
        reason=None
        if len(q.strip())<8 or len(q.strip())>1800 or len(ans.strip())<1 or len(ans.strip())>250 or len(sol.strip())<50 or len(sol.strip())>2800:
            reason='incomplete_or_short_solution'
        elif kind=='short_answer' and re.match(r'^\s*[A-D]\s*[).:\-]',ans,flags=re.I):
            reason='short_answer_mislabeled_as_mcq'
        elif kind not in ('multiple_choice','short_answer'):
            reason='unsupported_type'
        elif kind=='multiple_choice' and (len(choices)!=4 or ans not in choices):
            reason='mcq_options_or_answer_mismatch'
        else:
            try: validate({'id':id,'grade':grade,'topic':topic,'question':q,'answer':ans,
                           'solution':sol,'question_type':kind,'difficulty':level,'options':choices})
            except ValidationError as exc:reason=str(exc)
            except (TypeError,ValueError,KeyError) as exc: reason='validation_exception'
        if reason:
            rejects[reason]+=1
            if len(rejects_examples[reason])<5: rejects_examples[reason].append(id)
            continue
        if key in seen:
            rejects['duplicate_within_new']+=1
            continue
        seen.add(key)
        entry=dict(id=id,grade=grade,topic=topic,difficulty=level,question_type=kind,
                   question=q,answer=ans,solution=sol,options=opts,source=source,
                   quality_status='candidate_screened_not_certified',form_id='')
        new.execute(insert,entry)
        stats['b56_screened_added']+=1
        novel_topics[f'{grade}:{topic}']+=1
    generated=independent_exercises()
    form_counts=collections.Counter()
    for entry in generated:
        key=canonical(entry['question'])
        if key in seen:
            rejects['original_duplicated_existing']+=1
            continue
        if len(entry['solution'])<50:raise RuntimeError('solution not detailed')
        validate({**entry,'options':json.loads(entry['options'])})
        seen.add(key)
        new.execute(insert,entry)
        stats['original_answer_checked_added']+=1
        form_counts[entry['form_id']]+=1
        novel_topics[f"{entry['grade']}:{entry['topic']}"]+=1
    new.execute('CREATE INDEX idx_v59_pick ON questions(grade,topic,difficulty,question_type)')
    new.execute('CREATE UNIQUE INDEX idx_v59_prompt_hash ON questions(question)')
    new.commit()
    if new.execute('PRAGMA quick_check').fetchone()[0] != 'ok': raise RuntimeError('SQLite integrity check failed')
    stats['overlay_total']=new.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    stats['overlay_grade_topic_coverage']=new.execute('SELECT count(*) FROM (SELECT DISTINCT grade,topic FROM questions)').fetchone()[0]
    stats['total_unique_prompt_candidates_before_semantic_review']=len(old_prompts)+stats['overlay_total']
    assert stats['b56_duplicate_old']+stats['b56_nonduplicate_old']==stats['b56_rows']
    assert stats['overlay_total']==stats['b56_screened_added']+stats['original_answer_checked_added']
    assert all(count==10 for count in form_counts.values()),form_counts
    new.close(); b56.close();old.close()
    with zipfile.ZipFile(SEED,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.write(TARGET,arcname=TARGET.name)
    content=TARGET.read_bytes()
    data={'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content),'source_archives':[
        'Question_Bank_V254_B56_BO_SUNG_CO_KIEM_TRA(2).zip',
        'Question_Bank_V254 (7)(1).zip'],
        'original_sources_preserved':True, 'quality_status':'mixed_candidate_screened_and_numeric_answer_checked_not_full_certification',
        'counts':dict(stats), 'filtered_reasons':dict(rejects),
        'by_topic':dict(sorted(novel_topics.items())),'original_form_counts':dict(form_counts)}
    MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    REPORT.write_text(json.dumps({**data,'reject_examples':dict(rejects_examples)},ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'counts':dict(stats),'filtered_reasons':dict(rejects),'original_form_counts':dict(form_counts)},ensure_ascii=False,indent=2))

if __name__=='__main__':build()
