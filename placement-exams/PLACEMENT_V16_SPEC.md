# MATH_WEB NEON V16: Đề đầu vào cố định Toán 10, 11, 12

## 1. Phạm vi và tình trạng thực tế

Đây là **ba bản thiết kế đề riêng biệt**, một bản cho mỗi lớp, không phải ba đề đã được duyệt. Tại checkpoint V15, **0 câu đã được phê duyệt độc lập** cho kỳ kiểm tra đầu vào chính thức. Hệ thống V16 không tự nâng cấp câu ứng viên thành câu đã kiểm chứng.

| Lớp | Chủ đề | Mức độ/chủ đề | Câu/mức | Câu tối thiểu trong đề |
|---|---:|---:|---:|---:|
| 10 | 49 | 3 | 3 | 441 |
| 11 | 51 | 3 | 3 | 459 |
| 12 | 50 | 3 | 3 | 450 |
| **Tổng** | **150** | | | **1.350** |

Ba file `grade_10_blueprint.json`, `grade_11_blueprint.json`, `grade_12_blueprint.json` chứa toàn bộ 150 chủ đề, các ô yêu cầu của ba mức, phiên bản và quy tắc đề cố định. **Các file này chỉ là ma trận đề, không chứa câu hỏi/đáp án được duyệt.**

## 2. Cơ sở chuyên môn

- Chương trình GDPT 2018 môn Toán: năng lực tư duy và lập luận, mô hình hóa, giải quyết vấn đề, giao tiếp toán học và sử dụng công cụ.
- OECD PISA 2022 Mathematics Framework: mathematical reasoning; formulate, employ, interpret/evaluate; bốn miền nội dung. MATH_WEB chỉ tham khảo **khung năng lực**, không sử dụng lại câu hỏi có bản quyền và không tự nhận là đề PISA.
- Standards for Educational and Psychological Testing: tính hợp lệ của diễn giải điểm, độ tin cậy, tính công bằng phải có bằng chứng thực nghiệm, không thể khẳng định chỉ từ mã nguồn.

Nguồn:
1. https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721
2. https://www.oecd.org/en/publications/pisa-2022-assessment-and-analytical-framework_dfe0bf9c-en/full-report/component-3.html
3. https://www.pearson.com/content/dam/one-dot-com/one-dot-com/global/Files/efficacy-and-research/reports/PTE-Academic-Assessment-Efficacy-Report-2019.pdf

## 3. Quy trình duyệt và công bố

1. Giáo viên tạo hoặc nhập câu hỏi đúng chủ đề, đúng lớp, phân mức **Nền tảng, Trung cấp, Nâng cao**.
2. Kiểm tra độc lập đáp án và lời giải; phát hiện trùng đề và lựa chọn tương đương. Mỗi dạng QF2 phải có >=10 câu trước khi công nhận dạng mới.
3. Chỉ câu có nguồn `qf2-approved` trong **ngân hàng backend** được chọn vào đề chính thức. Không lấy câu từ `verified-lessons.json` công khai ở frontend vì dễ lộ đáp án.
4. Hệ thống cố định chọn **3 câu/mức/chủ đề** theo thuật toán tất định, không phụ thuộc tài khoản học sinh. Phải có >=2 hình thức trả lời trong mỗi chủ đề. Nếu bất kỳ chủ đề/mức nào thiếu, **không xuất bản**.
5. Admin duyệt và công bố qua trang Admin hoặc `POST /api/roadmap-v2/fixed/publish/{grade}`. Đề được lưu dưới dạng bản chụp bất biến và có SHA-256; nếu câu bị thu hồi/đổi nội dung, đề bị vô hiệu hóa cho lần thi mới.
6. Học sinh chọn lớp rồi làm bài qua `mode=fixed_placement`. API không gửi đáp án/lời giải trước khi nộp. Mỗi người chỉ được làm một lần trên cùng một phiên bản đề cố định để tránh nhớ đáp án; bản nháp có thể tiếp tục.
7. Sau nộp: lưu đúng/sai/bỏ qua theo thứ tự, thống kê từng chủ đề/mức, khoảng tin cậy Wilson 95% và khuyến nghị ôn tập. Không gọi đó là kết luận năng lực chuẩn hóa.
8. Lộ trình ba chủ đề và kiểm tra 30 câu chỉ mở khi có bài đầu vào chính thức đủ điều kiện và ngân hàng câu hỏi của từng chủ đề đạt chuẩn.

