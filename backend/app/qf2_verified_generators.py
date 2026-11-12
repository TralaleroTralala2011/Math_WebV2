"""Small, deterministic, auditable Question Factory generators.

These return *candidate* forms. Every arithmetic answer is recomputed from the
parameters. Changing numeric inputs yields exercises, never independent types.
Publication still requires independent review in question_factory_v2_routes.
"""
from __future__ import annotations

from math import isqrt

TIERS = ['nền tảng'] * 4 + ['trung cấp'] * 3 + ['nâng cao'] * 3


def _integer_options(correct: int):
    return [str(correct), str(correct + 1), str(correct - 2), str(correct + 3)]


def _complex(real: int, imag: int):
    if imag == 0:
        return str(real)
    return f'{real}{"+" if imag >= 0 else "-"}{abs(imag)}i'


def _complex_options(a: int, b: int):
    return [_complex(a,b), _complex(a+1,b), _complex(a,b+1), _complex(a-2,b-1)]


def _form(*, grade, topic_id, title, concept, method, conditions, distinguishing, instances):
    assert len(instances) == 10, title
    questions = []
    for i, (prompt, correct, explanation, options) in enumerate(instances):
        assert len(set(options)) == 4 and options[0] == correct
        assert len(explanation) >= 24
        if i < 7:
            shift = i % 4
            choices = options[shift:] + options[:shift]
            question_type = 'multiple_choice'
            answer = correct
            correct_index = choices.index(correct)
            question = prompt
        elif i < 9:
            question_type, choices, correct_index = 'written', [], None
            question, answer = prompt, correct
        else:
            # The final item is a mathematically checked true/false statement.
            claim = correct if sum(ord(ch) for ch in prompt) % 2 == 0 else options[1]
            truth = claim == correct
            question = f'{prompt} Khẳng định đáp án là {claim}. Đúng hay sai?'
            answer = 'Đúng' if truth else 'Sai'
            explanation += (' Khẳng định là đúng.' if truth else f' Khẳng định là sai; kết quả đúng phải là {correct}.')
            question_type, choices, correct_index = 'true_false', [], None
        questions.append({'question':question,'question_type':question_type,
                          'difficulty':TIERS[i],'choices':choices,'correct_index':correct_index,
                          'answer':answer,'explanation':explanation})
    return {'grade':grade,'topic_id':topic_id,'title':title,'concept':concept,
            'method':method,'conditions':conditions,'distinguishing':distinguishing,
            'questions':questions}


def quadratic_evaluation():
    params=[(1,2,3,1),(2,1,-1,2),(-1,3,2,1),(1,-2,4,3),
            (3,2,-5,-2),(-2,3,1,3),(2,-4,6,-3),(4,-3,5,4),
            (-3,5,-7,-4),(5,-6,8,5)]
    items=[]
    for a,b,c,x in params:
        y=a*x*x+b*x+c
        assert y == a*(x**2)+b*x+c
        items.append((f'Cho f(x)={a}x²+({b})x+({c}). Tính f({x}).',str(y),
                      f'Thay x={x} vào biểu thức: f({x})={a}×({x})²+({b})×({x})+({c})={y}.',_integer_options(y)))
    return _form(grade=10,topic_id='ham_so_bac_hai',title='Tính giá trị hàm số bậc hai tại một điểm',
                 concept='Giá trị f(x0) của đa thức bậc hai',method='Thay trực tiếp hoành độ x0 vào ax²+bx+c và tính đúng thứ tự phép toán',
                 conditions='a khác 0, hệ số và x0 nguyên',distinguishing='Tính giá trị tại một điểm, không tìm đỉnh hay nghiệm phương trình',instances=items)


