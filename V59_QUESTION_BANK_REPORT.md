# MATH_WEB V59 · Báo cáo bổ sung và kiểm tra ngân hàng câu hỏi

## Nền tảng và bảo toàn

- Cơ sở: MATH_WEB V58 (không thay giao diện, tài khoản, Battle, các file Word, hoặc dữ liệu người dùng).
- ZIP B56 tải lên trùng **chính xác SHA-256** với ZIP B56 đã đóng gói trong V58.
- ZIP `Question_Bank_V254 (7)(1).zip` trùng chính xác với ZIP `Question_Bank_V254_latest_uploaded.zip` đã đóng gói; B56 có 4 file bổ sung và sửa 3 Word so với ZIP cũ.
- Toàn bộ 150 file Word, các JSON/JSONL/ZIP nguồn, 2 SQLite nguồn và dữ liệu cũ được giữ nguyên.

## Đối chiếu số lượng (không cộng trùng)

| Hạng mục | Số lượng |
|---|---:|
| V254 cũ | 83.298 câu |
| B56 | 85.878 câu |
| Trùng nguyên văn sau chuẩn hóa Unicode/khoảng trắng giữa V254 và B56 | 83.041 câu |
| B56 khác nguyên văn V254 | 2.837 câu |
| B56 mới tạm loại do đáp án trả lời ngắn mang nhãn A/B/C/D | 330 câu |
| B56 mới tạm loại vì lời giải quá ngắn hoặc trường dữ liệu không đạt giới hạn | 90 câu |
| B56 mới qua kiểm tra cấu trúc | 2.417 câu |
| Bài mới V59 tự thiết kế, đáp án kiểm tra lại bằng công thức/SymPy | **170 câu** |
| Nhóm phương pháp dùng tạo 170 câu mới (10 câu/nhóm) | **17 nhóm** |
| Tổng câu trong lớp bổ sung V59 | **2.587 câu** |
| Tổng câu khác nguyên văn đủ điều kiện truy vấn từ V254 + lớp V59 | **85.885 câu** |

Lưu ý: **85.885 không có nghĩa là 85.885 bài toán khác bản chất, không phải toàn bộ đã kiểm chứng độc lập về toán học**. Việc thay số vẫn là cùng một dạng. Các câu B56 vượt qua vòng lọc cấu trúc vẫn được đánh dấu *ứng viên chưa chứng nhận*. 170 câu mới đã đối chiếu đáp án bằng tính toán độc lập trong giới hạn dạng đã thiết kế, chưa có thẩm định giáo viên.

## Bao phủ chủ đề

- Hệ thống `backend/app/ai/knowledge/index.json` định nghĩa **150 chủ đề**.
- Tất cả 150 chủ đề chính thức đã có bản ghi trong hợp các nguồn V254 + lớp bổ sung V59 sau khi bổ sung vào ba chủ đề thiếu dữ liệu.
- Có ba ID ở B56 không trùng ID trong danh mục học tập: `chia_du`, `chia_het`, `phuong_trinh_bac_hai`. Giữ nguyên các mã này vì Battle và một số phần cũ đang dùng. Chưa tự ý gộp sang chủ đề khác để tránh sai kiến thức.

## Cơ chế dùng dữ liệu

1. `v59_screened_additions.sqlite` chứa 2.587 câu đọc-only được chọn từ B56 và câu tự thiết kế mới; không thay đổi các SQLite gốc.
2. `v59_screened_additions.seed.zip` và manifest SHA-256 cho phép máy chủ Render khôi phục tệp SQLite V59 nếu thiếu.
3. `AIQuestionService._v254_candidates` ưu tiên kết hợp **V59 đã lọc + V254 cũ**, không lấy lại 83.041 bản sao B56 theo vòng lặp thứ hai; nếu V59 không thể phục hồi thì fallback về V254 + B56 gốc.
4. Bộ chọn câu trong frontend `js/practise.js` không hiển thị hai câu có cùng nội dung trong một lượt. Nếu ngân hàng không cấp đủ số câu khác nhau, hiện lỗi rõ ràng, không lặp câu để đủ số lượng.
5. Battle dùng chung `AIQuestionService._v254_candidates`, nên cũng được hưởng cơ chế lọc trùng và dữ liệu bổ sung, nhưng phần matchmaking, điểm, đồng hồ và tuyển đề không bị sửa.
6. API verified-bank khi gặp con trỏ Git LFS chưa tải đúng file thực sẽ trả trạng thái `503` có thông báo; không đếm nhầm con trỏ thành dữ liệu đã chứng nhận.

## Kiểm thử

- `pytest backend/tests/test_v59_screened_bank.py backend/tests/test_v59_lfs_placeholder.py backend/tests/test_v53_b56_topic_selection.py`: **9/9 đạt**.
- API Luyện tập thử với 5 chủ đề lớp 10–12: trả 3/3 câu không trùng trong mỗi lượt.
- Battle chủ đề `phuong_trinh_bac_hai`: thử tạo 10 câu trắc nghiệm và 10 câu trả lời ngắn riêng biệt, không lặp nguyên văn trong từng bộ.
- Kiểm tra chuẩn hóa/cú pháp Python, cú pháp JavaScript, SQLite quick_check và checksum seed.
- Các bộ kiểm thử cũ vẫn có bài kỳ vọng Battle `PLAYING` ngay sau khi nhận lời mời. Bản hiện tại cần hai người chọn chủ đề trước nên các bài kiểm thử cũ đó chưa được cập nhật.
- Tệp `verified_seed_bank.jsonl` riêng biệt vẫn là con trỏ Git LFS trong nguồn hiện có. Chưa thể chứng nhận toàn bộ dữ liệu bởi thiếu file JSONL thật.
- **Chưa kiểm thử trên Render/GitHub Pages thật**, chưa xác nhận tất cả câu đúng toán học hay không trùng *ngữ nghĩa*.

## Phạm vi file thay đổi

- Backend: `backend/app/ai/engine/service.py`, `backend/app/ai/engine/v59_bank.py`, `backend/app/verified_bank_routes.py`.
- Frontend: `js/practise.js` (chốt chặn chống trùng).
- Dữ liệu *bổ sung*: `backend/app/ai/storage/v59_screened_additions.*`.
- Công cụ tái tạo, bài kiểm thử và báo cáo V59.
- Không thay đổi thông tin đăng nhập, Admin, bạn bè, Chat, Battle, navbar, Word, JSON/JSONL nguồn hay mã giao diện còn lại.
