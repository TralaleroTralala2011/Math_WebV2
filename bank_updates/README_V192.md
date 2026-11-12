# MATH_WEB V192 | NGÂN HÀNG CÂU HỎI, KHÔNG CHỈ REVIEW_ONLY

## Kết quả đã kiểm chứng trong phiên

- Nguồn: bản **V191 FULL WEB BANK QA IMPORT** của cùng dự án, kế thừa 150 chủ đề và 7.636 bản ghi kiểm tra đầu vào.
- **150 nhóm dạng toán ỨNG VIÊN mới** được viết cho **150/150 chủ đề** (mỗi chủ đề ít nhất một nhóm mới). Từng nhóm có đặc tả bản chất, điều kiện, phương pháp, mức khó và **10 bài tập khác nhau**.
- **1.500 câu mới**: 1.050 trắc nghiệm bốn lựa chọn, 300 câu trả lời ngắn, 150 câu đúng/sai bốn nhận định. Tất cả đã qua kiểm tra giá trị chính xác bằng SymPy/đối chiếu biểu thức, validator, bộ chấm và kiểm tra duy nhất một lựa chọn đúng cho trắc nghiệm. Đây không phải một cuộc duyệt chứng minh thủ công đầy đủ mọi lời giải.
- Đối chiếu với V191 staging: 0 trùng đề nguyên văn, 0 trùng mẫu đề khi thay các số thành ký hiệu. Bộ lọc này **không chứng minh khác nhau về bản chất toán học**.
- Tổng bộ hợp nhất = **9.136 bản ghi** (7.636 trước đó + 1.500 mới), mỗi chủ đề đều được bổ sung thêm đúng 10 câu.
- **Đã nhập vào SQLite của BẢN WEBSITE ĐƯỢC ĐÓNG GÓI:** `backend/database/mathweb.db`, bảng `admin_question_bank` 0 → 9.136; 1.500 câu mới có nguồn V192. Thử nhập lần hai thêm 0 câu.
- **Kiểm tra trên chính bộ đọc và chấm câu của website** cho từng chủ đề và từng định dạng: **450/450** tổ hợp chủ đề × định dạng đạt.
- Các bảng `users`, `game_results`, `friends`, `messages`, `notifications`, `question_sessions` được đối chiếu trước và sau nhập: **không đổi**. Bản website cũ V191 được giữ nguyên nội dung từng tệp, chỉ thay đổi SQLite ngân hàng và bổ sung tệp V192.

## Những gì CHƯA được xác nhận

- **0 dạng toán mới được chứng nhận độc lập trên toàn bộ lịch sử dự án.** 150 nhóm là ứng viên đã được kiểm tra đầu vào và toán học cơ bản, còn cần thẩm định ngữ nghĩa với toàn bộ ngân hàng cũ. Các bài thay số được gom về 1 mã `form_id`/nhóm, tuyệt đối không cộng chúng thành 1.500 dạng mới.
- **0 câu đã xác nhận được nhập vào SQLite production đang chạy trên máy chủ/người dùng.** Bản website ZIP có ngân hàng SQLite đã nạp là bản sao độc lập, không phải production; không có quyền thay thế dữ liệu đang chạy.
- Chưa có cơ sở xác định số thiếu thật sự của mỗi chủ đề trên production. Cột production trong báo cáo 150 chủ đề được để `null` thay vì bịa số.
- Không chứng nhận thành tích 10.000 dạng độc lập và 100.000 câu mới trong phiên. Chưa chạy đủ 60 phút có bằng chứng.

## Sử dụng bản website đầy đủ

1. Giải nén `MATH_WEB_GITHUB_READY_V192_FULL_WEB_BANK_INTEGRATED.zip`, mở thư mục `MATH_WEB_GITHUB_READY`.
2. Nếu MATH_WEB dùng **đường dẫn SQLite mặc định**, ngân hàng **9.136 câu** đã nằm sẵn trong `backend/database/mathweb.db`. Không cần nhập lại.
3. Nếu bạn đang chạy MATH_WEB với `MATHWEB_DATA_DIR` hoặc `MATHWEB_DB_PATH` trỏ ra cơ sở dữ liệu khác, thì đó là DB riêng. **KHÔNG thay DB đó bằng file trong ZIP**, để bảo vệ tài khoản, mật khẩu băm, XP và lịch sử. Để cập nhật, dùng công cụ dưới đây.

