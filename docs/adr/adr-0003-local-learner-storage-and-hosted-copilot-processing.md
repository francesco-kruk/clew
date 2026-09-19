---
title: "ADR-0003: Local learner storage and hosted Copilot processing"
status: "Proposed"
date: "2026-09-18"
authors: "Francesco Kruk (requesting maintainer)"
tags: ["architecture", "decision", "learner-model", "copilot"]
supersedes: ""
superseded_by: ""
---

# ADR-0003: Local learner storage and hosted Copilot processing

## Status

**Proposed** | Accepted | Rejected | Superseded | Deprecated

Proposed on 2026-09-18 at requesting maintainer Francesco Kruk's direction.
Implementation was requested through the reorganization plan; this is not
lifecycle acceptance, and no other contributor's approval is inferred.

Revised on 2026-09-19 at Francesco Kruk's request for manual notes handoff and
evidence-first continuity, subsequently simplified that day to compact learning
memory rather than typed records or an operational advanced profile.
The original proposal date and Proposed
status are retained; this revision records no lifecycle approval.

## Context

The historical learner-model specification says that only serialized adaptation
decisions and grounded course excerpts cross the machine boundary. The student
workflow uses hosted GitHub Copilot inference, where relevant local tool results
can enter hosted context. Local file storage alone cannot enforce the historical
network boundary or demonstrate every transmitted payload.

The maintainer requested ordinary hosted student use without a new
per-workspace opt-in gate, while retaining bounded access, learner ownership,
and evidence-based model safeguards. The skills guide operations; they do not
implement a model storage engine, transport audit, or local inference backend.
Compact learning memory needs an honest hosted-processing disclosure without
imposing numerical or record-graph machinery on ordinary tutoring.
ADR-0004 separately proposes a portable-reading default; ADR-0001 is unchanged.

## Decision

Persist learner records in the selected external local vault and disclose that
bounded, task-relevant contents are transmitted to hosted GitHub Copilot/model
processing when used. Ordinary student task use permits these reads without a
separate new opt-in ritual. This is not permission to bulk-upload the model,
access unrelated learners' vaults, introduce passive telemetry, publish records,
or provide teacher/institutional access.

Resolve the selected vault from explicit task/CLI configuration, not a home
directory guess or the clone. Follow the learner-model contract's cheapest-first
retrieval and stop when the request has enough context. Course-only lookup
remains independent of learner records. Vault configure/status commands never
read course or learner-file contents. Copying a bundle or setting a path creates
no learner records and is not evidence of learning.

Local memory is not a network audit and does not enumerate all context
transmitted to hosted processing. Local correction/deletion cannot erase context already transmitted to a
host. Make no promises about hosted retention, training, deletion, or encryption.

Use one compact summary and meaningful dated session notes under learner-model
3.0.0. Preserve ordinary evidence links, dates, no trait labels, and learner
ownership. Bare continue/inspection is read-only; updates require meaningful
learning input, decisions, or results. No numeric scores, schedules, typed graph,
or domain taxonomy is required.

Unknown existing models, including earlier evidence-first and advanced formats,
require an explicit migration decision. Advanced documentation is archived
outside the runtime, not an alternate operational contract. Correct memory
directly, noting changes concisely when useful; clarify ambiguous forget,
stop-use, or explicitly scoped local deletion. Do not invent an enforcement
engine or promise hosted erasure.

## Consequences

### Positive

- **POS-001**: The disclosure matches the requested hosted Copilot workflow
  rather than presenting local storage as local-only inference.
- **POS-002**: Task-scoped retrieval enables learner-driven adaptation while
  preserving course/model separation and restrictions on unrelated access.
- **POS-003**: Compact summaries and ordinary evidence links support
  understandable continuity without claims of complete transport auditing.

### Negative

- **NEG-001**: Relevant learner content leaves the machine during hosted use;
  this design does not offer machine-boundary isolation.
