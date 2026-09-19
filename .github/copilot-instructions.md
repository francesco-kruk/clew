# Clew student workspace

Follow [AGENTS.md](../AGENTS.md), [student setup](../README.md#student-setup), and
the [learner-model contract pointer](../docs/LEARNER_MODEL.md).

## Manual notes handoff and vault selection

The student creates an external vault, copies an entire portable notes/assets
bundle as-is into any chosen folder, and supplies the vault path once.
Teacher `digest` conversion belongs in `clew-content`, not this workspace.
Do not require `courses`, a hub, catalog, manifest, or schema migration.

Configure with
`python -m src.vault.cli configure --vault "C:\Path\To\Existing Vault"`;
inspect configuration with `python -m src.vault.cli status`.
The path must be absolute and already exist outside the clone.
Ignored `.clew.local.json` stores `version: 1` and canonical `vault`.
Never use a home fallback or create a vault/learner records from a path.
Use Python 3.11+ standard library and Git; no pip/requirements installation.
Both command outputs use the stable `vault` JSON field. Explicit configure with
a valid supplied path can replace a malformed setting; status never updates
configuration or ignore rules.

Configure/status do not read course or learner-file contents. They retain Git
index checks and report reserved `model`/`artifacts` path presence only, not
ownership. Configure alone adds ignore rules additively; status is read-only.
Existing reserved root names trigger warnings even for files or case variants,
without reading inside them. Resolve ownership through the skill, not the tool.
Never initialize/push vault Git. `.gitignore` does not untrack or encrypt;
stop for already tracked private paths and give actionable guidance.
Ask before writing when reserved names, format, or destination ownership is
uncertain. Configuration is not a permission bypass or sandbox.

## Bounded tutoring and continuity

Use `course-content` v2 to read only the relevant portable notes and linked
context. Cite sources; surface ambiguity and missing assets. Do not infer
domains or automatically rename, reorganize, or migrate notes. Teacher notes
remain read-only unless the user explicitly requests a change.

Tutoring produces personal `artifacts` at an agreed destination; genuine goals,
supplied work, observed errors, and confirmed preferences can become readable
learner evidence. Configuring a path or copying notes is not evidence.
Use `learner-model` 3.0.0: one compact `model/learner.md` summary with exactly one
`<!-- clew-learning-memory: v1 -->` marker, dates, and ordinary evidence links.
Goals, Confirmed preferences, and Learning notes are recommended optional
headings, not mandatory schema sections. Meaningful sessions use
`model/sessions/YYYY-MM-DD-topic.md` with collision suffixes `-2`, and so on.
Store each original attempt once and link it; artifacts are optional when useful.
No profile/index files, typed-record/UUID graphs, overlays/tombstone engine,
numerical scores, automatic schedules, or domain taxonomy.

Bare continue/inspection is read-only: no session/evidence/artifact writes.
Only meaningful learning input, decisions, or results justify updates.
Configure/status do not read or create memory; path-only input asks the goal.
Correct directly with a concise note if useful; clarify ambiguous forget versus
stop-use versus explicitly scoped local deletion. Existing unknown models,
including prior evidence-first/advanced formats, need an explicit migration
decision. Archived advanced documentation is not an operational alternative.

Use the canonical contract and clarification gates, not invented record rules.
Preserve evidence attribution, no trait labels, and learner inspection/correction.
Skills are not an enforced storage backend.

## Hosted processing and dependencies

Ordinary task use permits bounded relevant reads into hosted Copilot/model
context without a new opt-in. Retrieve source/model context cheapest-first and
stop when enough is available; course-only lookup needs no learner records.
Never bulk-upload the model, read another learner's vault, add passive telemetry,
publish private records, or provide teacher/institutional access. Tool
permissions remain applicable. Do not promise local-only inference, hosted
retention/training/deletion/encryption behavior, or a complete network audit.
Local correction/deletion cannot erase already-sent hosted context.

Runtime dependencies remain only `course-content` and `learner-model`.
Both are pinned to `clew-skills` revision
`79c3aefa1817b2e3215df8f070815ef470b1ebdb`; restore the matching deployment.
Contributor/Obsidian tooling uses direct
original upstream pins, not a development package. Restore with **APM 0.28.0**
and `apm install --frozen`, keeping both `copilot` and `agent-skills` targets.
`--target copilot` alone silently skips hybrid skills. Preserve LF deployments,
lockfiles, notices, and the optional `red-markdown` extension; never hand-edit
generated skills. Test with synthetic notes, not real learner data.

Read the [ADR process](../docs/adr/README.md) before architectural work.
New records remain Proposed until explicit human lifecycle approval.
Do not rewrite accepted ADR-0001 to reflect the new proposed default.
