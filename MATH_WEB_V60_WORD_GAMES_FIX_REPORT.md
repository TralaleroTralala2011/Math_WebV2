# MATH_WEB V60 · Tích hợp Word và sửa Luyện tập (2026-11-15)

## Nền và bảo toàn
- Nền: `MATH_WEB_V59_QUESTION_BANK_AUDITED_DEDUP_20261114.zip`.
- Giữ nguyên các tài liệu Word gốc, V254/B56/V59, tài khoản, Battle, Admin và cấu trúc database người dùng.
- Lưu `150_CHU_DE_WORD_SOURCE_V60.zip` nguyên byte từ ZIP người dùng.
- Xuất `question_bank_word_v60.zip`: 150 JSONL, mỗi file tương ứng một Word.
- Ngân hàng bổ sung `v60_word_candidates.seed.zip` là lớp ứng viên tách biệt, SQLite kiểm tra checksum và tự khôi phục.

## Kết quả chuyển Word
- 150 Word, 95.544 mục đánh dấu Câu (bao gồm các mục trùng và thiếu cấu trúc).
- 16.274 ứng viên đủ cấu trúc chưa được thẩm định toán học độc lập toàn diện.
- 77.194 mục trùng nguồn V254/V59; 1.375 mục trùng trong Word; 345 trắc nghiệm không hợp lệ; 356 mục thiếu trường.
- Có 3 chủ đề từ Word không xuất hiện trong danh mục AI 150 chủ đề, được hỗ trợ ánh xạ riêng thay vì làm tăng số lượng menu lên 153.
- Không được cộng tổng số bản ghi trong các nguồn để tuyên bố là câu hỏi độc lập.

## Sửa game và câu hỏi
- Bộ nạp câu hỏi dùng chung `js/game-question-bridge-v60.js` cho 528 trang game.
- 3 trò chơi: `Khởi động`, `Tăng tốc`, `Chinh phục` (mỗi chủ đề). Bỏ quy tắc ẩn trò chơi số 3 dựa vào tên cũ.
- Game số 3 dùng bộ câu hỏi hỗn hợp bình thường, không đọc nhầm dữ liệu bài toán nhiều phần (`problems`) như `questions`.
- Game thử nguồn khác/cấu hình phù hợp trong **cùng chủ đề**, không lấy câu chủ đề khác làm phương án bù.
- Chặn trùng theo nội dung đã chuẩn hóa trong toàn bộ lượt game và qua các đợt tải; nếu thiếu câu trả ít hơn và báo hết, không lặp câu.
- Backend chỉ cho phép kết quả một phần đối với yêu cầu từ game (`game_id`); chế độ đề thông thường và Battle giữ quy tắc cũ.
- Sửa ánh xạ game cũ như `remainder -> chia_du`, `divisibility -> chia_het`, `quadratic-equation -> phuong_trinh_bac_hai`, `sequence -> day_so` lớp 11.

## Kiểm chứng
- Toàn bộ 528 HTML game: JavaScript kiểm tra cú pháp với Node.js, đạt.
- TestClient API thử chọn câu theo 3 mức của Chia dư: mỗi lần trả 8 câu không trùng.
- TestClient các game Chia dư, Chia hết, Phương trình bậc hai và Dãy số: HTTP 200, 5 câu mỗi chủ đề.
- Test kiểm tra khôi phục ngân hàng V59, placeholder Git LFS: 6/6 đạt.
- Kiểm tra ZIP Word, bản SQLite seed: CRC không lỗi, nguồn Word nguyên byte.
- Đã thử trình duyệt Chromium nhưng môi trường chặn truy cập localhost; chưa kiểm thử trực tiếp thao tác trên GitHub Pages/Render.
- Một số test Battle **cũ** vẫn mong đợi trạng thái `PLAYING` ngay; bản hiện tại dùng `SELECTING` theo yêu cầu chọn chủ đề của cả hai, nên test cũ không phản ánh quy trình mới. Không sửa ngược Battle.

## Triển khai
- Cần đưa **toàn bộ frontend** lên GitHub Pages và **backend cùng phiên bản** lên Render.
- Không xóa database người dùng khi deploy.
- Giữ checksum trong `backend/app/ai/storage/v60_word_manifest.json` và tệp seed bên cạnh. Nếu Render không lưu bền vững, nguồn seed giúp dựng lại kho ứng viên.
- Dữ liệu ứng viên không đồng nghĩa đã chứng nhận toán học. Chưa chứng minh 100% bài trong kho có đáp án chính xác.
