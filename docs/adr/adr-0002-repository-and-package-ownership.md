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
The reorganization plan authorizes implementation, not ADR acceptance. No
acceptance or approval by another contributor is asserted.

## Context

Clew currently mixes student tools, first-party skill sources, generated
third-party skills, PDF ingestion, and a learner-model specification. Teachers
need a publishing workspace and students need a safe course handoff without
copying development tools or putting private learner files in a source clone.
Portable skills cannot depend on a consumer's documentation or sibling checkout.

ADR-0001 accepts one canonical course hub and one complete file per chapter.
That content contract remains unchanged. The repository split concerns source
ownership, packaging, and delivery, not a replacement course structure or a
retroactive rewrite of ADR-0001's implementation notes.

Both existing PDF workflows must survive: the fidelity-focused
`brute-force-pdf-to-obsidian` workflow, renamed `digest`, and Alexandra's
image-first `content-ingest` engine. Their capabilities must not be conflated.

## Decision

Assign first-party skill sources, executable helpers, portable contracts, and
pinned upstream dependencies to `clew-skills`. Assign teacher authoring and
validated published course packages to `clew-content`. Keep student Copilot
setup, external-vault configuration/import tools, architecture records, and the
optional Markdown canvas in `clew`.

Consume independently installable skill packages through APM 0.28.0 at immutable
commits. Generated `.agents/skills` deployments are not another source of truth.
Keep upstream skills at their original sources with existing pins and licenses
unless a demonstrated compatibility need requires a change. The full learner
specification belongs in the learner-model package; `docs/LEARNER_MODEL.md` is a
pointer to its pinned deployed copy.

Keep `digest`'s page-by-page fidelity workflow and standalone non-course support.
Package the `content-ingest` Python engine with its skill, retaining its
image-first behavior and the `python -m src.ingest.cli` compatibility wrapper in
Clew. PDF dependencies are optional, installed from the deployed skill's
`requirements.txt`, separate from student validator dependencies. Extraction
must be assembled into the shared course format and verified before publication.

Store learner vaults outside the clone. Resolve explicit `--vault` or ignored
`.clew.local.json`, never a guessed home directory. Import validated immutable
course snapshots preserving the `courses\<course>` prefix. An intact identical
reimport is a no-op; changed revisions are staged, never activated automatically.
Dirty or unrecognized destinations are conflicts. Importers never read or modify
the model or personal artifacts and do not initialize vault Git.

## Consequences

### Positive

- **POS-001**: Teachers, students, and skill maintainers have distinct ownership
  boundaries without duplicating the shared contract or validator.
- **POS-002**: Immutable pins and import receipts make installed tools and course
  revisions identifiable; staged updates protect student work.
- **POS-003**: Both PDF approaches remain available, with honest image-first
  limitations and a preserved legacy command.

### Negative

- **NEG-001**: Cross-repository releases require dependency ordering and clean
  consumer-restore tests; unreleased package refs are not usable dependencies.
- **NEG-002**: Snapshot staging deliberately leaves activation/comparison work
  to a later authorized step rather than providing automatic synchronization.
- **NEG-003**: A structurally valid package does not prove source fidelity or
  distribution rights; publishing requires separate evidence and review.

## Alternatives Considered

### Keep all ownership and copied skills in the student repository

- **ALT-001**: **Description**: Retain the engine, contracts, first-party skills,
  teacher artifacts, and student workflows together.
- **ALT-002**: **Rejection Reason**: Conflicts with the requested three-repository
  ownership split and makes portable contracts depend on a consumer checkout.

### Replace one PDF workflow with the other

- **ALT-003**: **Description**: Standardize all PDF tasks on one ingestion method.
- **ALT-004**: **Rejection Reason**: Loses either the source-verification workflow
  or Alexandra's image-preserving extraction and violates the explicit request
  to preserve both.

### Synchronize course revisions over the installed vault course

- **ALT-005**: **Description**: Treat the teacher repository as an automatically
  updated mirror inside the student vault.
- **ALT-006**: **Rejection Reason**: Risks overwriting local work and importing
  unrelated repository files; immutable snapshots with explicit staging are the
  requested first-version boundary.

## Implementation Notes

- **IMP-001**: Publish `clew-skills` first at a reachable immutable revision,
  then regenerate teacher/student APM deployments and lockfiles with 0.28.0.
  Do not invent lock hashes or hand-edit generated skills. Preserve MIT
  attribution and upstream notices; software licenses do not license textbooks.
- **IMP-002**: Teacher consumers install `digest`, `content-ingest`, and shared
  course/Obsidian dependencies, not learner-model. Students install course-content
  and learner-model, with content-ingest for optional legacy use.
- **IMP-003**: Keep a versioned package manifest, inventory/hashes, catalog, and
  shared validator in the portable course contract. Resolve a remote ref once
  to an immutable commit. Reject unsafe paths and validate the full staged
  package before final installation; never execute course content.
- **IMP-004**: Trigonometry publication remains gated on documented permission
  scope/evidence and checks. This record grants no redistribution permission.
  An unavailable catalog must produce actionable guidance, not a bypass.
  Use synthetic original packages while publication is blocked.
- **IMP-005**: Use synthetic tests for clean restores, imports, no-op reimports,
  staged revisions, dirty conflicts, unsafe packages, and interrupted operations.
  Verify model/artifact sentinels remain byte-identical. Do not inspect real
  learner data for tests.
- **IMP-006**: Keep vault ignore rules additive and stop for already tracked
  private paths. Ignoring does not untrack or encrypt files. Never initialize or
  push vault Git. Preserve the existing optional `red-markdown` extension.

## References

- **REF-001**: [ADR-0001: Shared Obsidian course content contract](adr-0001-shared-obsidian-course-content-contract.md).
- **REF-002**: [ADR-0003: Local learner storage and hosted Copilot processing](adr-0003-local-learner-storage-and-hosted-copilot-processing.md).
- **REF-003**: [Student setup, release order, and skill management](../../README.md).
- **REF-004**: [Learner-model contract pointer](../LEARNER_MODEL.md).
- **REF-005**: [Reorganization coordination session](ghapp://sessions/7ad4168d-d57d-4678-99c3-555c5888f1a3):
  requesting maintainer's implementation plan and publication gates; not an ADR
  acceptance record.
- **REF-006**: [Original Clew revision](https://github.com/francesco-kruk/clew/tree/6b03b5e8fdaefc16478de179bac00e9baa188c20)
  preserves the pre-migration sources and attribution.
