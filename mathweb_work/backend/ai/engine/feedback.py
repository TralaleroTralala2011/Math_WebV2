import random

CORRECT = (
    "Wow, bạn làm đúng rồi!",
    "Chuẩn bài! Tiếp tục chiến nào!",
    "Quá ổn! Câu này xử đẹp rồi!",
    "Đáp án chính xác! Giữ phong độ nhé!",
    "Nice! Một điểm nữa trong túi!",
)
WRONG = (
    "Oh oh, câu này chưa đúng. Cố lên nhé!",
    "Chưa đúng rồi, mình xem lại cách làm nhé!",
    "Gần rồi! Đừng bỏ cuộc nhé!",
    "Tiếc quá! Cùng chiến tiếp nào!",
)


def message(correct):
    return random.choice(CORRECT if correct else WRONG)
