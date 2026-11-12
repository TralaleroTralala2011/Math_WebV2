"""Fixed, grade-specific placement papers with an evidence-first release gate.

A *blueprint* is NOT an exam. Only a published immutable snapshot of approved,
independently reviewed private-bank items can be used as an official placement exam.
"""
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

TIERS = ('nền tảng', 'trung cấp', 'nâng cao')
MIN_PER_TIER = 3
FORMATS = ('multiple_choice', 'true_false', 'written')
MIN_DISTINCT_FORMS_PER_TIER = 2
VERSION = '2026.11.11'


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def blueprint_path(root: Path, grade: int):
    if grade not in (10, 11, 12):
        raise ValueError('Invalid grade')
    return root / 'placement-exams' / f'grade_{grade}_blueprint.json'


def load_blueprint(root: Path, grade: int):
    data = json.loads(blueprint_path(root, grade).read_text(encoding='utf-8'))
    if data['grade'] != grade or data['min_questions_per_tier'] != MIN_PER_TIER:
        raise ValueError('Invalid blueprint')
    topics = data['topics']
    if len(topics) != len({t['topic_id'] for t in topics}):
        raise ValueError('Duplicate topic in blueprint')
    for t in topics:
        if set(t['tiers']) != set(TIERS) or any(t['tiers'][d] != MIN_PER_TIER for d in TIERS):
            raise ValueError('Invalid tier requirements')
    return data


def item_signature(item):
    return re.sub(r'\s+', ' ', str(item.get('question', '')).casefold()).strip()


def assemble_fixed_paper(blueprint, topic_pools):
    """Deterministic selection, never falling back to unreviewed questions.

    `topic_pools` is an injectable mapping to allow independent test fixtures.
    Each item must already have passed the question bank's approval pipeline.
    """
    grade = blueprint['grade']
    chosen, gaps, seen_questions, seen_ids = [], [], set(), set()
    diversity_gaps = []
    for topic in blueprint['topics']:
        tid = topic['topic_id']
        available = topic_pools.get(tid, [])
        for tier in TIERS:
            target = topic['tiers'][tier]
            eligible = [q for q in available if q.get('topic_id') == tid
                        and q.get('grade') == grade and q.get('difficulty') == tier
                        and q.get('source') == 'qf2-approved']
            # A stable, public blueprint determines the paper, not a student's identity.
            eligible.sort(key=lambda q: (digest([grade, tid, tier, q.get('qid')]), str(q.get('qid'))))
            # Choose at least two mathematically distinct reviewed methods
            # per tier, not three numeric substitutions from one generator.
            by_form = defaultdict(list)
            for q in eligible:
                fid=q.get('form_id')
                if isinstance(fid,int) and not isinstance(fid,bool) and fid>0:
                    by_form[fid].append(q)
            eligible_forms=sorted(by_form)
            # Count independent forms in the *selected* items, not only the
            # candidate pool: duplicate statements can remove a whole form.
            selection_start=len(chosen)
            # Round robin: first sample from each distinct form, then fill.
            ordered=[]
            while any(by_form.values()):
                for fid in eligible_forms:
                    if by_form[fid]:ordered.append(by_form[fid].pop(0))
            added = 0
            for q in ordered:
                signature = item_signature(q)
                if not signature or signature in seen_questions or q['qid'] in seen_ids:
                    continue
                if q.get('question_type') not in FORMATS or not str(q.get('explanation','')).strip():
                    continue
                chosen.append(dict(q))
                seen_questions.add(signature)
                seen_ids.add(q['qid'])
                added += 1
                if added == target:
                    break
            selected_form_count=len({q.get('form_id') for q in chosen[selection_start:]})
            if selected_form_count<MIN_DISTINCT_FORMS_PER_TIER:
                diversity_gaps.append({'topic_id':tid,'tier':tier,
                                       'required_distinct_forms':MIN_DISTINCT_FORMS_PER_TIER,
                                       'available_distinct_forms':len(eligible_forms),
                                       'selected_distinct_forms':selected_form_count})
            if added < target:
                gaps.append({'topic_id': tid, 'title': topic['title'], 'tier': tier,
                             'required': target, 'available_unique_reviewed': added,
                             'missing': target-added})
    # This is an objective validity warning, not a fabricated type label.
    by_topic = defaultdict(set)
    for q in chosen:
        by_topic[q['topic_id']].add(q['question_type'])
    format_warnings = [t['topic_id'] for t in blueprint['topics'] if len(by_topic[t['topic_id']]) < 2]
    # Require at least two formats for each topic. This gate is deliberate.
    ready = not gaps and not format_warnings and not diversity_gaps
    return {
        'ready': ready, 'grade': grade, 'blueprint_version': blueprint['version'],
        'blueprint_hash': digest(blueprint), 'required': len(blueprint['topics'])*len(TIERS)*MIN_PER_TIER,
        'selected': len(chosen), 'topics_required': len(blueprint['topics']),
        'topics_with_format_diversity': len(blueprint['topics'])-len(format_warnings),
        'format_warnings': format_warnings, 'gaps': gaps,
        'distinct_form_gaps': diversity_gaps, 'minimum_distinct_forms_per_tier': MIN_DISTINCT_FORMS_PER_TIER,
        'paper_hash': digest(chosen) if ready else None,
        'questions': chosen if ready else [],
        'note': ('Đủ điều kiện kỹ thuật để giáo viên công bố; không phải bằng chứng về độ tin cậy tâm trắc.'
                 if ready else 'Đề thiếu câu đã duyệt, đa dạng dạng toán hoặc hình thức; không thể công bố.'),
    }


