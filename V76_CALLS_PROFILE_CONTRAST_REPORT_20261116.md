# MATH_WEB V76 · Voice/Video Calls, Public Profile, Practice Quiz Contrast

## Baseline and scope
- Based on V74 + V75 practice-popup contrast repair.
- **No account database, signing secret, media recording, chat history, or question-bank contents** are replaced by this patch.
- The existing `/api/users/profile/{player_id}` authenticated public-profile API is reused. Other users' emails, messages, passwords and private study logs are **not** displayed.

## New features
- `Chat`: buttons for **voice call**, **video call**, **view friend's profile**.
- WebRTC peer-to-peer media signalling over `/api/live/calls`, with bearer-token authentication at WebSocket handshake and accepted-friendship validation before initiating a call.
- Incoming call requires explicit acceptance. Browser microphone/camera permission is requested **only after acceptance** for receiver and after acceptance for caller; no media recording/storing by this feature.
- Reject/end/busy/disconnect, mic/camera toggles, ring timeout. Only one active call per account process.
- Public profile page at `user-profile.html?player_id=MW-...` linked from Chat; the existing Account user-search profile popup continues to work.
- Question practice modal from V75 fixes white-on-white answer text for multiple choice/true-false/short answer with locally scoped CSS.

## Verified
- 2/2 backend WebSocket signalling tests passed (authenticated accepted friends and stranger rejection; offer/answer/ICE exchange; termination).
- Frontend Chromium **mocked** WebSocket UI tests at 1280px and 393px: outgoing voice call, simulated inbound video call, decline, end; 0 JavaScript exceptions during those tested actions.
- `node --check` passed on changed JS. Python compilation passed on changed backend.
- V75 practice modal contrast checks were performed prior to this extension (V75).

## Limitations (important)
- **WebRTC peer-to-peer media is not yet verified on two real browsers/accounts on live Render/GitHub Pages.** Browser access to local application URLs is restricted in the current environment.
- STUN-only connectivity can fail on strict/mobile NATs. Reliable production calls require a **TURN relay with short-lived credentials**, monitoring and rate controls.
- The signal hub is intentionally process-local; more than one Uvicorn worker/Render replica requires Redis or equivalent shared signalling and distributed call-state management.
- Calls are received **only while Chat is open**. This release does not claim background call notifications, group calling, or million-user capacity.
- Roll out frontend and backend from the same release; restart Render after installing WebSocket dependencies.
- The original MATH_WEB account datastore must remain on persistent storage and be backed up separately. This ZIP cannot recover previously lost accounts.

## Deployment (without losing user data)
1. Back up existing account/progress databases and preserve existing signing secret in Render environment.
2. Never overwrite persistent production SQLite with a ZIP copy. V76 ZIP deliberately excludes generated account DB and secret.
3. Deploy backend with requirements (includes `websockets`) and launch one worker for this prototype's signalling hub.
4. Deploy GitHub frontend from same version. Log in with two accepted friends, open `chat.html` in two different browser sessions, test call accept and permissions.
5. Before high-availability or widespread production use, configure TURN and distributed signalling.
