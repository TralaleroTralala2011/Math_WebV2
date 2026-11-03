# MATH_WEB Battle & Account Upgrade Report

Date: 2026-11-01
Base: `MATH_WEB_TWO_MODES_ASSIGNMENTS_UPGRADED(1).zip`

## Battle challenge flow

- Direct invitations enter a pending state and expire after 18 seconds if not accepted.
- The challenged player receives a top-right game-style toast with Accept and Reject actions. The toast X action rejects the invitation and marks its notification read.
- Accepting marks the invite notification read and moves both players into the waiting room.
- The waiting room gives both players a separate 18-second ready-confirmation window. Each player must confirm independently. The backend refuses to start a direct challenge until both readiness flags are set.
- Rejection records `cancel_reason=REJECTED`, marks the receiver's invite notification read, and sends the challenger a `pvp_rejected` notification. The challenger returns to Player ID opponent search.
- Expiry and leaving a waiting room cancel the match and notify the other participant.
- Random matchmaking retains its existing automatic-start behavior and is not subject to the direct-challenge ready gate.

## Account, Player ID and notifications

- Account loading/error elements now target the actual `accountLoadingState` and `accountErrorState` elements. Missing profile payloads are surfaced as an error rather than leaving an empty account page.
- Player ID lookup is case-insensitive, strips an optional `ID:` prefix, and accepts numeric internal account IDs as a fallback.
- Chat notifications now store the sender user ID and open the matching conversation from a notification deep link.
- Live notification polling shows new unread game-style toast cards.

## Backend changes

- `matches`: readiness flags, cancellation reason and direct-challenge readiness requirement.
- New endpoint: `POST /api/matchmaking/match/{match_id}/ready`.
- New endpoint: `POST /api/matchmaking/match/{match_id}/cancel`.
- Existing accept/reject/start endpoints enforce the new lifecycle.

## Validation

- `python -m pytest -q`: **92 passed**, 4 existing FastAPI lifecycle deprecation warnings.
- `node --check` for updated JavaScript files.
- `python -m py_compile` for updated matchmaking, friends and chat backend modules.

## Manual verification still recommended

A two-browser test with two real accounts is recommended to verify the visual notification timing, both ready indicators, 18-second countdowns, and navigation on the target deployment/browser. Automated tests cover backend state transitions and notification persistence; they do not replace that live visual test.
