# NEON V14 - Kiểm soát dữ liệu đánh giá năng lực

Nguồn: NEON V13 được cung cấp trong cuộc trò chuyện.

## Thay đổi
- Lưu nguồn câu hỏi và trạng thái `verified_for_diagnostic` trong kết quả xem lại từng câu.
- Câu chưa được duyệt vẫn được hiển thị để người học xem lại, nhưng không cập nhật mô hình theo dõi năng lực.
- Kết quả trả số câu đã duyệt và số câu ứng viên riêng biệt.
- Giữ nguyên giao diện và các tính năng khác của V13.

## Giới hạn
Chưa tạo đủ bộ đề đầu vào chuẩn cho toàn bộ 150 chủ đề; không công nhận kết quả đầu vào là đánh giá năng lực toàn diện nếu thiếu câu đã kiểm chứng. Chưa hoàn thành toàn bộ Question Factory, Battle/Chat hai thiết bị hoặc kiểm tra UI theo hình mẫu.

## Kiểm tra
Python syntax compilation đạt. Bộ pytest đầy đủ chưa có kết quả xác nhận trong lượt này (quá thời gian chạy).

## Dữ liệu
Không đưa database hoặc khóa đăng nhập vào ZIP. Sao lưu dữ liệu trước khi nâng cấp.
