# MATH_WEB NEON V16 | Báo cáo đề đầu vào cố định
Ngày: 11/11/2026
Nguồn: `MATH_WEB_GITHUB_READY_NEON_V15_QUALITY_ROADMAP_2026-11-11.zip`

## Công việc hoàn thành trong V16

1. **Ba ma trận đề cố định** riêng cho lớp 10, 11, 12, đúng 49/51/50 chủ đề, mỗi chủ đề 3 mức, mỗi mức 3 câu. Tổng yêu cầu 1.350 câu.
2. **Bộ lắp đề tất định**: cùng một phiên bản đề cho mọi học sinh trong một khối, chỉ lấy câu từ ngân hàng QF2 được Admin duyệt; chống trùng câu, chặn thiếu câu/mức, yêu cầu ít nhất hai hình thức trả lời/chủ đề.
3. **Quy trình công bố riêng của Admin**: chặn công bố nếu thiếu, khóa đề theo SHA-256, lưu bản chụp bất biến trong SQLite, phát hiện thu hồi/sửa câu hỏi. Học sinh không thể tự công bố.
4. **API đề chính thức**: `mode=fixed_placement`, lưu bản nháp, không gửi đáp án trước khi nộp, chặn làm lại cùng đề sau khi nộp để giảm học thuộc đáp án. Các phiên bài thử V15 được giữ lại nhưng không mở khóa lộ trình.
5. **Đánh giá sau thi**: đúng/sai/bỏ qua theo từng câu và theo từng chủ đề/mức; khoảng Wilson 95% để thể hiện độ bất định; gia sư tiếp tục dùng dữ liệu đã duyệt.
6. **Phân tích thử nghiệm**: API Admin báo cáo độ khó, tỷ lệ bỏ qua, độ phân biệt, Cronbach alpha nếu có ít nhất 30 bài làm thực tế cùng một phiên bản đề; không tự nhận đã chứng minh độ tin cậy.
7. **Admin UI**: ba thẻ trạng thái đề cố định, số câu thiếu, nút công bố chỉ bật khi đạt điều kiện; responsive cho điện thoại.
8. **Tài liệu chuyên môn**: khung GDPT 2018, OECD PISA 2022 và nguyên tắc hợp lệ/độ tin cậy/công bằng. Không sao chép đề thi có bản quyền.
9. **Gói duyệt học liệu**: xuất lại 80 câu ứng viên từ 8 bộ sinh đã có của V15 (lớp 10: 20; lớp 11: 30; lớp 12: 30), **không phải câu đã duyệt**.

## Tình trạng dữ liệu thực tế

| Khối | Chủ đề | Chỉ tiêu câu đã duyệt | Câu được duyệt trong database kiểm toán | Tình trạng đề chính thức |
|---|---:|---:|---:|---|
| Lớp 10 | 49 | 441 | 0 | Chưa xuất bản |
| Lớp 11 | 51 | 459 | 0 | Chưa xuất bản |
| Lớp 12 | 50 | 450 | 0 | Chưa xuất bản |
| **Tổng** | **150** | **1.350** | **0** | **Chưa hoàn thành nội dung** |

Câu ứng viên trong học liệu không được tính là câu được chứng nhận. Khi chưa có đề được công bố, học sinh có thể làm **bài thử không chính thức**, nhưng không thể dùng bài thử để mở khóa lộ trình.

## Kiểm thử

- `pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'`: **187 passed, 1 deselected**, 29,41 giây.
- Bộ kiểm thử riêng V16: **4 passed**.
- Đã kiểm tra cú pháp Python và JavaScript.
- Bài kiểm thử sinh 4 bộ lượng giác liên tiếp bị loại khỏi lượt kiểm thử tổng hợp vì thời gian chạy dài; không khẳng định đã chạy đủ 188/188.
- ZIP được kiểm tra CRC và số lượng tệp sau khi đóng gói.

## Việc còn phải làm để đạt yêu cầu 100%

1. Soạn/kiểm tra/duyệt ít nhất **1.350 câu đúng toán học** đủ độ phủ từng chủ đề và ba mức; tránh sao chép câu hỏi từ học liệu công khai vào đề chính thức.
2. Giáo viên xác nhận độ khó, mục tiêu năng lực, tính phù hợp SGK và lời giải từng câu; thử nghiệm thực địa, hiệu chuẩn độ khó/độ phân biệt và đánh giá công bằng.
3. Admin xuất bản từng đề lớp 10/11/12 sau khi hệ thống báo `ready=true`.
4. Kiểm thử người học thật trên nhiều thiết bị, tính dễ đọc và tải đề lớn 441–459 câu; xem xét chia thành nhiều phiên có hiệu chuẩn để giảm quá tải.
5. Bổ sung tối thiểu 30 câu đã duyệt/chủ đề cho bài kiểm tra kết thúc chủ đề để kích hoạt quy tắc 25/30 và mở khóa ba chủ đề.

**Không tuyên bố hoàn thành 100% ba đề đầu vào. V16 hoàn thành phần kiến trúc và quy trình kiểm soát chất lượng, chưa có đủ câu đã duyệt hoặc bằng chứng đo lường thực địa.**