def quadratic_root_count():
    params=[(1,0,-4),(1,2,1),(1,0,4),(2,0,-8),(2,4,2),
            (-1,2,-3),(3,-6,2),(2,-8,8),(3,2,5),(-2,3,4)]
    items=[]
    for a,b,c in params:
        d=b*b-4*a*c
        count=2 if d>0 else (1 if d==0 else 0)
        assert (count==2 and d>0) or (count==1 and d==0) or (count==0 and d<0)
        options=['0','1','2','Vô số']
        items.append((f'Phương trình {a}x²+({b})x+({c})=0 có bao nhiêu nghiệm thực phân biệt?',str(count),
                      f'Vì a={a} khác 0, biệt thức Δ=b²−4ac=({b})²−4×({a})×({c})={d}. '
                      f'Suy ra phương trình có {count} nghiệm thực phân biệt.',[str(count)]+[x for x in options if x!=str(count)]))
    return _form(grade=10,topic_id='ham_so_bac_hai',title='Xác định số nghiệm thực bằng dấu của biệt thức',
                 concept='Số nghiệm thực phân biệt của phương trình bậc hai',
                 method='Tính biệt thức Δ=b²−4ac và phân biệt các trường hợp Δ âm, bằng không, dương',
                 conditions='Phương trình ax²+bx+c=0, a khác 0',
                 distinguishing='Phân loại số nghiệm thực, khác việc tính f(x) hay tọa độ đỉnh',instances=items)


def arithmetic_nth():
    params=[(2,3,4),(1,4,5),(5,2,6),(-2,3,4),(7,-1,5),
            (3,5,8),(-4,2,10),(8,-3,9),(-7,4,12),(11,-5,15)]
    items=[]
    for u,d,n in params:
        v=u+(n-1)*d
        items.append((f'Cấp số cộng có u₁={u}, công sai d={d}. Tính u_{n}.',str(v),
                      f'Áp dụng uₙ=u₁+(n−1)d: u_{n}={u}+({n}−1)×({d})={v}.',_integer_options(v)))
    return _form(grade=11,topic_id='cap_so_cong',title='Tìm số hạng thứ n của cấp số cộng',
                 concept='Công thức số hạng tổng quát của cấp số cộng',
                 method='Thay u₁, công sai d và chỉ số n vào uₙ=u₁+(n−1)d',
                 conditions='n nguyên dương, công sai và số hạng đầu nguyên',
                 distinguishing='Tìm một số hạng cụ thể, không phải tổng n số hạng hay suy ra công sai',instances=items)


def arithmetic_sum():
    params=[(1,2,5),(2,3,4),(5,1,6),(-1,4,5),(7,-2,7),
            (3,5,8),(-4,2,10),(8,-3,9),(-7,4,12),(11,-5,15)]
    items=[]
    for u,d,n in params:
        numerator=n*(2*u+(n-1)*d)
        assert numerator%2==0
        total=numerator//2
        items.append((f'Cấp số cộng có u₁={u}, d={d}. Tính tổng {n} số hạng đầu S_{n}.',str(total),
                      f'Áp dụng Sₙ=n[2u₁+(n−1)d]/2: S_{n}={n}×[2×({u})+({n}−1)×({d})]/2={total}.',_integer_options(total)))
    return _form(grade=11,topic_id='cap_so_cong',title='Tính tổng n số hạng đầu của cấp số cộng',
                 concept='Tổng n số hạng đầu của cấp số cộng',
                 method='Áp dụng công thức Sₙ=n(2u₁+(n−1)d)/2 và rút gọn',
                 conditions='n nguyên dương, cấp số cộng có số hạng đầu và công sai nguyên',
                 distinguishing='Tính tổng dãy, khác tìm số hạng uₙ hoặc tìm công sai',instances=items)


def arithmetic_difference():
    params=[(2,3,2,5),(1,4,3,7),(5,2,1,6),(-2,3,4,9),(7,-1,2,8),
            (3,5,5,11),(-4,2,6,13),(8,-3,2,10),(-7,4,3,12),(11,-5,7,15)]
    items=[]
    for u,d,p,q in params:
        up=u+(p-1)*d;uq=u+(q-1)*d
        assert q>p and (uq-up)//(q-p)==d and (uq-up)%(q-p)==0
        items.append((f'Cấp số cộng có u_{p}={up} và u_{q}={uq}. Tìm công sai d.',str(d),
                      f'Ta có u_{q}−u_{p}=({q}−{p})d, nên d=({uq}−({up}))/({q}−{p})={d}.',_integer_options(d)))
    return _form(grade=11,topic_id='cap_so_cong',title='Suy ra công sai từ hai số hạng bất kỳ',
                 concept='Quan hệ hiệu hai số hạng trong cấp số cộng',
                 method='Lấy (u_q−u_p)/(q−p) để suy ra công sai d',
                 conditions='p và q nguyên dương, p nhỏ hơn q, các số hạng thuộc cùng cấp số cộng',
                 distinguishing='Suy ra tham số công sai từ dữ kiện gián tiếp, không tính uₙ hoặc Sₙ',instances=items)