## Nhập đúng 1.500 câu V192 vào DB hiện có, không thay dữ liệu cũ

Trên bản đầy đủ V192, xem trước khi nhập:

```
python backend/scripts/import_bank_updates.py --db "<DUONG_DAN_DB_HIEN_CO>" --input bank_updates/V192_IMPORT_READY.jsonl
```

Sau khi đã dừng tiến trình backend đang dùng DB, kiểm tra số liệu xem trước, dùng sao lưu mới và cho phép ghi:

```
python backend/scripts/import_bank_updates.py --db "<DUONG_DAN_DB_HIEN_CO>" --input bank_updates/V192_IMPORT_READY.jsonl --write --backup "<DUONG_DAN_SAO_LUU_MOI>.sqlite"
```

Trên Windows, có thể dùng `IMPORT_BANK_V192_NEW_ONLY.bat` cùng đối số đường dẫn DB; mặc định là `backend\database\mathweb.db`. Lệnh bắt buộc xác nhận và tạo sao lưu trước khi thêm. Không xóa/sửa câu hỏi hoặc dữ liệu người dùng cũ, và từ chối ghi nếu DB không tồn tại, không đúng cấu trúc, hoặc đường sao lưu đã có.

Đối với nơi chưa nhập V191, chỉ dùng `V192_CUMULATIVE_QA_IMPORT.jsonl` khi đã xác nhận dữ liệu thực còn thiếu, đã xem trước và có bản sao lưu, vì tệp bao gồm cả 7.636 câu trước.

## Bằng chứng và dữ liệu

- `V192_IMPORT_READY.jsonl`: 1.500 câu mới, đã qua các kiểm tra trên.
- `V192_FAMILY_SPECS.json`: 150 nhóm với phương pháp và điều kiện.
- `V192_CUMULATIVE_QA_IMPORT.jsonl`: 9.136 câu hợp nhất, không trùng nguyên văn trong tệp.
- `V192_COVERAGE_150_STAGING.csv`/`.json`: số đã bổ sung theo từng chủ đề, cột production để trống.
- `V192_GENERATION_AUDIT.json`, `V192_METHOD_SIMILARITY_REVIEW.json`, `V192_IMPORT_REHEARSAL.json`, `V192_FULL_TOPIC_RETRIEVAL_TEST.json`, `V192_RELEASE_REPORT.json`, `V192_SOURCE_MANIFEST.json`: các mức xác minh riêng biệt.
- `backend/question_factory/v192_generate.py`: mã tái tạo 1.500 câu từ tham số, với kiểm tra chính xác biểu thức và bộ chấm.
- `backend/scripts/v192_integrate_and_audit.py`: thử nhập tích hợp, **chỉ chạy trên bản sao V191 chưa có ngân hàng**; sẽ từ chối nếu bảng `admin_question_bank` không rỗng. Không chạy trên production.
- `backend/scripts/v192_verify_150_topics.py`: đọc, dựng và chấm mẫu từ 150 chủ đề, cả ba định dạng, trong bản website mặc định.

## Chỉ tiêu tiếp theo

Kiểm chứng độc lập ngữ nghĩa từng nhóm với tài liệu/ngân hàng gốc, tăng chất lượng distractor và nhận định đúng/sai, thêm các dạng còn thiếu dưới đúng phạm vi 150 chủ đề, và xác nhận việc nhập trên DB production thông qua số bản ghi trước/sau + truy xuất thật. Mốc cuối cùng là 300.000 dạng độc lập và 3.000.000 bài tập; không suy ra đã đạt từ số dạng ứng viên.
