# MATH_WEB NEON V20 | Báo cáo nghiên cứu và mở rộng đề đầu vào lớp 10–12

**Ngày:** 12/11/2026  
**Nền mã nguồn:** V19 EVIDENCE FAIRNESS (ZIP cung cấp trong hội thoại).  
**Kết luận:** Đã triển khai một đợt mở rộng ngân hàng câu hỏi và kiểm định tự động có thực; **chưa đạt 100% điều kiện công bố ba đề đầu vào chính thức**.

## 1. Phần công việc thực hiện trong V20

1. Tra cứu nguồn cấu trúc thi/khung đánh giá: Chương trình GDPT 2018, đề minh họa và đề tham khảo môn Toán từ 2025 của Bộ GD&ĐT, cấu trúc ba hình thức MCQ/Đúng-Sai/Trả lời ngắn, OECD PISA 2022, AERA/APA/NCME.
2. **Viết mới 31 dạng toán ứng viên theo phương pháp**, tổng **310 câu**, có lời giải, đáp án và các phương án nhiễu. Không nhầm 310 bài thay số là 310 dạng độc lập.
3. Phân phối dạng mới: lớp 10 = 10 dạng/100 câu; lớp 11 = 10 dạng/100 câu; lớp 12 = 11 dạng/110 câu.
4. Kết hợp bộ dạng ứng viên cũ (V16–V17) và mới: **46 dạng/460 câu ứng viên/37 chủ đề** trên tổng 150 chủ đề. Đây là **ứng viên chưa qua duyệt độc lập**.
5. Xuất gói **PRIVATE_TEACHER_REVIEW** bên ngoài thư mục công khai: file riêng lớp 10, 11, 12 có đáp án và lời giải, bảng kiểm kê toàn bộ 150 chủ đề, quy trình kiểm duyệt.
6. Bổ sung API Admin `POST /api/admin/qf2/generate/placement-v20-review-batch` để đưa đúng 31 dạng/310 câu mới vào hàng chờ kiểm duyệt. Gọi lại không tạo trùng. Mặc định `pending_review`, **không tự phê duyệt**.
7. Bổ sung danh mục V20 riêng `GET /api/admin/qf2/generate/placement-v20-catalog`, giữ nguyên API danh mục bộ sinh V7 để tương thích ngược.
8. Bổ sung nút **“Đề đầu vào V20 · 31 dạng / 310 câu”** trong Admin NEON. Học sinh không có chức năng này.
9. Sửa kiểm tra đáp án trắc nghiệm tương đương dạng thập phân có dấu phẩy: `0,5` và `1/2` là cùng một giá trị. Kiểm tra lại cả trong đề cố định đã công bố; bộ đề sai cấu trúc phải bị chặn.
10. Bổ sung kiểm thử kiểm tra 310 đáp án từ công thức tính riêng, bốn lựa chọn trắc nghiệm, Đúng/Sai, quyền Admin, idempotency, bảo vệ đề cố định.

## 2. Con số được xác minh

| Khối | Chủ đề chương trình | Số câu chính thức tối thiểu | Dạng ứng viên từ tất cả bộ sinh | Câu ứng viên | Chủ đề có ứng viên |
|---|---:|---:|---:|---:|---:|
| 10 | 49 | 441 | 15 | 150 | 12 |
| 11 | 51 | 459 | 15 | 150 | 12 |
| 12 | 50 | 450 | 16 | 160 | 13 |
| **Tổng** | **150** | **1.350** | **46** | **460** | **37** |

**Câu ứng viên = 460 không đồng nghĩa câu đã duyệt = 460.** Trên snapshot kiểm kê hiện tại chưa có câu nào được xác nhận là đã duyệt và đủ tư cách chọn vào đề cố định chính thức. Số liệu DB máy chủ triển khai có thể khác.

## 3. Kết quả kiểm thử

- Lệnh: `cd backend && pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'`.
- **200 passed, 1 deselected** (bộ kiểm thử lượng giác dài chưa chạy).
- `node --check js/admin-neon-v7.js`: đạt.
- `python -m compileall` các module thay đổi: đạt.
- Bộ QA 310 câu V20 xác nhận: 31 dạng, không lặp nguyên văn câu hỏi, đáp án khớp hàm kiểm tra riêng, 7 trắc nghiệm + 2 tự luận + 1 Đúng/Sai/dạng, không có hai lựa chọn tương đương được phát hiện.
- Tạo hàng chờ thử nghiệm: 31/31 dạng được tạo lần đầu; gọi lại 31/31 được nhận diện là đã tồn tại; không có dạng tự phê duyệt; học sinh bị chặn 403.
- Kiểm tra ZIP bằng CRC: ghi trong quy trình đóng gói.

