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
