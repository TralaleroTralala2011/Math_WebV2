"""Export ORIGINAL grade-10/11/12 review candidates outside all web-served directories.

Usage: python tools/export_v20_private_review.py --output /ABSOLUTE/OUTSIDE/PROJECT
The generated files contain full answer keys. Never host publicly.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.qf2_verified_generators import GENERATORS, PLACEMENT_GENERATORS
from app.placement_v20_original_forms import GENERATORS as V20_GENERATORS
from app.question_factory_v2_routes import Candidate, build_parabola_vertex_candidate
from app.ai.engine.validator import options_equivalent


def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def export(output):
    output=output.resolve()
    if output==ROOT or ROOT in output.parents:
        raise ValueError('Private answer key must NOT be inside the public MATH_WEB root')
    output.mkdir(parents=True,exist_ok=True)
    os.chmod(output,0o700)
    raw=[('parabola-vertex',build_parabola_vertex_candidate().model_dump(), 'V16')]
    raw.extend((name,fn(),'V16') for name,fn in GENERATORS.items())
    raw.extend((name,fn(),'V17') for name,fn in PLACEMENT_GENERATORS.items())
    raw.extend((name,fn(),'V20') for name,fn in V20_GENERATORS.items())
    grade_forms=defaultdict(list)
    topic_forms=defaultdict(list)
    signatures=set()
    questions=set()
    for slug, candidate, release in raw:
        form=Candidate.model_validate(candidate)
        signature=(form.grade,form.topic_id,form.method)
        assert signature not in signatures,signature
        signatures.add(signature)
        assert len(form.questions)==10
        for item in form.questions:
            assert len(item.explanation)>=24
            assert item.question not in questions, (slug,item.question)
            questions.add(item.question)
            if item.question_type=='multiple_choice':
                assert item.answer==item.choices[item.correct_index]
                assert not any(options_equivalent(a,b) for i,a in enumerate(item.choices)
                               for b in item.choices[i+1:]),(slug,item.choices)
        form_data={**form.model_dump(),
                   'slug':slug,'added_in':release,
                   'provenance':'original_questions_inspired_by_frameworks_not_copied_from_exams',
                   'answer_check':'generator_and_algebraic_tests_not_independent_teacher_approval',
                   'difficulty_calibration':'provisional',
                   'review_status':'NOT_APPROVED',
                   'assessed_process':candidate.get('assessed_process','not_yet_tagged'),
                   'form_hash':hashlib.sha256(json.dumps(form.model_dump(),ensure_ascii=False,sort_keys=True).encode()).hexdigest()}
        grade_forms[form.grade].append(form_data)
        topic_forms[(form.grade,form.topic_id)].append(form_data)
    topics=json.loads((ROOT/'learn-assets/topics.json').read_text(encoding='utf-8'))
    csv_path=output/'REVIEW_GAPS_ALL_150_TOPICS.csv'
    with csv_path.open('w',encoding='utf-8-sig',newline='') as fh:
        writer=csv.writer(fh)
        writer.writerow(['grade','topic_id','topic_title','minimum_questions','candidate_questions',
                         'candidate_methods','certified_in_clean_snapshot','official_exam_ready',
                         'review_priority'])
        for topic in topics:
            forms=topic_forms.get((topic['grade'],topic['id']),[])
            writer.writerow([topic['grade'],topic['id'],topic['title'],9,len(forms)*10,len(forms),
                             0,'NO','HIGH' if not forms else 'TEACHER_REVIEW_REQUIRED'])
    counts={}
    for grade in (10,11,12):
        fs=grade_forms[grade]
        doc={'grade':grade,'official_paper':False,'review_status':'UNAPPROVED_PRIVATE_CANDIDATES',
             'forms':fs,'form_count':len(fs),'question_count':sum(len(f['questions']) for f in fs),
             'not_for_student_website':True,
             'limitations':'A generator checking its own arithmetic is not an independent teacher review or psychometric validation.'}
        path=output/f'GRADE_{grade}_PRIVATE_TEACHER_REVIEW.json'
        write_json(path,doc)
        os.chmod(path,0o600)
        counts[str(grade)]={'candidate_forms':doc['form_count'],'candidate_questions':doc['question_count'],
             'topics_with_any_candidates':sum((grade,tid) in topic_forms for tid in [x['id'] for x in topics if x['grade']==grade]),
             'official_verified_questions':0}
    write_json(output/'COUNTS_AND_LIMITATIONS.json',{'release':'V20','status':'TEACHER_REVIEW_ONLY',
        'total_candidate_forms':sum(x['candidate_forms'] for x in counts.values()),
        'total_candidate_questions':sum(x['candidate_questions'] for x in counts.values()),
        'unique_topics_with_candidate_forms':len(topic_forms),'total_curricular_topics':len(topics),
        'official_verified_questions_in_snapshot':0,
        'per_grade':counts,'minimum_official_needed':{'10':441,'11':459,'12':450},
        'note':'310 NEW candidate questions in V20; the other 150 are carried from V16/V17. No approval or student grades changed.'})
    (output/'REVIEW_PROTOCOL.md').write_text('''# QUY TRÌNH DUYỆT ĐỀ ĐẦU VÀO, CHỈ DÀNH CHO GIÁO VIÊN

**Tuyệt đối không chia sẻ các JSON này với học sinh hoặc đặt trong web root.**

1. Kiểm chứng nội dung phù hợp chính xác chủ đề, khối lớp và yêu cầu cần đạt của CTGDPT 2018.
2. Giải từng câu độc lập, không nhìn đáp án sinh sẵn; đối chiếu đáp án và lời giải từng bước.
3. Kiểm tra tính xác định của điều kiện, không có nhiều diễn giải hoặc nhiều đáp án đúng.
4. Kiểm tra 4 lựa chọn trắc nghiệm không tương đương, lời giải và định dạng đáp án chính xác.
5. Đánh giá mức độ Nền tảng, Trung cấp, Nâng cao theo độ phức tạp thao tác tư duy. Nhãn ứng viên không đủ căn cứ.
6. Đối chiếu phương pháp giải với các dạng đã duyệt trong cùng chủ đề và chủ đề gần; đổi số không tính dạng mới.
7. Tăng tỷ trọng câu vận dụng, mô hình hóa, lập luận và diễn giải; không đánh giá chỉ bằng bài thay số.
8. Kiểm tra ngôn ngữ, khả năng truy cập trên điện thoại, dữ kiện, thời gian và tính công bằng.
9. Khi đã duyệt từng dạng, nhập qua API Admin QF2, **không** tự sửa trường source hoặc database để giả phê duyệt.
10. Sau khi có đủ đề ở từng chủ đề/mức, chạy thử với học sinh thật có chấp thuận, phân tích độ khó, độ phân biệt, tỷ lệ bỏ qua, độ ổn định và sai lệch do mệt mỏi. Không tuyên bố đạt chuẩn chỉ nhờ số lượng câu.

### Nguồn định hướng (KHÔNG sao chép nguyên văn đề thi)
- Bộ GD&ĐT, Chương trình GDPT 2018 môn Toán, TT 32/2018/TT-BGDĐT: https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721
- Bộ GD&ĐT, Đề tham khảo Toán 2025: https://xaydungchinhsach.chinhphu.vn/de-tham-khao-thi-tot-nghiep-thpt-mon-toan-tu-nam-2025-119241018154616944.htm
- Cấu trúc đề thi Toán từ 2025: https://xaydungchinhsach.chinhphu.vn/cau-truc-de-thi-tot-nghiep-thpt-tu-nam-2025-119240308200554932.htm
- OECD, PISA 2022 Mathematics Framework: https://www.oecd.org/en/publications/pisa-2022-assessment-and-analytical-framework_dfe0bf9c-en/full-report/component-3.html
- AERA/APA/NCME, Standards for Educational and Psychological Testing: https://ncme.org/resources/books/testing-standards/

### Trạng thái
- Các bộ sinh có kiểm tra logic tự động nhưng CHƯA được giáo viên kiểm tra độc lập.
- Một bộ dạng có 10 câu thay số, tính là 1 dạng ứng viên, không phải 10 dạng.
- Đây là tài liệu **có đáp án riêng tư**, không dùng làm đề đầu vào chính thức.
''',encoding='utf-8')
    os.chmod(output/'REVIEW_PROTOCOL.md',0o600)
    print(json.dumps({'output':str(output),'total_forms':len(signatures),'total_questions':len(questions),
                      'unique_topics':len(topic_forms),'grade_counts':counts},ensure_ascii=False))
    return counts

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    export(args.output)
