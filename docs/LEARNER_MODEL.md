# Learner-model contract

The canonical contract is owned by the portable `learner-model` package in
[clew-skills](https://github.com/francesco-kruk/clew-skills), not maintained as a
second specification here.

Read the installed [profile entrypoint and specification](../.agents/skills/learner-model/references/learner-model-spec.md)
and [operational skill](../.agents/skills/learner-model/SKILL.md). Restore their
matching immutable pin with **APM 0.28.0** and `apm install --frozen`, retaining
both manifest targets (`copilot` and `agent-skills`).

The v2 package is pinned to `clew-skills` revision
`16f727da7bbffbb9f905eb9a9ac40fa6d12ca27f`. The stable specification path above is
the profile entrypoint. Restore the matching pin rather than treating an older
installed specification as the redesigned default. Student CLI availability
follows the [PR #9 setup guidance](../README.md#student-setup).

The default **`evidence-first-v1`** profile (`schema_version: 1`) uses `model/profile.md`,
`model/index.md`, and readable evidence for goals, supplied work, observed
errors, and confirmed preferences. It does not assign numerical scores or
schedules. Existing unmarked models require clarification, not automatic
migration. Configure/status never read or create the marker. A path-only
exchange asks the learner's goal; the skill initializes at first genuine intake
once ownership and intent are clear, not merely when a vault is configured.

The complete former specification remains separately available as **`advanced-v1`**:

- [Advanced specification](../.agents/skills/learner-model/references/advanced-model-spec.md)
- [Advanced operations](../.agents/skills/learner-model/references/advanced-operations.md)
- [Advanced clarification gates](../.agents/skills/learner-model/references/advanced-clarification-gates.md)

These are the v2 deployment paths for the matching pin. Advanced domain indexing, confidence/efficacy,
scheduling, provenance, stable-ID and append-only/tombstone safeguards and
undefined-rule gates remain profile-specific, not mandatory default machinery.
Neither profile constitutes an enforced storage backend.

Both profiles preserve learner ownership, attributable evidence, no trait
labels, and bounded retrieval. Reserved `model`/`artifacts` names may belong
to copied notes; ask before writing if ownership is unclear.
See [student setup](../README.md#student-setup) and the
[hosted-processing disclosure](../README.md#local-files-hosted-copilot).
Ordinary task-scoped reads can enter hosted context without a new opt-in gate;
that does not authorize bulk uploads, telemetry, or teacher access. Local
corrections/tombstones cannot erase already-sent hosted context, and this
project makes no provider retention, training, deletion, or encryption promises.

Rationale: [hosted processing](adr/adr-0003-local-learner-storage-and-hosted-copilot-processing.md)
and [evidence-first learner continuity](adr/adr-0005-evidence-first-learner-continuity.md)
are Proposed ADRs, not lifecycle approvals.
