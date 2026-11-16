MATH_WEB V72 - FIX GITHUB ACTIONS

Source: V71 full ZIP provided earlier. This is NOT a copy of the current GitHub HEAD.

1) scripts/v54_preflight.py on the user's GitHub runner fails with:
   AttributeError: 'IncludeRouter' object has no attribute 'path'

   Change:
       routes={route.path for route in app.routes}
   to:
       routes={p for route in app.routes if isinstance((p := getattr(route, 'path', None)), str)}

   This skips non-route entries but keeps the required API path checks.
   On an existing checkout you can run:
       python scripts/ci_route_guard_hotfix.py
   BEFORE the preflight command. This patches v54 in place without discarding
   any additional v54-specific checks.

2) backend/tests/test_api_integration.py was updated for the SELECTING state:
   no questions before both players submit topic selections; one shared deck
   after both ready. Old tests incorrectly expected 10 questions immediately.

3) backend/app/main.py now registers the Question Factory API and initializes
   its separate storage lazily on first use.

Local verification: 47/47 focused CI tests passed, v34 preflight 0 failures,
GET /api/factory/progress returned 200. Full suite: 430 passed, 32 failed.
Some failures are old tests or missing Git LFS data; DO NOT claim all CI jobs
are fixed or disable the remaining checks. Preserve database and user data.