**Giới hạn QA:** Mã kiểm tra đáp án độc lập về đường mã không thay thế việc giáo viên giải từng câu, kiểm định độ khó và thực nghiệm độ phân biệt với học sinh.

## 4. Bài toán đánh giá năng lực khách quan vẫn chưa giải quyết xong

- Thiếu **các câu hỏi đã được kiểm tra độc lập** theo từng chủ đề và mức độ: phải có 1.350 câu chính thức cùng điều kiện ít nhất hai phương pháp/dạng trong mỗi ô chủ đề × mức.
- 113/150 chủ đề hiện chưa có dạng ứng viên trong bộ sinh xuất riêng; ngay cả 37 chủ đề có ứng viên cũng chưa chắc đủ hai dạng/mức và chưa được kiểm duyệt.
- Độ khó Nền tảng/Trung cấp/Nâng cao trong bộ sinh là **nhãn sơ bộ, không phải độ khó tâm trắc đã được đo**; không thể gắn nhãn cao chỉ vì thay số lớn.
- Cần bài làm thí điểm từ học sinh thật, độ khó thực nghiệm, chỉ số phân biệt, khoảng tin cậy, kiểm tra tính công bằng, kết quả sau học và ảnh hưởng mệt mỏi của đề dài 441–459 câu.
- Cần kiểm thử trên hai máy thật Battle/Chat và kiểm tra đối chiếu UI với ảnh mẫu ở desktop/mobile nếu mục tiêu toàn bộ hệ thống vẫn là 100%. V20 không sửa hoặc chứng nhận các phần này.

## 5. Cách sử dụng, giữ an toàn đáp án

1. Giải nén ZIP mã nguồn `MATH_WEB_GITHUB_READY_NEON_V20...zip` vào workspace.
2. Sao lưu SQLite và khóa ký token ở hệ thống đang dùng. Không chép đè DB người dùng bằng DB trong bản test.
3. Đăng nhập Admin rồi chọn **Đề đầu vào V20 · 31 dạng / 310 câu** để tạo hàng chờ xem xét; thao tác chỉ tạo **ứng viên**.
4. Chỉ giáo viên đã kiểm tra toán học và mức độ mới phê duyệt. Công cụ tự động **không** xuất bản đề đầu vào.
5. Gói `MATH_WEB_V20_PRIVATE_TEACHER_REVIEW.zip` chứa đề + đáp án + lời giải. **Không đặt trong thư mục frontend/public**, không công khai URL.
6. Khởi chạy thử website và chạy bộ kiểm thử trước khi triển khai cho học sinh.

## 6. Các nguồn đã kiểm tra

- [Chương trình GDPT, Thông tư 32/2018/TT-BGDĐT](https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721)
- [Đề minh họa Toán từ năm 2025, Cổng thông tin Chính phủ](https://xaydungchinhsach.chinhphu.vn/de-thi-minh-hoa-mon-toan-tot-nghiep-thpt-tu-nam-2025-119231229180528163.htm)
- [Đề tham khảo Toán 2025, Cổng thông tin Chính phủ](https://xaydungchinhsach.chinhphu.vn/de-tham-khao-thi-tot-nghiep-thpt-mon-toan-tu-nam-2025-119241018154616944.htm)
- [Cấu trúc đề thi tốt nghiệp từ 2025, Cổng thông tin Chính phủ](https://xaydungchinhsach.chinhphu.vn/cau-truc-de-thi-tot-nghiep-thpt-tu-nam-2025-119240308200554932.htm)
- [OECD PISA 2022 Mathematics Framework](https://www.oecd.org/en/publications/pisa-2022-assessment-and-analytical-framework_dfe0bf9c-en/full-report/component-3.html)
- [AERA/APA/NCME Standards for Educational and Psychological Testing](https://ncme.org/resources/books/testing-standards/)

**Bản V20 dùng các nguồn trên để định hướng kỹ năng, cấu trúc câu hỏi và kiểm định, không sao chép nguyên văn đề thi có bản quyền.**
