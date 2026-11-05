from app.questions.answer_checker import grade_answer

def test_equivalent_verdict_numeric_answers():
    q = {"question_type": "short_answer", "answer": "Sai; 9(7+3)=90"}
    for answer in ("Sai, 90", "Sai; 90", "Không đúng; kết quả là 90", "Sai; 9(7+3)=90"):
        assert grade_answer(q, answer), answer
    for answer in ("Đúng, 90", "Sai, 66", "Sai", "90"):
        assert not grade_answer(q, answer), answer
