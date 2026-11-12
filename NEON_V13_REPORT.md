# MATH_WEB NEON V13: Question Factory exam safety

Source: NEON V12 uploaded/generated in this conversation.

## Actual change
- The roadmap question pool now independently revalidates approved Question Factory 2.0 rows before using them in placement and topic exams.
- Rejects multiple-choice questions with mathematically equivalent options (such as 1/2 and 0.5), missing explanations, malformed answers, or unrecognized difficulty tiers.
- Three new regression tests added for ambiguous options, valid options, and missing tier labels.
- All 179 backend tests passed.

## Not yet completed
- No full certification of all 150 topics and three tiers; many lack verified items.
- UI has not been compared pixel-by-pixel to the five supplied reference screenshots.
- Battle and Chat not verified on two physical devices.
- Tutor does not retrain a foundation model.
- Existing NEON design, learning navigation, Admin and Battle/Chat code preserved.

## Upgrade
Backup user data before replacing a running installation. The release ZIP excludes runtime database and login secrets.
