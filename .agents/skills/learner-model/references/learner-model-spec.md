# Default operational profile: evidence-first-v1

Profile ID **`evidence-first-v1`**, schema version **`1`**. Package versioning is
separate (learner-model 2.x). These agent-operated Markdown conventions are not
the older full schema with fields omitted. [Advanced-v1](advanced-model-spec.md)
retains that schema separately. No automatic conversion in either direction.

Contents: [scope](#1-scope-and-initialization),
[storage and continuity](#2-storage-ids-and-continuity),
[record templates](#3-common-record-template),
[file tools](#4-file-tool-protocol-not-enforced-guarantees),
[corrections and suppression](#5-inspection-correction-and-logical-suppression),
[boundaries](#6-boundaries-and-profile-evolution).

## 1. Scope and initialization

Remember learner-stated goals, actual supplied work, observed factual errors,
explicitly confirmed preferences, and actual sessions. No numerical mastery,
confidence, efficacy, durability, weighting, decay, review queue or automatic
scheduling. Dates the learner supplies as goals are facts, not scheduled actions.
Do not infer mastered/unseen state from a course inventory or diagnose a
misconception from an error. No clinical, psychological or learning-style labels.

Resolve an explicitly authorized external vault before access. Clew's ignored
`.clew.local.json` has `version: 1` and an absolute `vault` path; this skill does
not create or change that setting. Other hosts must supply an explicit root.
The learner manually copies a complete teacher bundle; no importer, catalog,
manifest, hub, frontmatter, Obsidian app or concept registry is required.

Path configuration alone creates nothing. Ask for the learner's goal or work.
A genuine intake statement/attempt authorizes the corresponding bounded records
under the established tutoring task, not invented history. Before the first
write, inspect reserved path names and existing files. If `model/` or `artifacts/`
already contains unrelated data, an unknown marker, old schemas or unexplained
records, ask about ownership/profile before changing anything. Empty directories
may be used. Never silently adopt, overwrite, migrate or delete an existing model.

For a fresh initialization with real evidence, create this exact marker:

```markdown
# Learner model profile

- profile: evidence-first-v1
- schema_version: 1
- records: model/
- artifacts: artifacts/
```

Store it at `model/profile.md`. The marker declares the conventions, not proof
that all files are valid. Missing, duplicate or conflicting marker values block
writes. Alternative root layouts require explicit agreement; do not discover
one by searching the entire vault.

## 2. Storage, IDs and continuity

All paths below are relative to the configured vault. Use native filesystem
separators in tool calls; portable Markdown links use `/`.

| Path | Contents |
| --- | --- |
| `model/profile.md` | Exact profile/version marker above. |
| `model/index.md` | Compact routing index described below; no scored summary. |
| `model/goals/goal-<uuid>.md` | The learner's stated intent. |
| `model/observations/obs-<uuid>.md` | One deliberate statement, attempt, supplied work or confirmation. |
| `model/errors/error-<uuid>.md` | One grounded factual discrepancy, not a diagnosis. |
| `model/preferences/pref-<uuid>.md` | Explicitly confirmed future working condition and scope. |
| `model/sessions/session-<uuid>.md` | Actual session, evidence and outcomes. |
| `model/mappings/map-<uuid>.md` | Optional source-grounded domain/concept identity binding. |
| `model/changes/change-<uuid>.md` | Append-only corrections, lifecycle changes and scoped suppression. |
| `artifacts/artifact-<uuid>.md` | Supplied work or generated personal output, clearly distinguished. |

Allocate a new UUID using an available UUID tool, use the storage table's prefix, and check
the intended paths and index IDs for collisions. Never reuse or renumber an ID;
a correction refers to the original ID. Reserve IDs before cross-linking an
operation. Use actual ISO 8601 timestamps with timezone for `created_at`, not
guessed lesson times. If the original event time is unknown, say so in the body;
`created_at` is the recording time. New sessions receive new IDs even on one day.

Use this routing index, created with the first records:

```markdown
# Learner record index

## Latest session
<!-- One link to the latest actually recorded session, not a planned session. -->

## Active goals
<!-- ID | record link | literal short goal | change links -->

## Records
<!-- ID | kind | record link | source context or stated scope | change links -->

## Session history
<!-- timestamp | session link | brief actual topic -->
```

Replace instructional comments with actual rows as needed; never save fabricated
example evidence. Each record/artifact has one `Records` row, including changes.
Each affected target row lists all its change links in append order. Keep rows
short: routing facts and links only, not copied work. When a target is suppressed,
replace its descriptive index text with `suppressed` while retaining ID, path
and change links; remove it from `Active goals` if appropriate. Historical notes
stay on disk. Session history is append-only routing history, not a due queue.

The index is a maintained aid, not an independent authority. Use bounded heading
reads and exact ID/label searches within it as it grows. If it disagrees with
records, a linked file is missing or an operation was interrupted, stop affected
writes and reconcile with the learner rather than inventing support. Do not
repair by recursively ingesting the vault.

Fresh-context continuation:

1. Resolve vault and marker, then read the relevant index sections/rows.
2. For "continue", start with latest actual session and active goal pointers.
   For a named item, select only its relevant rows; do not load unrelated records.
3. Read a target's listed change notes **before** original evidence. Apply
   corrections/suppression; suppressed evidence is not tutoring context.
4. Follow only the necessary observation, artifact and source-section links.
   Say what was actually supplied, what feedback was given, and what remains
   unchecked. A past request/goal is not proof of progress.
5. Append new actual evidence and a session note; update the index last.

Copied course-only reading uses `course-content` and skips all model reads.

## 3. Common record template

Every note in the typed directories and `artifacts/` uses this frontmatter.
All listed keys are required; placeholders below are instructions, not values.
Use `[]` for no mappings or no evidence where explicitly allowed, never invent
IDs or unknown scalar fields from the advanced schema.

```yaml
---
profile: evidence-first-v1
schema_version: 1
id: <prefix-uuid from storage table, matching filename>
kind: <goal|observation|error|preference|session|mapping|change|artifact>
created_at: <actual ISO 8601 timestamp with timezone>
session: <session-id; sessions refer to themselves>
evidence: []
mapping_refs: []
---
```

`evidence` is a list of record IDs, not a confidence measure. `mapping_refs`
contains mapping IDs only when identity has actually been grounded; `[]` means
unresolved/not needed, not "no concepts exist". Include ordinary Markdown links
to each referenced note in the body. The body preserves human-readable source
citations with exact vault-relative note, actual heading/block or item, and
applicable physical/printed page distinctions. Links are relative to the note
that contains them; citations do not imply a file/image was inspected.

All domain-specific fields below are additional required frontmatter keys for
that kind. Body headings are the readable template for its facts. Do not save
empty placeholder records just to fill directories.

| Kind | Additional keys | Body and evidence rules |
| --- | --- | --- |
| `observation` | `event: statement\|attempt\|supplied-work\|confirmation` | `## Observed`, `## Context`, `## Limits`. Preserve the learner's words/actual answer. This is root evidence, so `evidence: []` is valid; link an artifact if used. Identify source as current conversation or exact supplied item, never an invented transcript URL. |
| `goal` | `status: active\|met\|abandoned`, `deadline: null` or learner-stated date/text | `## Goal`, `## Context`. At least one statement observation. Change status only from real learner report/evidence, with a change note; no automatic expiry or success. |
| `error` | `assessment: source-grounded\|agent-derived` | `## Attempt`, `## Discrepancy`, `## Basis`, `## Limits`. At least one attempted-work observation. Cite the authoritative section or show the derivation that establishes the error. If unsure, retain an unchecked observation instead. |
| `preference` | `confirmation: explicit`, `scope: <learner-confirmed scope>` | `## Condition`, `## Confirmation`, `## Limits`. At least one explicit standing-preference confirmation/statement observation. Quote the agreed scope, such as this topic or all future explanations; never infer global scope or benefit. |
| `session` | `adaptation: none\|requested\|confirmed-preference` | `## Request`, `## Observations`, `## Work and feedback`, `## Outcome and open questions`, `## Presentation`. Link actual evidence and artifacts; `evidence: []` is valid for an actual inspection-only session. State unknown outcomes. No invented duration, repair, review dates or future session entries. |
| `mapping` | `domain: <grounded identity>`, `concept: null` or source concept, `source_id: null` or source-established ID | `## Identity`, `## Sources`, `## Limits`. Cite exact source metadata/statement defining the identity. `evidence: []` allowed for a binding grounded only in course metadata, never learner state. |
| `artifact` | `origin: supplied\|generated`, `adaptation: none\|requested\|confirmed-preference` | `## Content`, `## Provenance`, `## Presentation`. Preserve supplied work separately from generated feedback. Link supporting observations, goals, selected source sections and any used preferences. A supplied artifact may have `evidence: []`; a generated one requires supporting record IDs. |
| `change` | See section 5 | Human-readable requested change, reason, effective replacement (if any), evidence and exact scope. |

Observation and supplied-artifact evidence may form a referenced pair: allocate
both IDs before writing, write the supplied artifact first with `evidence: []`,
then observation referencing it. The actual session starts with its request
and reserved ID; append evidence/outcome when recorded. Never treat a partially
written operation as complete.

### Identity without a catalog

Goals/errors/preferences use stable record IDs, not course folders. Course name
and exact note are context values, not identity keys. Keep `mapping_refs: []`
while unresolved. A factual answer and a literal goal do not require a domain.
Reuse a mapping across courses only when grounded identity really matches;
record the supporting locations. "Normal" in statistics and geometry, or "Java"
the language and island, are not equivalent labels. Ask when identity affects
selection, reuse or merging; do not ask merely to fill optional metadata.
No generic concept index becomes evidence about this learner.

### Adaptation may be absent

`adaptation: none` with `## Presentation` stating "No adaptation used" is valid.
For `requested`, quote the current request and scope, without creating a standing
preference. For `confirmed-preference`, name and link the unsuppressed preference
IDs used and the actual changes. Generated artifacts and sessions link those
preferences; index rows make reverse lookup possible. Agreement and an attractive
presentation are not efficacy evidence. This profile does not measure efficacy
or silently upgrade to advanced decisions.

## 4. File-tool protocol (not enforced guarantees)

Before a mutation, read the marker, relevant index rows, targets and overlays;
check profile fields, kinds, timestamps, IDs, references and reserved-path
ownership. Inspect source paths without following links outside the authorized
scope. Note tool limitations; prose supplies no filesystem sandbox.

Prepare the complete change in memory, preserving unknown/unrelated data and
history. Re-read files immediately before editing, comparing content with what
was read; unexpected differences require stopping and reconciling, not overwrite.
Use create-only behavior if available for new IDs. Prefer exact-context patches
to whole-file replacement. Do not claim these checks prevent every race.

Write dependencies first, derived notes next and index links last. Re-read all
affected files; check frontmatter, matching IDs, timestamps, local links, evidence,
effective overlays and that the intended history is still present. Confirm the
original teacher notes were unchanged. No bundled writer or atomic transaction
exists. A partial failure needs an exact persisted/not-persisted report and a
pause for recovery, not silent success or destructive rollback.

Append observations as new files, and append session events rather than rewriting
earlier events. Corrections/lifecycle updates use section 5; index routing may be
updated after evidence persists. Never commit private records to the skills or
consumer repository, and never require a whole-vault upload for continuity.

## 5. Inspection, correction and logical suppression

Inspection reads selected records with overlays and follows bounded evidence on
request. Explain effective facts and limitations, not scores. Original history
can be inspected explicitly, with corrected/suppressed content labelled as such.

Changes use common metadata plus:

```yaml
action: correct # correct | tombstone
target: <one existing record ID>
suppressed_evidence: [] # tombstone only; IDs whose contribution to target is suppressed
supersedes: [] # earlier change IDs explicitly replaced for the same target
```

Required body headings: `## Request`, `## Reason`, `## Effective replacement`,
`## Scope`. A change records the learner's actual request and can have
`evidence: []` when quoting that direct request; otherwise link its observation.
`target` cannot be a profile marker, index or another change. Never change an
ID, kind, profile, recording timestamp, original evidence, or original history
with a correction.

For **correct**, write a complete replacement of the affected effective body
section(s) and list any replacement mutable fields (`status`, `deadline`,
`scope`, `mapping_refs`, `assessment`, `adaptation`, or `event`) by exact name.
The original stays intact. An incorrect supplied answer can be marked as a
transcription mistake without pretending the initial recording never happened.
Append a new change for later corrections, explicitly naming superseded
overlapping change IDs. Apply non-overlapping changes together; conflicting
overlays without explicit supersession block reliance and writes. Do not use
timestamp sorting as an implicit conflict resolver.

For **tombstone**, explain the target, shared evidence and retained history,
then obtain confirmation of that logical-suppression scope. Set
`suppressed_evidence` to the supporting IDs to exclude **for this target only**;
`[]` means suppress the target without altering evidence contributions elsewhere.
`## Effective replacement` says `Suppressed; no replacement`. Remove the target
from normal active lookup/inference and suppress its old index description.
Keep its ID/path/change pointers, original files and all observation history.
Never cascade deletion/suppression to other targets sharing the observation.
Their use of shared evidence remains valid unless separately authorized.

A direct request to correct is sufficient authority for that bounded correction.
"Forget" needs the logical/physical distinction made clear, not a false erasure
claim. True file erasure or provider-side erasure is outside this profile:
stop and explain the limitation and need for explicit separate handling. A
tombstone cannot remove hosted context already processed, logs, backups or
copies, and no such guarantee is offered.

## 6. Boundaries and profile evolution

Teacher bundles remain read-only unless the student explicitly requests their
editing. Personal output and model data belong only in the authorized external
vault. Relevant bounded records may enter hosted GitHub Copilot during a task;
local storage does not imply local inference or automatic backup/sync. No teacher
access, institutional dashboard, passive telemetry or bulk vault upload.

Unknown versions, malformed records or a partially initialized model need a
focused clarification/recovery step. Do not weaken this profile with ad hoc
fields, import advanced thresholds, silently migrate or manufacture null-filled
advanced records. Future profiles require explicit versioning and an authorized
migration plan. These are behavioral instructions, not enforced storage,
security, privacy, concurrency or provider-deletion guarantees.
