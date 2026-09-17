---
title: "ADR-0001: Shared Obsidian course content contract"
status: "Accepted"
date: "2026-09-16"
authors: "Dominique Broeglin"
tags: ["architecture", "decision", "course-content", "skills"]
supersedes: ""
superseded_by: ""
---

# ADR-0001: Shared Obsidian course content contract

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

Proposed on 2026-09-16. Dominique Broeglin requested the skill implementation
and confirmed the hub-based layout and stakeholder attribution. That initial
implementation request did not constitute lifecycle acceptance.

Accepted on 2026-09-17 by Dominique Broeglin following the explicit request
"Accept the ADR changes", recorded in REF-005. Acceptance approves this decision;
it does not independently authorize additional implementation.

## Context

Clew needs a reusable way for multiple skills to read authoritative course
content in Obsidian without depending on the original source format or PDF
extraction internals. The learner-model specification already identifies
`courses/<course>/hub.md` as read-only metadata supplying course domains and a
concept index, separate from domain-indexed private learner state.

The supplied tutor-spike reference uses a hub as a stable course interface,
but its documented authoring contract also requires plans and dashboards.
Clew's current PDF skill instead describes a standalone index and allows
long chapters to be split into section notes. Neither is the requested
source-neutral, one-file-per-chapter reading contract.

The requested constraints are one complete Markdown file per chapter, a
single main file connecting the course, optional supporting concepts/assets,
and a clear responsibility split between course reading and PDF conversion.

## Decision

Introduce the first-party `course-content` skill as the shared owner of course
organization and reading. Use `courses/<course>/hub.md` as the canonical main
file, one complete note per chapter, and stable headings for finer sections.
The hub provides domain metadata, ordered chapter links, a concept index, and
navigation to supporting content. Its bundled structure reference is the
format contract; this ADR records the rationale rather than duplicating it.

Consumers load the hub first and retrieve only the needed authoritative
chapter sections, with exact file/anchor citations and explicit limitations.
Reading is read-only, source-neutral, and independent of learner state.
Optional concept notes are navigation or labeled synthesis, not replacement
chapters or evidence of mastery.

PDF course imports compose with this skill. `brute-force-pdf-to-obsidian`
retains source inspection, extraction/OCR, math and artwork recovery, fidelity,
coverage reports, and packaging. Section-sized processing batches are merged
into complete chapter files. Explicitly non-course PDF bundles retain their
standalone behavior; legacy courses can be read without automatic migration.

## Consequences

### Positive

- **POS-001**: Reading and downstream teaching skills share a stable interface
  without understanding PDF extraction manifests or tools.
- **POS-002**: A hub and complete chapter files preserve course order and source
  context while allowing bounded heading-level reads.
- **POS-003**: Course metadata remains separate from domain-indexed learner
  evidence, consistent with the learner-model specification.

### Negative

- **NEG-001**: Long chapter files require bounded reads and incremental authoring;
  splitting processing work is no longer a reason to split delivered chapters.
- **NEG-002**: Existing standalone bundles and section-based courses are not
  automatically compliant. Consolidation requires an authorized migration.
- **NEG-003**: Repeated `hub.md` basenames require qualified links. Importers
  must preserve or explicitly rewrite the declared vault-relative prefix.
- **NEG-004**: An instructional contract does not itself enforce structure or
  source fidelity; producers must perform and accurately report those checks.

## Alternatives Considered

### Keep course structure inside the PDF converter

- **ALT-001**: **Description**: Have readers depend on the converter's index,
  layout, and extraction-specific conventions.
- **ALT-002**: **Rejection Reason**: Couples course reading to one ingestion
  source and duplicates format decisions in future non-PDF importers, contrary
  to the requested reuse and responsibility split.

### Deliver section notes with a chapter index

- **ALT-003**: **Description**: Retain the PDF skill's long-chapter split policy
  and reconstruct chapters through an index or embeds.
- **ALT-004**: **Rejection Reason**: Does not satisfy the explicitly requested
  one-complete-Markdown-file-per-chapter delivery unit. Bounded processing
  remains available without fragmenting the final chapter.

## Implementation Notes

- **IMP-001**: Maintain the new skill and PDF integration as first-party files.
  Do not edit APM-generated skills or change dependency pins for this work.
- **IMP-002**: New course writers use the shared contract. Readers may follow
  explicitly selected legacy links read-only, reporting missing metadata and
  blocking ambiguous lookup rather than silently migrating content.
- **IMP-003**: Keep chapter inventory, hub reachability, anchors, and asset
  resolution checks distinct from PDF source-coverage and fidelity checks.
  Synthetic skill scenarios exercise bounded reads and the producer handoff;
  they are not evidence of a real PDF conversion or live Obsidian rendering.
- **IMP-004**: Do not require the reference project's learning plan, prerequisite
  exercise hierarchy, or learner dashboard just to publish or read a course.

## References

- **REF-001**: [Learner-model specification](../LEARNER_MODEL.md).
- **REF-002**: [Course-content skill](../../.agents/skills/course-content/SKILL.md)
  and [structure contract](../../.agents/skills/course-content/references/structure.md).
- **REF-003**: [PDF conversion skill](../../.agents/skills/brute-force-pdf-to-obsidian/SKILL.md)
  and [quality reference](../../.agents/skills/brute-force-pdf-to-obsidian/references/quality-and-linking.md).
- **REF-004**: User-supplied tutor-spike worktree, reviewed on 2026-09-16:
  `course-authoring`, `tutor-session`, and learner-model schema guidance.
  It provided documented hub-first patterns, not implemented course examples.
- **REF-005**: [Course content skill](ghapp://sessions/b00d89a8-3dd2-448a-9e33-2d1249ba6c04)
  session discussion: Dominique Broeglin explicitly accepted this ADR on
  2026-09-17 with "Accept the ADR changes".
