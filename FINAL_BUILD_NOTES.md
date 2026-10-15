# MATH WEB FINAL 100P

This package is built additively from the latest Super Bank build plus the later multi-part Problem Generator layer.

Preserved: existing UI, practice/game/battle/account/friends/chat/notifications/auth flows, legacy game bank, template bank, Super Bank, extended bank, adaptive difficulty, duplicate detection, server-side answer checking, XP/level behavior, and existing geometry/game pages.

Added: reusable problem archetypes, coherent multi-part problems, mixed sub-question types, structured deterministic geometry diagrams, problem-mode API, problem-mode practice UI, and current Render API configuration.

## Local run

Backend:
`cd backend`
`python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Frontend in a second terminal:
`python -m http.server 5500`

Open `http://127.0.0.1:5500/`.

## Online backend

Production API: `https://math-webv2.onrender.com`

## GitHub update

Extract this package over the existing GitHub working tree, then run:
`UPDATE_GITHUB.bat`

The updater runs the project preflight checks first, then stages, commits, and pushes `main`.


## Geometry game routing fix (2026-10-12)

- The local fallback now checks the selected knowledge topic before generating a question. Circle games use circle angles/radii/tangents, and triangle-metric games use triangle relations or distance applications; they no longer fall through to the generic rectangle-area example.
- The geometry AI bank receives the selected game identity so the three games for each of these topics use distinct archetype families.
- Updated the 3 game labels for `Đường tròn`, `Hệ thức lượng trong tam giác`, and the duplicate legacy topic entry, keeping the existing shared visual layout intact.
- Static audit: 276 manifest entries, 92 topic IDs, 3 unique page paths per topic, all manifest paths exist, and all inline JavaScript blocks pass `node --check`.
- Backend regression suite: 12 tests passed. This is a tested build, not a guarantee that no environment-specific issue can ever occur.
