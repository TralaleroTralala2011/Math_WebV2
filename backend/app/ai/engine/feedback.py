import random
CORRECT = ["Wow, bạn làm đúng rồi!", "Chuẩn bài!", "Quá tốt!", "Đáp án chính xác!", "Nice! Tiếp tục nhé!"]
WRONG = ["Oh oh, câu này chưa đúng. Cố lên nhé!", "Chưa đúng rồi, thử câu tiếp theo nào!", "Gần rồi! Đừng bỏ cuộc nhé!", "Tiếc quá! Cùng làm tiếp nào!"]

def feedback(correct: bool) -> str:
    return random.choice(CORRECT if correct else WRONG)