def complex_add():
    params=[(1,2,3,4),(2,-1,4,3),(-3,2,5,-1),(4,-5,-2,3),
            (5,6,-3,-2),(-7,4,2,-6),(8,-3,-5,7),(-4,-8,6,9),
            (12,-7,-9,5),(-11,10,8,-12)]
    items=[]
    for a,b,c,d in params:
        real=a+c;imag=b+d
        answer=_complex(real,imag)
        assert complex(a,b)+complex(c,d)==complex(real,imag)
        items.append((f'Cho z₁={_complex(a,b)}, z₂={_complex(c,d)}. Tính z₁+z₂.',answer,
                      f'Cộng từng phần thực và ảo: z₁+z₂=({a}+({c}))+({b}+({d}))i={answer}.',_complex_options(real,imag)))
    return _form(grade=12,topic_id='so_phuc',title='Cộng hai số phức ở dạng đại số',
                 concept='Phép cộng hai số phức a+bi',method='Cộng phần thực với phần thực, phần ảo với phần ảo',
                 conditions='Các hệ số thực và ảo nguyên, i²=−1',
                 distinguishing='Phép cộng số phức, khác phép nhân và phép tính môđun',instances=items)


def complex_multiply():
    params=[(1,2,3,4),(2,-1,4,3),(-3,2,5,-1),(4,-5,-2,3),
            (5,6,-3,-2),(-7,4,2,-6),(8,-3,-5,7),(-4,-8,6,9),
            (12,-7,-9,5),(-11,10,8,-12)]
    items=[]
    for a,b,c,d in params:
        real=a*c-b*d;imag=a*d+b*c
        answer=_complex(real,imag)
        assert complex(a,b)*complex(c,d)==complex(real,imag)
        items.append((f'Cho z₁={_complex(a,b)}, z₂={_complex(c,d)}. Tính z₁×z₂.',answer,
                      f'Nhân và dùng i²=−1: phần thực={a}×({c})−({b})×({d})={real}; '
                      f'phần ảo={a}×({d})+({b})×({c})={imag}; kết quả {answer}.',_complex_options(real,imag)))
    return _form(grade=12,topic_id='so_phuc',title='Nhân hai số phức bằng khai triển đại số',
                 concept='Phép nhân hai số phức a+bi',method='Khai triển tích rồi thay i²=−1, gom phần thực và phần ảo',
                 conditions='Các hệ số nguyên, i²=−1',
                 distinguishing='Phép nhân số phức, khác phép cộng và môđun',instances=items)


def complex_modulus():
    params=[(3,4),(5,12),(8,15),(7,24),(20,21),(-3,4),
            (9,12),(-10,-24),(15,-20),(-12,35)]
    items=[]
    for a,b in params:
        square=a*a+b*b;mod=isqrt(square)
        assert mod*mod==square
        items.append((f'Cho số phức z={_complex(a,b)}. Tính môđun |z|.',str(mod),
                      f'Theo công thức |a+bi|=√(a²+b²), |z|=√(({a})²+({b})²)=√{square}={mod}.',_integer_options(mod)))
    return _form(grade=12,topic_id='so_phuc',title='Tính môđun số phức theo định lý Pythagore',
                 concept='Môđun |a+bi| của số phức',method='Áp dụng |z|=√(a²+b²) và khai căn không âm',
                 conditions='Số phức có phần thực và ảo nguyên, môđun không âm',
                 distinguishing='Tính độ dài vectơ biểu diễn số phức, không phải cộng hoặc nhân',instances=items)




def _set_text(values):
    return '{' + ', '.join(str(v) for v in sorted(values)) + '}'


