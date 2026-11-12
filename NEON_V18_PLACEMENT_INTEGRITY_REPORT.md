# MATH_WEB NEON V18 | Kiểm toán và gia cố hệ thống đề đầu vào cố định

**Ngày:** 12/11/2026  
**Nguồn:** `MATH_WEB_GITHUB_READY_NEON_V17_PLACEMENT_2026-11-11.zip`  
**Phạm vi thay đổi:** Hệ thống thi đầu vào cố định lớp 10–12, an toàn ngân hàng đề và độ tin cậy dữ liệu. Các chức năng khác của V17 được giữ nguyên.

## 1. Những điểm thực tế đã tìm thấy và khắc phục

1. **Đếm đa dạng dạng toán sai vị trí:** V17 kiểm tra số `form_id` trong cả kho câu hỏi đủ 2 dạng, nhưng khi chọn đề có thể chỉ còn một dạng do các câu còn lại trùng câu hỏi. V18 bắt buộc kiểm tra **hai dạng được chọn thực tế trong mỗi mức**, tránh đề nhìn đa dạng trên giấy nhưng thực chất lặp dạng.
2. **Đề đã xuất bản không kiểm tra ma trận mới:** Đề lưu trong DB giờ buộc khớp với bản ma trận lớp đang dùng (hash của blueprint), tổng số câu, phân bổ đúng ba mức, nguồn đã duyệt, hai dạng/mức, hai hình thức/chủ đề và không trùng câu/ID. Thay đổi ma trận hoặc thu hồi câu phải làm đề cũ mất hiệu lực; bổ sung câu đã duyệt mới vào kho mà không đổi cấu trúc cũ không tự vô hiệu hóa đề đã xuất bản.
3. **Xung đột khi tái xuất bản:** ID đề mới lấy từ cả hash câu hỏi và hash ma trận. Admin có thể xuất bản lại cùng tập câu dưới phiên bản ma trận mới mà không bị nhầm với bản cũ.
4. **Lộ đáp án của đề cố định:** Sau khi thi, V17 trả về cả đáp án và lời giải của toàn bộ câu. Người thi đầu tiên có thể chia sẻ đáp án cho người khác, gây sai lệch đánh giá. V18 giữ chìa khóa đáp án ở máy chủ, trả về tổng điểm, phân tích theo chủ đề/mức và gợi ý ôn; với bài đầu vào *cố định dùng chung* không xuất bản chi tiết đáp án/lời giải qua `/submit`, `/status` hay `/latest`. Với bài luyện tập và kiểm tra chủ đề 30 câu, quyền xem đáp án và giải thích **giữ nguyên**.
5. **Giới hạn bản nháp và bài nộp chưa đồng đều:** V18 thống nhất kiểm tra ID, kiểu dữ liệu, tối đa 2.000 ký tự/câu, tổng 150.000 byte cho hai tuyến nộp bài và lưu bản nháp. Giảm khả năng nộp chuỗi quá lớn làm nghẽn backend.
6. **Giao diện kết quả:** bổ sung thông báo rõ lý do giữ riêng đáp án của đề đầu vào dùng chung; vẫn giữ phần phân tích theo năng lực và xuất hồ sơ JSON.

## 2. Kết quả kiểm thử

- `pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'` trong thư mục `backend`: **196 passed, 1 deselected** (30,27 giây).
- **4 kiểm thử hồi quy V18 mới:** kiểm tra phân bổ đề và 2 dạng, chặn dạng trùng trong đề đã chọn, giới hạn đầu vào, hủy hiệu lực/tái xuất bản theo phiên bản và kiểm tra không lộ đáp án trong cả ba API trả dữ liệu.
- `node --check js/roadmap-v5.js`: đạt.
- Kiểm tra cú pháp Python: đạt.
- Kiểm tra tính toàn vẹn ZIP bằng CRC: ghi trong lúc đóng gói.
- Kiểm thử lượng giác nhiều lượt `test_trig_equation_topic_survives_multiple_sets`: chưa chạy trong đợt tổng hợp vì thường chạy lâu; không tuyên bố toàn bộ test đã đạt.

## 3. Trạng thái đề lớp 10–12

| Lớp | Chủ đề | Bắt buộc 3 câu x 3 mức/chủ đề | Ứng viên V17 | Đủ chứng nhận trong gói? |
|---|---:|---:|---:|---|
| 10 | 49 | 441 | 50 | Không |
| 11 | 51 | 459 | 50 | Không |
| 12 | 50 | 450 | 50 | Không |
| **Tổng** | **150** | **1.350** | **150** | **Chưa** |

**Không được gộp 150 ứng viên thành 150 câu đã phê duyệt.** Gói phần mềm xuất bản không đính kèm database thực của người dùng; số câu đã phê duyệt trên hệ thống vận hành phải đọc trực tiếp từ DB nơi triển khai. Các bản báo cáo độ phủ trong ZIP là snapshot của checkpoint, không phải dữ liệu người dùng thời gian thực.

## 4. Chưa đủ để công bố đề khách quan

- Thiếu tối thiểu 1.350 câu được giáo viên độc lập kiểm tra, kèm đáp án/lời giải/độ khó đã chuẩn hóa; các dạng phải khác nhau về bản chất, không chỉ thay số.
- Cần thử nghiệm trên học sinh thật, hiệu chuẩn độ khó, chỉ số phân biệt, độ tin cậy, mức độ phù hợp chương trình và công bằng giữa các nhóm học sinh. Thống kê mô tả ban đầu không bảo đảm tính khách quan hoàn toàn.
- Đề cố định 441–459 câu có thể gây mệt mỏi, thiên lệch theo thời lượng làm bài. Cần thiết kế thời gian nghỉ, lưu tạm và nghiên cứu rút gọn/thi theo đợt có neo chuẩn, không áp đặt một kết luận đơn lẻ dựa trên điểm.
- Đề cố định dùng chung vẫn có nguy cơ bị ghi nhớ/chia sẻ nội dung dù đã giấu đáp án chi tiết. Để giảm hơn nữa cần bộ đề cân bằng nhiều phiên bản, bảo vệ quyền truy cập và giám sát thực địa.
- Bản nâng cấp này **không** chứng minh đã hoàn thành 100% ngân hàng 150 chủ đề hay độ tin cậy tâm trắc của đề.

## 5. Cách triển khai

1. Sao lưu database trước khi thay ZIP; đừng ghi đè dữ liệu đang chạy.
2. Chạy các kiểm thử; cho giáo viên duyệt ngân hàng theo checklist chuyên môn và bấm công bố từng đề khi trạng thái `ready` đạt.
3. Hệ thống sẽ không cho làm đề cố định chính thức nếu thiếu câu đạt chuẩn hoặc đề đã bị vô hiệu hóa.
4. Dùng HTTPS và web root riêng, **không** cho máy chủ tĩnh truy cập thư mục `backend`, database hay bộ đáp án kiểm duyệt.
5. Không lưu hay công bố đáp án chính thức trong frontend hoặc gói tài liệu học sinh.

## Nguồn tham khảo về thiết kế

- Chương trình giáo dục phổ thông môn Toán, Bộ GD&ĐT, 2018.
- OECD PISA 2022 Mathematics Framework: https://www.oecd.org/en/publications/pisa-2022-assessment-and-analytical-framework_dfe0bf9c-en/full-report/component-3.html
- AERA/APA/NCME, Standards for Educational and Psychological Testing (2014). Các nguyên tắc được vận dụng như tài liệu tham khảo, không tuyên bố chứng nhận theo các chuẩn này.
