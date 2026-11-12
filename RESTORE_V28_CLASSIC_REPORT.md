# V28 Classic Restoration (12/11/2026)

- Base: V28 restored account fix ZIP supplied by user.
- Original theme: Math_WebV2-main(6).zip.
- Reinstated original home HTML and original core styles (style, home, battle, account, login).
- Removed conflicting NEON CSS on other root pages; account retains V5-V8 CSS for dashboard components and placement fix.
- Removed visual NEON runtime scripts from root pages; existing application JS and backend remain.
- Corrected auth navigation guard to wait for DOM and hide trial banner when authenticated.
- No passwords are stored by this patch; existing session token persistence is retained.
- NOT a full browser/E2E validation; battle/chat/login need live server verification.
