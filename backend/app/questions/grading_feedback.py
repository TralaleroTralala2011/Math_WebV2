"""Conservative feedback from an authoritative scoring result.

No fabricated step-by-step reasoning. Never exposes an answer before grading.
"""
from .answer_checker import grade_answer, canonical_type


def feedback_for_result(question, submitted, correct, is_correct, explanation=None):
    """Describe the verdict without overriding the authoritative grade."""
    question = question if isinstance(question, dict) else {}
    kind = canonical_type(question)
    solution = explanation or question.get('solution') or question.get('explanation')
    if is_correct:
        message = 'Đúng. Kết quả của bạn phù hợp với đáp án chuẩn.'
    else:
        message = 'Chưa đúng. Hãy đối chiếu điều kiện bài toán, các bước biến đổi và kết quả cuối.'
    if kind in ('essay', 'written'):
        message += ' Hệ thống mới xác minh đáp án, chưa xác nhận tính đúng đắn của toàn bộ lập luận.'
    if not solution:
        message += ' Chưa có lời giải được kiểm duyệt cho câu này.'
    return {'feedback': message, 'explanation': str(solution) if solution else None,
            'needs_solution_review': not bool(solution), 'grading_scope': 'final_answer_only'}


def grade_with_feedback(question, submitted, correct=None):
    expected = correct if correct is not None else question.get('correct_answer', question.get('answer'))
    if expected is None:
        return {'is_correct': False, 'status': 'ungradable', 'feedback': 'Thiếu đáp án chuẩn, cần kiểm duyệt.', 'explanation': None}
    verdict = grade_answer(question, submitted, expected)
    return {'is_correct': verdict, 'status': 'graded', **feedback_for_result(question, submitted, expected, verdict)}
