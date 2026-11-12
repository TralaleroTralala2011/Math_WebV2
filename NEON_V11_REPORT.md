# MATH_WEB NEON V11 — bản vá đánh giá năng lực

Nguồn: MATH_WEB_GITHUB_READY_NEON_V10_UPGRADED_2026-11-11.zip.

## Thay đổi thực tế
- Báo cáo kết quả bài đầu vào nay dùng cùng hàm `assessment_quality` với lúc bắt đầu và khôi phục bài thi.
- Chỉ tính các câu `lesson-reviewed` hoặc `qf2-approved` khi xác định độ phủ ba mức của từng chủ đề.
- Trả về `verified_items`, `candidate_items`, `reliable_for_placement`, và `assessment_quality` trong kết quả bài thi.
- Không công nhận độ phủ ba mức dựa trên câu ứng viên chưa được duyệt.

## Kiểm thử
- 3/3 kiểm thử lộ trình trong `tests/test_neon_round5_roadmap.py` đạt.
- Chưa hoàn tất toàn bộ bộ kiểm thử backend trong lượt này; không khẳng định 100%.

## Việc còn thiếu
- Chưa đủ 3–4 câu đã kiểm chứng cho từng mức ở mọi chủ đề của lớp 10, 11, 12.
- Chưa đủ 30 câu đã kiểm chứng cho mọi bài kiểm tra chủ đề.
- Chưa xác nhận giao diện trùng khớp 5 ảnh và Battle/Chat trên hai thiết bị thật.
- Gia sư hiện dùng cập nhật ước lượng năng lực, không phải huấn luyện lại mô hình AI.

Gói không chứa database hoặc khóa đăng nhập; hãy giữ bản sao dữ liệu cũ trước khi nâng cấp.
