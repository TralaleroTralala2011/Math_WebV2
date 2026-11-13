# MATH_WEB V43: Logout confirmation and secure Admin configuration

- Account and Admin logout actions now require a centered modal confirmation. Cancel, Escape and backdrop click preserve login and storage.
- Do not commit Admin passwords to a public GitHub repository or bundle them in JavaScript, HTML, render.yaml or ZIP.
- Admin username is `admin19022011`. For first-time setup, open Render Dashboard > math-webv2 > Environment and set `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` to the desired secret. Redeploy backend. This environment variable is used only when admin account is first created.
- For an EXISTING admin account, setting the environment variable does NOT change its password. Log in with existing credentials and use the Admin 'Đổi mật khẩu' feature. If credentials are lost, use a secure server-side recovery process; do not wipe user data.
- Since the password was typed in chat, it is recommended to choose a different strong unique password before a real pilot. Do not share it in GitHub issues, logs, screenshots or code.
- Logout clears the browser's auth session and requests token revocation. Cancel never clears localStorage.
- Manual acceptance checks: cancel, Escape, backdrop, confirm, refresh, logout after re-login, mobile modal, Admin logout.
