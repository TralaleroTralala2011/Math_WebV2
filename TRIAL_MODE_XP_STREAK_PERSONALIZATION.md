# MATH WEB: Trial mode, admin separation, personalization, XP and streaks

## Trial experience
- The public trial button calls `POST /api/auth/demo` and creates a disposable `trial_*` learner identity.
- The trial uses the learner API/token and can exercise learner features without using admin credentials.
- Admin sessions use `mathweb_admin_token`, `mathweb_admin_user`, and `mathweb_admin_profile`; learner/trial sessions use `mathweb_token`, `mathweb_user`, and `mathweb_profile`.
- Trial accounts and their game activity are excluded from admin learner counts, user lists, assignment recipients, and aggregate game reports.

## Admin controls
- `GET/PUT /api/admin/learning/config`: question sources, distribution rules, default difficulty, XP multiplier, and daily activity target.
- `GET/PUT /api/admin/users/{user_id}/personalization`: preferred difficulty, difficulty adjustment, source mode, question-count scale, and teacher note.
- Personalization applies to teacher-assigned work when a student starts it. Admin-bank-only mode does not silently fall back to AI if no reviewed bank questions match.

## XP and learning streak
- Regular game completion uses the existing game XP rules, with the admin-configured XP multiplier. Duplicate game IDs are rejected by the existing finish guard.
- Teacher-assigned work awards 10 XP per correct answer plus a 5 XP completion bonus, multiplied by the same configured factor. A submitted assignment cannot be submitted again for more XP.
- Completing a valid game or submitting assigned work updates the Vietnam-local daily learning streak. Multiple activities on the same day do not increase the streak more than once.
- The streak API is `GET /api/games/streak`.

## Limitations
- Configuring source names does not connect external services automatically. External sources require a legitimate integration/API and appropriate access.
- Reasoning text is stored for teacher review; this version does not claim fully reliable AI grading of mathematical proof quality.
- Trial accounts are excluded from admin reports but are not automatically purged; a future maintenance policy should delete stale trial data.
