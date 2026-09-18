# Working in Clew

Before architectural changes, read the [ADR process and index](docs/adr/README.md),
applicable records, and relevant specifications such as the
[learner model](docs/LEARNER_MODEL.md).

## Student workspace and selected vault

This clone contains tools and instructions, not the learner vault. Resolve the
external vault from an explicit task/CLI `--vault` or the ignored
`.clew.local.json` configuration. Configure it with
`python -m src.courses.cli configure --vault "C:\Path\To\Vault"`.
Do not guess a home-directory vault or use the clone. Work only within the
selected learner/task scope; do not search unrelated vaults.

Use `course-content` for hub-first, bounded, read-only course lookup. Preserve
`courses\<course>\hub.md` and complete chapter files; cite source sections.
Personal work and adaptations belong in external-vault `artifacts`, not the
authoritative course snapshot. Import with `python -m src.courses.cli`, using the
default `francesco-kruk/clew-content` source, explicit `--ref main`, or a selected
`--source-checkout`. See [student setup](README.md#student-setup).

Identical intact imports are no-ops. New revisions remain staged at
`.clew\staging\<id>\<commit>-<hash>\courses\<course>`, preserving the course prefix.
There is no activation command; never activate updates automatically.
Dirty or unrecognized destinations are conflicts;
do not overwrite them. The importer must never inspect or modify `model` or
personal `artifacts`, or manufacture learner records from installation.
Never initialize or push vault Git. Ignore rules are not encryption and do not
untrack private data; stop if relevant private paths are already tracked.

## Hosted learner-model use

Learner files persist locally, but ordinary student tasks permit bounded,
task-relevant reads into hosted GitHub Copilot/model context. Do not invent
another per-workspace opt-in requirement or claim local-only inference.
Use the installed `learner-model` specification and clarification gates,
retrieving cheapest-first and stopping once the request has enough context.
Course-only reading needs no learner data. Never bulk-upload the model, read
another learner's records, introduce passive telemetry, publish private records,
or provide teacher/institutional access.

Preserve domain indexing, provenance, independent confidence and efficacy,
scheduling, no-trait-label rules, learner inspection/correction, stable IDs,
and append-only/tombstone safeguards. Undefined inference, tombstone, storage,
and transaction semantics still block affected writes; do not invent rules.
Adaptation decisions retain traceability, but `sent_over_boundary` describes
that object, not all transmitted context or a network audit. Tombstoning does
not erase context already sent to a host. Make no provider retention, training,
deletion, or encryption promises. Skills are instructions, not an enforced
storage engine.

Follow [the contract pointer](docs/LEARNER_MODEL.md) and stop learner-model operations
if the required specification is absent or the deployed guidance still assumes
local-only processing. Do not patch generated skills to bridge that gap.

## Teacher/PDF handoff is optional

Authoritative skill sources live in `clew-skills`; course authoring/publication
belongs in `clew-content`. Do not globally route PDF tasks through one engine:

- `digest` (formerly `brute-force-pdf-to-obsidian`) is the source-faithful,
  page-by-page recovery workflow, with verified editable content and standalone
  non-course support.
- Alexandra's `content-ingest` is the image-first alternative. When explicitly
  selected, use its bundled engine, not ad-hoc raw text extraction. The legacy
  `python -m src.ingest.cli` wrapper delegates to the APM-restored engine.
  Install optional PDF dependencies from
  `.agents\skills\content-ingest\requirements.txt`, not the student dependency
  set. Output is chapter Markdown and formula/exercise/diagram images, not a
  promise of editable math, Mermaid diagrams, or interactive callouts.

Neither extraction output nor structural validation establishes fidelity or
redistribution rights. Before publication, assemble and validate the shared
hub/chapter package, preserve attribution/answers/caveats, and document rights.
The migrated Trigonometry catalog remains unpublished pending rights evidence.
Do not bypass this gate; use original synthetic packages for integration tests.
Publish immutable skill sources first, then pin/restore consumers, then publish
validated courses after rights clearance. Do not auto-push content.

## Architecture & Skills

For significant architectural decisions, use the APM-managed
[create-architectural-decision-record skill](.agents/skills/create-architectural-decision-record/SKILL.md)
and [ADR template](docs/adr/template.md). Ask for missing context, options,
rationale, or stakeholders rather than inventing them. New records start
Proposed; acceptance and other lifecycle changes require explicit human approval.
Acceptance is not authorization to implement. Keep the index and supersession
links consistent, and preserve historical records.

Do not edit generated files under `.agents/skills/`. Manage dependency changes
through `apm.yml` and **APM 0.28.0**, preserving immutable pins, the regenerated
lockfile/deployments, and license notices. Do not hand-author lock hashes.
Restore with `apm install --frozen`, retaining both manifest targets `copilot`
and `agent-skills`. Do not pass `--target copilot` alone: it silently skips the
hybrid first-party packages. The root pins all four skills (`course-content`,
`learner-model`, `content-ingest`, `digest`) and `packages/development` to
`5ed0f288a6c5c0c0f891939385ddf38fa5b32504` in `clew-skills`.
The development package supplies skill-creator, ADR, Defuddle, and Bases tooling
at their original upstream pins.
Keep Clew-specific guidance outside generated skills and preserve the optional
`.github/extensions/red-markdown` extension. Test with synthetic original
material and disposable external test vaults, never real learner records.
