from app.questions.answer_checker import grade_answer

def test_index_and_numeric_visible_text():
    question={"question_type":"multiple_choice","options":["2","5","7","9"],"answer":"5"}
    assert grade_answer(question,{"index":1}) is True
    assert grade_answer(question,{"index":0}) is False
    assert grade_answer(question,"5") is True
    assert grade_answer(question,"1") is False

def test_equivalent_two_options_rejected():
    from app.ai.engine.validator import validate, ValidationError
    q={"id":"x","topic":"xac_suat","grade":10,"difficulty":"easy","question_type":"multiple_choice",
       "question":"Chọn kết quả bằng một nửa.","answer":"0.5","options":["0.5","1/2","2","4"],"solution":"0.5 bằng 1/2"}
    try: validate(q)
    except ValidationError as exc: assert str(exc)=="mcq_equivalent_options"
    else: raise AssertionError("Equivalent choices must be rejected")
