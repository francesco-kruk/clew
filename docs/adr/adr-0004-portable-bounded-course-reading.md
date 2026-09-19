---
title: "ADR-0004: Portable bounded course reading"
status: "Proposed"
date: "2026-09-19"
authors: "Francesco Kruk (requesting maintainer)"
tags: ["architecture", "decision", "course-content", "reading"]
supersedes: ""
superseded_by: ""
---

# ADR-0004: Portable bounded course reading

## Status

**Proposed** | Accepted | Rejected | Superseded | Deprecated

Proposed on 2026-09-19 at requesting maintainer Francesco Kruk's direction.
This is the intended replacement default for ADR-0001's required hub/chapter
layout, not an accepted supersession. ADR-0001 remains Accepted and unchanged.
Both relationship fields remain empty until explicit lifecycle approval.
Approval to implement the redesign is not ADR acceptance or another
contributor's approval.

## Context

The student receives a portable bundle of teacher notes and assets and manually
copies it as-is into any chosen folder in a self-created external vault.
Requiring a particular course prefix, hub, metadata schema, or chapter layout
would turn reading into a migration task.

ADR-0001 established a shared reader contract with a canonical hub and complete
chapter files. Its bounded source-grounded retrieval and separation from learner
state remain useful, but its mandatory organization is not the requested
student default. Existing notes can have their own indexes and links without
being rewritten to satisfy a distribution format.

## Decision

Use `course-content` v2 as the portable bounded reader. Start from the student's
selected notes or topic and use relevant existing navigation and linked context.
No `courses` directory, hub, catalog, manifest, or schema migration is required.
Preserve the copied bundle's internal names, links, assets, and organization.

Read only what the task needs, cite source files and sections, distinguish
source material from agent synthesis, and surface missing assets or ambiguous
targets. Do not infer domains or silently repair, rename, or migrate notes.
An existing hub can be useful navigation, but is not mandatory.

Teacher notes are read-only unless the student explicitly requests a change.
Tutoring explanations, practice, and personal work belong in the agreed
`artifacts` destination, not in automatic edits to teacher sources. Course-only
lookup does not require learner records and does not establish mastery.

Teacher conversion with `digest` stays in `clew-content`. The student copies
the entire portable notes/assets bundle; this workspace has no teacher
conversion or course distribution requirement.

## Consequences

### Positive

- **POS-001**: Existing portable notes are useful immediately without a
  structural rewrite or duplicated canonical index.
- **POS-002**: Bounded reads and exact citations retain source grounding while
  keeping course lookup independent of learner state.
- **POS-003**: Preserving bundles as-is avoids accidental loss of source
  caveats, answers, links, and asset context.

### Negative

- **NEG-001**: Arbitrary bundle navigation can be ambiguous; the agent may
  need the learner to identify a source rather than assume a global structure.
- **NEG-002**: Manual copying and reading do not verify fidelity, rights, or
  every link. Missing assets must be reported honestly.
- **NEG-003**: Without mandatory metadata, the agent cannot assume chapter
  order, domain labels, or a global concept registry.

## Alternatives Considered

### Keep ADR-0001's organization mandatory

- **ALT-001**: **Description**: Require a canonical course hub, complete chapter
  files, and fixed metadata before reading.
- **ALT-002**: **Rejection Reason**: Makes an as-is manual bundle handoff depend
  on a migration the student did not request.

### Automatically normalize every copied bundle

- **ALT-003**: **Description**: Rename and restructure source notes, infer
  domains, and generate replacement navigation.
- **ALT-004**: **Rejection Reason**: Risks breaking links or misrepresenting
  source intent, and violates the read-only-by-default boundary.

### Read all source and learner files at session start

- **ALT-005**: **Description**: Use the entire vault as context to compensate
  for a lack of prescribed organization.
- **ALT-006**: **Rejection Reason**: Violates task-bounded retrieval and exposes
  unrelated records without improving source selection reliably.

## Implementation Notes

- **IMP-001**: Consume the matching course-content v2 immutable package and
  keep its operating contract in the skill bundle, not duplicated here.
- **IMP-002**: Test bounded lookup with synthetic portable bundles in varied
  folders, ambiguous links, and missing assets. Do not claim that behavioral
  tests prove complete source fidelity or sandbox enforcement.
- **IMP-003**: Ask before writing to reserved `model`/`artifacts` paths when
  ownership is uncertain; source bundles can already use those names.
- **IMP-004**: If this proposal is explicitly accepted as ADR-0001's
  replacement, update both lifecycle records, relationship fields, and index
  together through the ADR process. Do not do so merely because code changes.

## References

- **REF-001**: [ADR-0001: Shared Obsidian course content contract](adr-0001-shared-obsidian-course-content-contract.md), intended replacement default.
- **REF-002**: [ADR-0002: Repository and package ownership](adr-0002-repository-and-package-ownership.md).
- **REF-003**: [Course-content skill](../../.agents/skills/course-content/SKILL.md).
- **REF-004**: [Student setup](../../README.md#student-setup).
- **REF-005**: [Student workspace session](ghapp://sessions/357f9483-e268-444b-92aa-a417df6fec4b),
  2026-09-19 redesign direction from the requesting maintainer, not acceptance.