## 4. Đánh giá khách quan cần làm thêm

Bộ đề nhiều câu không tự động có độ tin cậy. Cần học sinh tham gia thử nghiệm thực tế có đồng ý phù hợp, người kiểm định chuyên môn và dữ liệu không định danh để đánh giá:
- Độ khó thực tế từng câu (`p_correct`), tỷ lệ bỏ qua.
- Độ phân biệt (tương quan câu với tổng điểm đã loại chính câu đó).
- Độ nhất quán nội tại (Cronbach alpha) và độ ổn định theo thời gian.
- Tính phù hợp chương trình, tính công bằng, sai lệch do ngôn ngữ và khả năng tiếp cận.

Endpoint Admin `GET /api/roadmap-v2/fixed/calibration/{grade}` chỉ trả thống kê tổng hợp khi có >=30 người học thực tế cùng một đề, nhưng **30 chỉ là ngưỡng tối thiểu để hiển thị phân tích sơ bộ, KHÔNG phải cỡ mẫu đủ để chứng minh tính khách quan**. Phải tiếp tục thử nghiệm với cỡ mẫu lớn hơn và đa dạng.

## 5. Vận hành và an toàn

- Tài khoản học sinh **không có quyền xuất bản**; API Admin xác thực quyền trên máy chủ.
- Khi triển khai thực tế, **không** đặt thư mục backend/database, file `.db`, khóa ký token, file JSON có đáp án hoặc nhật ký vào web root công khai. `python -m http.server` ở thư mục dự án chỉ nên dùng thử cục bộ, không dùng để phát đề chính thức trên Internet.
- Câu hỏi có sẵn ở thư viện công khai không được dùng trong đề cố định chính thức.
- Mỗi đề cố định dài 441–459 câu, vì vậy giao diện lưu bản nháp để người học nghỉ và làm tiếp. Cần nghiên cứu giảm tải qua đánh giá nhiều giai đoạn hoặc đề thích ứng đã hiệu chuẩn, thay vì coi bài dài là mặc nhiên chính xác.
- Không huấn luyện lại LLM từ bài làm; gia sư hiện cập nhật ước lượng năng lực bằng dữ liệu câu đã duyệt, có giới hạn độ tin cậy.

## 6. Các tệp

- `grade_10_blueprint.json`, `grade_11_blueprint.json`, `grade_12_blueprint.json`: ma trận 150 chủ đề.
- `grade_10_readiness.json`, `grade_11_readiness.json`, `grade_12_readiness.json`: số liệu kiểm định từ database trống, có thể xuất lại khi thêm câu.
- `MATH_WEB_PRIVATE_TEACHER_REVIEW_V17/GRADE_*_CANDIDATE_ITEMS_PRIVATE.json` (gói riêng, không phục vụ qua web): **80 câu ứng viên** từ 8 bộ sinh hiện có, có kiểm tra tính toán trong bộ sinh nhưng **chưa được giáo viên phê duyệt**, không được tính là câu đầu vào chính thức.
- `backend/app/fixed_placement.py`: tạo và kiểm tra đề cố định.
- `backend/app/placement_psychometrics.py`: phân tích thô độ khó, độ phân biệt, alpha khi có dữ liệu thực tế.
- `backend/tests/test_neon_v16_fixed_placement.py`: kiểm thử blueprint, quyền, xuất bản, chấm, lộ trình và không lộ đáp án.

**Kết luận:** V16 hoàn thiện **kiến trúc ba đề đầu vào cố định và kiểm soát chất lượng trước công bố**, nhưng **chưa hoàn thiện nội dung 1.350 câu đã được phê duyệt**, chưa có bằng chứng hiệu chuẩn thực địa. Không tuyên bố đạt 100% chất lượng đánh giá năng lực.
