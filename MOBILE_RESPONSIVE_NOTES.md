# MATH_WEB Mobile Responsive Update

Added additive mobile stylesheet to 532 HTML pages. Desktop styles and application JavaScript are unchanged.

Testing: static HTML/CSS integration and archive integrity only. Physical device/browser layout, Battle, admin, and backend connectivity have not been end-to-end verified.

To use a phone on the same Wi-Fi network: start frontend with `python -m http.server 5500 --bind 0.0.0.0` and backend bound to `0.0.0.0`; open `http://<PC_LAN_IP>:5500` on the phone. Configure frontend API host to the PC LAN IP instead of `127.0.0.1`, and allow firewall access only on trusted networks.

`UPDATE_GITHUB.bat` runs `CHECK_PROJECT.ps1`, then `git add -A`, `git commit`, `git push origin main`. It publishes committed source to GitHub, not the running server. Review changes and secrets before use.
