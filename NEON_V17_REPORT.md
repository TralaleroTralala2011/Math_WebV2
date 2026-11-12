# MATH_WEB NEON V17 | Đề đầu vào cố định lớp 10–12

**Ngày:** 11/11/2026  
**Nguồn thực tế:** `MATH_WEB_GITHUB_READY_NEON_V16_FIXED_PLACEMENT_2026-11-11.zip`  
**Phạm vi:** Chỉ nâng cấp hệ thống kiểm tra đầu vào, chất lượng câu hỏi và trải nghiệm làm đề; giữ các chức năng còn lại.

## 1. Kết quả triển khai thực tế

1. Giữ ba ma trận đề cố định lớp 10, 11, 12, bao phủ lần lượt **49, 51, 50 chủ đề**; mỗi chủ đề **3 mức × 3 câu**. Yêu cầu nội dung chính thức: **441 + 459 + 450 = 1.350 câu đã duyệt**.
2. Thêm **6 dạng toán ứng viên mới, 60 câu**, gồm: giao/hợp tập hợp lớp 10; số hạng/tổng cấp số nhân lớp 11; hệ số góc/phương trình tiếp tuyến lớp 12. Mỗi dạng có 10 câu, 7 trắc nghiệm + 2 tự luận + 1 Đúng/Sai, đáp án và lời giải. Bộ sinh có kiểm tra công thức và lựa chọn không tương đương. **Chưa phải câu được giáo viên chứng nhận**.
3. Kết hợp với **9 dạng/90 câu ứng viên đã có** (gồm dạng đỉnh parabol), tạo **15 dạng và 150 câu ứng viên** (50 câu/khối), liên quan **6/150 chủ đề**. Xuất riêng thành gói kiểm duyệt giáo viên để không đưa đáp án vào website công khai.
4. **Nâng cổng chất lượng đề cố định:** bắt buộc ít nhất **2 dạng toán QF2 khác nhau đã duyệt trong mỗi mức của từng chủ đề**, ngoài tối thiểu 3 câu/mức và ít nhất 2 hình thức trả lời/chủ đề. Không lấy 3 câu thay số của một dạng để giả làm đánh giá đa dạng.
5. **Kiểm tra nguồn gốc QF2:** một câu được coi là duyệt chính thức chỉ khi trùng khớp nội dung câu, đáp án, lựa chọn, lời giải, độ khó và chủ đề với bản chụp của dạng QF2 đã được duyệt trong database. Chỉ đặt nhãn `qf2-approved` hoặc `form:ID` là không đủ.
6. **Chấm tương đương toán học:** thêm bộ phân tích cú pháp hạn chế, không thực thi mã người học, để công nhận phương trình tương đương như `y=2x+3`, `2y=4x+6`. Không nhận phương trình sai hoặc biểu thức nguy hiểm.
7. **Giao diện làm đề dài:** chuyển đến chủ đề, nhảy đến câu chưa làm, đếm số câu đã trả lời, lưu vị trí phiên thi, xác nhận trước khi nộp nếu còn câu bỏ qua, hiển thị phù hợp máy tính và điện thoại.
8. **Admin:** thêm nút sinh 6 dạng/60 câu ứng viên cho ba lớp, chỉ vào hàng chờ kiểm duyệt, không tự phê duyệt.
9. **Tách dữ liệu kiểm duyệt:** chuyển các tệp chứa đáp án mẫu ra khỏi `placement-exams/teacher-review` của web root, xuất gói `MATH_WEB_PRIVATE_TEACHER_REVIEW_V17.zip` riêng. Không phục vụ gói này qua máy chủ tĩnh.

## 2. Tình trạng nội dung đầu vào

| Lớp | Số chủ đề | Chỉ tiêu câu đã duyệt | Ứng viên trong gói giáo viên V17 | Câu được duyệt trong checkpoint V16 | Đủ đề chính thức? |
|---|---:|---:|---:|---:|---|
| 10 | 49 | 441 | 50 | 0 | Không |
| 11 | 51 | 459 | 50 | 0 | Không |
| 12 | 50 | 450 | 50 | 0 | Không |
| **Tổng** | **150** | **1.350** | **150** | **0** | **Không** |

Các con số duyệt là **baseline V16**, không tự khẳng định trạng thái database riêng của người dùng. Các dạng ứng viên phải được giáo viên đánh giá tính đúng đắn, độ khó, nội dung và tính độc lập; sau đó mới có thể xuất bản.

## 3. Kiểm thử

- Backend: `pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'` → **192 passed, 1 deselected**.
- 5 bài kiểm thử V17 mới: sinh 60 câu, cổng đa dạng dạng toán, chấm phương trình tương đương và chống đầu vào nguy hiểm, quyền Admin/idempotent, chống giả mạo nguồn câu.
- JavaScript: `node --check` với `js/roadmap-v5.js` và `js/admin-neon-v7.js` → đạt.
- ZIP: kiểm tra CRC sau đóng gói; loại database, khóa ký, cache và tệp bí mật.
- **Chưa kiểm thử thực tế** độ chính xác đánh giá năng lực với học sinh thật, tính công bằng giữa các nhóm người học hoặc tính ổn định theo thời gian.

## 4. Cơ sở thiết kế đánh giá

- Chương trình GDPT 2018 môn Toán theo Thông tư 32/2018/TT-BGDĐT: https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721
- OECD PISA 2022 Mathematics Framework: https://www.oecd.org/en/publications/pisa-2022-assessment-and-analytical-framework_dfe0bf9c-en/full-report/component-3.html

Các khung trên hướng đến tư duy, lập luận, mô hình hóa, giải quyết vấn đề, vận dụng và diễn giải. Bộ câu hiện có chủ yếu là bài tính toán quy trình, **chưa có đủ bằng chứng đo được toàn bộ các năng lực trên**. Không sao chép đề PISA hay tự nhận tương đương đề PISA.

## 5. Giới hạn bắt buộc phải nói rõ

- **Chưa đạt 100% ba bộ đề đầu vào**: còn thiếu câu đã kiểm chứng cho phần lớn 150 chủ đề.
- Không thể bảo đảm “đánh giá khách quan tuyệt đối” chỉ bằng phần mềm. Cần kiểm định chuyên môn độc lập và thử nghiệm với mẫu học sinh phù hợp, phân tích độ khó, độ phân biệt, độ tin cậy, tính công bằng và sai lệch do mệt mỏi khi làm 441–459 câu.
- Bài thử với câu ứng viên không được dùng để tuyên bố năng lực hoặc mở khóa lộ trình chính thức.
- Bài đầu vào cố định dùng 3 câu/mức/chủ đề có độ bất định cao ở từng mức; điểm theo chủ đề cần diễn giải thận trọng.
- Để hoạt động chính thức, giáo viên cần duyệt đủ 1.350 câu và ít nhất 2 dạng độc lập mỗi mức/chủ đề; sau đó Admin công bố từng đề và chạy thử nghiệm thực địa.
- Khi triển khai web thật, không dùng `python -m http.server` trên toàn thư mục chứa backend/database hoặc các gói kiểm duyệt. Cần tách web root khỏi backend và bảo vệ cơ sở dữ liệu.

**Kết luận:** V17 bổ sung 60 câu ứng viên có kiểm tra toán, tăng độ đa dạng, chống giả mạo chứng nhận và cải thiện việc làm/chấm đề. Đây là một bước nâng cấp thực tế, **không phải chứng nhận hoàn thiện 100%**.
