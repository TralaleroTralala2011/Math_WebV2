# MATH WEB AI Super Bank Upgrade

## Preservation rule
This upgrade is additive. Existing UI, game pages, game bank, legacy AI generator, composer, template bank, validator, authentication, battle and database files were not intentionally removed or redesigned.

## What was added
- `backend/app/ai/engine/super_bank.py`: structure-first question generation layer.
- `backend/app/ai/knowledge/super_bank_catalog.json`: inspectable map of topic groups and archetypes.
- `/api/ai/bank/stats`: reports the additive Super Bank coverage.
- AI generation now tries the Super Bank before the existing additive/legacy fallback when no specific game is selected.
- Set-level diversity now tracks named mathematical archetypes in addition to exact and structural fingerprints.

## Coverage
The Super Bank maps the curriculum to families such as:
- algebra, systems, inequalities, sets
- counting, probability and experiments
- statistics and data analysis
- functions, sequences and coordinate geometry
- trigonometry, limits, derivatives and integrals
- complex numbers
- plane and spatial geometry
- Oxyz
- exponentials and logarithms
- Newton binomial, induction and transformations
- real-life modelling

The bank contains dozens of structural archetypes and a large parameter/context space. It is generated at runtime instead of storing millions of hard-coded near-duplicate questions.

## Anti-repeat layers
1. exact question fingerprint
2. numeric-normalized structure fingerprint
3. template family / generation style / context variation key
4. named mathematical archetype tracking within a practice set

When a topic has fewer available archetypes than the requested number of questions, the service falls back rather than failing the whole request.

## Verification performed
- Python compilation of the full backend
- FastAPI application import
- One-question generation for all 84 curriculum topics
- Multiple-question generation for representative probability, geometry, derivative and complex-number topics
- Existing frontend UI files remain unchanged by this upgrade
