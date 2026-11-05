from app.ai.answer_equivalence import numeric_equivalent

def test_equivalent():
    assert numeric_equivalent('2/4','0.5') is True
    assert numeric_equivalent('π','pi') is True
    assert numeric_equivalent('7*(9+6)',105) is True
    assert numeric_equivalent('3/4','0.5') is False
    assert numeric_equivalent('x=2','2') is None
    assert numeric_equivalent('__import__("os")','2') is None
