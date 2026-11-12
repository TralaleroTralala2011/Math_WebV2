# MATH_WEB V191 | Tiếp tục phát triển NGÂN HÀNG, không sửa tính năng khác

## Phạm vi thực tế

- Nguồn mã nền: `MATH_WEB_GITHUB_READY_V182_FULL_WEB_150_TOPIC_BANK.zip` (150 chủ đề), bảo toàn mã nguồn website và dữ liệu staging V181–V182.
- Các tệp của V183–V190 được giữ trong `bank_updates/` (bản cũ được bảo toàn).
- Tạo **52 nhóm dạng ứng viên mới, 520 câu mới**, theo tỷ lệ 364 trắc nghiệm, 104 trả lời ngắn, 52 đúng/sai (mỗi nhóm 10 câu). SymPy và bộ validator / answer_checker của ứng dụng đã kiểm tra.
- Phục hồi **360 câu** từ các bản vá V186–V190 bằng cách chỉnh **mã chủ đề** theo bảng ánh xạ đúng danh mục, **20 câu** không khớp chủ đề được cách ly (V186 `chia_du`, V190 `da_thuc`). Không tạo chủ đề mới.
- Hợp nhất với **6.756 câu** đã qua kiểm tra QA của V185, tạo `V191_CUMULATIVE_QA_IMPORT.jsonl` có **7.636 câu**, không trùng nguyên văn trong tệp này. 7.636 **không** phải số câu mới V191 và **không** chứng minh mọi lời giải đều đúng tuyệt đối.
- Mỗi chủ đề trong 150 chủ đề có ít nhất 10 câu staging, từ 10 đến 290 câu. Đây **không** phải mức độ bao phủ thật của production.
- **Dạng toán độc lập mới được chứng nhận: 0; câu xác nhận ghi production: 0.** Không có SQLite production trong ZIP nguồn.

## Kiểm thử đã thực hiện

- Sử dụng SQLite *tạm*, không chứa dữ liệu cá nhân: importer đã ghi `0 → 7.636` câu; nhập lại `7.636 → 7.636` (0 câu mới), `quick_check=ok`.
- Thử truy xuất câu hỏi trên `AIQuestionService._curated_admin_candidates`, dựng câu và chấm đáp án cho ba định dạng ở Toán 10, 11, 12.
- Đối chiếu V191 mới với 20.166 bản ghi đọc được từ các ZIP V181–V190 (7.209 đề duy nhất): trùng nguyên văn 0, trùng mẫu lời văn thay số 0. Đây không phải bằng chứng chống trùng ngữ nghĩa hoàn chỉnh.
- `backend/scripts/import_bank_updates.py` đã sửa **2 chỗ tối thiểu** để câu trả lời ngắn thiếu khóa `choices` được ghi bằng `[]` (trước đó viết DB báo `KeyError`). Các chức năng ngoài nhập ngân hàng không đổi.

## Nhập vào cơ sở dữ liệu MATH_WEB đang hoạt động

**Không có quyền truy cập database production từ phiên này.** Người quản trị phải nhập trên hệ thống của mình, sau khi dừng backend để tránh cập nhật song song. Chạy thử kiểm tra trước:

```bash
python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db --input bank_updates/V191_CUMULATIVE_QA_IMPORT.jsonl
```

Nếu số `potential_new` phù hợp, dừng backend và chạy ghi có sao lưu SQLite mới:

```bash
python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db --input bank_updates/V191_CUMULATIVE_QA_IMPORT.jsonl --write --backup backups/mathweb-before-v191.sqlite
```

Trên Windows có thể mở `IMPORT_BANK_V191.bat`, truyền đường dẫn DB nếu khác mặc định, nhập chữ `NHAP` để cho phép ghi.

- Công cụ từ chối tạo DB mới nếu không tìm được tệp đích; dùng transaction, ledger và đối chiếu before/after; không xóa câu, tài khoản hay kết quả cũ.
- Số bản ghi `inserted` sau ghi và kết quả truy xuất thực tế mới là bằng chứng tích hợp; đừng dùng số file staging để báo sản phẩm đã hoạt động.
- Một số câu là ứng viên cần tiếp tục thẩm định độc lập về ý nghĩa, độ khó, nghiệm và cách giải. Trước khi sử dụng rộng rãi nên kiểm duyệt học thuật.

## Các tệp quan trọng

- `V191_IMPORT_READY.jsonl`: 520 câu tạo mới V191, có oracle, bài giải.
- `V191_FAMILY_SPECS.json`: 52 mô tả nhóm dạng/phương pháp.
- `V191_RESCUED_PRIOR_IMPORT.jsonl`: 360 câu cũ được sửa mã chủ đề để nhập được.
- `V191_RESCUE_QUARANTINE.json`: 20 câu chưa có chủ đề khớp, không nhập.
- `V191_CUMULATIVE_QA_IMPORT.jsonl`: 7.636 câu đã qua bộ kiểm tra nhập của ứng dụng.
- `V191_COVERAGE_150_STAGING.csv`: thống kê từng chủ đề. Cột production để trống do không có DB thật.
- `V191_GENERATION_AUDIT.json`, `V191_AUDIT_AND_SANDBOX_INTEGRATION.json`, `V191_IMPORT_REHEARSAL.json`: chứng cứ kiểm tra trong môi trường cô lập.
- `backend/question_factory/v191_generate.py`: nguồn tạo 520 câu V191.
- `backend/scripts/v191_rescue_prior_patches.py`: ánh xạ thận trọng chủ đề cũ.
- `backend/scripts/v191_full_rehearsal.py`: kiểm tra nhập và truy xuất vào DB tạm, có thể chạy lại.

## Tiến độ mục tiêu

- 150 × 2.000 dạng = **300.000 dạng** / 3.000.000 câu. **Chưa xác minh** số thiếu từng chủ đề trong production.
- Mốc 10.000 dạng mới và 100.000 câu mới trong phiên này **chưa đạt**.
- Cần ưu tiên nhận cơ sở dữ liệu production (không chứa dữ liệu cá nhân nhạy cảm khi chia sẻ), chạy bản xem trước, thẩm định ngữ nghĩa và kiểm tra truy xuất sau ghi.
