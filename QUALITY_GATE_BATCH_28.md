# Batch 28: Kiểm định cấu trúc kiến thức và bản đồ tiên quyết (bản nền)

## Đã thực hiện
- Thêm API đọc dữ liệu từ `learn-assets/topics.json` và `verified-lessons.json`, không nhân bản nguồn dữ liệu.
- `GET /api/curriculum/quality`: thống kê độ phủ và các mục còn thiếu theo từng chủ đề.
- `GET /api/curriculum/topics/{topic_id}/readiness`: kiểm tra điều kiện cấu trúc trước khi duyệt bài.
- `GET /api/curriculum/graph`: bản đồ kiến thức tiên quyết bước đầu, có nhãn `curated_partial`.
- Mọi bài chỉ được đánh dấu `draft` hoặc `needs_review`, KHÔNG tự xuất bản chỉ dựa vào việc có trường dữ liệu.

## Chưa hoàn thành
- Chưa xác minh độc lập nội dung Toán, chưa hoàn thiện 150 bài lý thuyết.
- Chưa có AI gia sư tổng quát, phòng hình học tương tác đầy đủ, thi thử, lộ trình thích ứng, ôn tập, nhiệm vụ, hoặc quy trình xuất bản thực sự.
- Chưa chạy kiểm thử tích hợp frontend, Battle và triển khai production.

## Cách kiểm tra
Chạy backend như README hiện có rồi mở `/api/curriculum/quality` và `/api/curriculum/graph`.
