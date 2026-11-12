# MATH_WEB V28 restored with targeted fixes

- Base is V28 Natural UI, not V29.
- Original V28 home HTML is no longer hidden by the injected dashboard.
- Existing V28 V6 dashboard moved to account page before original account content.
- Battle, desktop navigation, and all other V28 page styles/scripts remain unchanged.
- Trial banner only displays when no login token exists; trial no longer removes real login credentials.
- Explicit logout clears old trial snapshots. Passwords are not stored for persistence.
- Account-only scoped responsive CSS prevents column-like wrapping.

This is a focused code fix, not a claim of complete end-to-end validation.
