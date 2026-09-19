---
title: "ADR-0002: Repository and package ownership"
status: "Proposed"
date: "2026-09-18"
authors: "Francesco Kruk (requesting maintainer)"
tags: ["architecture", "decision", "repositories", "packages"]
supersedes: ""
superseded_by: ""
---

# ADR-0002: Repository and package ownership

## Status

**Proposed** | Accepted | Rejected | Superseded | Deprecated

Proposed on 2026-09-18 at requesting maintainer Francesco Kruk's direction.
Revised on 2026-09-19 for the user-approved student-only redesign and manual
notes handoff, replacing this proposal's earlier distribution-tooling plan.
Implementation authorization is not ADR acceptance. No lifecycle approval
or another contributor's agreement is asserted.

## Context

Students need to use teacher notes without running teacher conversion tools or
conforming an existing bundle to a distribution schema. A source clone should
not contain the learner's vault. Reusable skills should not depend on a sibling
checkout or duplicate specifications in their consumers.

The previous proposal coupled student setup to packaged course distribution
and teacher tooling. The requested redesign instead has the teacher prepare
portable notes/assets and the student copy the entire bundle as-is into a
self-created external vault.

ADR-0001's accepted layout remains historical policy until an explicit lifecycle
decision. Proposed ADR-0004 describes the intended portable-reading replacement
default; this revision does not silently rewrite or supersede ADR-0001.

## Decision

Keep `clew` student-only: vault-location configuration, tutoring instructions,
architecture records, and the existing optional Markdown canvas.
`clew-content` owns teacher authoring and `digest` conversion.
`clew-skills` owns reusable skills and their canonical contracts.

The student manually copies the entire portable notes/assets bundle into any
chosen folder within an external vault. Preserve its internal layout; no
`courses` prefix, hub, catalog, manifest, or schema migration is a prerequisite.
Teacher source notes remain read-only except for an explicit user request.
Source fidelity and distribution rights remain teacher responsibilities;
manual copying does not confer rights.

Student runtime skills are only `teach`, `course-content`, and `learner-model`, consumed
at immutable pins through APM 0.28.0. Contributor skill-creator/ADR/Defuddle/Bases
and Obsidian Canvas/Markdown/optional CLI tooling use direct upstream dependencies
at existing pins, not a development package. Generated skill deployments are not
another source of truth.

`teach` composes the existing reading and memory contracts for the conversational
student loop; it adds no local runtime, learner schema, or dedicated UI.

Configure an absolute, existing external vault with `python -m src.vault.cli
configure --vault PATH`; inspect it with `python -m src.vault.cli status`.
Ignored `.clew.local.json` stores version 1 and the canonical vault path.
There is no home fallback, automatic vault creation, or record creation from a
path. Configuration is a location setting, not a permissions bypass or sandbox.

Both commands avoid reading course and learner-file contents. They retain Git
index checks and report presence of reserved `model`/`artifacts` names without
determining ownership. Configure alone adds relevant ignore rules additively;
status is read-only. The agent asks before writes if reserved names collide or
ownership is uncertain.

## Consequences

### Positive

- **POS-001**: Students can use existing portable bundles without learning a
  publishing protocol or installing teacher conversion tooling.
- **POS-002**: Separate source ownership prevents student instructions from
  becoming another maintained copy of skill contracts.
- **POS-003**: Narrow location commands establish no learner facts and do not
  inspect private record contents.

### Negative

- **NEG-001**: Manual copying does not provide automatic delivery, version
  activation, synchronization, or verification of source fidelity.
- **NEG-002**: Broken or ambiguous bundle links need a bounded clarification
  rather than an automatic reorganization.
- **NEG-003**: Reserved-name collisions and existing learner records can
  require a conversation before writes; configuration cannot prove ownership.

## Alternatives Considered

### Keep teacher workflows in the student workspace

- **ALT-001**: **Description**: Deploy teacher conversion engines alongside
  student runtime skills.
- **ALT-002**: **Rejection Reason**: Contradicts the student-only boundary and
  adds dependencies unrelated to learning from already prepared notes.

### Require a standardized distribution layout

- **ALT-003**: **Description**: Require a catalog, manifest, canonical hub and
  fixed course directory before the student can read a bundle.
- **ALT-004**: **Rejection Reason**: The requested handoff is a portable bundle
  copied as-is; a migration requirement obstructs that workflow.

### Create a default vault automatically

- **ALT-005**: **Description**: Guess a home-directory destination and initialize
  storage when a learner first starts the workspace.
- **ALT-006**: **Rejection Reason**: Obscures the chosen data location and risks
  confusing existing files with Clew-owned records.

## Implementation Notes

- **IMP-001**: Publish the matching skill sources at a reachable immutable
  revision before pinning consumers. Restore with `apm install --frozen`, using
  both manifest targets `copilot` and `agent-skills`; narrowing to
  `--target copilot` alone silently skips hybrid skills.
- **IMP-002**: Keep deployed files LF-normalized, regenerate lockfiles through
  APM, and preserve licenses/notices and original upstream pins. Do not hand-edit
  generated skills or invent lock hashes. Software licensing does not license
  teacher content.
- **IMP-003**: Never initialize or push vault Git. Stop for already tracked
  private paths; additive ignore rules do not untrack or encrypt them.
- **IMP-004**: Keep configuration/status tests synthetic and verify no source
  or learner-file content is read. Test reserved-name collisions without
  interpreting their contents as learner records.
- **IMP-005**: Preserve the optional `red-markdown` extension. Store tutoring
  artifacts and compact learner memory only for meaningful learning and
  after destination ownership is clear; location setup is not initialization.

## References

- **REF-001**: [ADR-0001: Shared Obsidian course content contract](adr-0001-shared-obsidian-course-content-contract.md).
- **REF-002**: [ADR-0003: Local learner storage and hosted Copilot processing](adr-0003-local-learner-storage-and-hosted-copilot-processing.md).
- **REF-003**: [ADR-0004: Portable bounded course reading](adr-0004-portable-bounded-course-reading.md).
- **REF-004**: [ADR-0005: Evidence-first learner continuity](adr-0005-evidence-first-learner-continuity.md).
- **REF-005**: [Student setup](../../README.md#student-setup).
- **REF-006**: [Coordination session](ghapp://sessions/7ad4168d-d57d-4678-99c3-555c5888f1a3)
  and [student workspace session](ghapp://sessions/357f9483-e268-444b-92aa-a417df6fec4b):
  implementation direction and the 2026-09-19 redesign, not ADR acceptance.
