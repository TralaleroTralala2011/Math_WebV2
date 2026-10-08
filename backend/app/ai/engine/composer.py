import json, random, re
from fractions import Fraction
from pathlib import Path

class TemplateComposer:
    """Internal question composer.

    The template bank is the large knowledge database. This layer selects a
    problem family, question style and context, then composes a finished item
    from an already verified mathematical generator. It never uses an external
    LLM or network service.
    """

    THEORY = {
        'Xác suất': [
            ('Trong mô hình xác suất cổ điển, xác suất của một biến cố bằng gì?',
             'Số kết quả thuận lợi chia cho số kết quả có thể',
             ['Số kết quả có thể chia cho số kết quả thuận lợi','Tổng số kết quả thuận lợi và không thuận lợi','Hiệu giữa hai số trên']),
            ('Xác suất của một biến cố chắc chắn bằng bao nhiêu?', '1', ['0','1/2','Không xác định']),
            ('Xác suất của một biến cố không thể bằng bao nhiêu?', '0', ['1','1/2','Không xác định'])
        ],
        'Tổ hợp': [
            ('Khi chọn một nhóm và không xét thứ tự, công cụ đếm phù hợp là gì?', 'Tổ hợp', ['Chỉnh hợp','Hoán vị','Quy tắc cộng']),
            ('Trong tổ hợp C(n,k), điều gì thay đổi khi đổi thứ tự các phần tử đã chọn?', 'Không tạo ra cách chọn mới', ['Luôn tạo ra cách chọn mới','Chỉ tạo ra hai cách mới','Làm mất một phần tử'])
        ],
        'Chỉnh hợp': [
            ('Khi chọn k phần tử rồi xếp vào k vị trí khác nhau, công cụ đếm phù hợp là gì?', 'Chỉnh hợp', ['Tổ hợp','Hoán vị toàn bộ n phần tử','Quy tắc cộng']),
            ('Trong bài toán xếp vị trí, vì sao thứ tự quan trọng?', 'Vì đổi vị trí tạo thành cách sắp xếp khác', ['Vì số phần tử thay đổi','Vì mọi phần tử phải giống nhau','Vì không cần xét vị trí'])
        ],
        'Hàm số': [
            ('Điểm (x₀,y₀) thuộc đồ thị y=f(x) khi nào?', 'y₀=f(x₀)', ['x₀=f(y₀)','y₀=x₀+f(x₀)','f(y₀)=0']),
            ('Đồ thị hàm số bậc hai có dạng cơ bản nào?', 'Parabol', ['Đường tròn','Đường thẳng luôn luôn','Elip'])
        ],
        'Hệ phương trình': [
            ('Nghiệm của hệ phương trình hai ẩn là gì?', 'Cặp giá trị đồng thời thỏa mãn mọi phương trình của hệ', ['Cặp bất kỳ thỏa một phương trình','Một giá trị chỉ thỏa phương trình đầu','Một biểu thức không cần kiểm tra']),
            ('Một hệ hai phương trình có nghiệm duy nhất khi hai đường thẳng biểu diễn chúng thế nào?', 'Cắt nhau tại một điểm', ['Song song phân biệt','Trùng nhau','Không có điểm biểu diễn'])
        ],
        'Phương trình bậc hai': [
            ('Biệt thức của ax²+bx+c=0 là gì?', 'Δ=b²−4ac', ['Δ=b²+4ac','Δ=2b−4ac','Δ=a²−bc']),
            ('Nếu Δ=0 thì phương trình bậc hai có dạng nghiệm nào?', 'Một nghiệm kép', ['Hai nghiệm phân biệt','Vô nghiệm trong mọi trường hợp','Ba nghiệm thực'])
        ],
        'Bất phương trình': [
            ('Khi nhân hoặc chia một bất phương trình cho số âm, dấu bất phương trình thay đổi thế nào?', 'Đổi chiều', ['Giữ nguyên','Biến mất','Luôn thành dấu bằng']),
            ('Nghiệm của bất phương trình là gì?', 'Các giá trị làm bất phương trình đúng', ['Mọi giá trị của biến','Chỉ giá trị nguyên','Chỉ giá trị dương'])
        ],
        'Dãy số': [
            ('Số hạng tổng quát của một dãy số dùng để làm gì?', 'Xác định số hạng theo vị trí n', ['Tính diện tích hình','Xác định góc','Tính xác suất']),
            ('Trong một dãy số, chỉ số n thường biểu thị điều gì?', 'Vị trí của số hạng', ['Giá trị của số hạng','Tổng các số hạng','Số lượng biến'])
        ],
        'Chia hết': [
            ('Một số chia hết cho 3 khi nào?', 'Tổng các chữ số của nó chia hết cho 3', ['Chữ số cuối chia hết cho 3','Hai chữ số đầu chia hết cho 3','Số đó phải là số chẵn']),
            ('Một số chia hết cho 2 khi nào?', 'Chữ số tận cùng là 0, 2, 4, 6 hoặc 8', ['Tổng chữ số chia hết cho 2','Chữ số đầu là số chẵn','Có đúng hai chữ số'])
        ],
        'Chia dư': [
            ('Số dư khi chia một số nguyên cho m phải nằm trong khoảng nào?', 'Từ 0 đến m−1', ['Từ 1 đến m','Từ −m đến m','Mọi số nguyên']),
            ('Nếu a chia hết cho m thì số dư của a khi chia cho m là bao nhiêu?', '0', ['1','m','−1'])
        ],
        'Căn thức': [
            ('Với căn thức √A trong tập số thực, điều kiện cơ bản của A là gì?', 'A ≥ 0', ['A > 0','A ≤ 0','A ≠ 0']),
            ('√(a²) bằng gì khi a là số thực?', '|a|', ['a²','a','−a'])
        ],
        'Hằng đẳng thức': [
            ('Hằng đẳng thức (a+b)² bằng gì?', 'a²+2ab+b²', ['a²+b²','a²−2ab+b²','a²+ab+b²']),
            ('Hằng đẳng thức a²−b² phân tích thành gì?', '(a−b)(a+b)', ['(a−b)²','(a+b)²','a(a−b)'])
        ],
        'Phân thức đại số': [
            ('Phân thức A/B xác định khi điều kiện nào đúng?', 'B ≠ 0', ['A ≠ 0','A=B','B=0']),
            ('Muốn rút gọn phân thức, có thể làm gì với tử và mẫu?', 'Chia cả tử và mẫu cho cùng một nhân tử khác 0', ['Chỉ chia tử','Chỉ chia mẫu','Cộng cùng một số vào cả hai'])
        ],
        'Hình học': [
            ('Tổng ba góc trong một tam giác bằng bao nhiêu?', '180°', ['90°','270°','360°']),
            ('Trong tam giác vuông, định lý Pythagore liên hệ ba cạnh như thế nào?', 'Bình phương cạnh huyền bằng tổng bình phương hai cạnh góc vuông', ['Cạnh huyền bằng tổng hai cạnh góc vuông','Tổng ba cạnh bằng 180°','Hai cạnh góc vuông bằng nhau'])
        ],
        'Thống kê': [
            ('Trung bình cộng của một mẫu số liệu được tính bằng gì?', 'Tổng các giá trị chia cho số giá trị', ['Giá trị lớn nhất trừ nhỏ nhất','Giá trị giữa duy nhất','Tích các giá trị']),
            ('Trung vị của mẫu số liệu đã sắp xếp là gì?', 'Giá trị nằm giữa hoặc trung bình của hai giá trị giữa', ['Luôn là giá trị lớn nhất','Luôn là giá trị nhỏ nhất','Luôn bằng trung bình cộng'])
        ],
}

