# V20 | Thiết kế đánh giá năng lực Toán 10–12 và điều kiện phát hành

## Phạm vi

- Giữ nguyên 3 ma trận cố định: 49 chủ đề lớp 10 = 441 câu; 51 chủ đề lớp 11 = 459 câu; 50 chủ đề lớp 12 = 450 câu.
- Mỗi chủ đề cần tối thiểu 3 câu đã duyệt độc lập cho mỗi mức độ **Nền tảng, Trung cấp, Nâng cao**, đa dạng phương pháp và hình thức.
- Không cho học sinh thi chính thức khi còn thiếu độ phủ hoặc tính đúng toán học.
- Giao diện có tính năng lưu tiến độ, nhưng đề 441–459 câu phải nghiên cứu chia phiên tránh mệt mỏi; không coi bài dài là tự động khách quan.

## Nguồn giáo dục đã tra cứu

- **Thông tư 32/2018/TT-BGDĐT, Chương trình GDPT 2018**: https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721
- **Bộ GD&ĐT, đề minh họa môn Toán từ 2025**: https://xaydungchinhsach.chinhphu.vn/de-thi-minh-hoa-mon-toan-tot-nghiep-thpt-tu-nam-2025-119231229180528163.htm
- **Bộ GD&ĐT, đề tham khảo môn Toán từ 2025**: https://xaydungchinhsach.chinhphu.vn/de-tham-khao-thi-tot-nghiep-thpt-mon-toan-tu-nam-2025-119241018154616944.htm
- **Cấu trúc đánh giá từ 2025 gồm nhiều lựa chọn, Đúng/Sai, trả lời ngắn**: https://xaydungchinhsach.chinhphu.vn/cau-truc-de-thi-tot-nghiep-thpt-tu-nam-2025-119240308200554932.htm
- **OECD PISA 2022 Mathematics Framework**, lập luận; mô hình hóa; sử dụng; diễn giải: https://www.oecd.org/en/publications/pisa-2022-assessment-and-analytical-framework_dfe0bf9c-en/full-report/component-3.html
- **AERA/APA/NCME, Standards for Educational and Psychological Testing**, độ tin cậy, hợp lệ, công bằng: https://ncme.org/resources/books/testing-standards/

Các nguồn này dùng để tham khảo **cách xây dựng ma trận, hình thức, năng lực đánh giá**, không chép đề và không đồng nghĩa MATH_WEB đã đạt chuẩn OECD/Bộ GD&ĐT.

## Nội dung mới V20

- 31 dạng ứng viên độc lập theo cách giải thiết kế, tổng 310 câu mới có đáp án và lời giải qua kiểm tra công thức tự động. Phân bố: 10 dạng lớp 10, 10 dạng lớp 11, 11 dạng lớp 12.
- Tổng câu ứng viên có thể xuất ra để giáo viên kiểm duyệt: 460 câu / 46 dạng / 37 chủ đề (gồm 150 câu từ 15 dạng V16–V17).
- Hàng chờ V20 chỉ có ở API Admin `/api/admin/qf2/generate/placement-v20-review-batch`; **không tự duyệt**.
- Câu hỏi và lời giải đầy đủ xuất riêng bằng `python tools/export_v20_private_review.py --output /path/outside/webroot`.
- Kiểm thử thêm kiểm tra 4 đáp án trắc nghiệm không tương đương toán học, kể cả `0,5` và `1/2`.

## Điều kiện để xác nhận sử dụng chính thức

1. Giáo viên độc lập kiểm tra đúng toán học, độ rõ ràng, chủ đề, lớp, mức độ của từng câu và xác nhận dạng có phương pháp riêng.
2. Có tối thiểu 1.350 câu đạt yêu cầu theo ma trận 150 chủ đề, và ít nhất 2 dạng khác phương pháp ở mỗi ô chủ đề×mức; không dùng một dạng thay số để lấp đề.
3. Không lộ đáp án qua giao diện hoặc đường dẫn web tĩnh, và có phương án chống học thuộc khi dùng đề cố định.
4. Thử nghiệm với học sinh ở các mức năng lực khác nhau, phân tích độ khó, độ phân biệt, thời gian, tỷ lệ bỏ qua và tính công bằng.
5. Chỉ sau khi đạt tất cả mới cân nhắc nhãn **đề chính thức có bằng chứng đánh giá**. Chưa có dữ liệu học sinh thật thì mọi điểm năng lực vẫn là ước lượng sơ bộ.

**KẾT LUẬN:** V20 tạo được câu ứng viên và quy trình kiểm chứng, KHÔNG hoàn tất 100% đề đánh giá năng lực và không tự công bố đề.