- **NEG-002**: Local deletion cannot recall prior hosted context. This project
  cannot establish provider retention/deletion behavior through file operations.
- **NEG-003**: Instructional safeguards and unresolved model semantics limit
  operations; this change does not deliver a fully enforced storage backend.

## Alternatives Considered

### Retain local-only inference for private records

- **ALT-001**: **Description**: Enforce the historical rule that hosted tools
  must never read raw learner-model records.
- **ALT-002**: **Rejection Reason**: Prevents the explicitly requested hosted
  student workflow and requires an unimplemented local processing backend.

### Add a new per-workspace opt-in before relevant reads

- **ALT-003**: **Description**: Require a separate authorization flag or ceremony
  before ordinary hosted task access to the configured learner vault.
- **ALT-004**: **Rejection Reason**: The maintainer explicitly requested normal
  task-scoped use without this additional gate. Clear disclosure and bounded
  retrieval remain required.

### Send the whole model for every task

- **ALT-005**: **Description**: Load all records to maximize available context.
- **ALT-006**: **Rejection Reason**: Violates cheapest-first bounded retrieval
  and needlessly exposes unrelated evidence; selected task use is not bulk
  upload authorization.

## Implementation Notes

- **IMP-001**: Update the portable specification, skill instructions,
  clarification gates, course-content privacy wording, evaluations, and student
  onboarding together. Restore the released immutable package before model
  operations; missing or incompatible deployed guidance is not permission to
  invent schema/update rules.
- **IMP-002**: Keep `docs/LEARNER_MODEL.md` as a pointer to the pinned deployed
  specification. Preserve historical sources through immutable links rather
  than rewriting ADR-0001 or retaining competing active specifications.
- **IMP-003**: Use synthetic learner scenarios to check relevant bounded reads,
  refusal to publish unrelated/private records, and retained write safeguards.
  Never send real learner records to evaluation services. Report manual skill
  checks separately from executable storage or transport enforcement.
- **IMP-004**: Configure an absolute existing external vault with
  `python -m src.vault.cli configure --vault PATH`; the ignored
  `.clew.local.json` stores its canonical path and version 1.
  Configuration does not bypass permissions. Configure/status retain Git index
  checks without reading learner/course contents; only configure adds ignore
  rules. Status is read-only. Never initialize or push vault Git; stop for
  already tracked private paths. Ignore rules do not untrack or encrypt.
- **IMP-005**: Explain that there is no automatic backup or cross-device sync.
  This proposal adds no inference backend, passive telemetry, institutional
  dashboard, teacher override, or statistical/tombstone algorithm.
- **IMP-006**: Presence of `model` or `artifacts` does not establish ownership.
  Commands report presence only. The agent must ask before writing where
  collisions or an unfamiliar existing model leave intent uncertain.

## References

- **REF-001**: [Historical learner-model specification](https://github.com/francesco-kruk/clew/blob/6b03b5e8fdaefc16478de179bac00e9baa188c20/docs/LEARNER_MODEL.md),
  particularly its machine-boundary claims in sections 4, 8, and 9.
- **REF-002**: [Current learner-model contract pointer](../LEARNER_MODEL.md).
- **REF-003**: [ADR-0002: Repository and package ownership](adr-0002-repository-and-package-ownership.md).
- **REF-004**: [ADR-0001: Shared Obsidian course content contract](adr-0001-shared-obsidian-course-content-contract.md).
- **REF-005**: [Student hosted-processing disclosure](../../README.md#local-files-hosted-copilot).
- **REF-006**: [Reorganization coordination session](ghapp://sessions/7ad4168d-d57d-4678-99c3-555c5888f1a3):
  requesting maintainer's hosted-use direction; not an ADR acceptance record.
- **REF-007**: [ADR-0005: Evidence-first learner continuity](adr-0005-evidence-first-learner-continuity.md).
- **REF-008**: [ADR-0004: Portable bounded course reading](adr-0004-portable-bounded-course-reading.md).
