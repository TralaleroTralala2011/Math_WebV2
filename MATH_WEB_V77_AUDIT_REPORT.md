# MATH_WEB V77 | V74 base + calling/profiles/contrast and stability audit

## What changed
- Preserved the V74-integrated site, existing question bank, existing login/Battle/admin/learning modules.
- Kept voice/video calls for accepted friends, public user profile, and contrast fixes from the V76 patch.
- Corrected an asynchronous WebRTC permission race: if a call is cancelled while camera/microphone permission is pending, any tracks granted afterward are immediately stopped rather than left active.
- Guarded offer creation against changes in active call, and capped the queued ICE candidates to prevent unbounded browser memory growth.

## Checked this session
- New Battle topic-selection workflow: 12/12 tests passed (`test_v53_b56_topic_selection.py` and `test_api_integration.py`).
- 2/2 call signalling tests passed.
- JS call script syntax check (`node --check`) passed.
- ZIP integrity verified.

## Known limits / important deployment conditions
- Do NOT claim 100% of all website functionality works: exhaustive end-to-end tests on Render/two real accounts and devices are still pending.
- The legacy Battle tests that call `/start` immediately after `/accept` fail because the current flow requires two topic submissions. Do not remove this user-driven topic-selection guard to satisfy legacy assertions.
- WebRTC without TURN may fail on strict networks. Calls require HTTPS, browser permissions, a single signalling process, and an open Chat page.
- No live customer database, admin secret, media recording or account data should be bundled in this distribution. Back up deployment data separately and keep existing Render secret keys.
- The V74 restoration was constructed by layering V70 full ZIP + V70/V72/V73/V74 patches followed by V76 calls/profiles/quiz-contrast patch. Full deployment regression testing remains necessary.
