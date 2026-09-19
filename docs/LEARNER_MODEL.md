# Learner-model contract

The authoritative learner-model 3.0.0 contract lives in the installed
[specification](../.agents/skills/learner-model/references/learner-model-spec.md),
[clarification gates](../.agents/skills/learner-model/references/clarification-gates.md),
and [operational skill](../.agents/skills/learner-model/SKILL.md).
Sources belong in [clew-skills](https://github.com/francesco-kruk/clew-skills),
not in a second specification here.

Both runtime skills are pinned to `clew-skills` revision
`79c3aefa1817b2e3215df8f070815ef470b1ebdb`. Restore this matching release with **APM 0.28.0** and
`apm install --frozen`, retaining both `copilot` and `agent-skills` targets.

Memory is one compact `model/learner.md` summary with exactly one
`<!-- clew-learning-memory: v1 -->` marker, dates, and ordinary source/evidence
links. Goals, Confirmed preferences, and Learning notes are recommended optional
headings, not mandatory schema sections. Meaningful sessions
use `model/sessions/YYYY-MM-DD-topic.md` with collision suffixes `-2`, and so on.
Store original attempts once and link them; artifacts are optional when useful.

Bare continue or inspection is read-only. Only meaningful learning input,
decisions, or results justify updates. Configure/status neither read nor create
memory; a path-only exchange asks the learner's goal. Corrections are direct,
with a concise note if useful. Clarify ambiguous forget, stop-use, and explicitly
scoped local deletion requests.

No profile/index files, typed-record graph, evidence-ID machinery, overlays,
tombstone engine, numerical scores, automatic schedules, or domain taxonomy are
required or supported by this contract. Unknown existing models—including
earlier evidence-first and advanced formats—require an explicit migration
decision. The former advanced documentation is historical material archived
outside the installed package in the
[historical source archive](https://github.com/francesco-kruk/clew-skills/tree/9c8fb3b3754716c4cbf7c961c4a5f269cd003c15/docs/archive/learner-model),
not a supported runtime alternative.

Preserve learner ownership, attributable evidence, no trait labels, and bounded
retrieval. Ask before writing where reserved `model`/`artifacts` ownership is
uncertain. Skills are instructions, not an enforced backend.
See [student setup](../README.md#student-setup) and the
[hosted-processing disclosure](../README.md#local-files-hosted-copilot).
Local correction/deletion cannot erase hosted context already sent; do not
promise provider retention, training, deletion, or encryption behavior.

Rationale: [hosted processing](adr/adr-0003-local-learner-storage-and-hosted-copilot-processing.md)
and [evidence-first learner continuity](adr/adr-0005-evidence-first-learner-continuity.md)
remain Proposed ADRs.
