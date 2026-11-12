# MATH_WEB V131 | Báo cáo nghiên cứu và kiểm toán

**Nền:** MATH_WEB_GITHUB_READY_V130_METHOD_PROVENANCE_GATE.zip. Không sửa mã vận hành của bản nền.

## Mục tiêu và kết quả thực tế

| Hạng mục | Kết quả V131 |
|---|---:|
| Yêu cầu của người dùng trong lượt | Ít nhất 1.000 dạng mới, 10 câu/dạng |
| Dạng ứng viên mới đã biên soạn | **15** |
| Câu hỏi mới có đáp án và lời giải | **150** |
| Chủ đề có dữ liệu mới | **15/150** |
| Kiểm tra đáp án bằng phép tính độc lập/đối chiếu | **150/150 khớp** |
| Câu trùng nguyên văn với V121 và V123 (13.500 câu quét) | **0** |
| Dạng toán mới được chứng nhận độc lập | **0** |
| Kiểm thử riêng V131 | **10/10 đạt** |
| Hồi quy tích hợp toàn bộ backend, frontend, Battle | **Chưa chạy** |

## Nội dung cập nhật

- `V131_RESEARCH/V131_CANDIDATE_METHODS.jsonl`: 15 nhóm kỹ năng giải toán khác nhau được biên soạn và phân chủ đề, **chờ thẩm định phương pháp**.
- `V131_RESEARCH/V131_VERIFIED_QUESTIONS.jsonl`: 10 câu mỗi nhóm với đáp án, lời giải bằng tiếng Việt và kết quả phép kiểm tra.
- `V131_RESEARCH/generate.py`: mã sinh mẫu có kiểm tra số học/đại số thay thế; dữ liệu cố định 10 câu mỗi nhóm, không dùng ID để tạo dạng mới.
- `V131_RESEARCH/test_v131.py`: kiểm thử số lượng, tính duy nhất câu chữ, đáp án, trạng thái không công bố, liên kết lớp/chủ đề và phát hiện sửa đáp án.
- `V131_RESEARCH/audit.py`, `V131_RESEARCH/V131_RESULTS.json`: kiểm toán và minh bạch phạm vi.

## Phạm vi chứng minh

Kiểm tra độc lập chủ yếu dựa vào SymPy (đạo hàm, giải hệ, tích phân, nghiệm phức,...) và liệt kê trực tiếp một số trường hợp xác suất, số học. Không phải thẩm định chuyên gia toàn bộ lời giải bằng văn bản, không bảo đảm mọi phép kiểm toán đều hoàn toàn độc lập về cách tiếp cận. Các câu mới chỉ có một định dạng `tra_loi_ngan`; **chưa đạt yêu cầu đa dạng định dạng**.

Rà trùng đã bao phủ phần câu hỏi trong hai kho nghiên cứu V121 (3.000) và V123 (10.500). Việc đối chiếu không bao phủ tất cả JSONL cũ trong ZIP, không phát hiện trùng phương pháp bằng ngữ nghĩa và không tra cứu mọi nguồn ngoài. Tiêu đề không trùng nguyên văn với 1.350 bản ghi dạng của hai kho này, nhưng đây **không phải bằng chứng khác biệt toán học**.

## Bảo toàn dự án

Chỉ thêm thư mục V131_RESEARCH, giữ nguyên các mục đã có của V130 trong ZIP. Do không chạy web tích hợp nên không thể xác nhận Battle, đăng nhập, Admin và toàn frontend hoạt động bình thường chỉ từ việc giữ nguyên file.

## Bước kiểm chứng tiếp

Cần rà soát chuyên gia để loại trùng phương pháp, hoàn thiện câu hỏi trắc nghiệm/đúng-sai/tự luận thực sự phù hợp, phân phối thêm các dạng độc lập ở các chủ đề còn thiếu và chạy hồi quy hệ thống. Không được nhập dữ liệu V131 vào ngân hàng công khai trước khi duyệt.
