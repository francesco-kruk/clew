---
title: "ADR-0005: Evidence-first learner continuity"
status: "Proposed"
date: "2026-09-19"
authors: "Francesco Kruk (requesting maintainer)"
tags: ["architecture", "decision", "learner-model", "profiles"]
supersedes: ""
superseded_by: ""
---

# ADR-0005: Evidence-first learner continuity

## Status

**Proposed** | Accepted | Rejected | Superseded | Deprecated

Proposed on 2026-09-19 at requesting maintainer Francesco Kruk's direction.
The user authorized the redesign's implementation, not ADR acceptance.
No approval is attributed to another contributor and no accepted record's
lifecycle is changed by this proposal.

## Context

Useful continuity can start with what the learner actually supplies or confirms:
goals, work, observed errors, and preferences. The former complete learner model
includes numerical confidence/efficacy, scheduling, and unresolved statistical
and transaction rules. Requiring all of that machinery for ordinary tutoring
would either block basic continuity or encourage the agent to invent semantics.

A copied bundle can already contain folders called `model` or `artifacts`.
Neither a path setting nor a directory name identifies a Clew profile or
authorizes overwriting existing records. A simpler default needs an explicit
identity and must coexist with advanced records without automatic migration.

## Decision

Use learner-model v2 with **`evidence-first-v1`** (schema version 1) as the default profile.
`model/profile.md` identifies the selected profile; `model/index.md` supports
bounded lookup of readable records for goals, supplied work, observed errors,
and confirmed preferences. Exact fields and operations belong to the installed
canonical contract, not this ADR.

Do not assign numerical confidence/mastery scores or schedules in the default
profile. Record genuine evidence from tutoring, with attributable sources and
learner correction; do not manufacture facts from a configured vault, copied
notes, or agent-generated practice. Preserve learner ownership and no-trait-label
rules, and distinguish observations from unsupported generalizations.

Keep the complete former specification as a separate **`advanced-v1`** profile.
Its domain indexing, confidence/efficacy distinction, scheduling, stable IDs,
provenance, and append-only/tombstone safeguards remain intact alongside its
undefined-rule gates. Do not silently mix advanced fields into default records
or treat the profile split as a new statistical or storage implementation.

An existing unmarked model requires clarification, not automatic initialization,
replacement, or migration. Ask before writes if reserved paths or ownership
are uncertain. Configuring the vault creates neither profile files nor learner
records, and configure/status do not read the profile marker. A path-only
exchange asks the learner's goal. The skill initializes at first genuine intake
only once intent and destinations are clear; tutoring then creates artifacts
and retains genuine evidence.

Both profiles use bounded task-relevant retrieval under the hosted-processing
disclosure in ADR-0003. A profile is an instructional contract, not an enforced
backend, permission bypass, or sandbox.

## Consequences

### Positive

- **POS-001**: Learners can inspect understandable evidence without unsupported
  precision or numerical claims of mastery.
- **POS-002**: Explicit profile identity reduces accidental mixing of record
  semantics and protects existing unmarked data from automatic migration.
- **POS-003**: The advanced specification remains available rather than being
  silently deleted or weakened to make ordinary tutoring possible.

### Negative

- **NEG-001**: The default does not offer numerical adaptive scheduling or
  efficacy estimation; those capabilities cannot be implied in the interface.
- **NEG-002**: Ambiguous ownership or profile selection requires clarification
  before writes and can interrupt continuity.
- **NEG-003**: Skill instructions do not enforce storage transactions or
  guarantee correctness; unsupported operations must remain blocked.

## Alternatives Considered

### Require the complete advanced model for every learner

- **ALT-001**: **Description**: Make numerical scores, scheduling, and advanced
  lifecycle objects prerequisites for all continuity.
- **ALT-002**: **Rejection Reason**: Adds unsupported complexity to basic tutoring
  and risks inventing rules where the specification remains undefined.

### Remove the advanced model entirely

- **ALT-003**: **Description**: Replace the former complete specification and
  records with only the simple default.
- **ALT-004**: **Rejection Reason**: Loses the preserved advanced contract and
  encourages destructive migration of existing learner history.

### Infer the profile from whatever files are present

- **ALT-005**: **Description**: Treat any `model` folder as Clew-owned and
  normalize its records into the default automatically.
- **ALT-006**: **Rejection Reason**: Directory presence proves neither ownership
  nor profile; existing unmarked data requires the learner's clarification.

## Implementation Notes

- **IMP-001**: The installed `references/learner-model-spec.md` becomes the
  canonical profile entrypoint and links the separately retained advanced
  references `advanced-model-spec.md`, `advanced-operations.md`, and
  `advanced-clarification-gates.md` in that same directory. Keep
  `docs/LEARNER_MODEL.md` as a concise pointer. Restore the matching package
  pinned to `16f727da7bbffbb9f905eb9a9ac40fa6d12ca27f` before profile operations.
- **IMP-002**: Publish and restore the matching immutable v2 package before
  profile operations. Update skill guidance and evaluations together; never
  hand-edit generated deployments to bridge a contract mismatch.
- **IMP-003**: Use synthetic scenarios for source-grounded tutoring, genuine
  evidence, bounded continuity, unmarked models, and reserved-name collisions.
  Do not test against real learner records or report manual scenarios as an
  implemented enforcement engine.
- **IMP-004**: Local correction/deletion/tombstoning cannot erase hosted context
  already sent. Retain no-bulk-upload, no-passive-telemetry, and no-teacher-access
  restrictions and do not promise provider behavior.

## References

- **REF-001**: [Learner-model contract pointer](../LEARNER_MODEL.md).
- **REF-002**: [Installed profile entrypoint](../../.agents/skills/learner-model/references/learner-model-spec.md).
- **REF-003**: [ADR-0003: Local learner storage and hosted Copilot processing](adr-0003-local-learner-storage-and-hosted-copilot-processing.md).
- **REF-004**: [ADR-0004: Portable bounded course reading](adr-0004-portable-bounded-course-reading.md).
- **REF-005**: [Student workspace session](ghapp://sessions/357f9483-e268-444b-92aa-a417df6fec4b),
  2026-09-19 redesign direction from the requesting maintainer, not acceptance.
