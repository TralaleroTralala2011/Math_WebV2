# MATH WEB: Audit and repair report

This update is based on `MATH_WEB_UNIFIED_COMPLETE_100P_2_GEOMETRY_AI_UPGRADED_FINAL`.
The existing HTML/CSS layouts were preserved; changes focus on backend reliability, AI question generation, and regression checks.

## Repairs made

1. **SQLite lock between matchmaking and AI history**
   - The random matchmaking route starts modifying its queue before generating the battle questions.
   - The AI anti-repeat ledger previously wrote to the same SQLite file during that transaction. When a second player joined, the backend could raise `sqlite3.OperationalError: database is locked`; browsers could misleadingly report it as a CORS failure because the unhandled server error had no CORS header.
   - AI question history now uses a separate persistent SQLite file. Set `MATHWEB_AI_HISTORY_DB_PATH` to choose its location. If `MATHWEB_DB_PATH` is set, the history database is placed beside it automatically.
   - History-table schema setup now runs once per database path per process instead of on every read/write, reducing schema-lock pressure.

2. **CORS development origins**
   - Localhost, loopback, common private LAN ranges, and the configured GitHub Pages origin are accepted for HTTP(S) requests.
   - Credentials remain enabled without using a wildcard origin.

3. **Grade 11 trigonometry generator exhaustion**
   - The old shared trig bank contained a few fixed prompts. The permanent anti-repeat ledger eventually marked them all as seen and the API returned `Could not generate a valid unique question: None`.
   - Value, identity/formula, trig-function, and trig-equation topics now use dedicated, parameterized builders with a much larger question pool.
   - The question set no longer silently raises the difficulty for its final questions solely because the set has at least eight questions. The selected level stays consistent unless adaptive history explicitly changes the level.

4. **Grade 11 triangle topic mapping**
   - Triangle-law topics no longer fall through to unrelated vector questions in the Grade 11 geometry curriculum path.

5. **Small JavaScript config cleanup**
   - Removed duplicated `window.MATHWEB_API_URL` fallback checks without changing API selection precedence.

6. **Linear-system repetition in practice and games**
   - Expanded the system-question builder from one main solve pattern into multiple structures: sum/difference, coefficient systems, scaled equations, expression-finding, word problems, and checking a proposed solution.
   - Updated the existing “Điều tra”, “Tìm giá trị”, and “Ghép đáp án” game builders so their prompts do not all repeat `x+y=...; x-y=...`.
   - Kept level boundaries meaningful: foundational tasks focus on direct systems, intermediate tasks combine steps, and advanced tasks add modeling, algebraic transformations, and reasoning.

7. **Broader plane geometry and diagram variety**
   - `hinh_hoc_10` now draws from 18 original archetypes, including basic area/perimeter and angle facts, similarity, rhombi, trapezoids, cyclic quadrilaterals, angle bisectors, tangent-secant power, medians, and proof reasoning.
   - Expanded the SVG renderer to show distinct diagram families for quadrilaterals, circle chords, tangents, cyclic quadrilaterals, and pyramids instead of reusing a single generic triangle.
   - Diagram captions identify illustrative figures that are not to scale; existing page layouts and controls remain intact.

## Validation performed

- `python -m pytest -q`: **32 tests passed**.
- AI question generation across every listed curriculum topic at easy, medium, and hard: **252/252 cases passed**.
- Repeated Grade 11 trig practice sets: **24 sets of 10 questions passed**, with no duplicate question text inside each set.
- CORS preflight tested for localhost, loopback, a private LAN origin, and the configured GitHub Pages origin.
- Two-user API smoke tests passed for account registration, friend request/acceptance, and chat message delivery.
- Two-user matchmaking successfully moved from `QUEUED` to `MATCHED`, generated 10 battle questions, and passed match-start, current-match, answer, and progress checks.
- All JavaScript files passed `node --check`, including the extended geometry SVG renderer.
- All five AI knowledge JSON files parsed successfully.
- Checked **330 HTML files** and **1,064 local `href`/`src` references**; no missing local references found.
- All **276 knowledge-game pages** contain the expected unified controls.

## Notes

These checks validate the source code and backend APIs locally. They do not prove that an already-deployed external backend is online or that every browser/device behaves identically. After replacing the project, restart the backend using `START_BACKEND.bat` and check `http://127.0.0.1:8000/health` before testing the site.


## Bổ sung hiển thị chuyên đề hình học theo khối lớp (6.5)
- Bổ sung các thẻ chuyên đề hình học nền tảng/trung cấp/nâng cao cho Toán 10, 11, 12 trong `js/practise.js`.
- Bổ sung ánh xạ từ các thẻ mới tới mã chủ đề AI hiện có để khi mở chuyên đề, AI nhận đúng nội dung hình học.
- Giữ nguyên cấu trúc giao diện; thay đổi chỉ ở dữ liệu chủ đề và ánh xạ AI.
