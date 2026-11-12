# MATH_WEB V182 | Ngân hàng câu hỏi 150 chủ đề

**Mục tiêu đang triển khai:** 150 chủ đề × 200 dạng toán độc lập thực sự × 10 câu/dạng = **30.000 dạng và 300.000 câu**. **Chưa đạt** mục tiêu này. Không được dùng số lượng ID hoặc biến thể số học để tuyên bố đã có 200 dạng/chủ đề.

## Đã bổ sung

- Giữ nguyên toàn bộ website V181, kế thừa bản mã nguồn V167 và 3.695 câu hợp lệ chờ nhập của V181.
- Thêm **1.660 câu mới** cho **83 chủ đề** chưa có câu trong gói nhập V181; mỗi chủ đề 20 câu thuộc **01 nhóm phương pháp ứng viên**. Có đáp án và lời giải, phân bổ **1.106 trắc nghiệm, 388 trả lời ngắn, 166 câu đúng/sai 4 nhận định**.
- Cả **150/150 chủ đề** hiện có ít nhất một câu trong **gói dữ liệu sẵn sàng nhập** V181+V182. Đây không phải 200 dạng/chủ đề.
- Bộ kiểm chứng số học, trình kiểm tra của ứng dụng và chấm đáp án kiểm tra được 1.660/1.660 câu. Trắc nghiệm có đúng một đáp án; đúng/sai được kiểm tra từng mệnh đề số học.
- Sửa đúng phạm vi ngân hàng: nhập đúng/sai 4 nhận định; chấm đúng/sai bằng cả mảng Boolean và chuỗi Đúng/Sai; nhóm các câu cùng phương pháp dưới cùng `archetype` để hỗ trợ chống lặp dạng trong Luyện tập.
- **Không sửa** giao diện, tài khoản, Battle, Admin, bạn bè, tin nhắn, thông báo hay dữ liệu cá nhân.

## Chạy và nhập dữ liệu trên Windows

1. Giải nén bản V182 **vào thư mục mới**, không đè lên mã GitHub mới hơn V167.
2. Để sử dụng dữ liệu người dùng cũ, giữ nguyên `mathweb.db` và các tệp lưu trữ cũ. Nếu SQLite nằm ở nơi khác, đặt biến môi trường `MATHWEB_DB_PATH` đến **đúng cơ sở dữ liệu đang sử dụng**.
3. Dừng backend. Chạy `IMPORT_BANK_V182.bat`. Công cụ chỉ **xem trước** trước khi yêu cầu xác nhận, rồi nhập lần lượt V181 và V182, **sao lưu riêng trước mỗi lượt**, dùng transaction và chống nhập trùng.
4. Khởi động `START_MATH_WEB.bat`. Kiểm tra Luyện tập, dạng trắc nghiệm, tự luận và đúng/sai ở Toán 10, 11, 12.
5. Muốn xuất thống kê 150 chủ đề theo dữ liệu thực tế: `python backend/scripts/bank_coverage_v182.py --db <duong-dan-mathweb.db> --output coverage.json`.

## Kiểm thử đã thực hiện (trên SQLite cô lập, KHÔNG phải production)

- V181: nhập 3.695 câu; V182: nhập thêm 1.660 câu; tổng 5.355 câu, 150/150 chủ đề; `PRAGMA integrity_check=ok`.
- Chạy lại V182: 0 bản ghi thêm; không nhân đôi.
- 150/150 chủ đề: API `/api/ai/questions` lấy được câu từ Admin bank và `/api/ai/questions/{id}/answer` chấm đúng.
- 83/83 chủ đề V182: câu đúng/sai 4 nhận định lấy được và chấm đúng với chuỗi/mảng Boolean.
- 35 bài kiểm thử hồi quy đạt.
- Đối chiếu nguyên văn đã chuẩn hóa với 344.280 câu JSONL cũ: không phát hiện trùng câu; **không** có nghĩa là đã loại được trùng bản chất toán học.

## Phần chưa đạt

- **0 dạng mới** được chứng nhận đủ cả 8 tiêu chí độc lập, 10 câu, toán học, chống trùng ngữ nghĩa, tích hợp production và truy vết.
- **0 câu** được xác nhận đã nhập vào production. Mọi con số nhập nêu trên là trên bản sao SQLite cô lập.
- Chưa thẩm định toàn diện từng bước lời giải bằng một công cụ độc lập và chưa chứng minh tính độc lập so với 344.280 câu nghiên cứu cũ.
- 5.355/300.000 câu là số liệu **gói nhập V181+V182**, không phải số câu đã được chứng nhận hoàn thành mục tiêu 300.000.
- Bản V182 không tự ý ghi đè cơ sở dữ liệu của người dùng, không thể kiểm tra commit GitHub mới nhất từ môi trường này.

**Tệp tham khảo:** `bank_updates/V182_REPORT.json`, `bank_updates/V182_150_TOPIC_COVERAGE.json`, `bank_updates/V182_FORM_SPECS.json`, `bank_updates/V182_ORACLE_AUDIT.jsonl`, `bank_updates/V182_150_TOPIC_API_SMOKE.json`.
