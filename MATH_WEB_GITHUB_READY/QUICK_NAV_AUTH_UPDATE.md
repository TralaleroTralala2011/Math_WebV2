# Quick navigation authentication visibility

- Logged-out users and users in trial mode do not see the three floating shortcuts: Lộ trình học, Vẽ hình, Học bài.
- The shortcuts appear when `mathweb_token` exists and trial mode is not active.
- On page restoration, cross-tab storage changes, or `mathweb:auth-changed` events, the shortcuts are re-evaluated.
- This is UI visibility only, not server-side authorization. Backend routes and protected pages must independently validate the session token.
