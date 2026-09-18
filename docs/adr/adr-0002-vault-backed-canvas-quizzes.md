---
title: "ADR-0002: Vault-backed canvas quizzes"
status: "Proposed"
date: "2026-09-18"
authors: "Requesting Clew user; GitHub Copilot (implementation)"
tags: ["architecture", "decision", "skills", "quiz"]
supersedes: ""
superseded_by: ""
---

# ADR-0002: Vault-backed canvas quizzes

## Status

**Proposed** | Accepted | Rejected | Superseded | Deprecated

The requesting user authorized implementation on 2026-09-18, selecting
on-demand invocation, a form canvas, project scope, suggested answers after
submission, and separate records in the source vault's Quizzes folder.
These choices do not constitute ADR lifecycle acceptance.

Later on 2026-09-18, the user refined the scope to basic learner-model recording:
"drop assessing answers and updating concept knowledge for now ... Just append
the quiz to the learner model in a basic way." The initial version wrote only
quiz artifacts; this revision adds ungraded provenance without assessment.
The record remains Proposed.

## Context

A learner wants a reusable skill that generates exactly three questions from
the Obsidian Markdown currently displayed in a canvas. Paths differ between
vaults and machines. The quiz needs an actual interactive form and durable
local answer recording without modifying authoritative course content.

## Decision

Use a first-party instruction skill plus a project-local `vault-quiz` extension.
The skill resolves the active reader's path and Markdown at invocation time.
It supplies three grounded question/solution pairs and a fresh attempt ID.
The extension discovers the nearest `.obsidian` ancestor or requires a
user-confirmed root, then publishes one Markdown record under `Quizzes` on
Submit. Suggested answers appear only after persistence.

The attempt ID, not the panel ID, identifies durable work. Save exact written
answers as ungraded artifacts, separate from inferred learner attributes.
After saving a new quiz, append one linked `supplied-work` observation locally
under the learner-model provenance contract. Keep answers local; the
agent-facing status action returns metadata only. Explicitly report partial
saves and support idempotent local retries without overwriting ledger history.

## Consequences

### Positive

- **POS-001**: Source resolution and persistence are portable between vaults.
- **POS-002**: A local form records answers without routing them through chat.
- **POS-003**: Authoritative notes and inferred learner attributes remain
  unchanged; new evidence is available for a separately authorized local process.

### Negative

- **NEG-001**: Discovery needs a marker or explicit user confirmation.
- **NEG-002**: Unsaved drafts are ephemeral; math initially appears as text.
- **NEG-003**: Atomic publication requires filesystem hard-link support.
- **NEG-004**: Suggested answers require agent judgment; excerpt matching only
  checks grounding mechanically, not educational quality or correctness.
- **NEG-005**: Quiz publication and ledger append are separate filesystem
  operations. Partial completion needs visible retry behavior, and stale writer
  locks or damaged ledgers need manual investigation.

## Alternatives Considered

### Chat-based questions

- **ALT-001**: **Description**: Ask one question per chat turn and save responses.
- **ALT-002**: **Rejection Reason**: The user selected a canvas with fields and a
  submit button instead.

### Trigger on every opened note

- **ALT-003**: **Description**: Install a hook that creates quizzes automatically.
- **ALT-004**: **Rejection Reason**: The user clarified that quizzes should start
  only when explicitly requested.

### Assess answers and update concept knowledge

- **ALT-005**: **Description**: Evaluate answers and apply inferred concept changes,
  potentially after per-quiz opt-in.
- **ALT-006**: **Rejection Reason**: The user deferred assessment and knowledge
  updates; this revision records ungraded evidence only, without requiring an
  AI evaluator or inventing missing inference policies.

## Implementation Notes

- **IMP-001**: Use Node built-ins and the host SDK, without new dependencies.
- **IMP-002**: Generate attempts without changing existing course layouts.
  Local Markdown records contain a JSON block for exact durable round trips.
- **IMP-003**: Exercise vault discovery, no-overwrite persistence, same-origin
  form submission, reload recovery, and skill routing with synthetic data.
- **IMP-004**: Follow the learner-model skill for any separately authorized model
  operation; quiz submission itself performs no mastery inference.
- **IMP-005**: Use the original attempt ID and UTC timestamp for retry-safe
  observation identity and monthly routing. Older saved attempts are not
  backfilled. See section 3.6.1 of the model specification for null fields,
  unassessed capability tier, and the append-only evidence contract.

## References

- **REF-001**: [Shared course contract](adr-0001-shared-obsidian-course-content-contract.md).
- **REF-002**: [Learner-model specification](../LEARNER_MODEL.md).
- **REF-003**: [Quiz skill](../../.github/skills/canvas-quiz/SKILL.md).
- **REF-004**: [Extension and persistence contract](../../.github/extensions/vault-quiz/README.md).
- **REF-005**: Requesting user's choices in the 2026-09-18 canvas-quiz
  implementation conversation; no ADR acceptance has been requested or given.
