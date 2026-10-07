from .feedback import message


def feedback(correct, solution=None):
    return {
        "correct": bool(correct),
        "message": message(correct),
        "solution": solution,
    }
