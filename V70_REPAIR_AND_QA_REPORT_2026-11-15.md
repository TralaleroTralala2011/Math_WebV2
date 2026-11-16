# MATH_WEB V70 – Repair and regression QA

**Source:** User-uploaded `MATH_WEB_V69_GEOMETRY_3D_NAVBAR_CRASH_FIXED_20261115(1).zip` (197,943,900 bytes).

## Verified and fixed

1. **Shared navbar would remove legitimate page headers.** V69 detected the word `MATH` in the first header and replaced the entire element. On the roadmap page, this removed the title and introductory instructions; on Battle it removed the dedicated PvP status header. `js/unified-navbar-v55.js` now only replaces a real site navigation header, preserves page headers, and refuses to mount twice. Geometry mode buttons and its tool header remain intact.
2. **Geometry AI right-angle invariant.** For a generic right triangle ABC described as right-angled at A, the coordinates formerly made B the right-angle vertex while marking A as 90°. The geometry AI now constructs AB perpendicular to AC at A and keeps the right-angle mark there.
3. **Rectangle versus square.** The AI previously matched the mere word `vuông` (as in `góc vuông`) and could incorrectly make a rectangle into a square. The square branch now activates only when the described shape is explicitly a square (`hình vuông` / `hinh vuong`).
4. **Extra null guards in MathGeo `switchMode`.** The mode controls and status label are now handled safely if another layout extension omits an optional element.
5. **Broken legacy game HTML.** 31 HTML copies under `mathweb_work/games/knowledge` contained malformed nested `<script src="...<script>...` fragments. These were repaired from their corresponding current, identical-topic `games/knowledge` pages. Their six shared JS/CSS references now point at the real repository-root assets, avoiding nonexistent files under the legacy subtree. No live `games/knowledge` page was rewritten.

## Tests run

- **23 focused Chromium browser checks** using the actual inline geometry JavaScript and navbar script, with local HTML injected into Chromium because this test runner blocks direct localhost navigation. Includes: preserve roadmap and geometry-lab titles; preserve Battle header and Geometry toolbar; navbar idempotence; all 13 3D templates; AI right triangle perpendicularity; rectangle not turned into square; Oxyz point/vector construction; mobile drawer behavior at 393 and 768 pixels. All passed without JavaScript page errors.
- **57 targeted Python backend pytest cases passed**, including geometry diagrams, bank V61/V62/V63, HTML integrity, security/Battle logout, Admin encrypted backups.
- **V68 integration smoke:** 528 game HTML topic IDs recognized; 9 API scenarios for Dãy số / Phân thức đại số returned eight non-repeating questions per scenario; radical MCQ distractor example had exactly one correct answer.
- **Static asset audit:** 4,532 local `<script src>` and `<link href>` references across HTML files; **0 missing paths** after fixing legacy copies.
- Changed JavaScript passed `node --check`; both inline Geometry JavaScript sections passed `node --check`.
- Original ZIP files compared by CRC; exactly **33 existing project files intentionally changed**. **66 test-altered files restored from the original ZIP**, including `backend/database/mathweb.db` and cached Python bytecode. No existing file removed. Added this report and `tools/test_v70_nav_geometry_integration.py` (the browser test script needs optional `playwright` and `beautifulsoup4`, not installed by the production app).

## Not proven

This was not an end-to-end deployment on GitHub Pages/Render, and does not certify all 150 topics' mathematical correctness, all 1,134 HTML pages' user interactions, all multiplayer race conditions, or every possible geometry text prompt. Actual live deployment, authenticated two-user Battle, database backup/restore, and broad mathematical quality assurance still require separate verification. Do not claim the website is 100% bug-free based on these tests.
