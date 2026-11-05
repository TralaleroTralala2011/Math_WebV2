from app.ai.engine.solver import equivalent


def test_labeled_scalar_equivalence():
    assert equivalent("x = 2", "2")
    assert equivalent("2", "x=2")
    assert equivalent("x = 2/4", "x = 0.5")
    assert not equivalent("x = 2", "y = 2")
    assert not equivalent("x = 2", "x = 3")


def test_ordered_pair_equivalence():
    assert equivalent("(x,y) = (7;5)", "(7,5)")
    assert equivalent("(7;5)", "(x,y)=(7;5)")
    assert equivalent("(x,y)=(7;5)", "(x,y)=(7,5)")
    assert not equivalent("(x,y)=(7;5)", "(5;7)")
    assert not equivalent("(x,y)=(7;5)", "(x,y)=(5;7)")


def test_numeric_equivalence():
    assert equivalent("1/2", "0.5")
    assert not equivalent("1/2", "0.6")
