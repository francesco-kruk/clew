# Learner-model contract

The authoritative specification belongs to the portable `learner-model` package
in [clew-skills](https://github.com/francesco-kruk/clew-skills), not to an
independently maintained copy in this student repository.

After restoring the pinned package with **APM 0.28.0** (`apm install --frozen`
from the clone root), read:

- [Complete learner-model specification](../.agents/skills/learner-model/references/learner-model-spec.md)
- [Operational skill](../.agents/skills/learner-model/SKILL.md)
- [Clarification gates](../.agents/skills/learner-model/references/clarification-gates.md)

The deployed package is restored from immutable `clew-skills` revision
`5ed0f288a6c5c0c0f891939385ddf38fa5b32504`. The links above identify its canonical
specification and operating guidance. If these files are missing or stale,
restore the pinned package before learner-model operations. Do not hand-edit
generated files or improvise missing schema/update rules.

For student setup and the local-storage/hosted-processing disclosure, see the
[README](../README.md#local-files-hosted-copilot). Relevant records can enter
hosted Copilot context during ordinary bounded task use without a new opt-in
gate. That does not authorize bulk uploads, unrelated vault access, publication,
passive telemetry, or teacher/institutional access.

The package retains domain indexing, no trait labels, provenance, independent
confidence and efficacy, scheduling, learner ownership, stable IDs, and
append-only/tombstone safeguards. Undefined statistical, tombstone, storage, and
transaction semantics remain clarification gates; an instructional skill is not
an enforced storage engine. Local tombstoning does not remove already-sent
hosted context, and this project makes no hosted retention or deletion promises.

Architecture rationale:

- [ADR-0001: Shared Obsidian course content contract (Accepted)](adr/adr-0001-shared-obsidian-course-content-contract.md)
- [ADR-0002: Repository and package ownership (Proposed)](adr/adr-0002-repository-and-package-ownership.md)
- [ADR-0003: Local learner storage and hosted Copilot processing (Proposed)](adr/adr-0003-local-learner-storage-and-hosted-copilot-processing.md)

The [pre-migration specification at the original source revision](https://github.com/francesco-kruk/clew/blob/6b03b5e8fdaefc16478de179bac00e9baa188c20/docs/LEARNER_MODEL.md)
is retained for historical reference only. Its machine-boundary claims are not
the hosted student workflow contract.
