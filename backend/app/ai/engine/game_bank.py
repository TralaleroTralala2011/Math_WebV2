import math
import random
from fractions import Fraction


def _fmt_fraction(v, denominator=None):
    v = Fraction(v, denominator) if denominator is not None else Fraction(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def _sign(n):
    return f"+ {n}" if n >= 0 else f"- {abs(n)}"


class GameQuestionBank:
    """Question bank by GAME, not only by topic.

    Each game has its own context and problem structures. The bank intentionally
    keeps the mathematical theme locked to the selected game.
    """

    def __init__(self, generator):
        self.g = generator
        self._builders = {
            "Bốc bi": self.marble,
            "Xúc xắc": self.dice,
            "Chọn tình huống": self.probability_situation,
            "Chọn đội": self.team,
            "Ghép lựa chọn": self.choice,
            "Săn tổ hợp": self.combination_hunt,
            "Xếp vị trí": self.position,
            "Mật mã": self.code,
            "Sắp thứ tự": self.order,
            "Bắt điểm": self.function_point,
            "Tìm giao điểm": self.function_intersection,
            "Đồ thị bí ẩn": self.function_graph,
            "Điều tra": self.system_investigation,
            "Tìm giá trị": self.system_value,
            "Ghép đáp án": self.system_match,
            "Săn nghiệm": self.quadratic_root,
            "Ghép nghiệm": self.quadratic_match,
            "Mở khóa": self.quadratic_unlock,
            "Vùng an toàn": self.inequality_safe,
            "Chọn khoảng": self.inequality_interval,
            "Vượt rào": self.inequality_barrier,
            "Tìm quy luật": self.sequence_rule,
            "Điền số": self.sequence_fill,
            "Đường đua dãy số": self.sequence_race,
            "Truy tìm số": self.divisibility_find,
            "Chọn số": self.divisibility_select,
            "Phá khóa": self.divisibility_unlock,
            "Bốc số": self.remainder_draw,
            "Săn số dư": self.remainder_hunt,
            "Thử thách modulo": self.remainder_modulo,
            "Săn căn": self.radical_hunt,
            "Rút gọn nhanh": self.radical_simplify,
            "Mở khóa căn thức": self.radical_unlock,
            "Phá biểu thức": self.identity_break,
            "Ghép công thức": self.identity_match,
            "Công thức bí ẩn": self.identity_mystery,
            "Rút gọn": self.fraction_simplify,
            "Tìm điều kiện": self.fraction_condition,
            "Phân thức tốc độ": self.fraction_speed,
            "Tìm góc": self.geometry_angle,
            "Săn độ dài": self.geometry_length,
            "Bản đồ hình học": self.geometry_map,
            "Đọc biểu đồ": self.statistics_chart,
            "Săn số liệu": self.statistics_data,
            "Thử thách thống kê": self.statistics_challenge,
        }

    def generate(self, game_id, grade, difficulty):
        fn = self._builders.get(game_id)
        if not fn:
            return None
        return fn(difficulty)

    def base(self, question, answer, solution, distractors=(), hint=""):
        return self.g._base(question, answer, solution, list(distractors), hint)

    def mc(self, answer, *wrong):
        return [answer, *wrong]

    # ---------- XÁC SUẤT ----------
    def marble(self, d):
        variant = random.randrange(6)
        r, b, y = random.randint(2, 8), random.randint(2, 8), random.randint(1, 6)
        if variant == 0:
            t = r + b
            a = Fraction(r, t)
            return self.base(f"Một túi có {r} bi đỏ và {b} bi xanh. Lấy ngẫu nhiên 1 viên. Xác suất lấy được bi đỏ là bao nhiêu?", _fmt_fraction(a), f"Có {t} viên, trong đó {r} viên đỏ nên P={r}/{t}={_fmt_fraction(a)}.", [f"{_fmt_fraction(Fraction(b,t))}", "1/2", "1/3"])
        if variant == 1:
            t = r + b + y
            a = Fraction(r + y, t)
            return self.base(f"Hộp có {r} bi đỏ, {b} bi xanh và {y} bi vàng. Lấy 2 viên? Không, lần này chỉ lấy 1 viên. Xác suất lấy được bi đỏ hoặc vàng là?", _fmt_fraction(a), f"Bi thuận lợi: {r}+{y}={r+y}, tổng {t}.", [f"{_fmt_fraction(Fraction(b,t))}", f"{_fmt_fraction(Fraction(r,t))}", "1/2"])
        if variant == 2:
            a = Fraction(r * b, (r+b)*(r+b-1))
            return self.base(f"Túi có {r} bi đỏ và {b} bi xanh. Lấy liên tiếp 2 viên không hoàn lại. Xác suất viên đầu đỏ và viên sau xanh là?", _fmt_fraction(a), f"P={r}/{r+b} × {b}/{r+b-1}={_fmt_fraction(a)}.", [f"{_fmt_fraction(Fraction(r,b+r))}", f"{_fmt_fraction(Fraction(b,b+r))}", "1/2"])
        if variant == 3:
            t = r+b
            a = Fraction(r*(r-1), t*(t-1))
            return self.base(f"Có {r} bi đỏ và {b} bi xanh. Lấy 2 viên không hoàn lại. Xác suất cả hai đều đỏ là?", _fmt_fraction(a), f"P={r}/{t} × {r-1}/{t-1}={_fmt_fraction(a)}.", [f"{_fmt_fraction(Fraction(r,t))}", f"{_fmt_fraction(Fraction(r*(r-1),t*t))}", "1/2"])
        if variant == 4:
            t = r+b
            a = Fraction(2*r*b, t*(t-1))
            return self.base(f"Túi có {r} bi đỏ và {b} bi xanh. Lấy 2 viên không hoàn lại. Xác suất hai viên khác màu là?", _fmt_fraction(a), f"Hai thứ tự thuận lợi: đỏ-xanh hoặc xanh-đỏ, nên P=2rb/[{t}({t}-1)]={_fmt_fraction(a)}.", [f"{_fmt_fraction(Fraction(r*b,t*t))}", f"{_fmt_fraction(Fraction(r,t))}", "1/2"])
        total = r+b
        # inverse-style: after one red draw, conditional probability next red
        a = Fraction(r-1, total-1)
        return self.base(f"Hộp có {r} bi đỏ và {b} bi xanh. Biết lần đầu đã lấy được một viên đỏ và không hoàn lại. Xác suất lần hai tiếp tục là bi đỏ?", _fmt_fraction(a), f"Sau lần đầu còn {r-1} đỏ trên {total-1} viên, nên P={_fmt_fraction(a)}.", [f"{_fmt_fraction(Fraction(r,total))}", f"{_fmt_fraction(Fraction(b,total))}", "1/2"])

    def dice(self, d):
        v = random.randrange(7)
        if v == 0:
            face = random.randint(1,6)
            return self.base(f"Một con xúc xắc cân đối được gieo một lần. Xác suất xuất hiện mặt {face} là?", "1/6", "Có 6 kết quả đồng khả năng và chỉ 1 kết quả thuận lợi.", ["1/3", "1/2", "1/4"])
        if v == 1:
            good = len([x for x in range(1,7) if x % 2 == 0])
            return self.base("Gieo một con xúc xắc cân đối. Xác suất xuất hiện số chấm chẵn là?", "1/2", "Các mặt chẵn là 2,4,6, có 3/6=1/2.", ["1/3", "2/3", "1/6"])
        if v == 2:
            sums = [(a,b) for a in range(1,7) for b in range(1,7) if a+b >= 9]
            a = Fraction(len(sums),36)
            return self.base("Gieo đồng thời hai xúc xắc cân đối. Xác suất để tổng số chấm lớn hơn hoặc bằng 9 là?", _fmt_fraction(a), f"Có {len(sums)} cặp thuận lợi trên 36 cặp đồng khả năng.", ["1/4", "5/18", "1/3"])
        if v == 3:
            pairs = [(a,b) for a in range(1,7) for b in range(1,7) if (a*b)%3==0]
            a=Fraction(len(pairs),36)
            return self.base("Gieo hai xúc xắc. Xác suất tích hai số chấm chia hết cho 3 là?", _fmt_fraction(a), f"Đếm các cặp có ít nhất một mặt chia hết cho 3: {len(pairs)}/36.", ["1/3", "1/2", "5/9"])
        if v == 4:
            # at least one six in two rolls
            a=Fraction(11,36)
            return self.base("Gieo hai lần một xúc xắc. Xác suất xuất hiện ít nhất một lần mặt 6 là?", "11/36", "Dùng biến cố đối: 1-(5/6)^2=11/36.", ["1/6", "1/3", "25/36"])
        if v == 5:
            a=Fraction(1,6)
            return self.base("Một trò chơi yêu cầu gieo hai xúc xắc. Người chơi thắng nếu hai mặt giống nhau. Xác suất thắng là?", "1/6", "Có 6 cặp đôi giống nhau trong 36 kết quả.", ["1/12", "1/3", "1/2"])
        return self.base("Gieo hai xúc xắc. Biết tổng số chấm bằng 8. Xác suất để xúc xắc thứ nhất ra số 3 là?", "1/5", "Các cặp có tổng 8 là (2,6),(3,5),(4,4),(5,3),(6,2). Chỉ một cặp có xúc xắc thứ nhất bằng 3.", ["1/6", "1/4", "2/5"])

    def probability_situation(self, d):
        v=random.randrange(6)
        if v==0:
            return self.base("Một lớp có 30 học sinh, trong đó 18 bạn tham gia câu lạc bộ thể thao. Chọn ngẫu nhiên 1 bạn. Xác suất chọn được bạn tham gia câu lạc bộ là?", "3/5", "18/30=3/5.", ["2/5","3/10","1/2"])
        if v==1:
            return self.base("Một hộp có 20 sản phẩm, trong đó 3 sản phẩm lỗi. Chọn ngẫu nhiên 1 sản phẩm. Xác suất chọn được sản phẩm tốt là?", "17/20", "Có 20-3=17 sản phẩm tốt.", ["3/20","7/10","4/5"])
        if v==2:
            return self.base("Một vé quay có 8 ô, trong đó 2 ô thưởng lớn. Quay 1 lần, các ô đồng khả năng. Xác suất trúng thưởng lớn là?", "1/4", "2/8=1/4.", ["1/8","3/8","1/2"])
        if v==3:
            return self.base("Một khảo sát có 50 người, 32 người chọn phương án A. Chọn ngẫu nhiên 1 người trong khảo sát. Xác suất người đó chọn A là?", "16/25", "32/50=16/25.", ["8/25","3/5","18/25"])
        if v==4:
            return self.base("Một hộp có 12 vé, 5 vé trúng quà. Rút 2 vé liên tiếp không hoàn lại. Xác suất cả hai vé đều trúng là?", "5/33", "P=5/12×4/11=5/33.", ["5/36","10/33","1/3"])
        return self.base("Một lớp có 24 học sinh, 15 bạn biết chơi cờ và 9 bạn biết chơi cầu lông. Hai nhóm không giao nhau. Chọn ngẫu nhiên 1 bạn. Xác suất bạn đó biết ít nhất một trong hai môn là?", "1", "24/24=1 vì toàn bộ lớp thuộc một trong hai nhóm.", ["5/8","3/4","7/8"])

    # ---------- TỔ HỢP ----------
    def team(self,d):
        n=random.randint(8,14); k=random.randint(3,5); a=math.comb(n,k)
        return self.base(f"Một lớp có {n} học sinh. Chọn {k} bạn lập một đội, không xét thứ tự. Có bao nhiêu cách chọn?", a, f"Số cách là C({n},{k})={a}.", [a+1,a-k,a+n])

    def choice(self,d):
        a,b,c=random.randint(3,6),random.randint(2,5),random.randint(2,4); ans=a*b*c
        return self.base(f"Một cửa hàng có {a} loại áo, {b} loại quần và {c} loại giày. Một bộ gồm 1 áo, 1 quần và 1 đôi giày. Có bao nhiêu lựa chọn?", ans, f"Quy tắc nhân: {a}×{b}×{c}={ans}.", [ans+a,ans-b,ans+c])

    def combination_hunt(self,d):
        n=random.randint(7,12); k=random.randint(2,4); forbidden=random.randint(1,n)
        # choose k with a fixed person included
        ans=math.comb(n-1,k-1)
        return self.base(f"Có {n} học sinh, trong đó bạn An bắt buộc phải có mặt. Chọn {k} bạn lập đội. Có bao nhiêu đội khác nhau?", ans, f"Đã cố định An, chọn thêm {k-1} người từ {n-1}: C({n-1},{k-1})={ans}.", [math.comb(n,k),ans+1,max(1,ans-k)])

    # ---------- CHỈNH HỢP ----------
    def position(self,d):
        n=random.randint(6,10); k=random.randint(2,4); ans=math.perm(n,k)
        return self.base(f"Có {n} học sinh. Chọn và xếp {k} bạn vào {k} vị trí khác nhau. Có bao nhiêu cách?", ans, f"A({n},{k})={ans}.", [math.comb(n,k),ans+1,ans-k])

    def code(self,d):
        n=random.randint(5,8); k=random.randint(3,5); ans=n**k
        return self.base(f"Một mã gồm {k} ký tự, mỗi vị trí chọn từ {n} ký tự và được phép lặp. Có bao nhiêu mã?", ans, f"Mỗi vị trí có {n} lựa chọn nên có {n}^{k}={ans} mã.", [math.perm(n,k),n*k,ans-n])

    def order(self,d):
        n=random.randint(5,9); ans=math.factorial(n)
        return self.base(f"Có {n} cuốn sách khác nhau cần xếp thành một hàng. Có bao nhiêu thứ tự xếp?", ans, f"Hoán vị {n} phần tử: {n}!={ans}.", [math.perm(n,2),ans//n,ans+n])

    # ---------- HÀM SỐ ----------
    def function_point(self,d):
        a=random.randint(2,7); b=random.randint(-8,8); x=random.randint(-5,5); y=a*x+b
        return self.base(f"Điểm M({x};y) thuộc đồ thị y={a}x {_sign(b)}. Tìm y.", y, f"Thay x={x}: y={a}·{x}{_sign(b)}={y}.", [y+1,y-1,y+2])

    def function_intersection(self,d):
        x=random.randint(-5,6); m1=random.randint(1,5); m2=random.choice([-4,-3,-2,-1,2,3,4]); b1=random.randint(-6,6); b2=(m1-m2)*x+b1
        return self.base(f"Hai đường thẳng y={m1}x {_sign(b1)} và y={m2}x {_sign(b2)} cắt nhau tại điểm có hoành độ bằng bao nhiêu?", x, f"Cho hai biểu thức bằng nhau: ({m1}-{m2})x={b2-b1}, suy ra x={x}.", [x+1,x-1,0])

    def function_graph(self,d):
        a=random.choice([1,2,-1,-2]); h=random.randint(-4,4); k=random.randint(-6,6)
        return self.base(f"Đồ thị y={a}(x-{h})² {_sign(k)} có đỉnh tại điểm nào?", f"({h};{k})", f"Dạng y=a(x-h)²+k có đỉnh I(h;k), nên I({h};{k}).", [f"({-h};{k})",f"({h};{-k})",f"(0;{k})"])

    # ---------- HỆ PHƯƠNG TRÌNH ----------
    def _system_data(self):
        x=random.randint(2,10); y=random.randint(1,9); return x,y,x+y,x-y
    def system_investigation(self,d):
        x,y,s,dv=self._system_data()
        return self.base(f"Một cuộc điều tra cho biết hai số có tổng {s} và hiệu {dv}. Hai số đó là gì?", f"({x};{y})", f"x+y={s}, x-y={dv} nên 2x={s+dv}, x={x}, y={y}.", [f"({y};{x})",f"({x+1};{y})",f"({x};{y+1})"])

    def system_value(self,d):
        x,y,s,dv=self._system_data(); target=random.choice([x,y,x+y,x-y])
        return self.base(f"Giải hệ x+y={s}; x-y={dv}. Giá trị cần tìm là {('x' if target==x else 'y') }.", target, f"Cộng hai phương trình được 2x={s+dv}, suy ra x={x}; rồi y={y}.", [target+1,target-1,target+2])

    def system_match(self,d):
        x,y,s,dv=self._system_data()
        return self.base(f"Hệ x+y={s}; x-y={dv} có nghiệm nào dưới đây?", f"({x};{y})", f"Cộng hai phương trình: 2x={s+dv}, nên x={x}, y={y}.", [f"({y};{x})",f"({x+1};{y})",f"({x};{y-1})"])

    # ---------- PHƯƠNG TRÌNH BẬC HAI ----------
    def _quadratic(self):
        r1=random.randint(-7,7); r2=random.randint(-7,7); B=-(r1+r2); C=r1*r2; return r1,r2,B,C
    def quadratic_root(self,d):
        r1,r2,B,C=self._quadratic(); target=random.choice([r1,r2])
        return self.base(f"Một nghiệm của phương trình x² {_sign(B)}x {_sign(C)}=0 là?", target, f"Phương trình có hai nghiệm x={r1}, x={r2}.", [r1+1,r2+1,0])

    def quadratic_match(self,d):
        r1,r2,B,C=self._quadratic(); s=r1+r2
        return self.base(f"Phương trình x² {_sign(B)}x {_sign(C)}=0 có tổng hai nghiệm bằng bao nhiêu?", s, f"Theo Viète, tổng nghiệm = -B = {s}.", [B,C,r1*r2])

    def quadratic_unlock(self,d):
        a=random.choice([1,2,3]); b=random.randint(-8,8); c=random.randint(-8,8); D=b*b-4*a*c
        return self.base(f"Xét phương trình {a}x² {_sign(b)}x {_sign(c)}=0. Biệt thức Δ bằng bao nhiêu?", D, f"Δ=b²-4ac={b}²-4·{a}·{c}={D}.", [D+1,D-1,abs(D)])

    # ---------- BẤT PHƯƠNG TRÌNH ----------
    def inequality_safe(self,d):
        lo=random.randint(-6,2); hi=lo+random.randint(3,8)
        return self.base(f"Một vùng an toàn được mô tả bởi {lo} ≤ x ≤ {hi}. Có bao nhiêu số nguyên x thuộc vùng này?", hi-lo+1, f"Các số nguyên từ {lo} đến {hi} có {hi-lo+1} giá trị.", [hi-lo,hi-lo+2,hi])

    def inequality_interval(self,d):
        a=random.randint(2,7); b=random.randint(-9,9); c=random.randint(-5,8); r=Fraction(c-b,a)
        return self.base(f"Giải bất phương trình {a}x {_sign(b)} < {c}. Mốc chia khoảng là bao nhiêu?", _fmt_fraction(r), f"{a}x < {c-b}, nên x < ({c-b})/{a}={_fmt_fraction(r)}.", [_fmt_fraction(r+1),_fmt_fraction(r-1),"0"])

    def inequality_barrier(self,d):
        a=random.randint(2,8); b=random.randint(-8,8); x0=random.randint(-4,6); c=a*x0+b
        return self.base(f"Vượt qua rào nếu {a}x {_sign(b)} > {c}. Giá trị nguyên nhỏ nhất của x để vượt rào là?", x0+1, f"Bất phương trình tương đương x>{x0}; số nguyên nhỏ nhất là {x0+1}.", [x0,x0+2,max(0,x0-1)])

    # ---------- DÃY SỐ ----------
    def sequence_rule(self,d):
        a=random.randint(-5,8); step=random.randint(2,6); n=random.randint(5,9); terms=[a+i*step for i in range(5)]
        return self.base(f"Dãy số bắt đầu {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ... theo quy luật cộng đều. Số hạng thứ {n} là?", a+(n-1)*step, f"Đây là CSC với a1={a}, d={step}; a{n}={a}+({n}-1)·{step}.", [a+n*step,a+(n-2)*step,a+n])

    def sequence_fill(self,d):
        a=random.randint(-4,7); step=random.randint(2,7); idx=random.randint(2,5); missing=a+(idx-1)*step
        return self.base(f"Điền số còn thiếu: {a}, {a+step}, {a+2*step}, ..., {a+4*step}. Số hạng thứ {idx} là?", missing, f"Mỗi bước tăng {step}; số hạng thứ {idx} là {missing}.", [missing+step,missing-step,a+idx*step])

    def sequence_race(self,d):
        a=random.randint(2,8); d0=random.randint(2,5); n=random.randint(6,12); total=n*(2*a+(n-1)*d0)//2
        return self.base(f"Một tay đua ghi điểm theo dãy  {a}, {a+d0}, {a+2*d0}, ... trong {n} lượt. Tổng điểm là bao nhiêu?", total, f"CSC: S={n}(2·{a}+({n}-1)·{d0})/2={total}.", [total+n,total-n,total+d0])

    # ---------- CHIA HẾT ----------
    def divisibility_find(self,d):
        m=random.randint(3,12); q=random.randint(10,40); n=m*q
        return self.base(f"Trong các số sau, số nào chắc chắn chia hết cho {m}?", n, f"{n}={m}×{q} nên chia hết cho {m}.", [n+1,n-1,n+2])

    def divisibility_select(self,d):
        m=random.choice([3,4,5,6,8,9,10]); q=random.randint(8,25); n=m*q
        return self.base(f"Số nào sau đây là bội của {m}?", n, f"{n}={m}×{q}.", [n+1,n+2,n-1])

    def divisibility_unlock(self,d):
        d0=random.choice([3,4,5,6,8,9]); q=random.randint(10,30); n=d0*q
        return self.base(f"Một mã khóa là số có dạng {n-2}, {n-1}, {n}, {n+1}. Chỉ số chia hết cho {d0} mới mở được khóa. Số mở khóa là?", n, f"{n}={d0}×{q}, nên chỉ {n} thỏa điều kiện trong bốn số liên tiếp đã chọn.", [n-1,n+1,n-2])

    # ---------- CHIA DƯ ----------
    def remainder_draw(self,d):
        n=random.randint(50,500); m=random.randint(3,17); r=n%m
        return self.base(f"Bốc số {n} rồi chia cho {m}. Số dư là bao nhiêu?", r, f"{n}={n//m}·{m}+{r}.", [r+1,(r+2)%m,(r+3)%m])

    def remainder_hunt(self,d):
        m=random.randint(5,19); r=random.randint(1,m-1); q=random.randint(10,50); n=m*q+r
        return self.base(f"Một số khi chia cho {m} dư {r}. Với n={n}, số dư đúng là?", r, f"{n}={q}·{m}+{r}.", [0,(r+1)%m,(r+2)%m])

    def remainder_modulo(self,d):
        m=random.randint(5,13); a=random.randint(20,80); b=random.randint(20,80); r=((a%m)+(b%m))%m
        return self.base(f"Trong modulo {m}, tính số dư của {a}+{b}.", r, f"({a} mod {m})+({b} mod {m}) ≡ {r} (mod {m}).", [(r+1)%m,(r+2)%m,(r+3)%m])

    # ---------- CĂN THỨC ----------
    def radical_hunt(self,d):
        k=random.randint(2,9); n=k*k*random.randint(2,5); base=int(math.isqrt(n));
        # choose a perfect square multiplier and a squarefree part
        s=random.choice([2,3,5,6,7]); n=k*k*s; ans=f"{k}√{s}"
        return self.base(f"Rút gọn √{n}.", ans, f"√({k}²·{s})={k}√{s}.", [f"{k}√{s*k}",f"{s}√{k}",f"{k+s}√2"])

    def radical_simplify(self,d):
        a=random.randint(2,8); b=random.randint(2,8); ans=a*b
        return self.base(f"Với a>0, b>0, tính √({a*a}·{b*b}).", ans, f"√({a}²·{b}²)=ab={ans}.", [ans+a,ans-b,a+b])

    def radical_unlock(self,d):
        k=random.randint(2,7); s=random.choice([2,3,5,6,7]); n=k*k*s
        return self.base(f"Mở khóa bằng cách chọn hệ số trước căn trong √{n}. Hệ số nguyên lớn nhất có thể đưa ra ngoài căn là?", k, f"{n}={k}²·{s}, nên hệ số đưa ra ngoài là {k}.", [k+1,max(1,k-1),s])

    # ---------- HẰNG ĐẲNG THỨC ----------
    def identity_break(self,d):
        a=random.randint(2,9); b=random.randint(1,7); ans=(a+b)**2
        return self.base(f"Phá biểu thức: tính ({a}+{b})² bằng hằng đẳng thức.", ans, f"(a+b)²=a²+2ab+b²={a*a}+{2*a*b}+{b*b}={ans}.", [a*a+b*b,2*(a+b),ans-1])

    def identity_match(self,d):
        a=random.randint(2,8); b=random.randint(1,6); ans=(a-b)**2
        return self.base(f"Ghép công thức đúng: ({a}-{b})² bằng bao nhiêu?", ans, f"(a-b)²=a²-2ab+b²={ans}.", [a*a-b*b,(a-b),a*a+b*b])

    def identity_mystery(self,d):
        a=random.randint(3,10); b=random.randint(1,5); value=a*a+2*a*b+b*b
        return self.base(f"Một công thức bí ẩn cho giá trị {value} có dạng ({a}+{b})². Kết quả cần xác nhận là?", value, f"{a}²+2·{a}·{b}+{b}²=({a}+{b})²={value}.", [value-2,value+2,a+b])

    # ---------- PHÂN THỨC ----------
    def fraction_simplify(self,d):
        k=random.randint(2,9); a=random.randint(2,9); b=random.randint(2,9)
        return self.base(f"Với x≠0, rút gọn phân thức {k*a}x/{k*b}x.", _fmt_fraction(a,b), f"Khử nhân tử chung {k}x: được {a}/{b}.", [_fmt_fraction(k*a,k*b),_fmt_fraction(a,k*b),_fmt_fraction(k*a,b)])

    def fraction_condition(self,d):
        a=random.randint(1,8); b=random.randint(1,8); c=random.randint(1,8)
        return self.base(f"Phân thức {a}/(x-{b}) xác định khi điều kiện nào đúng?", f"x ≠ {b}", f"Mẫu số phải khác 0: x-{b}≠0 nên x≠{b}.", [f"x = {b}",f"x > {b}",f"x < {b}"])

    def fraction_speed(self,d):
        dist=random.randint(60,240); time=random.randint(2,6); speed=Fraction(dist,time)
        return self.base(f"Một xe đi {dist} km trong {time} giờ. Vận tốc trung bình là bao nhiêu km/h?", _fmt_fraction(speed), f"v=s/t={dist}/{time}={_fmt_fraction(speed)} km/h.", [str(dist-time),str(dist+time),_fmt_fraction(Fraction(dist,time+1))])

    # ---------- HÌNH HỌC ----------
    def geometry_angle(self,d):
        a=random.randint(35,75); b=random.randint(35,75); c=180-a-b
        if c<=0: return self.geometry_angle(d)
        return self.base(f"Trong tam giác ABC, biết ∠A={a}° và ∠B={b}°. Tính ∠C.", c, f"Tổng ba góc tam giác là 180°, nên C=180-{a}-{b}={c}°.", [c+5,c-5,180-c])

    def geometry_length(self,d):
        a=random.randint(3,12); b=random.randint(4,12); h=math.sqrt(a*a+b*b)
        if int(h)!=h: return self.geometry_length(d)
        return self.base(f"Một tam giác vuông có hai cạnh góc vuông dài {a} và {b}. Cạnh huyền dài bao nhiêu?", int(h), f"Theo Pitago: c²={a}²+{b}²={a*a+b*b}, nên c={int(h)}.", [int(h)+1,int(h)-1,a+b])

    def geometry_map(self,d):
        x1,y1=random.randint(0,8),random.randint(0,8); x2,y2=x1+random.randint(3,8),y1+random.randint(3,8)
        d2=(x2-x1)**2+(y2-y1)**2
        return self.base(f"Trên bản đồ tọa độ, A({x1},{y1}) và B({x2},{y2}). Tính AB².", d2, f"AB²=({x2}-{x1})²+({y2}-{y1})²={d2}.", [d2+1,d2-1,(x2-x1)+(y2-y1)])

    # ---------- THỐNG KÊ ----------
    def statistics_chart(self,d):
        data=[random.randint(4,18) for _ in range(5)]; total=sum(data)
        return self.base(f"Một biểu đồ có 5 nhóm với số liệu {data}. Tổng số quan sát là bao nhiêu?", total, f"Cộng các cột: {'+'.join(map(str,data))}={total}.", [total+1,total-1,max(data)])

    def statistics_data(self,d):
        data=sorted(random.sample(range(3,25),5)); med=data[2]
        return self.base(f"Bộ số liệu đã sắp xếp: {data}. Trung vị là?", med, "Với 5 số đã sắp xếp, trung vị là số đứng giữa.", [data[1],data[3],sum(data)//5])

    def statistics_challenge(self,d):
        data=[random.randint(4,15) for _ in range(6)]; mean=Fraction(sum(data),len(data));
        return self.base(f"Mẫu số liệu gồm {data}. Tính số trung bình cộng.", _fmt_fraction(mean), f"x̄={sum(data)}/{len(data)}={_fmt_fraction(mean)}.", [_fmt_fraction(mean+1),_fmt_fraction(mean-1),str(max(data))])

# Additional varied structures. They are deliberately attached to individual games
# so repeated play does not collapse into a single numeric template.
def _install_variants():
    B = GameQuestionBank

    def marble_v(self,d):
        r,b=random.randint(3,8),random.randint(3,8); t=r+b; a=Fraction(r*(r-1),t*(t-1))
        return self.base(f"Trong túi có {r} bi đỏ và {b} bi xanh. Lấy 2 viên không hoàn lại. Xác suất cả hai đều đỏ là?",_fmt_fraction(a),f"P={r}/{t}×{r-1}/{t-1}={_fmt_fraction(a)}.",[f"{_fmt_fraction(Fraction(r,t))}","1/2","1/3"])
    def team_v(self,d):
        n=random.randint(8,15); k=random.randint(3,5); ans=math.comb(n,k)-math.comb(n-1,k)
        return self.base(f"Có {n} học sinh, trong đó An không được chọn. Chọn {k} bạn lập đội. Có bao nhiêu cách?",ans,f"Không chọn An nên chọn k người từ n-1 người: C({n-1},{k})={ans}.",[math.comb(n,k),ans+1,max(1,ans-1)])
    def choice_v(self,d):
        p=random.randint(4,8); q=random.randint(3,7); ans=p*q-p
        return self.base(f"Có {p} món chính và {q} đồ uống. Một suất gồm 1 món chính và 1 đồ uống, nhưng món chính số 1 không dùng với bất kỳ đồ uống nào. Có bao nhiêu suất hợp lệ?",ans,f"Tổng {p}q, loại {q} suất chứa món bị cấm: {p*q}-{q}={ans}.",[p*q,ans+q,ans-1])
    def hunt_v(self,d):
        n=random.randint(8,14); k=random.randint(2,4); ans=math.comb(n,k)
        return self.base(f"Săn tổ hợp: có {n} thẻ khác nhau, chọn {k} thẻ không xét thứ tự. Số nhóm có thể tạo là?",ans,f"C({n},{k})={ans}.",[math.perm(n,k),ans+1,ans-k])

    def position_v(self,d):
        n=random.randint(6,9); ans=2*math.factorial(n-1)
        return self.base(f"Có {n} người xếp hàng. Hai bạn A và B phải đứng cạnh nhau. Có bao nhiêu cách xếp?",ans,f"Gộp A,B thành một khối: 2·({n}-1)!={ans}.",[math.factorial(n),math.factorial(n-1),ans+2])
    def code_v(self,d):
        n=random.randint(5,9); k=random.randint(3,5); ans=math.perm(n,k)
        return self.base(f"Một mã gồm {k} ký tự khác nhau lấy từ {n} ký tự. Không được lặp. Có bao nhiêu mã?",ans,f"A({n},{k})={ans}.",[n**k,math.comb(n,k),ans+n])
    def order_v(self,d):
        n=random.randint(5,8); ans=math.factorial(n)//2
        return self.base(f"Có {n} cuốn sách khác nhau xếp thành hàng, nhưng hai cuốn Toán và Văn phải đứng ở hai đầu. Có bao nhiêu cách?",ans,f"Hai đầu có 2 cách đặt, {n-2} cuốn còn lại xếp ({n}-2)!: 2·({n-2})!={ans}.",[math.factorial(n),math.factorial(n-2),ans+2])

    def point_v(self,d):
        a=random.randint(-5,5) or 2; b=random.randint(-7,7); x=random.randint(-5,5); y=a*x+b
        return self.base(f"Điểm A({x};{y}) có thuộc đường thẳng y={a}x {_sign(b)} không?", "Có", f"Thay x={x} được y={a*x+b}={y}, nên điểm thuộc đồ thị.",["Không","Chỉ khi x=0","Không đủ dữ kiện"])
    def inter_v(self,d):
        x=random.randint(-4,5); m1=random.choice([1,2,3]); m2=random.choice([-3,-2,-1]); b1=random.randint(-5,5); b2=(m1-m2)*x+b1
        return self.base(f"Hai đường thẳng y={m1}x {_sign(b1)} và y={m2}x {_sign(b2)} cắt nhau tại điểm có hoành độ bằng bao nhiêu?", x, f"Đặt hai vế bằng nhau: ({m1}-{m2})x={b2-b1}, suy ra x={x}.",[x+1,x-1,0])
    def graph_v(self,d):
        a=random.choice([1,2,-1,-2]); h=random.randint(-3,3); k=random.randint(-5,5); x=h+1; y=a+k
        return self.base(f"Parabol y={a}(x-{h})² {_sign(k)}. Khi x={x}, y bằng bao nhiêu?",y,f"y={a}·1²+{k}={y}.",[y+1,y-1,k])

    def inv_v(self,d):
        x=random.randint(2,9); y=random.randint(2,9); s=x+y; p=x*y
        return self.base(f"Một cuộc điều tra cho biết tổng của hai số là {s} và tích của chúng là {p}. Cặp số dương là?",f"({x};{y})",f"Hai số {x},{y} có tổng {s} và tích {p}.",[f"({x+1};{y-1})",f"({y};{x+1})",f"({x};{y+1})"])
    def value_v(self,d):
        x=random.randint(1,9); y=random.randint(1,9); a=random.randint(2,5); b=random.randint(1,4); c=a*x+b*y
        return self.base(f"Biết {a}x+{b}y={c} và x={x}. Tìm y.",y,f"{b}y={c}-{a}·{x}, nên y={y}.",[y+1,y-1,x])
    def match_v(self,d):
        x=random.randint(2,8); y=random.randint(2,8); s=x+y; p=x-y
        return self.base(f"Cặp số nào thỏa đồng thời x+y={s} và x-y={p}?",f"({x};{y})",f"Cộng hai phương trình: 2x={s+p}, nên x={x}, y={y}.",[f"({y};{x})",f"({x+1};{y})",f"({x};{y+1})"])

    def root_v(self,d):
        r=random.randint(-8,8); a=random.randint(1,4); b=-a*r; c=0
        return self.base(f"Phương trình {a}x² {_sign(b)}x=0 có một nghiệm khác 0 là?",r,f"x({a}x{_sign(b)})=0 nên nghiệm khác 0 là x={r}.",[0,r+1,r-1])
    def matchq_v(self,d):
        r1=random.randint(-6,6); r2=random.randint(-6,6); B=-(r1+r2); C=r1*r2
        return self.base(f"Nếu phương trình x² {_sign(B)}x {_sign(C)}=0 có hai nghiệm {r1},{r2}, tích hai nghiệm là?",C,f"Theo Viète, tích nghiệm = C={C}.",[r1+r2,B,C+1])
    def unlockq_v(self,d):
        a=random.choice([1,2,3]); c=random.randint(1,8); b=2*math.isqrt(a*c)
        # choose b so delta is easy but nonnegative
        D=b*b-4*a*c
        return self.base(f"Mở khóa: Δ của {a}x² {_sign(b)}x+{c}=0 bằng bao nhiêu?",D,f"Δ={b}²-4·{a}·{c}={D}.",[D+4,max(0,D-4),b*b])

    def safe_v(self,d):
        lo=random.randint(-8,1); hi=lo+random.randint(4,9); x=random.randint(lo,hi)
        return self.base(f"Điểm an toàn thỏa {lo}≤x≤{hi}. Giá trị x={x} có nằm trong vùng an toàn không?","Có",f"{x} nằm giữa {lo} và {hi}.",["Không","Chỉ khi x={}","Không xác định"])
    def interval_v(self,d):
        a=random.randint(2,6); r=Fraction(random.randint(-8,8),a); b=-a*r
        return self.base(f"Bất phương trình {a}x {_sign(int(b))} ≥ 0 có mốc nghiệm nào?",_fmt_fraction(r),f"{a}x{_sign(int(b))}≥0, mốc là x={_fmt_fraction(r)}.",[_fmt_fraction(r+1),_fmt_fraction(r-1),"0"])
    def barrier_v(self,d):
        a=random.randint(2,7); limit=random.randint(5,15); b=random.randint(-5,5); x=math.ceil((limit-b)/a)
        return self.base(f"Muốn vượt rào cần {a}x {_sign(b)} ≥ {limit}. Giá trị nguyên nhỏ nhất của x là?",x,f"x≥({limit-b})/{a}, nên x nguyên nhỏ nhất là {x}.",[x-1,x+1,max(0,x-2)])

    def rule_v(self,d):
        a=random.randint(1,8); d0=random.randint(2,5); n=random.randint(6,10); terms=[a+i*d0 for i in range(4)]
        return self.base(f"Dãy {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ... có số hạng thứ {n} bằng?",a+(n-1)*d0,f"Mỗi lần tăng {d0}, nên a{n}={a} + ({n}-1)·{d0}.",[a+n*d0,a+(n-2)*d0,a*n])
    def fill_v(self,d):
        a=random.randint(1,7); q=random.choice([2,3]); n=random.randint(5,8); ans=a*q**(n-1)
        return self.base(f"Dãy nhân {a}, {a*q}, {a*q*q}, ... có số hạng thứ {n} bằng?",ans,f"CSN với a1={a}, q={q}: a{n}={a}·{q}^{n-1}={ans}.",[ans*q,ans//q if ans%q==0 else ans+q,a+(n-1)*q])
    def race_v(self,d):
        a=random.randint(3,9); q=random.choice([2,3]); n=random.randint(4,7); ans=a*q**(n-1)
        return self.base(f"Trong đường đua, điểm thưởng tăng theo CSN: lượt 1 là {a}, công bội {q}. Điểm ở lượt {n} là?",ans,f"a{n}={a}·{q}^{n-1}={ans}.",[ans+q,ans-q,a*n])

    def div_find_v(self,d):
        n=random.randint(100,999); return self.base(f"Số {n} chia hết cho 3 khi nào? Tổng các chữ số của {n} bằng bao nhiêu?",sum(map(int,str(n))),"Tính tổng các chữ số để áp dụng dấu hiệu chia hết cho 3.",[sum(map(int,str(n)))+3,max(0,sum(map(int,str(n)))-3),n%9])
    def div_select_v(self,d):
        m=random.choice([4,8,9,11]); q=random.randint(10,30); n=m*q
        return self.base(f"Chọn số chia hết cho {m}: số nào sau đây đúng?",n,f"{n}={m}×{q}.",[n+1,n-2,n+2])
    def div_unlock_v(self,d):
        m=random.choice([3,5,9]); a=random.randint(1,9); b=random.randint(0,9); c=m-((100*a+10*b)%m); c%=m
        n=100*a+10*b+c
        return self.base(f"Phá khóa: số có dạng {a}{b}{c} cần chia hết cho {m}. Chữ số hàng đơn vị là?",c,f"Chọn c để {100*a+10*b+c} chia hết cho {m}, được c={c}.",[ (c+1)%10,(c+2)%10,(c+5)%10])

    def rem_draw_v(self,d):
        n=random.randint(100,900); m=random.randint(4,15); r=n%m
        return self.base(f"Bốc số {n}. Khi chia số đó cho {m}, thương nguyên là bao nhiêu?",n//m,f"{n}={n//m}·{m}+{r}.",[n//m+1,max(0,n//m-1),r])
    def rem_hunt_v(self,d):
        m=random.randint(5,12); r=random.randint(1,m-1); k=random.randint(10,30); n=m*k+r
        return self.base(f"Tìm số nhỏ nhất lớn hơn {m*k} và chia cho {m} dư {r}.",n,f"Số cần tìm là {m}·{k}+{r}={n}.",[n+1,n-1,n+m])
    def rem_mod_v(self,d):
        m=random.randint(5,12); a=random.randint(20,70); b=random.randint(20,70); r=((a%m)*(b%m))%m
        return self.base(f"Tính số dư của {a}×{b} khi chia cho {m}.",r,f"Lấy các số dư modulo {m}: {a}%{m} và {b}%{m}, nhân rồi lấy modulo {m} được {r}.",[(r+1)%m,(r+2)%m,(r+3)%m])

    def radical_hunt_v(self,d):
        k=random.randint(2,7); s=random.choice([2,3,5,6]); n=k*k*s
        return self.base(f"Săn căn: √{n} được viết dưới dạng a√{s}. Hệ số a là?",k,f"{n}={k}²·{s}, nên a={k}.",[k+1,k-1,s])
    def radical_simplify_v(self,d):
        s=random.choice([2,3,5,6]); a=random.randint(2,8); b=random.randint(1,5); coeff=a+b; ans=f"{coeff}√{s}"
        return self.base(f"Tính {a}√{s}+{b}√{s}.",ans,f"Hai căn đồng dạng nên cộng hệ số: ({a}+{b})√{s}={coeff}√{s}.",[f"{a*b}√{s}",f"{coeff+1}√{s}",f"{abs(a-b)}√{s}"])
    def radical_unlock_v(self,d):
        s=random.choice([2,3,5]); a=random.randint(2,7); b=random.randint(1,5); ans=(a+b)
        return self.base(f"Mở khóa: hệ số của √{s} trong {a}√{s}+{b}√{s} là?",ans,f"Cộng hệ số {a}+{b}={ans}.",[ans+1,ans-1,a*b])

    def identity_break_v(self,d):
        a=random.randint(3,9); b=random.randint(1,5); ans=(a-b)*(a+b)
        return self.base(f"Dùng hiệu hai bình phương để tính {a}²-{b}².",ans,f"a²-b²=(a-b)(a+b)={a-b}·{a+b}={ans}.",[a*a+b*b,a-b,a+b])
    def identity_match_v(self,d):
        a=random.randint(2,8); b=random.randint(1,6); ans=a*a-2*a*b+b*b
        return self.base(f"Biểu thức {a*a}-2·{a}·{b}+{b*b} được viết gọn thành?",ans,f"Đó là ({a}-{b})²={ans}.",[a+b,a*a+b*b,a*a-b*b])
    def identity_mystery_v(self,d):
        a=random.randint(2,7); b=random.randint(2,6); ans=(a+b)*(a-b)
        return self.base(f"Công thức bí ẩn: ({a}+{b})({a}-{b}) bằng bao nhiêu?",ans,f"Dùng a²-b²: {a}²-{b}²={ans}.",[a+b,a-b,a*a+b*b])

    def fraction_simplify_v(self,d):
        a=random.randint(2,8); b=random.randint(2,8); k=random.randint(2,5); ans=Fraction(a,b)
        return self.base(f"Rút gọn phân thức ({k*a}x²)/({k*b}x²), với x≠0.",_fmt_fraction(ans),f"Khử kx², còn {a}/{b}={_fmt_fraction(ans)}.",[_fmt_fraction(Fraction(k*a,k*b)),_fmt_fraction(Fraction(a,k*b)),_fmt_fraction(Fraction(k*a,b))])
    def fraction_condition_v(self,d):
        a=random.randint(1,9); b=random.randint(1,9); c=random.randint(1,9)
        return self.base(f"Phân thức ({a}x+{b})/(x-{c}) xác định khi nào?",f"x ≠ {c}",f"Mẫu x-{c} phải khác 0 nên x≠{c}.",[f"x={c}",f"x>{c}",f"x<{c}"])
    def fraction_speed_v(self,d):
        d1=random.randint(60,180); t1=random.randint(2,5); d2=random.randint(60,180); t2=random.randint(2,5); ans=Fraction(d1+d2,t1+t2)
        return self.base(f"Một xe đi {d1} km trong {t1} giờ rồi {d2} km trong {t2} giờ. Vận tốc trung bình của cả hành trình là?",_fmt_fraction(ans),f"v_tb=(s1+s2)/(t1+t2)=({d1}+{d2})/({t1}+{t2})={_fmt_fraction(ans)} km/h.",[str(d1//t1),str(d2//t2),_fmt_fraction(Fraction(d1+d2,t1+t2+1))])

    def angle_v(self,d):
        a=random.randint(40,80); c=random.randint(30,70); b=180-a-c
        if b<=0:return self.angle_v(d)
        return self.base(f"Hai góc trong tam giác là {a}° và {c}°. Góc còn lại bằng?",b,f"180-{a}-{c}={b}°.",[b+5,b-5,180-b])
    def length_v(self,d):
        a=random.randint(3,9); b=random.randint(3,9); ans=a+b
        return self.base(f"Một đoạn đường gồm hai chặng dài {a} km và {b} km. Tổng chiều dài là?",ans,f"{a}+{b}={ans} km.",[ans+1,abs(a-b),a*b])
    def map_v(self,d):
        x1,y1=random.randint(0,6),random.randint(0,6); dx,dy=random.randint(2,6),random.randint(2,6); x2,y2=x1+dx,y1+dy; ans=dx+dy
        return self.base(f"Trên bản đồ ô vuông, đi từ A({x1},{y1}) đến B({x2},{y2}) theo hai trục. Tổng số đơn vị phải đi là?",ans,f"Đi ngang {dx} và dọc {dy}, tổng {dx}+{dy}={ans}.",[ans+1,dx*dy,abs(dx-dy)])

    def chart_v(self,d):
        vals=[random.randint(5,20) for _ in range(4)]; total=sum(vals); largest=max(vals)
        return self.base(f"Biểu đồ có bốn cột với số liệu {vals}. Cột cao nhất biểu diễn bao nhiêu quan sát?",largest,f"Giá trị lớn nhất trong bảng là {largest}.",[min(vals),sum(vals)//4,total])
    def data_v(self,d):
        data=sorted(random.sample(range(2,30),6)); q1=data[1]; q3=data[4]
        return self.base(f"Số liệu đã sắp xếp {data}. Hiệu giữa tứ phân vị thứ ba và thứ nhất là?",q3-q1,f"Theo cách lấy vị trí trong mẫu 6 số: Q1={q1}, Q3={q3}, nên IQR={q3-q1}.",[q3,q1,q3+q1])
    def challenge_v(self,d):
        data=[random.randint(4,16) for _ in range(5)]; mean=Fraction(sum(data),5); total=sum(data)
        return self.base(f"Mẫu số liệu {data}. Nếu thêm một giá trị bằng trung bình hiện tại, trung bình mới là?",_fmt_fraction(mean),f"Thêm đúng giá trị trung bình không làm thay đổi trung bình: vẫn là {_fmt_fraction(mean)}.",[str(mean+1),str(mean-1),str(total+1)])

    variants={
      'Bốc bi':marble_v,'Chọn đội':team_v,'Ghép lựa chọn':choice_v,'Săn tổ hợp':hunt_v,
      'Xếp vị trí':position_v,'Mật mã':code_v,'Sắp thứ tự':order_v,
      'Bắt điểm':point_v,'Tìm giao điểm':inter_v,'Đồ thị bí ẩn':graph_v,
      'Điều tra':inv_v,'Tìm giá trị':value_v,'Ghép đáp án':match_v,
      'Săn nghiệm':root_v,'Ghép nghiệm':matchq_v,'Mở khóa':unlockq_v,
      'Vùng an toàn':safe_v,'Chọn khoảng':interval_v,'Vượt rào':barrier_v,
      'Tìm quy luật':rule_v,'Điền số':fill_v,'Đường đua dãy số':race_v,
      'Truy tìm số':div_find_v,'Chọn số':div_select_v,'Phá khóa':div_unlock_v,
      'Bốc số':rem_draw_v,'Săn số dư':rem_hunt_v,'Thử thách modulo':rem_mod_v,
      'Săn căn':radical_hunt_v,'Rút gọn nhanh':radical_simplify_v,'Mở khóa căn thức':radical_unlock_v,
      'Phá biểu thức':identity_break_v,'Ghép công thức':identity_match_v,'Công thức bí ẩn':identity_mystery_v,
      'Rút gọn':fraction_simplify_v,'Tìm điều kiện':fraction_condition_v,'Phân thức tốc độ':fraction_speed_v,
      'Tìm góc':angle_v,'Săn độ dài':length_v,'Bản đồ hình học':map_v,
      'Đọc biểu đồ':chart_v,'Săn số liệu':data_v,'Thử thách thống kê':challenge_v,
    }
    B._variants=variants
    old_generate=B.generate
    def generate(self,game_id,grade,difficulty):
        fn=self._builders.get(game_id)
        if not fn: return None
        # Every game has a primary structure plus a second, game-specific structure.
        # Probability games already contain several native variants, so retain their richer mix.
        if game_id in self._variants:
            # 3 mức độ: Dễ ưu tiên cấu trúc nền, Khá cân bằng, Khó ưu tiên
            # biến thể nâng cao để đề có nhiều bước và điều kiện hơn.
            rates = {"easy": 0.20, "medium": 0.52, "hard": 0.82}
            rate = rates.get(difficulty, 0.52)
            if game_id in {"Bốc bi", "Xúc xắc", "Chọn tình huống"}:
                rate *= 0.75
            if random.random() < rate:
                return self._variants[game_id](self,difficulty)
        return fn(difficulty)
    B.generate=generate

_install_variants()