def validate_frozen_paper(blueprint, questions):
    """Recheck a frozen exam independently of the current selection order.

    New approved questions may be added later without invalidating a published
    exam. Changes to its blueprint, item approval or content must invalidate it.
    This is a structural safeguard, NOT certification of mathematical validity.
    """
    if not isinstance(questions, list) or not isinstance(blueprint, dict):
        return False
    expected = {(t['topic_id'], tier): t['tiers'][tier]
                for t in blueprint['topics'] for tier in TIERS}
    if len(questions) != sum(expected.values()):
        return False
    topic_names = {t['topic_id']: t['title'] for t in blueprint['topics']}
    counts = Counter()
    forms = defaultdict(set)
    formats = defaultdict(set)
    ids, statements = set(), set()
    for q in questions:
        if not isinstance(q, dict) or q.get('source') != 'qf2-approved':
            return False
        pair = (q.get('topic_id'), q.get('difficulty'))
        if (pair not in expected or q.get('grade') != blueprint['grade']
                or q.get('title') != topic_names.get(q.get('topic_id'))):
            return False
        fid, qid = q.get('form_id'), q.get('qid')
        if (not isinstance(fid, int) or isinstance(fid, bool) or fid < 1
                or not isinstance(qid, str) or not qid.strip() or qid in ids):
            return False
        signature = item_signature(q)
        if not signature or signature in statements:
            return False
        if q.get('question_type') not in FORMATS or not str(q.get('explanation','')).strip():
            return False
        if q['question_type'] == 'multiple_choice':
            choices = q.get('choices')
            ix = q.get('correct')
            if (not isinstance(choices, list) or len(choices) != 4
                    or any(not str(ch).strip() for ch in choices)
                    or not isinstance(ix, int) or isinstance(ix, bool) or not 0 <= ix < 4):
                return False
            # Textual uniqueness is insufficient: 1/2 and 0,5 are the same
            # mathematical option. Reject an invalid frozen paper even if a
            # historic review/import marked the bank row as approved.
            from .ai.engine.validator import options_equivalent
            if any(options_equivalent(left, right)
                   for idx, left in enumerate(choices) for right in choices[idx+1:]):
                return False
        elif q.get('correct') is None or not str(q['correct']).strip():
            return False
        counts[pair] += 1
        forms[pair].add(fid)
        formats[q['topic_id']].add(q['question_type'])
        statements.add(signature)
        ids.add(qid)
    return (counts == Counter(expected)
            and all(len(forms[pair]) >= MIN_DISTINCT_FORMS_PER_TIER for pair in expected)
            and all(len(formats[topic_id]) >= 2 for topic_id in topic_names))


def wilson_interval(correct, total, z=1.96):
    """95% Wilson score interval for binary correct/incorrect outcomes."""
    if total == 0:
        return None
    p = correct / total
    denom = 1 + z*z/total
    centre = (p + z*z/(2*total))/denom
    margin = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))/denom
    return [round(max(0, centre-margin)*100, 1), round(min(1, centre+margin)*100, 1)]


def evidence_profile(review, blueprint):
    """Transparent descriptive feedback, NOT a psychometric ability estimate."""
    by_topic_tier = defaultdict(list)
    for r in review:
        if r.get('verified_for_diagnostic'):
            by_topic_tier[(r['topic_id'], r['difficulty'])].append(r)
    topic_results=[]
    for t in blueprint['topics']:
        tiers={}
        for tier in TIERS:
            answers=by_topic_tier[(t['topic_id'],tier)]
            counts=Counter(a['verdict'] for a in answers)
            n=len(answers)
            correct=counts['correct']
            answered=counts['correct']+counts['wrong']
            tiers[tier]={
                'total':n, 'answered':answered, 'correct':correct,
                'wrong':counts['wrong'], 'skipped':counts['skipped'],
                # Full-paper score describes completion as well as accuracy;
                # never mistake it for ability on the attempted questions.
                'percent_correct':round(correct*100/n,1) if n else None,
                'accuracy_among_answered':round(correct*100/answered,1) if answered else None,
                'answer_rate_percent':round(answered*100/n,1) if n else None,
                # Skip is missing evidence, not a wrong response for a
                # confidence interval about answered-item accuracy.
                'wilson_95_percent':wilson_interval(correct,answered),
                'coverage_complete':n>=t['tiers'][tier],
                'evidence_sufficient':answered>=t['tiers'][tier],
                'feedback':('Chưa trả lời câu nào; chưa có bằng chứng để suy luận' if not answered else
                            'Số câu đã trả lời còn quá ít để suy luận chắc chắn' if answered<t['tiers'][tier] else
                            'Cần ưu tiên ôn tập' if correct<=1 else
                            'Đang củng cố' if correct==2 else
                            'Làm đúng toàn bộ câu đã trả lời ở mức này'),
            }
        topic_results.append({'topic_id':t['topic_id'],'title':t['title'],'tiers':tiers})
    return {
        'model':'descriptive_criterion_referenced_v1',
        'topics':topic_results,
        'note':'Khoảng Wilson chỉ tính trên câu đã trả lời; câu bỏ qua là thiếu bằng chứng, không tự tính sai. Đây không phải thước đo năng lực chuẩn hóa. '
               'Cần thử nghiệm thực tế, phân tích độ khó, độ phân biệt, tính công bằng và độ ổn định trước khi tuyên bố khách quan.',
    }
