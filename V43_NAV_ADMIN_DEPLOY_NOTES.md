# MATH_WEB V43: Navbar reference and safe admin deployment

- Based on uploaded working ZIP dated 2026-11-13, not a replacement of existing app functionality.
- Added `css/mw-v43-reference-nav.css` after V42 navbar rules on 19 frontend pages. Colors, hover, glow, card elevation and reduced-motion behavior are adapted from supplied SortLab HTML. No presentation-only JavaScript, canvas, or fullscreen takeover was copied.
- Navbar layout stays driven by existing V42 shared navigation and V5 component; the image is the visual reference.
- Admin account `admin19022011` is already supported by the backend; `js/auth.js` redirects authenticated admins to `admin.html`. Admin authorization is server-side.
- **Do not commit an administrator password to GitHub.** To initialize a fresh backend, set `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` in the backend hosting provider's secret environment configuration before first startup. The setting does NOT reset existing admin passwords. If the admin already exists, sign in with its current password and use the Admin password-change feature; otherwise use a secure, authenticated server-side recovery process.
- GitHub Pages hosts static frontend only. Configure the frontend API to point to the separately hosted backend. GitHub Pages cannot execute FastAPI or store authenticated sessions itself.
- Deployment: push project contents to the repository root on `main`; workflow `.github/workflows/pages.yml` runs CI and publishes safe frontend assets. Do not upload `.env`, database files, or backend secrets.
- QA status: structural source inspection and changed-file checks only. Full end-to-end login, live Battle, production deployment and browser regression tests are NOT certified.
