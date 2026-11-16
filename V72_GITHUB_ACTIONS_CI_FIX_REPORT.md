# MATH_WEB V72 - GitHub Actions CI regression repair

## Root causes found from the run log
1. `scripts/v54_preflight.py` in deployed GitHub checkout crashes on a route object without `.path`.
2. `backend/tests/test_api_integration.py` has obsolete Battle expectations: questions are now created only after BOTH users commit topics.

## Additional regression issue discovered
The grouped CI suite also found that `/api/factory/progress`, `/api/factory/next` and `/api/factory/answer` were missing from `app.main` even though the factory router exists. The router is now mounted in `backend/app/main.py`. Factory storage has its own database; no original user/question bank database is overwritten by this change.

## Files updated from MATH_WEB V71
- `scripts/v34_preflight.py`: ignore non-endpoint objects during API route introspection; missing REQUIRED_PATHS continue to fail.
- `backend/tests/test_api_integration.py`: exercise actual two-user SELECTING -> PLAYING state transition, with an isolated deterministic question fixture, and assert one shared deck.
- `backend/app/main.py`: register the existing Question Factory router to restore required API paths.
- `scripts/ci_route_guard_hotfix.py`: patches the existing *v54_preflight.py* or v34 file **in place**, without overwriting new checks in that script.

## Very important for the GitHub run screenshot
The supplied V71 ZIP uses `scripts/v34_preflight.py`, while the screenshot shows the GitHub repository running `scripts/v54_preflight.py`. This package does NOT replace unknown future v54 preflight rules. In an existing checkout using v54, run `python scripts/ci_route_guard_hotfix.py` before its CI preflight to apply the one-line fix safely, or manually replace the comprehension in v54 as shown in the README.

## Limits
- The revised matchmaking tests isolate state and timing from the question bank through a deterministic fixture. They are not a substitute for bank-integrity or live two-user tests.
- No files in the user database or question bank are intentionally changed.
- CI may have other errors after these are fixed.

## Kiểm thử đã chạy trong phiên này
- `pytest -q backend/tests/test_api_integration.py`: 9/9 đạt.
- `pytest -q backend/tests/test_question_factory_v112.py backend/tests/test_api_integration.py backend/tests/test_learning_assignments.py backend/tests/test_geometry_diagrams.py`: 47/47 đạt.
- `PYTHONPATH=backend python scripts/v34_preflight.py`: 0 lỗi, 176 API routes, 22 trang frontend, 676 đường dẫn được quét, V254 giữ 83.298 câu và 95.514 nhãn Word trong bảng đếm gốc.
- `GET /api/factory/progress` với DB riêng đã bootstrap thử: HTTP 200, 150 chủ đề.
- Quét toàn bộ `pytest -q backend/tests`: **430 đạt, 32 không đạt trong lần quét**. Các nhóm còn thất bại gồm test Battle quá cũ, kiểm thử giao diện cũ, và test verified-bank phụ thuộc Git LFS bị thiếu dữ liệu thực. Không tuyên bố CI toàn bộ đã xanh. Không thay logic Battle để khớp test cũ.

## Áp dụng vào GitHub hiện có
Ảnh GitHub gọi `scripts/v54_preflight.py`, trong khi V71 gốc gọi `scripts/v34_preflight.py`. Sửa *ngay trong v54 hiện có* đoạn:

```python
routes={route.path for route in app.routes}
```

thành:

```python
routes={p for route in app.routes if isinstance((p := getattr(route, 'path', None)), str)}
```

Hoặc thêm `python scripts/ci_route_guard_hotfix.py` trước lệnh preflight của workflow hiện tại (công cụ này sửa trong chỗ, không ghi đè các bài kiểm tra khác của v54). Chỉ có sửa trên bản V71 trong ZIP đầy đủ, KHÔNG khẳng định nội dung V71 giống hệt repo đang ở trên GitHub.

Không sửa database hay Word; mọi tệp nguồn khác của V71 được bảo toàn trong bản đóng gói từ ZIP nguồn, không dùng database đã sinh bởi kiểm thử.
