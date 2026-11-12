"""Export existing arithmetic-checked QF2 generator candidates for TEACHER REVIEW.

Never approves them, never publishes them, and never changes user grades.
Run: cd backend && python ../tools/export_fixed_placement_review_pack.py
"""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.qf2_verified_generators import all_candidates
from app.ai.engine.validator import options_equivalent


def main():
    groups={10:[],11:[],12:[]}
    for form in all_candidates():
        assert len(form['questions'])>=10
        for q in form['questions']:
            assert len(q['question'])>=12 and len(q['explanation'])>=24
            if q['question_type']=='multiple_choice':
                assert len(q['choices'])==4 and q['answer']==q['choices'][q['correct_index']]
                assert not any(options_equivalent(a,b) for i,a in enumerate(q['choices']) for b in q['choices'][i+1:])
            elif q['question_type']=='true_false':
                assert q['answer'] in ('Đúng','Sai')
            else:
                assert q['question_type']=='written' and q['answer']
        groups[form['grade']].append(form)
    target=ROOT/'placement-exams'/'teacher-review';target.mkdir(parents=True,exist_ok=True)
    for grade,forms in groups.items():
        doc={'grade':grade,'status':'CANDIDATE_NOT_IN_OFFICIAL_EXAM',
             'question_count':sum(len(f['questions']) for f in forms),
             'form_count':len(forms),'forms':forms,
             'limitations':'Chỉ xác minh tính toán nội bộ của bộ sinh; giáo viên phải kiểm tra nội dung, độ khó và đáp án độc lập trước khi phê duyệt.'}
        (target/f'grade_{grade}_generator_candidates.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
        print(grade,doc['form_count'],doc['question_count'])

if __name__=='__main__':main()
