# MATH WEB social and trial upgrade (2026-10-29)

## Fixed

- `battle.html` now loads `js/presence.js` after API configuration and before `js/battle.js`. Without this heartbeat, a player who stayed on the Battle page could have a stale `last_seen`; the Player ID search then marked them offline and disabled the invite button.
- The trial CTA now opens `trial-practise.html?trial=1`, a dedicated practice-page copy for the trial experience, rather than the regular learner practice URL. The page uses the shared practice engine so fixes and question content remain aligned.
- `js/practise-auth.js` recognizes the dedicated trial practice page. Trial-only navigation links on that page keep the user in the trial practice route.
- The trial page checks both the trial-mode flag and `?trial=1` before running the practice experience.

## Social API checks

- Automated integration checks cover registration, friend request, acceptance, accepted-friend list, message send/history, and battle invite/start/answer flows.
- Chat remains restricted to accepted friends. Battle invitations continue to use server-side matchmaking endpoints and server-owned match state.

## Run / verify

1. Start the backend and frontend as described in `LOCAL_RUN.md`.
2. Sign in as two separate learner accounts in separate browser profiles or browsers.
3. Open the Battle page in both profiles and search by Player ID. Presence heartbeats should keep active players online.
4. Send and accept a friend request in Account, then verify both accounts see each other in Chat and can exchange messages.
5. Invite the other player to Battle, accept the invite in the other profile, and verify the same match ID reaches both clients.
6. Use the trial button from login. It should open the dedicated trial practice route and show the trial banner. Exit should restore the previous login context.

## Notes

The trial account is a disposable learner identity in the same backend database, excluded from ordinary learner reports by the existing `trial_` username rule. The separate page provides a dedicated trial experience; it is not a separate database or deployment.
