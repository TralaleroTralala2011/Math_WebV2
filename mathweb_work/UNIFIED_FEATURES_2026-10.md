# MATH_WEB Unified Build

## Gameplay updates
- Removed in-game Easy/Medium/Hard selection buttons. Difficulty varies internally across generated batches.
- Progress starts at 0/100: correct answer +5, wrong answer -1, floor is 0. Game completes at 100.
- Every answer pauses for review and shows a manual next-question button. Wrong answers do not auto-advance.
- Detailed feedback shows the selected answer, correct answer, and solution steps returned by the backend.
- Mixed question batches include multiple choice, short answer, and true/false where the API supports each type.
- Geometry questions display a structured SVG illustration when the AI response includes diagram data; geometry problem mode supplies diagrams bound to generated data.
- Per-game progress, best progress, play count, and answer totals are saved in browser localStorage and remain after leaving the game on that browser/device.
- Completing 100/100 displays an animated celebration screen with confetti.

## Quick launch on Windows
- Double-click `START_BACKEND.bat` to install backend dependencies and start the API.
- Double-click `START_FRONTEND.bat` to start the static frontend server.

## Run in VS Code (Windows PowerShell)
Open two terminals at the project root.

Backend terminal:
```powershell
cd backend
python -m pip install -r ..\requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend terminal at project root:
```powershell
python -m http.server 5500
```

Open `http://127.0.0.1:5500/`.

The API URL can be set in `js/api-config.js`. If the browser says `ERR_CONNECTION_REFUSED`, the backend process is not listening at the configured address/port.

## Notes
- All 92 × 3 individual knowledge-game HTML pages are preserved and updated in place. The 45 legacy standalone game pages and the universal game reference were updated to follow the same gameplay rules too.
- Existing authentication, account, battle, chat, notifications, and navigation files are retained.
- Browser localStorage records are per browser profile and device; they do not synchronize between devices unless a server-side save endpoint is configured.
