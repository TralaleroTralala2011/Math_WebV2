# MATH_WEB: Friend requests, chat and Battle upgrade

## Friend request flow
- Friend requests are persisted in the shared backend database, so separate registered accounts can discover one another using their player ID.
- Incoming `friend_request` notifications now provide **Chấp nhận** and **Từ chối** actions directly in the notification item.
- Actions use the authenticated `/api/friends/accept/{request_id}` and `/api/friends/reject/{request_id}` endpoints and disable both buttons while a request is in flight.
- Failures are shown in the notification item and actions become available again.
- Once accepted, the existing `/api/chat/{friend_id}/messages` routes authorize messaging through the accepted-friend relationship, and Battle can load the accepted friends list.

## Run and verify
1. Start one shared backend process (`cd backend`, install `requirements.txt`, run `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`).
2. Serve the project root on port 5500 and open `index.html`.
3. Register two separate accounts. Use account A's player ID to send a request from account B.
4. Sign into account A in a separate browser profile (or separate browser) and open notifications. Accept the request.
5. Confirm both accounts list each other as friends, open Chat, exchange messages, then invite the other account to Battle.

## Important deployment note
All accounts must connect to the same reachable backend and same persistent database. If the site is opened on two devices but each device points at `127.0.0.1:8000`, they are talking to two different local servers. For LAN testing, configure `window.MATHWEB_API_BASE`/`window.MATHWEB_API_URL` to the host machine's LAN IP and allow that port through the firewall. For public use, deploy FastAPI plus a persistent shared database; a local SQLite database on separate machines is not a shared account service.

## Verification scope
The current Python suite and JavaScript syntax checks are run during packaging. These do not replace a two-browser end-to-end test against a live backend. Large concurrent deployments should use a production database and load testing rather than assuming SQLite supports unlimited simultaneous matches.
