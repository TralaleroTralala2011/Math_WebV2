# MATH_WEB NEON V21 | MathGeo Studio Pro + gia sư thích ứng

**Nguồn:** MATH_WEB_GITHUB_READY_NEON_V20_PLACEMENT_EXPANSION_2026-11-12.zip.  
**Ngày:** 12/11/2026.  
**Phạm vi sửa:** Vẽ hình trong bài kiểm tra, giao diện MathGeo Studio Pro trên điện thoại, mô hình cá nhân hóa từ bài làm đã chấm.

## Những thay đổi đã triển khai

1. `geometry-studio.html`: giao diện có thanh công cụ nhanh trên điện thoại; điểm, đoạn thẳng, đường tròn, chọn/kéo, di chuyển và hoàn tác. Công cụ nâng cao nằm trong ngăn mở rộng, bố cục máy tính giữ nguyên.
2. Thao tác canvas dùng Pointer Events để hỗ trợ chuột, bút cảm ứng, chạm và hỗ trợ hai ngón để phóng to/thu nhỏ bản vẽ 2D.
3. `js/roadmap-v5.js`: câu có dấu hiệu liên quan hình học mở MathGeo Studio Pro với nội dung đề. Học sinh có thể gửi ảnh PNG của bản vẽ về đúng câu hỏi. Ảnh này là bản nháp và không được dùng để thay đáp án hay hình chuẩn của đề.
4. `admin.html`: chức năng gửi hình vào Admin vẫn riêng biệt; nút gửi hình Admin không hiển thị cho học sinh trên Studio.
5. `backend/app/roadmap_v2_routes.py`: lưu lịch sử bằng chứng đã chấm (đúng, sai, bỏ qua, khối lớp, chủ đề, mức độ) theo từng học sinh, không lưu lặp lại đáp án hay nội dung câu hỏi trong bảng sự kiện.
6. Mô hình theo dõi kiến thức Bayesian Knowledge Tracing cập nhật mức thành thạo từ mỗi câu đã duyệt được chấm. Câu bỏ qua vẫn lưu làm dữ liệu mô tả nhưng không tự hạ mức thành thạo. Câu ứng viên không được dùng làm bằng chứng để cập nhật mô hình.
7. API `/api/roadmap-v2/tutor/{grade}` thêm mức tin cậy mô tả, nguyên nhân ưu tiên ôn, mức độ cần tập trung và các thống kê đã chấm.
8. API `/api/roadmap-v2/tutor-data/{grade}` cho học sinh đăng nhập xuất dữ liệu học của **chính mình** (tối đa 2.500 sự kiện gần nhất), không kèm khóa đáp án và dữ liệu học sinh khác. Giao diện lộ trình có nút xuất dữ liệu.

## Kiểm thử

- Backend: **191 passed**, chạy `pytest -q --ignore=tests/test_trig_generation.py` tại `backend/`.
- 13 trường hợp tham số hóa trong `test_trig_generation.py` chưa chạy trong đợt hồi quy này.
- Bổ sung kiểm thử V21: chặn rò dữ liệu sang học sinh khác, chỉ cập nhật mô hình khi có câu đã duyệt, bỏ qua không hạ năng lực, công cụ di động và kết nối câu hỏi-MathGeo.
- Kiểm tra cú pháp JS Node.js và Python đạt.
- Headless Chromium với nội dung HTML/CSS/JS được nạp nội tuyến (do hệ thống kiểm thử chặn truy cập localhost/file): kích thước 390×844 và 1366×768, thanh công cụ mở/đóng, chọn công cụ, không có lỗi JS khi dựng trang.
- Không phải kiểm thử trên điện thoại vật lý, cũng chưa kiểm thử end-to-end với backend triển khai công khai.

## Giới hạn và điều kiện quan trọng

- Phần dựng hình tự động bằng bộ phân tích văn bản có thể dựng nhầm khi đề thiếu giả thiết hoặc phức tạp; hình người học tự dựng không tự động được chứng nhận là hình chính xác.
- Đây là mô hình BKT **cập nhật trạng thái năng lực trực tuyến cho từng học sinh**, không phải huấn luyện lại mô hình ngôn ngữ lớn. Các xác suất đoán đúng/sơ suất vẫn là tham số giả định, **chưa hiệu chuẩn từ mẫu học sinh thực tế**.
- Ba bộ đề đầu vào lớp 10, 11, 12 **chưa đủ 1.350 câu được phê duyệt độc lập**; không thể tuyên bố đánh giá năng lực toàn diện hoặc độ tin cậy tâm trắc đạt chuẩn.
- Battle, Chat và các chức năng khác được giữ nguyên trên nền V20 nhưng không được tái chứng nhận 100% trong đợt này.

## Lưu ý dữ liệu

Không đưa `backend/database/mathweb.db`, `.mathweb_hmac_secret` vào gói nguồn. Khi nâng cấp hệ thống đang sử dụng cần sao lưu database người dùng, không chép đè lên dữ liệu thật. Bảng bằng chứng mới được tạo khi backend mở database.

## Các tệp đã sửa hoặc thêm

- `geometry-studio.html`
- `css/geometry-mobile-v21.css` (mới)
- `js/geometry-mobile-v21.js` (mới)
- `js/roadmap-v5.js`
- `admin.html`
- `backend/app/roadmap_v2_routes.py`
- `backend/tests/test_neon_v21_geometry_personalization.py` (mới)
- `NEON_V21_REPORT.md` (mới)
