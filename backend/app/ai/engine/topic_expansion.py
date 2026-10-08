"""Expanded topic generators for MATH WEB.

These generators cover curriculum topics that are not tied to one of the 45
interactive game banks.  They are deterministic mathematical builders: no
network or LLM is required, and every returned answer is computed locally.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction


def _f(v):
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _base(question, answer, solution, distractors, hint=""):
    return {
        "question": question,
        "answer": answer,
        "solution": solution,
        "distractors": list(distractors),
        "hint": hint,
    }


def _linear(d):
    a = random.choice([2, 3, 4, 5, 7])
    x = random.randint(-8, 10)
    b = random.randint(-10, 10)
    c = a * x + b
    return _base(
        f"Giải phương trình {a}x {'+' if b >= 0 else '-'} {abs(b)} = {c}.",
        x,
        f"{a}x = {c - b}, nên x = {x}.",
        [x + 1, x - 1, -x],
        "Cô lập phần chứa ẩn rồi chia cho hệ số của x.",
    )


def _menh_de(d):
    n = random.randint(3, 9)
    statement = n % 2 == 0
    ans = "Đúng" if statement else "Sai"
    return _base(
        f"Mệnh đề ‘{n} là số nguyên tố’ là đúng hay sai?",
        ans,
        f"{n} {'không' if not statement else 'là'} số nguyên tố vì {'có ước khác 1 và chính nó' if not statement else 'chỉ có hai ước dương là 1 và chính nó'}.",
        ["Đúng" if not statement else "Sai", "Không xác định", "Vừa đúng vừa sai"],
        "Kiểm tra các ước dương của số đã cho.",
    )


def _tap_hop(d):
    a = set(random.sample(range(1, 12), 5))
    b = set(random.sample(range(1, 12), 5))
    op = random.choice(["giao", "hợp", "hiệu"])
    if op == "giao":
        s = sorted(a & b)
        ans = len(s)
        sol = f"A∩B={{{','.join(map(str,s))}}}, có {ans} phần tử."
    elif op == "hợp":
        s = sorted(a | b)
        ans = len(s)
        sol = f"A∪B={{{','.join(map(str,s))}}}, có {ans} phần tử."
    else:
        s = sorted(a - b)
        ans = len(s)
        sol = f"A\\B={{{','.join(map(str,s))}}}, có {ans} phần tử."
    return _base(
        f"Cho A={{{','.join(map(str,sorted(a)))}}}, B={{{','.join(map(str,sorted(b)))}}}. Số phần tử của {('A∩B' if op=='giao' else 'A∪B' if op=='hợp' else 'A\\B')} là?",
        ans, sol, [max(0,ans-1), ans+1, len(a)+len(b)],
        "Xác định đúng phép toán tập hợp trước khi đếm.",
    )


def _he_bpt(d):
    lo = random.randint(-5, 2)
    hi = lo + random.randint(2, 7)
    return _base(
        f"Nghiệm của hệ bất phương trình x > {lo} và x ≤ {hi} là khoảng nào?",
        f"({lo}; {hi}]",
        f"Lấy phần giao của hai điều kiện: {lo} < x ≤ {hi}, nên nghiệm là ({lo}; {hi}].",
        [f"[{lo}; {hi}]", f"({lo}; {hi})", f"(-∞; {hi}]"],
        "Vẽ hai điều kiện trên cùng một trục số rồi lấy phần chung.",
    )


def _ham_so(d):
    a = random.choice([2, 3, 4])
    b = random.randint(-6, 6)
    x = random.randint(-4, 5)
    y = a * x + b
    return _base(
        f"Cho hàm số f(x)={a}x {'+' if b >= 0 else '-'} {abs(b)}. Tính f({x}).",
        y,
        f"Thay x={x}: f({x})={a}·{x}{'+' if b>=0 else '-'}{abs(b)}={y}.",
        [y+1, y-1, a*x-b],
        "Thay giá trị x vào đúng biểu thức của hàm số.",
    )


def _ham_bac_nhat(d):
    a = random.choice([-4, -3, 2, 3, 5])
    b = random.randint(-8, 8)
    return _base(
        f"Đường thẳng y={a}x {'+' if b >= 0 else '-'} {abs(b)} có hệ số góc bằng bao nhiêu?",
        a,
        f"Trong y=ax+b, hệ số góc chính là a={a}.",
        [b, -a, abs(a)+1],
        "So sánh phương trình với dạng y=ax+b.",
    )


def _he_phuong_trinh(d):
    x, y = random.randint(-6, 7), random.randint(-6, 7)
    a, b, p, q = random.choice([(1,2,2,-1),(2,1,-1,3),(3,-1,1,2)])
    c, r = a*x+b*y, p*x+q*y
    return _base(
        f"Giải hệ: {a}x {'+' if b>=0 else '-'} {abs(b)}y={c}; {p}x {'+' if q>=0 else '-'} {abs(q)}y={r}.",
        f"({x}; {y})",
        f"Thay x={x}, y={y}: {a}·{x}{'+' if b>=0 else '-'}{abs(b)}·{y}={c} và {p}·{x}{'+' if q>=0 else '-'}{abs(q)}·{y}={r}.",
        [f"({x+1}; {y})", f"({x}; {y+1})", f"({-x}; {y})"],
        "Có thể dùng phương pháp thế hoặc cộng đại số.",
    )


def _he_thuc_luong(d):
    a, b, c = 5, 7, random.choice([6, 8, 9, 10])
    cos_c = Fraction(a*a+b*b-c*c, 2*a*b)
    return _base(
        f"Trong tam giác, hai cạnh kề góc C dài {a} và {b}, cạnh đối diện C dài {c}. Tính cos C.",
        _f(cos_c),
        f"Theo định lý cos: cos C=({a}²+{b}²-{c}²)/(2·{a}·{b})={_f(cos_c)}.",
        [_f(cos_c+Fraction(1,10)), _f(cos_c-Fraction(1,10)), _f(Fraction(c,a+b))],
        "Dùng định lý cosin và đặt đúng cạnh đối diện góc cần tìm.",
    )


def _toa_do_phang(d):
    x1, y1 = random.randint(-4, 4), random.randint(-4, 4)
    x2, y2 = x1 + random.randint(2, 6), y1 + random.randint(2, 6)
    ans = (x2-x1)**2 + (y2-y1)**2
    return _base(
        f"Trong mặt phẳng tọa độ, A({x1};{y1}), B({x2};{y2}). Tính AB².",
        ans,
        f"AB²=({x2}-{x1})²+({y2}-{y1})²={ans}.",
        [ans+1, ans-1, (x2-x1)+(y2-y1)],
        "Dùng công thức khoảng cách giữa hai điểm.",
    )


def _duong_thang(d):
    a = random.choice([-5,-3,2,4])
    b = random.randint(-7,7)
    return _base(
        f"Đường thẳng d: {a}x + y + {b} = 0 có hệ số góc bằng bao nhiêu?",
        -a,
        f"Đưa về y={-a}x-{b}, nên hệ số góc là {-a}.",
        [a, b, -b],
        "Đưa phương trình về dạng y=mx+n.",
    )


def _duong_tron(d):
    r = random.randint(2, 8)
    return _base(
        f"Đường tròn (x-2)²+(y+1)²={r*r} có bán kính bằng bao nhiêu?",
        r,
        f"So sánh với dạng (x-a)²+(y-b)²=R², ta có R²={r*r}, nên R={r}.",
        [r-1, r+1, r*r],
        "Nhận ra số ở vế phải là bình phương bán kính.",
    )


def _newton(d):
    n = random.randint(4, 7)
    k = random.randint(1, n-1)
    ans = math.comb(n, k)
    return _base(
        f"Trong khai triển (x+1)^{n}, hệ số của x^{n-k} là bao nhiêu?",
        ans,
        f"Hệ số cần tìm là C({n},{k})={ans}.",
        [math.comb(n,max(0,k-1)), math.comb(n,min(n,k+1)), n+k],
        "Nhớ công thức số hạng tổng quát của nhị thức Newton.",
    )


def _hinh_phang(d):
    a, b = random.randint(5, 12), random.randint(4, 10)
    ans = a*b/2
    return _base(
        f"Một tam giác có đáy {a} cm và chiều cao {b} cm. Diện tích là bao nhiêu cm²?",
        _f(Fraction(a*b,2)),
        f"S={a}·{b}/2={_f(Fraction(a*b,2))} cm².",
        [_f(a*b), _f(Fraction(a+b,2)), _f(Fraction(a*b,4))],
        "Diện tích tam giác bằng một nửa tích đáy và chiều cao.",
    )


def _real10(d):
    price = random.randint(30, 80) * 1000
    discount = random.choice([10, 15, 20, 25])
    pay = price * (100-discount) // 100
    return _base(
        f"Một chiếc balo giá {price:,} đồng được giảm {discount}%. Số tiền cần trả là bao nhiêu?".replace(',', '.'),
        pay,
        f"Số tiền giảm={price}·{discount}%={price*discount//100}; số tiền trả={pay} đồng.",
        [price*(100-discount)//100 + 10000, price*(100+discount)//100, price-discount],
        "Tính phần trăm được giảm rồi trừ khỏi giá ban đầu.",
    )


def _trig_value(d):
    values = [(0,"0"),(30,"1/2"),(45,"√2/2"),(60,"√3/2"),(90,"1")]
    deg, ans = random.choice(values)
    return _base(f"Giá trị của sin {deg}° là bao nhiêu?", ans, f"Theo bảng giá trị lượng giác cơ bản, sin {deg}°={ans}.", ["1/2" if ans!="1/2" else "√2/2", "0", "1"], "Nhớ các giá trị lượng giác góc đặc biệt.")


def _trig_formula(d):
    return _base("Biểu thức sin(a+b) bằng công thức nào?", "sin a cos b + cos a sin b", "Dùng công thức cộng: sin(a+b)=sin a cos b+cos a sin b.", ["sin a sin b + cos a cos b", "sin a cos b - cos a sin b", "cos a cos b - sin a sin b"], "Phân biệt công thức cộng của sin và cos.")


def _trig_function(d):
    return _base("Hàm số y=sin x có giá trị lớn nhất bằng bao nhiêu?", 1, "Với mọi x, -1≤sin x≤1 nên GTLN là 1.", [0, 2, -1], "Giá trị của sin luôn nằm trong đoạn [-1;1].")


def _trig_equation(d):
    return _base("Trên [0;2π], phương trình sin x=0 có bao nhiêu nghiệm?", 3, "sin x=0 khi x=kπ. Trên [0;2π] có 0, π, 2π.", [2,4,1], "Liệt kê các bội của π nằm trong đoạn đã cho.")


def _sequence(d):
    a1=random.randint(1,8); delta=random.randint(2,6); n=random.randint(5,12); ans=a1+(n-1)*delta
    return _base(f"Dãy số có a₁={a1}, công sai {delta}. Tính a₍{n}₎.",ans,f"aₙ=a₁+(n-1)d={a1}+({n}-1)·{delta}={ans}.",[ans-1,ans+1,a1+n*delta],"Xác định công sai và dùng công thức số hạng tổng quát.")


def _limit(d):
    a=random.randint(2,9)
    return _base(f"Tính lim(x→∞) ({a}x²+3)/x².",a,f"Chia tử và mẫu cho x²: giới hạn là {a}.",[a-1,a+1,0],"Chia các hạng tử cho lũy thừa cao nhất của x.")


def _continuity(d):
    a=random.randint(2,7)
    return _base(f"Hàm f(x)={a}x+1 liên tục tại x=2. Giá trị f(2) là?",2*a+1,f"f(2)={a}·2+1={2*a+1}.",[2*a,2*a+2,a+1],"Với hàm đa thức, chỉ cần thay x vào biểu thức.")


def _derivative_rule(d):
    a=random.randint(2,8); n=random.choice([2,3,4]); x=random.randint(-2,4); ans=a*n*(x**(n-1))
    return _base(f"Cho f(x)={a}x^{n}. Tính f'({x}).",ans,f"f'(x)={a*n}x^{n-1}, nên f'({x})={ans}.",[ans+1,ans-1,a*n*x],"Dùng quy tắc đạo hàm của lũy thừa.")


def _derivative_application(d):
    a=random.randint(1,5); h=random.randint(-3,5); k=random.randint(-6,6)
    return _base(f"Hàm y={a}(x-{h})²+{k} đạt cực tiểu bằng bao nhiêu?",k,f"Vì {a}>0, parabol mở lên và đạt cực tiểu tại x={h}; GTNN={k}.",[k-1,k+1,h],"Xét dấu hệ số của bình phương.")


def _space_parallel(d):
    return _base("Nếu hai mặt phẳng phân biệt cùng vuông góc với một đường thẳng thì chúng có quan hệ gì?", "Song song", "Hai mặt phẳng cùng vuông góc với một đường thẳng thì song song với nhau.", ["Cắt nhau", "Trùng nhau", "Vuông góc"], "Nhớ các định lý quan hệ song song và vuông góc trong không gian.")


def _space_perpendicular(d):
    return _base("Nếu một đường thẳng vuông góc với hai đường thẳng cắt nhau nằm trong mặt phẳng (P), quan hệ giữa đường thẳng đó và (P) là gì?", "Vuông góc với (P)", "Theo định lý, đường thẳng vuông góc với hai đường thẳng cắt nhau trong mặt phẳng thì vuông góc với mặt phẳng.", ["Song song với (P)", "Nằm trong (P)", "Trùng với (P)"], "Dùng định lý đường thẳng vuông góc với mặt phẳng.")


def _space_angle_distance(d):
    a,b=random.randint(3,9),random.randint(4,10); ans=math.sqrt(a*a+b*b)
    if int(ans)!=ans:
        ans=math.sqrt(a*a+b*b)
    ans_text=_f(int(ans)) if int(ans)==ans else f"√{a*a+b*b}"
    return _base(f"Một tam giác vuông có hai cạnh góc vuông {a} và {b}. Cạnh huyền bằng?",ans_text,f"Theo Pythagore, c²={a}²+{b}²={a*a+b*b}, nên c={ans_text}.",[str(a+b),str(abs(a-b)),str(a*b)],"Khoảng cách thường dẫn về một tam giác vuông và định lý Pythagore.")


def _stats(d):
    data=[random.randint(4,20) for _ in range(6)]
    ans=Fraction(sum(data),len(data))
    return _base(f"Mẫu số liệu {data}. Số trung bình cộng bằng bao nhiêu?",_f(ans),f"x̄={sum(data)}/{len(data)}={_f(ans)}.",[_f(ans+1),_f(ans-1),str(max(data))],"Cộng các giá trị rồi chia cho số lượng giá trị.")


def _real11(d):
    first=random.randint(20,60); rate=random.choice([5,10,20]); periods=random.randint(2,4)
    ans=first*((100+rate)/100)**periods
    # keep integer-friendly rates
    ans=round(ans,2)
    return _base(f"Một khoản tiết kiệm ban đầu {first} triệu đồng tăng {rate}% mỗi năm. Sau {periods} năm khoảng bao nhiêu triệu đồng?",ans,f"Giá trị sau {periods} năm={first}·(1+{rate}/100)^{periods}≈{ans} triệu đồng.",[round(ans+5,2),round(ans-5,2),round(first*(1+rate/100),2)],"Mỗi năm nhân với cùng một hệ số tăng trưởng.")


def _prob_independent(d):
    p1=Fraction(random.randint(1,4),5); p2=Fraction(random.randint(1,4),5); ans=p1*p2
    return _base(f"Hai biến cố độc lập có P(A)={_f(p1)} và P(B)={_f(p2)}. Tính P(A∩B).",_f(ans),f"Độc lập nên P(A∩B)=P(A)P(B)={_f(ans)}.",[_f(p1+p2),_f(p1-p2),_f(1-p1*p2)],"Với biến cố độc lập, xác suất giao bằng tích hai xác suất.")


def _recurrence(d):
    a1=random.randint(1,5); delta=random.randint(2,6); n=random.randint(4,9); ans=a1+(n-1)*delta
    return _base(f"Dãy xác định bởi a₁={a1}, aₙ₊₁=aₙ+{delta}. Tính a₍{n}₎.",ans,f"Mỗi bước tăng {delta}: aₙ={a1}+({n}-1)·{delta}={ans}.",[ans-1,ans+1,a1+n*delta],"Triển khai truy hồi vài bước hoặc nhận ra đây là cấp số cộng.")


def _induction(d):
    n=random.randint(3,7); lhs=sum(range(1,n+1)); rhs=n*(n+1)//2
    return _base(f"Công thức 1+2+…+n=n(n+1)/2 tại n={n} cho vế trái bằng bao nhiêu?",lhs,f"1+2+…+{n}={lhs}, đồng thời {n}({n}+1)/2={rhs}.",[lhs+1,lhs-1,n*n],"Thay giá trị n vào tổng số tự nhiên liên tiếp.")


def _transformation(d):
    x,y=random.randint(-4,4),random.randint(-4,4); dx=random.randint(2,5); dy=random.randint(-3,4)
    return _base(f"Tịnh tiến điểm A({x};{y}) theo vectơ ({dx};{dy}). Tọa độ ảnh A' là?",f"({x+dx}; {y+dy})",f"Cộng từng tọa độ: ({x}+{dx}; {y}+{dy})=({x+dx}; {y+dy}).",[f"({x-dx}; {y-dy})",f"({x+dx}; {y-dy})",f"({x}; {y})"],"Tịnh tiến theo vectơ nghĩa là cộng vectơ vào tọa độ điểm.")


def _section(d):
    return _base("Một mặt phẳng cắt một hình chóp và không đi qua đỉnh. Thiết diện có thể là hình gì?", "Đa giác", "Thiết diện của hình chóp bởi một mặt phẳng không đi qua đỉnh là một đa giác.", ["Luôn là đường tròn", "Luôn là điểm", "Luôn là đường thẳng"], "Xét giao tuyến của mặt phẳng với các mặt bên của hình chóp.")


def _count_prob_advanced(d):
    n=random.randint(6,10); k=random.randint(2,4); ans=math.comb(n,k)
    return _base(f"Từ {n} học sinh chọn {k} bạn vào đội, không xét thứ tự. Có bao nhiêu cách?",ans,f"Dùng tổ hợp C({n},{k})={ans}.",[ans+1,ans-k,math.factorial(n)//math.factorial(n-k)],"Không xét thứ tự thì dùng tổ hợp.")


def _real11_total(d):
    length=random.randint(80,180); rate=random.choice([2,3,4]); n=random.randint(3,5)
    ans=length*(1+rate/100)**n
    ans=round(ans,2)
    return _base(f"Một khoản đầu tư {length} triệu đồng tăng đều {rate}% mỗi năm. Sau {n} năm giá trị khoảng bao nhiêu?",ans,f"Giá trị={length}·(1+{rate}/100)^{n}≈{ans} triệu đồng.",[round(ans+10,2),round(ans-10,2),round(length*(1+rate/100),2)],"Mô hình tăng trưởng lũy thừa theo số năm.")


def _monotonic(d):
    a=random.choice([2,3,4]); return _base(f"Hàm f(x)={a}x+1 trên R đồng biến hay nghịch biến?", "Đồng biến", f"Hệ số góc {a}>0 nên hàm số đồng biến trên R.",["Nghịch biến","Không đổi","Không xác định"],"Với hàm bậc nhất, dấu hệ số góc quyết định tính đơn điệu.")


def _extrema(d):
    h=random.randint(-4,4); k=random.randint(-7,7); a=random.choice([1,2,3])
    return _base(f"Hàm y={a}(x-{h})²+{k} có điểm cực tiểu nào?",f"({h}; {k})",f"Parabol đạt cực tiểu tại đỉnh ({h};{k}) vì {a}>0.",[f"({h}; {-k})",f"({-h}; {k})",f"({h+1}; {k})"],"Tìm đỉnh của parabol dạng y=a(x-h)²+k.")


def _tangent(d):
    a=random.choice([2,3,4]); x0=random.randint(-3,4); b=random.randint(-5,5); y0=a*x0*x0+b*x0
    slope=2*a*x0+b
    return _base(f"Cho f(x)={a}x²+{b}x. Hệ số góc tiếp tuyến tại x={x0} là?",slope,f"f'(x)={2*a}x+{b}; f'({x0})={slope}.",[slope+1,slope-1,2*a*x0],"Hệ số góc tiếp tuyến bằng giá trị đạo hàm tại hoành độ tiếp điểm.")


def _asymptote(d):
    a=random.choice([2,3,5]); return _base(f"Đồ thị y={a}/x có tiệm cận đứng là đường nào?", "x=0", "Mẫu số tiến tới 0 khi x→0 nên x=0 là tiệm cận đứng.",["y=0","x=1",f"y={a}"],"Xét nơi mẫu số bằng 0.")


def _intersection(d):
    m=random.randint(1,5); b=random.randint(-4,4); x=random.randint(-3,5); y=m*x+b
    return _base(f"Hai đồ thị y={m}x+{b} và đường ngang y={y} cắt nhau tại hoành độ x bằng?",x,f"m x+{b}={y} nên x={x}.",[x+1,x-1,-x],"Cho hai biểu thức y bằng nhau tại giao điểm.")


def _exp(d):
    q=random.choice([2,3,4]); n=random.randint(2,6); ans=q**n
    return _base(f"Tính {q}^{n}.",ans,f"Nhân {q} với chính nó {n} lần, được {ans}.",[ans+q,ans-q,q*n],"Lũy thừa là phép nhân lặp lại.")


def _log(d):
    a=random.choice([2,3,5]); n=random.randint(1,4); value=a**n
    return _base(f"Tính log_{a}({value}).",n,f"Vì {a}^{n}={value}, nên log_{a}({value})={n}.",[n+1,max(0,n-1),value],"Đưa logarit về câu hỏi: cơ số cần nâng lên mũ nào để được số trong ngoặc?")


def _exp_equation(d):
    a=random.choice([2,3,5]); n=random.randint(2,6)
    return _base(f"Giải phương trình {a}^x={a}^{n}.",n,f"Hai vế cùng cơ số {a}>0, {a}≠1 nên x={n}.",[n+1,n-1,-n],"So sánh số mũ khi hai vế có cùng cơ số hợp lệ.")


def _log_equation(d):
    a=random.choice([2,3,5]); n=random.randint(1,5); value=a**n
    return _base(f"Giải phương trình log_{a}(x)={n}.",value,f"Theo định nghĩa logarit, x={a}^{n}={value}.",[value+1,value-1,a*n],"Đổi phương trình logarit về dạng lũy thừa.")


def _exp_ineq(d):
    a=random.choice([2,3,5]); n=random.randint(1,5)
    return _base(f"Giải bất phương trình {a}^x>{a}^{n}.",f"x>{n}",f"Vì cơ số {a}>1, hàm mũ đồng biến nên x>{n}.",[f"x<{n}",f"x≥{n}",f"x≤{n}"],"Cơ số lớn hơn 1 thì chiều bất phương trình giữ nguyên khi so sánh số mũ.")


def _log_ineq(d):
    a=random.choice([2,3,5]); n=random.randint(1,5)
    return _base(f"Giải bất phương trình log_{a}(x)>{n}.",f"x>{a**n}",f"Hàm logarit cơ số {a}>1 đồng biến, nên x>{a}^{n}={a**n}.",[f"x<{a**n}",f"x≥{a**n}",f"0<x<{a**n}"],"Đừng quên điều kiện x>0.")


def _integral_application(d):
    v=random.randint(4,12); t=random.randint(3,7); ans=v*t
    return _base(f"Một xe chuyển động với vận tốc không đổi {v} m/s trong {t} giây. Quãng đường đi được là bao nhiêu mét?",ans,f"s=v·t={v}·{t}={ans} m.",[ans+v,ans-v,v+t],"Quãng đường là tích vận tốc và thời gian.")


def _complex_repr(d):
    a=random.randint(-5,5); b=random.randint(-5,5)
    return _base(f"Số phức z={a}{'+' if b>=0 else ''}{b}i có phần thực bằng bao nhiêu?",a,f"Trong z=a+bi, phần thực là a={a}.",[b,-a,abs(b)],"Dạng chuẩn của số phức là a+bi.")


def _complex_equation(d):
    b=random.randint(1,7)
    return _base(f"Giải phương trình z+{b}={2*b} trong C.",b,f"z={2*b}-{b}={b}.",[b+1,b-1,-b],"Chuyển hằng số sang vế còn lại.")


def _plane(d):
    return _base("Mặt phẳng (P): 2x-y+3z-6=0 có một vectơ pháp tuyến là?", "(2; -1; 3)", "Các hệ số của x, y, z tạo thành một vectơ pháp tuyến của mặt phẳng.",["(2;1;3)","(1;-2;3)","(2;-1;-3)"],"Lấy trực tiếp các hệ số của x, y, z.")


def _line3d(d):
    return _base("Đường thẳng đi qua A(1;2;3) có vectơ chỉ phương u=(2;-1;4). Điểm nào thuộc đường thẳng?", "(3;1;7)", "A+u=(1;2;3)+(2;-1;4)=(3;1;7).", ["(2;1;7)","(3;3;7)","(1;1;4)"], "Điểm thuộc đường thẳng có dạng A+t·u.")


def _sphere(d):
    r=random.randint(2,8)
    return _base(f"Mặt cầu tâm I(0;0;0), bán kính {r}. Phương trình là?", f"x²+y²+z²={r*r}", f"Dạng mặt cầu tâm O là x²+y²+z²=R²={r*r}.",[f"x²+y²+z²={r}",f"x²+y²+z²={r*r+1}",f"x²+y²+z²={r**3}"],"Với tâm O, bình phương bán kính xuất hiện ở vế phải.")


def _space_volume(d):
    a,b,c=random.randint(3,8),random.randint(3,9),random.randint(2,7); ans=a*b*c
    return _base(f"Một hình hộp chữ nhật có kích thước {a} m, {b} m, {c} m. Thể tích bằng bao nhiêu?",ans,f"V={a}·{b}·{c}={ans} m³.",[ans+a,ans+b,a+b+c],"Thể tích hình hộp chữ nhật là tích ba kích thước.")


def _real12(d):
    r=random.randint(4,12); cost=random.randint(20,50); ans=r*cost
    return _base(f"Một xưởng sản xuất {r} sản phẩm, chi phí biến đổi trung bình {cost} nghìn đồng mỗi sản phẩm. Tổng chi phí biến đổi là?",f"{ans} nghìn đồng",f"Chi phí={r}·{cost}={ans} nghìn đồng.",[f"{ans+cost} nghìn đồng",f"{ans-cost} nghìn đồng",f"{r+cost} nghìn đồng"],"Nhân số sản phẩm với chi phí trên mỗi sản phẩm.")


def _combined(d):
    a=random.randint(3,8); b=random.randint(2,6); ans=a*b
    return _base(f"Một bài toán tổng hợp có {a} lựa chọn ở bước 1 và {b} lựa chọn độc lập ở bước 2. Có bao nhiêu phương án?",ans,f"Quy tắc nhân: {a}·{b}={ans}.",[ans+1,ans-1,a+b],"Khi các bước độc lập nối tiếp nhau, dùng quy tắc nhân.")


GENERATORS = {
    "menh_de": _menh_de, "tap_hop": _tap_hop, "he_bat_phuong_trinh": _he_bpt,
    "ham_so": _ham_so, "ham_so_bac_nhat": _ham_bac_nhat, "phuong_trinh": _linear,
    "he_phuong_trinh": _he_phuong_trinh, "he_thuc_luong": _he_thuc_luong,
    "he_thuc_luong_tam_giac": _he_thuc_luong, "toa_do_phang": _toa_do_phang,
    "duong_thang": _duong_thang, "duong_tron": _duong_tron, "nhi_thuc_newton": _newton,
    "hinh_hoc_10": _hinh_phang, "bai_toan_thuc_te_10": _real10,
    "gia_tri_luong_giac": _trig_value, "cong_thuc_luong_giac": _trig_formula,
    "ham_so_luong_giac_day_du": _trig_function, "phuong_trinh_luong_giac_day_du": _trig_equation,
    "day_so_tong_quat": _sequence, "gioi_han_ham_so": _limit, "ham_so_lien_tuc": _continuity,
    "dao_ham_quy_tac": _derivative_rule, "ung_dung_dao_ham_11": _derivative_application,
    "song_song_khong_gian": _space_parallel, "vuong_goc_khong_gian": _space_perpendicular,
    "goc_khoang_cach_11": _space_angle_distance, "thong_ke_11": _stats,
    "bai_toan_thuc_te_11": _real11, "to_hop_xac_suat_nang_cao_11": _count_prob_advanced,
    "bien_co_doc_lap_11": _prob_independent, "day_so_truy_hoi_11": _recurrence,
    "quy_nap_toan_hoc_11": _induction, "phep_bien_hinh_11": _transformation,
    "thiet_dien_hinh_khong_gian_11": _section, "bai_toan_thuc_te_tong_hop_11": _real11_total,
    "tinh_don_dieu": _monotonic, "cuc_tri": _extrema, "gtln_gtnn": _extrema,
    "tiep_tuyen": _tangent, "tien_can": _asymptote, "tuong_giao": _intersection,
    "ham_mu": _exp, "ham_logarit": _log, "pt_mu": _exp_equation, "pt_logarit": _log_equation,
    "bpt_mu": _exp_ineq, "bpt_logarit": _log_ineq, "ung_dung_tich_phan": _integral_application,
    "bieu_dien_so_phuc": _complex_repr, "pt_so_phuc": _complex_equation,
    "mat_phang_oxyz": _plane, "duong_thang_oxyz": _line3d, "mat_cau": _sphere,
    "goc_khoang_cach_oxyz": _space_angle_distance, "the_tich_khong_gian": _space_volume,
    "tong_hop_thpt": _combined, "bai_toan_thuc_te_12": _real12,
}


def generate(topic_id: str, difficulty: str = "medium"):
    fn = GENERATORS.get(topic_id)
    return fn(difficulty) if fn else None


def geometry_diagram(topic_id: str, question: str, answer: str | int | float):
    """Return a small structured diagram descriptor for the frontend.

    The browser renders the SVG itself, so the backend never injects arbitrary
    HTML into the page.
    """
    low = f"{topic_id} {question}".lower()
    if any(k in low for k in ("tam giác", "tam giac", "pythagore", "cos", "góc", "goc")):
        return {"type": "triangle", "labels": ["A", "B", "C"]}
    if "đường tròn" in low or "duong tron" in low or "mặt cầu" in low or "khối cầu" in low or "khoi cau" in low:
        return {"type": "circle", "labels": ["O"]}
    if "tọa độ" in low or "tọa do" in low or "oxyz" in low:
        return {"type": "coordinate", "labels": ["A", "B"]}
    if "hình hộp" in low or "hinh hop" in low or "hình chóp" in low:
        return {"type": "box", "labels": ["A", "B", "C", "D"]}
    geometry_ids = {
        "he_thuc_luong", "he_thuc_luong_tam_giac", "toa_do_phang", "duong_tron",
        "hinh_hoc_10", "hinh_khong_gian", "hinh_hoc_khong_gian", "song_song_khong_gian",
        "vuong_goc_khong_gian", "goc_khoang_cach_11", "thiet_dien_hinh_khong_gian_11",
        "toa_do_khong_gian", "mat_phang_oxyz", "duong_thang_oxyz", "mat_cau",
        "goc_khoang_cach_oxyz", "the_tich_khong_gian"
    }
    if topic_id in geometry_ids:
        return {"type": "triangle", "labels": ["A", "B", "C"]}
    return None


def real_life(topic_id: str, difficulty: str = "medium"):
    """A pool of genuine everyday/application problems by topic."""
    if topic_id == "xac_suat":
        total = random.randint(20, 60); good = random.randint(4, total-4)
        ans = Fraction(good, total)
        return _base(f"Một cửa hàng kiểm tra {total} sản phẩm, có {good} sản phẩm đạt chuẩn. Chọn ngẫu nhiên 1 sản phẩm. Xác suất sản phẩm đạt chuẩn là?", _f(ans), f"P={good}/{total}={_f(ans)}.", [_f(Fraction(total-good,total)), _f(Fraction(good+1,total)), "1/2"], "Xác suất bằng số trường hợp thuận lợi chia số trường hợp có thể.")
    if topic_id == "hoan_vi_chinh_hop_to_hop":
        n=random.randint(6,10); k=random.randint(2,4); ans=math.comb(n,k)
        return _base(f"Một câu lạc bộ có {n} thành viên. Chọn {k} bạn trực bàn trong một buổi, không phân biệt thứ tự. Có bao nhiêu cách?",ans,f"Không xét thứ tự nên dùng C({n},{k})={ans}.",[ans+1,ans-k,math.factorial(n)//math.factorial(n-k)],"Đây là chọn nhóm, không phải xếp vị trí.")
    if topic_id == "quy_tac_dem":
        a,b,c=random.randint(3,6),random.randint(2,5),random.randint(2,4); ans=a*b*c
        return _base(f"Một ứng dụng cho phép chọn {a} mẫu giao diện, {b} ảnh đại diện và {c} nhạc nền. Mỗi lựa chọn kết hợp được tạo thành một phương án. Có bao nhiêu phương án?",ans,f"Quy tắc nhân: {a}·{b}·{c}={ans}.",[ans+1,ans-a,ans+b],"Các lựa chọn độc lập theo từng bước thì nhân số khả năng.")
    if topic_id == "ham_so_bac_hai":
        a=random.choice([1,2]); h=random.randint(2,6); k=random.randint(3,10); x=h+random.randint(-2,2); y=a*(x-h)**2+k
        return _base(f"Độ cao của một mô hình vòm được mô tả bởi h(x)={a}(x-{h})²+{k} (m). Tại vị trí x={x}, độ cao là bao nhiêu mét?",y,f"h({x})={a}({x}-{h})²+{k}={y} m.",[y+1,y-1,k],"Thay vị trí x vào mô hình độ cao.")
    if topic_id in {"phuong_trinh_he", "he_phuong_trinh"}:
        notebooks=random.randint(2,6); pens=random.randint(3,9); total_items=random.randint(18,45); unit1=random.randint(8,20); unit2=random.randint(4,12)
        # Build a clean two-variable ticket-like system from chosen solution.
        x=random.randint(2,8); y=random.randint(2,7); total=x+y; money=x*unit1+y*unit2
        return _base(f"Một quầy bán vé có {x+y} vé gồm vé loại A giá {unit1} nghìn và vé loại B giá {unit2} nghìn. Tổng tiền thu được là {money} nghìn. Hỏi có bao nhiêu vé loại A?",x,f"Gọi x là số vé A, y là số vé B. Ta có x+y={total} và {unit1}x+{unit2}y={money}. Giải hệ được x={x}.",[x+1,max(0,x-1),y],"Đặt ẩn cho hai loại vé rồi lập hệ từ tổng số vé và tổng tiền.")
    if topic_id == "bat_phuong_trinh":
        budget=random.randint(80,200); fixed=random.randint(20,50); price=random.randint(8,20)
        maxn=(budget-fixed)//price
        return _base(f"Bạn có {budget} nghìn đồng, đã dùng {fixed} nghìn cho đồ dùng và mỗi quyển vở giá {price} nghìn. Có thể mua nhiều nhất bao nhiêu quyển vở?",maxn,f"{fixed}+{price}n≤{budget} nên n≤{maxn}.",[maxn+1,max(0,maxn-1),budget//price],"Lập bất phương trình theo ngân sách và lấy số nguyên lớn nhất thỏa điều kiện.")
    if topic_id == "thong_ke":
        data=[random.randint(5,30) for _ in range(5)]; ans=Fraction(sum(data),5)
        return _base(f"Một nhóm ghi nhận số phút đọc sách mỗi ngày trong 5 ngày: {data}. Thời gian đọc trung bình mỗi ngày là bao nhiêu phút?",_f(ans),f"Trung bình=({'+'.join(map(str,data))})/5={_f(ans)} phút.",[_f(ans+1),_f(ans-1),str(max(data))],"Tổng thời gian chia cho số ngày.")
    if topic_id in {"dao_ham", "ung_dung_dao_ham"}:
        x=random.randint(1,6); a=random.choice([2,3,4]); b=random.randint(5,15); ans=2*a*x+b
        return _base(f"Doanh thu biên của một cửa hàng được mô hình hóa bởi R'(x)={2*a}x+{b}. Tại x={x}, doanh thu biên bằng bao nhiêu?",ans,f"R'({x})={2*a}·{x}+{b}={ans}.",[ans+1,ans-1,a*x+b],"Thay sản lượng x vào hàm doanh thu biên.")
    if topic_id == "nguyen_ham_tich_phan":
        v0=random.randint(2,6); a=random.randint(1,3); t=random.randint(2,5)
        ans=v0*t+Fraction(a*t*t,2)
        return _base(f"Vận tốc của một vật là v(t)={v0}+{a}t (m/s). Quãng đường đi từ t=0 đến t={t} là bao nhiêu mét?",_f(ans),f"s=∫₀^{t}({v0}+{a}t)dt={v0}·{t}+{a}{t}²/2={_f(ans)} m.",[_f(ans+1),_f(ans-1),str(v0*t)],"Quãng đường là tích phân của vận tốc theo thời gian.")
    if topic_id in {"toa_do_phang", "duong_thang"}:
        x1,y1=random.randint(0,5),random.randint(0,5); dx,dy=random.randint(2,6),random.randint(2,6); x2,y2=x1+dx,y1+dy
        ans=dx+dy
        return _base(f"Trên bản đồ ô vuông, một robot đi từ A({x1};{y1}) đến B({x2};{y2}) theo hai hướng song song trục tọa độ. Tổng quãng đường theo lưới là bao nhiêu đơn vị?",ans,f"Đi ngang {dx} đơn vị và dọc {dy} đơn vị: tổng={dx}+{dy}={ans}.",[ans+1,dx*dy,abs(dx-dy)],"Đếm riêng số bước theo hai trục rồi cộng.")
    if topic_id in {"cap_so_cong", "day_so"}:
        first=random.randint(5,20); step=random.randint(2,5); n=random.randint(5,10); ans=first+(n-1)*step
        return _base(f"Một hàng ghế có {first} ghế ở hàng đầu và mỗi hàng sau tăng {step} ghế. Hàng thứ {n} có bao nhiêu ghế?",ans,f"Đây là cấp số cộng: aₙ={first}+({n}-1)·{step}={ans}.",[ans+step,ans-step,first+n*step],"Số ghế tăng đều nên dùng cấp số cộng.")
    if topic_id in {"ham_mu", "pt_mu", "bpt_mu"}:
        start=random.randint(100,500); rate=random.choice([2,5,10]); years=random.randint(2,4)
        factor=1+rate/100; value=round(start*(factor**years),2)
        return _base(f"Một khoản tiền {start} nghìn đồng tăng {rate}% mỗi năm. Sau {years} năm, số tiền khoảng bao nhiêu nghìn đồng?",value,f"Giá trị={start}·(1+{rate}/100)^{years}≈{value} nghìn đồng.",[round(value+20,2),round(value-20,2),round(start*factor,2)],"Tăng theo cùng một tỉ lệ qua nhiều kỳ là mô hình lũy thừa.")
    if topic_id in {"ham_logarit", "pt_logarit", "bpt_logarit"}:
        return _base("Độ pH được mô hình hóa bởi pH=-log₁₀[H⁺]. Nếu [H⁺]=10⁻³ thì pH bằng bao nhiêu?",3,"pH=-log₁₀(10⁻³)=3.",[2,4,-3],"Nhớ log₁₀(10^k)=k.")
    if topic_id in {"bai_toan_thuc_te_10", "bai_toan_thuc_te_11", "bai_toan_thuc_te_tong_hop_11", "bai_toan_thuc_te_12", "tong_hop_thpt"}:
        return _real12(difficulty)
    return None
