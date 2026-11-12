# Question mix sync status

Policy: 7 multiple-choice, 2 written/fill-in, 1 true/false per ten **when sufficient verified questions of each kind exist**. No fake conversions.

Frontend learn and learning-path banks now use the same mix helper. Existing UI renderers still only support `choices`/`correct`, so written and true/false records without that schema require additional renderer and grading work before end-to-end support. Backend AI and Battle mix from previous ZIP retained.

**Not 100% complete.** Existing lesson banks contain mostly multiple-choice records. The mix cannot be guaranteed until verified question types and full UI handling exist.