class TemplateBank:
    def __init__(self, path: Path):
        self.data=json.loads(path.read_text(encoding='utf-8'))

    def get(self, game):
        return self.data['games'].get(game)

    def choose(self, game, recent=None, difficulty="medium"):
        item=self.get(game)
        if not item: return None
        recent=set(recent or [])
        families=[x for x in item['families'] if x not in recent] or item['families']
        styles=item['question_styles']
        if difficulty == "easy":
            preferred={"knowledge", "theory_check", "calculation"}
            styles=[x for x in styles if x in preferred] or styles
        elif difficulty == "medium":
            preferred={"calculation", "application", "scenario", "real_life", "reasoning"}
            styles=[x for x in styles if x in preferred] or styles
        else:
            preferred={"reasoning", "reverse", "multi_step", "mistake_check", "application"}
            styles=[x for x in styles if x in preferred] or styles
        return {
            'family': random.choice(families),
            'style': random.choice(styles),
            'context': random.choice(item['contexts']),
            'topic': item['topic'],
        }

class QuestionComposer:
    def __init__(self, bank: TemplateBank):
        self.bank=bank

    def compose(self, q, game, recent=None, difficulty="medium"):
        meta=self.bank.choose(game, recent, difficulty)
        if not meta:
            return q
        q['template_family']=meta['family']
        q['generation_style']=meta['style']
        q['context']=meta['context']
        q['template_source']='template_bank'
        return q

    def theory_question(self, game, topic, generator):
        facts=self.bank.get(game)
        if not facts: return None
        topic_name=facts['topic']
        pool=TemplateComposer.THEORY.get(topic_name)
        if not pool: return None
        question,answer,wrong=random.choice(pool)
        return generator._base(question,answer,
            f"Kiến thức nền: {answer}.", wrong,
            "Nhớ lại định nghĩa hoặc quy tắc cốt lõi của kiến thức này.")

    def derived_task(self, q, topic, game, mode):
        """Create a second mathematical task from a verified result.

        The original problem remains in the prompt, so the derived question is
        self-contained. Only exact, safely computable transformations are used.
        """
        raw=q.get('answer')
        try:
            v=Fraction(str(raw))
        except Exception:
            return None
        base=q['question'].rstrip(' .?')
        if mode == 'percent' and 0 <= v <= 1:
            pct=v*100
            return {
                'question': base + ". Giá trị đó tương đương bao nhiêu phần trăm?",
                'answer': f"{pct}%",
                'solution': f"Đổi sang phần trăm: {v} × 100% = {pct}%.",
                'distractors':[f"{v}%",f"{pct+10}%",f"{max(0,pct-10)}%"],
                'hint':'Đổi một số thập phân hoặc phân số thành phần trăm bằng cách nhân với 100.'
            }
        if mode == 'complement' and topic.startswith('Xác suất') and 0 <= v <= 1:
            a=1-v
            return {
                'question': base + ". Xác suất của biến cố đối là bao nhiêu?",
                'answer': str(a.numerator) if a.denominator==1 else f"{a.numerator}/{a.denominator}",
                'solution': f"Biến cố đối có xác suất 1 − P = 1 − {v} = {a}.",
                'distractors':[str(v),str(1+v),str(abs(1-v/2))],
                'hint':'Hai biến cố bổ sung có tổng xác suất bằng 1.'
            }
        if mode == 'parity' and v.denominator == 1:
            ans='chẵn' if v.numerator % 2 == 0 else 'lẻ'
            return {
                'question': base + f". Giá trị vừa tìm được là số {ans} hay số {('lẻ' if ans=='chẵn' else 'chẵn')}?",
                'answer': ans,
                'solution': f"Giá trị là {v.numerator}, và {v.numerator} là số {ans}.",
                'distractors':['số nguyên tố','số âm','không phải số nguyên'],
                'hint':'Kiểm tra chữ số tận cùng của số nguyên.'
            }
        if mode == 'sign' and v.denominator == 1:
            ans='dương' if v>0 else ('âm' if v<0 else 'bằng 0')
            others=[x for x in ['dương','âm','bằng 0'] if x!=ans][:2]
            return {
                'question': base + ". Kết quả thu được thuộc loại nào?",
                'answer': ans,
                'solution': f"Kết quả là {v.numerator}, nên nó {ans}.",
                'distractors':others+['không xác định'],
                'hint':'Xét dấu của kết quả cuối cùng.'
            }
        if mode == 'tuple_sum':
            m=re.search(r"\(\s*(-?\d+)\s*[,;]\s*(-?\d+)\s*\)", str(raw))
            if m:
                x,y=int(m.group(1)),int(m.group(2)); val=x+y
                return {'question': base + f". Tổng hai giá trị trong nghiệm là bao nhiêu?", 'answer': str(val), 'solution': f"Nghiệm là ({x};{y}), nên tổng bằng {x}+{y}={val}.", 'distractors':[str(x),str(y),str(x-y)], 'hint':'Lấy hai thành phần của nghiệm và cộng chúng.'}
        if mode == 'tuple_product':
            m=re.search(r"\(\s*(-?\d+)\s*[,;]\s*(-?\d+)\s*\)", str(raw))
            if m:
                x,y=int(m.group(1)),int(m.group(2)); val=x*y
                return {'question': base + f". Tích hai giá trị trong nghiệm là bao nhiêu?", 'answer': str(val), 'solution': f"Nghiệm là ({x};{y}), nên tích bằng {x}×{y}={val}.", 'distractors':[str(x+y),str(x-y),str(abs(x*y)+1)], 'hint':'Lấy hai thành phần của nghiệm và nhân chúng.'}

        if mode == 'compare' and v.denominator == 1:
            k=abs(v.numerator)+random.randint(1,4)
            if v.numerator<k: ans='nhỏ hơn'
            elif v.numerator>k: ans='lớn hơn'
            else: ans='bằng'
            return {
                'question': base + f". So sánh kết quả với {k}: kết quả ... {k}.",
                'answer': ans,
                'solution': f"Kết quả là {v.numerator}, nên {v.numerator} {('<' if ans=='nhỏ hơn' else '>' if ans=='lớn hơn' else '=')} {k}.",
                'distractors':[x for x in ['nhỏ hơn','lớn hơn','bằng'] if x!=ans] + ['không thể kết luận'],
                'hint':'Lấy kết quả của bài toán và so sánh trực tiếp với số đã cho.'
            }
        return None
