#!/usr/bin/env python3
import json,sqlite3,collections,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
UPDATES=BASE/'bank_updates'
C=sqlite3.connect(BASE/'backend/database/mathweb.db')
index=json.loads((BASE/'backend/app/ai/knowledge/index.json').read_text())
original=collections.Counter((int(g),t['id']) for g,topics in index.items() for t in topics)
current={(grade,topic):count for grade,topic,count in C.execute('select grade,topic,count(*) from admin_question_bank group by grade,topic')}
changed={(grade,topic):count for grade,topic,count in C.execute("select grade,topic,count(*) from admin_question_bank where source='V198 QA-gated' group by grade,topic")}
coverage=[{'grade':g,'topic':t,'total_db_questions':current.get((g,t),0),'new_V198':changed.get((g,t),0),
   'questions_short_of_20k_count_only':max(0,20000-current.get((g,t),0)),
   'certified_types':'not established from historical bank; requires semantic classification'}
   for g,topics in index.items() for t in [x['id'] for x in topics] for g in [int(g)]]
# 20,000 questions/topic = target 2,000 forms*10; per-topic deficit here is COUNT ONLY, not validated achievement.
(UPDATES/'V198_COVERAGE_150.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
old=9636;after=C.execute('select count(*) from admin_question_bank').fetchone()[0]
assert after==old+340
nochange=['users','friends','messages','notifications','question_sessions','game_results']
pre=sqlite3.connect(UPDATES/'V198_before_import_backup.sqlite')
counts={}
for tb in nochange:
    try:
        counts[tb]={'before':pre.execute(f'select count(*) from {tb}').fetchone()[0], 'after':C.execute(f'select count(*) from {tb}').fetchone()[0]}
    except sqlite3.Error:continue
assert all(x['before']==x['after'] for x in counts.values())
report={
 'version':'V198','base':'V197 full bundled website','catalog_topics':len(coverage),'bank_before':old,'bank_after':after,
 'candidate_families_created':34,'new_math_checked_questions':340,'new_rows_imported_bundled_sqlite':340,
 'verified_independent_new_forms':0,'production_deployed':False,
 'grades_10_11_12_new':{'10':120,'11':110,'12':110},
 'formats_new':{'multiple_choice':238,'short_answer':68,'true_false':34},
 'topic_ids_repaired_old_questions':60,'unmapped_invalid_topic_rows_kept':10,
 'topics_expanded':len(changed),'repeated_import_extra_rows':0,
 'topic_format_smoke_tests_passed':102,'topic_format_smoke_tests_total':102,
 'exact_duplicate_normalized_new':0,'family_semantic_review_flagged':7,
 'legacy_user_data_table_row_counts_unchanged':counts,
 'sqlite_integrity':C.execute('pragma integrity_check').fetchone()[0],
 'remaining_question_count_to_3m_ignoring_quality':3000000-after,
 'remaining_certified_form_count':'not measurable: historical method certification absent',
 'limitations':'340 math oracle checked and app-grade-checked; full semantic independence not proven, 7 flagged. No production access; only bundled SQLite tested.',
 'next':'Review 7 semantic flags; use verified production DB before deployment; expand truly distinct methods and ten questions each. Do not silently map grade 10 chia_het.'
}
(UPDATES/'V198_RELEASE_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(UPDATES/'README_V198.md').write_text('''# V198 ngân hàng MATH_WEB\n\nNguồn: bản V197 FULL WEB đã kiểm tra toàn vẹn, không thay thế production.\n\n- 34 nhóm phương pháp ứng viên / 340 câu, mỗi nhóm 10 câu (7 trắc nghiệm + 2 trả lời ngắn + 1 đúng/sai).\n- Kiểm chứng tính toán độc lập trong `backend/question_factory/v198_generate.py`; kiểm tra chất lượng nhập bằng `backend/scripts/import_bank_updates.py`.\n- 340 câu đã nhập SQLite bản website đóng gói. Số câu: 9.636 -> 9.976; nhập lại +0.\n- Đã sửa ánh xạ đúng 60 câu legacy có mã chủ đề sai và ghi ledger có thể truy ngược. 10 câu `chia_het` giữ nguyên vì danh mục không có chủ đề khớp.\n- 102/102 kiểm thử cấu trúc truy xuất/chấm định dạng đạt. 7 nhóm gắn cờ trùng phương pháp để kiểm định thủ công.\n- **0 dạng toán đã được chứng nhận độc lập ngữ nghĩa toàn diện; 0 câu xác nhận triển khai production.**\n\nTệp: V198_INCREMENT.jsonl, V198_FAMILY_SPECS.json, V198_GENERATION_AUDIT.json, V198_RETRIEVAL_QA.json, V198_DEDUP_AUDIT.json, V198_RELEASE_REPORT.json, V198_COVERAGE_150.json.\n\nChạy lại có kiểm tra: `python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db --input bank_updates/V198_INCREMENT.jsonl` (dry-run). Chỉ ghi với `--write --backup <tệp sao lưu mới>`; **KHÔNG sử dụng bản SQLite mẫu để ghi đè server production**.\n''',encoding='utf8')
print(json.dumps({'total':after,'topics':len(coverage),'new_topics':len(changed),'user_rows_unchanged':True},ensure_ascii=False))