def set_intersection():
    """Original, arithmetic-checked questions on A intersection B."""
    instances=[]
    for n in range(1,11):
        a={n,n+1,n+3};b={n+1,n+2,n+4}
        intersection=a & b
        assert intersection=={n+1} and len(a-b)==2 and len(b-a)==2
        correct=_set_text(intersection)
        options=[correct,_set_text(a|b),_set_text(a-b),_set_text(b-a)]
        instances.append((f'Cho A={_set_text(a)} và B={_set_text(b)}. Tìm A∩B.',
                          correct,
                          f'Giao A∩B chỉ chứa phần tử thuộc cả A và B. '
                          f'Đối chiếu hai tập hợp, chỉ có {n+1} xuất hiện ở cả hai; A∩B={correct}.',
                          options))
    return _form(grade=10,topic_id='tap_hop',title='Tìm giao hai tập hợp hữu hạn',
                 concept='Phép giao A∩B của hai tập hợp hữu hạn',
                 method='So sánh từng phần tử và giữ lại các phần tử đồng thời thuộc A và B',
                 conditions='Hai tập hữu hạn, phần tử là các số nguyên khác nhau',
                 distinguishing='Giao chỉ giữ phần tử chung, không phải hợp hoặc hiệu hai tập hợp',instances=instances)


def set_union():
    instances=[]
    for n in range(2,12):
        a={n,n+1,n+3};b={n+1,n+2,n+4}
        union=a|b
        correct=_set_text(union)
        options=[correct,_set_text(a&b),_set_text(a),_set_text(b)]
        assert len(set(options))==4
        instances.append((f'Cho A={_set_text(a)} và B={_set_text(b)}. Tìm A∪B.',
                          correct,
                          f'Hợp A∪B chứa các phần tử thuộc A hoặc B. '
                          f'Gộp các phần tử rồi bỏ {n+1} bị lặp, được A∪B={correct}.',options))
    return _form(grade=10,topic_id='tap_hop',title='Tìm hợp hai tập hợp hữu hạn',
                 concept='Phép hợp A∪B của hai tập hợp hữu hạn',
                 method='Gộp các phần tử của hai tập hợp và loại phần tử trùng lặp',
                 conditions='Hai tập hữu hạn, phần tử là các số nguyên khác nhau',
                 distinguishing='Hợp lấy tất cả phần tử của cả hai tập, khác giao hoặc hiệu',instances=instances)


def geometric_nth():
    params=[(1,2,4),(2,3,3),(-1,2,5),(3,-2,4),(2,2,6),
            (-2,3,4),(5,-2,3),(1,3,5),(4,2,5),(-3,-2,4)]
    instances=[]
    for u,q,n in params:
        answer=u*q**(n-1)
        assert answer==u*__import__('functools').reduce(lambda a,b:a*b,[q]*(n-1),1)
        instances.append((f'Cấp số nhân có u₁={u}, công bội q={q}. Tính u_{n}.',str(answer),
                          f'Số hạng tổng quát là uₙ=u₁q^(n−1). '
                          f'Thay u₁={u}, q={q}, n={n}: u_{n}={u}×({q})^{n-1}={answer}.',
                          _integer_options(answer)))
    return _form(grade=11,topic_id='cap_so_nhan',title='Tính số hạng tổng quát của cấp số nhân',
                 concept='Số hạng thứ n của cấp số nhân có công bội q',
                 method='Dùng uₙ=u₁q^(n−1) và tính lũy thừa trước khi nhân',
                 conditions='n nguyên dương, công bội và số hạng đầu nguyên',
                 distinguishing='Tính một số hạng của cấp số nhân, không phải tổng n số hạng',instances=instances)


def geometric_sum():
    params=[(1,2,4),(2,3,3),(-1,2,5),(3,-2,4),(2,2,6),
            (-2,3,4),(5,-2,3),(1,3,5),(4,2,5),(-3,-2,4)]
    instances=[]
    for u,q,n in params:
        answer=sum(u*q**k for k in range(n))
        assert q!=1 and answer*(q-1)==u*(q**n-1)
        instances.append((f'Cấp số nhân có u₁={u}, công bội q={q}. Tính tổng {n} số hạng đầu S_{n}.',str(answer),
                          f'Vì q={q} khác 1, Sₙ=u₁(q^n−1)/(q−1). '
                          f'Thay vào: S_{n}={u}×(({q})^{n}−1)/({q}−1)={answer}.',
                          _integer_options(answer)))
    return _form(grade=11,topic_id='cap_so_nhan',title='Tính tổng n số hạng đầu cấp số nhân',
                 concept='Tổng hữu hạn của cấp số nhân có công bội khác 1',
                 method='Dùng Sₙ=u₁(q^n−1)/(q−1), kiểm tra q khác 1',
                 conditions='n nguyên dương, q khác 1, u₁ và q nguyên',
                 distinguishing='Tổng cấp số nhân, không phải tính riêng uₙ',instances=instances)


