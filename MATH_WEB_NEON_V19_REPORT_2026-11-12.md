# MATH_WEB NEON V19 - Kiểm toán và nâng cấp tính công bằng đánh giá

**Ngày:** 12/11/2026  
**Nền mã nguồn:** MATH_WEB_GITHUB_READY_NEON_V18_PLACEMENT_INTEGRITY_2026-11-12.zip

## Kết luận trung thực

Bản này **chưa đạt 100%** các yêu cầu. Bộ ma trận đề lớp 10–12 được khai báo, nhưng checkpoint V18/V19 **chưa có đề đầu vào chính thức được chứng nhận đầy đủ**. Không được công bố mô hình đánh giá năng lực học sinh như công cụ đo lường tâm trắc đã được kiểm định.

## Thay đổi V19 đã triển khai

1. **Không giảm mức thành thạo vì câu bỏ qua.** Theo dõi Bayesian Knowledge Tracing (BKT) đơn giản trước đây cập nhật mức thành thạo ngay cả khi câu bị bỏ qua. V19 vẫn ghi câu bỏ qua vào thống kê và gợi ý ôn, nhưng *không dùng nó làm bằng chứng trực tiếp rằng học sinh yếu kiến thức*. Điều này đặc biệt quan trọng với một đề dài 441-459 câu, khi học sinh có thể mệt hoặc thiếu thời gian.
2. **Phân biệt độ phủ nội dung và hiệu chuẩn độ tin cậy.** API `/api/roadmap-v2/fixed/status/{grade}` thêm `psychometric_validated: false` và `validation_stage`. Kết quả nộp đề có `content_coverage_complete` và `psychometric_validated: false`. Nhãn `reliable_for_placement` cũ vẫn giữ để không phá tương thích API và đang được dùng như cổng kiểm tra **độ phủ cấu trúc**, không phải tuyên bố độ tin cậy tâm trắc.
3. **Trình bày minh bạch với người học.** Trong lộ trình, kết quả bài đầu vào cố định hiển thị nút xem phân tích theo chủ đề thay vì hứa cho xem lại đáp án. Trình bày lý do đề cố định không công bố đáp án dùng chung. Phần giải thích năng lực giờ có thể mở rộng để xem **mọi chủ đề và cả ba mức độ** mà không tràn màn hình điện thoại.
4. **Không thay đổi chức năng khác**: chỉ sửa `backend/app/roadmap_v2_routes.py`, `js/roadmap-v5.js`, thêm CSS cho trang lộ trình và bài kiểm thử hồi quy V19.

## Bằng chứng từ gói V18/V19

| Lớp | Chủ đề | Mức | Câu phải có | Câu trong snapshot đủ điều kiện được chọn | Snapshot sẵn sàng |
|---|---:|---:|---:|---:|---|
| 10 | 49 | 3 | 441 | 0 | Không |
| 11 | 51 | 3 | 459 | 0 | Không |
| 12 | 50 | 3 | 450 | 0 | Không |
| **Tổng** | **150** | **3** | **1.350** | **0** | **Chưa** |

**Cảnh báo về phạm vi số liệu:** đây là snapshot đóng gói, không phải thống kê database thực tại hệ thống người dùng đang triển khai. 150 câu ứng viên của V17 cần kiểm duyệt độc lập; không được tự tính vào 1.350 câu đã phê duyệt. Ngoài ra, để mở đầy đủ kiểm tra chủ đề, mỗi chủ đề còn cần ít nhất 30 câu đã kiểm duyệt.

## Kiểm thử và UI

- `pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'`: **197 passed, 1 deselected** (đã chạy trên V19).
- Kiểm thử V19 kiểm tra: đề dù xuất bản vẫn **chưa được xác nhận độ tin cậy tâm trắc**; khi làm đúng 1 câu và bỏ qua 8 câu, BKT chỉ cập nhật từ 1 câu đã trả lời; kết quả hiển thị tổng hợp nhưng giữ kín đáp án chính thức.
- `node --check js/roadmap-v5.js`: đạt.
- Cả 20 HTML trong thư mục gốc có thẻ viewport responsive và tham chiếu tới hệ thiết kế NEON. Đây là **kiểm tra tĩnh**, không chứng minh tương đồng với 5 ảnh hay trải nghiệm máy thật.
- Chưa chạy kiểm thử lượng giác dài; chưa kiểm thử Battle/Chat trên hai thiết bị vật lý hay đối chiếu giao diện bằng ảnh chụp toàn trang.

## Chưa đủ điều kiện công bố 100%

1. Biên soạn và có **bằng chứng duyệt độc lập** cho ít nhất 1.350 câu lớp 10-12 đúng ma trận, mỗi chủ đề có 3 câu/mức với nhiều phương pháp và kiểu câu; đáp án và lời giải phải được kiểm chứng thực tế.
2. Thu thập bài làm thí điểm từ học sinh phù hợp, hiệu chuẩn độ khó, độ phân biệt, độ tin cậy, phân tích thời gian làm bài, mức bỏ qua và tính công bằng. Cronbach alpha hay khoảng Wilson đơn lẻ **không đủ** làm giấy chứng nhận khách quan.
3. Với bài 441-459 câu, thực hiện đánh giá mệt mỏi, chia đợt có lưu tạm và cân nhắc hình thức đề cân bằng để tránh học tủ; tính ổn định phải đo bằng dữ liệu thật.
4. Kiểm thử hai thiết bị vật lý, quyền truy cập Admin và ảnh giao diện trên desktop/mobile, điều kiện mạng yếu và trường hợp tải lại trang.
5. Kiểm tra thực tế đủ **30 câu đã duyệt/chủ đề** cho lộ trình và quy tắc đạt 25/30, khóa nhóm 3 chủ đề.

## Triển khai an toàn

Bản ZIP không bao gồm database học sinh hoặc bí mật ký token. Sao lưu database trước khi nâng cấp. Không để bộ đáp án, thư mục backend và khóa bảo mật dưới web root có thể tải qua HTTP. Nội dung học sinh và điểm phải lưu ở backend có xác thực.

## Tài liệu phương pháp luận tham khảo

- Chương trình Giáo dục phổ thông môn Toán 2018 (Bộ Giáo dục và Đào tạo).
- OECD, *PISA 2022 Mathematics Framework*.
- AERA/APA/NCME (2014), *Standards for Educational and Psychological Testing*.

Các tài liệu này định hướng xây dựng bằng chứng, **không xác nhận MATH_WEB đã đạt chuẩn**.
