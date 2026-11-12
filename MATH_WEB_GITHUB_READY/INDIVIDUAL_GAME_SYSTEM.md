# MATH WEB • Individual HTML Game System

Every one of the 92 current knowledge topics has 3 separate HTML game pages (276 pages total). The existing page layout, CSS, navigation, score feedback, and completion panel are preserved.

## Distinct play patterns
- **Game 1: Quick discovery** — easy-to-enter multiple-choice interaction, with visual context when available.
- **Game 2: Solve the mission** — medium-level typed answers, so the player must produce a result rather than only recognize it.
- **Game 3: Boss challenge** — hard multi-part problems with linked context, mixed response types, and step-by-step explanations.

The stage is determined from the existing numbered game path (`1-`, `2-`, or `3-`), so each knowledge topic uses the same three interaction categories without routing all buttons to one universal game. The Universal Game remains as a reference and is not used by the knowledge game buttons.

The game pages continue to request questions from the backend and retain a local fallback if the server is unavailable. AI-generated questions are checked server-side when question IDs are available.