def tangent_slope():
    params=[(1,2,3,1),(2,-3,1,2),(-1,4,0,3),(3,-2,5,-1),(2,5,-3,0),
            (-2,1,4,2),(1,-4,2,-2),(3,3,1,1),(-3,2,-1,-1),(4,-1,3,2)]
    instances=[]
    for a,b,c,x in params:
        m=2*a*x+b
        assert abs(((a*(x+1e-5)**2+b*(x+1e-5)+c)-(a*x*x+b*x+c))/1e-5-m)<0.001
        instances.append((f'Cho f(x)={a}x²+({b})x+({c}). Tính hệ số góc tiếp tuyến tại x₀={x}.',str(m),
                          f'Đạo hàm f′(x)=2×({a})x+({b}). '
                          f'Tại x₀={x}, hệ số góc là f′({x})=2×({a})×({x})+({b})={m}.',
                          _integer_options(m)))
    return _form(grade=12,topic_id='tiep_tuyen',title='Tìm hệ số góc tiếp tuyến parabol',
                 concept='Hệ số góc tiếp tuyến bằng đạo hàm tại tiếp điểm',
                 method='Lấy đạo hàm f′(x)=2ax+b rồi tính f′(x₀)',
                 conditions='Hàm đa thức bậc hai với a khác 0, tiếp điểm có hoành độ cho trước',
                 distinguishing='Chỉ tìm hệ số góc, không yêu cầu phương trình tiếp tuyến',instances=instances)


def tangent_equation():
    params=[(1,2,3,1),(2,-3,1,2),(-1,4,0,3),(3,-2,5,-1),(2,5,-3,0),
            (-2,1,4,2),(1,-4,2,-2),(3,3,1,1),(-3,2,-1,-1),(4,-1,3,2)]
    instances=[]
    for a,b,c,x in params:
        y=a*x*x+b*x+c;m=2*a*x+b;k=y-m*x
        assert m*x+k==y
        correct=f'y={m}x+({k})'
        options=[correct,f'y={m+1}x+({k})',f'y={m}x+({k+1})',f'y={m-1}x+({k-2})']
        instances.append((f'Cho f(x)={a}x²+({b})x+({c}). Viết phương trình tiếp tuyến tại x₀={x}.',correct,
                          f'Điểm tiếp xúc M({x};{y}); hệ số góc m=f′({x})=2×({a})×({x})+({b})={m}. '
                          f'Từ y−{y}={m}(x−({x})), suy ra y={m}x+({k}).',options))
    return _form(grade=12,topic_id='tiep_tuyen',title='Lập phương trình tiếp tuyến tại một điểm',
                 concept='Phương trình tiếp tuyến y−f(x₀)=f′(x₀)(x−x₀)',
                 method='Tính tung độ tiếp điểm, đạo hàm tại x₀ và thay vào công thức tiếp tuyến',
                 conditions='Hàm đa thức bậc hai, a khác 0, hoành độ tiếp điểm cho trước',
                 distinguishing='Xác định toàn bộ phương trình tiếp tuyến, không chỉ hệ số góc',instances=instances)


GENERATORS = {
    'quadratic-evaluation': quadratic_evaluation,
    'quadratic-root-count': quadratic_root_count,
    'arithmetic-nth': arithmetic_nth,
    'arithmetic-sum': arithmetic_sum,
    'arithmetic-difference': arithmetic_difference,
    'complex-add': complex_add,
    'complex-multiply': complex_multiply,
    'complex-modulus': complex_modulus,
}


PLACEMENT_GENERATORS = {
    'set-intersection': set_intersection,
    'set-union': set_union,
    'geometric-nth': geometric_nth,
    'geometric-sum': geometric_sum,
    'tangent-slope': tangent_slope,
    'tangent-equation': tangent_equation,
}


def all_candidates():
    """Original 8 generators; keep existing batch/API behavior stable."""
    return [fn() for fn in GENERATORS.values()]


def placement_candidates():
    """Six additional original forms for grade-specific placement pilots."""
    return [fn() for fn in PLACEMENT_GENERATORS.values()]
