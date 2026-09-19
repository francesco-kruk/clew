# Working in Clew

Read the [ADR process and index](docs/adr/README.md), applicable records, and
[learner-model contract pointer](docs/LEARNER_MODEL.md) before architectural
changes. This is a **student-only** Copilot workspace. Teacher conversion with
`digest` belongs in `clew-content`; do not introduce conversion or distribution
workflows here.

## Locate the selected vault

The student creates an external vault and manually copies an entire portable
notes/assets bundle into any chosen folder, as-is. There is no required
`courses` prefix, hub, catalog, manifest, or schema migration.

Once the student supplies the absolute path of an existing external vault, use:

```powershell
python -m src.vault.cli configure --vault "C:\Path\To\Existing Vault"
python -m src.vault.cli status
```

The ignored `.clew.local.json` stores `version: 1` and the canonical `vault`
path. Do not guess a home-directory location, create a vault, or use the clone.
Path configuration creates no model records and establishes no learning facts.
It is a location setting, not a permission bypass or sandbox.
The CLI requires Python 3.11+ (standard library only) and the Git executable;
no pip installation or requirements file is needed. Command JSON uses the stable
`vault` field. Explicit configure with a valid supplied path can replace a
malformed setting; status never repairs configuration or ignore rules.

Both commands avoid reading learner/course-file contents. They check the Git
index and report presence of reserved `model`/`artifacts` paths, not ownership.
Warn even when those root names are files or case variants, without reading
inside them; ownership is a skill-level clarification, not a tool finding.
Only configure adds relevant ignore rules additively; status is read-only.
Never initialize or push vault Git. Ignore rules do not untrack or encrypt;
stop and give actionable guidance for already tracked private paths.

Reserved names can collide with copied notes. Ask before writing if ownership,
format, or destination is uncertain. Never infer that an existing `model` or
`artifacts` directory belongs to Clew from its name or a status report.

## Read, tutor, and retain genuine evidence

Use `course-content` v2 for bounded reading of the selected portable notes.
Follow only relevant links and cite exact source locations. Stop at ambiguity
or missing context; do not automatically rename, migrate, reorganize, or infer
domains. Teacher notes are read-only except for an explicit user request.

Create tutoring artifacts in the agreed `artifacts` destination. Use
`learner-model` 3.0.0 for continuity grounded in actual goals, supplied work,
observed errors, and confirmed preferences—not the presence of course files
or an explanation the agent generated.

Keep one compact `model/learner.md` summary with exactly one
`<!-- clew-learning-memory: v1 -->` marker and dated ordinary source/evidence
links. Goals, Confirmed preferences, and Learning notes are recommended optional
headings, not mandatory schema sections. Meaningful dated sessions
use `model/sessions/YYYY-MM-DD-topic.md`, with `-2` and subsequent suffixes for
collisions. Store original attempts once and link them; artifacts are optional
when useful. Do not create profile/index files, typed objects, UUID/evidence-ID
graphs, overlays, tombstone machinery, scores, schedules, or domain taxonomy.

Bare continue and inspection are read-only: no session/evidence/artifact writes.
Only meaningful learning input, decisions, or results justify memory updates.
Configure/status never read or create memory; a path-only exchange asks the
learner's goal. Apply corrections directly, noting them concisely if useful.
Clarify ambiguous forget, stop-use, or explicitly scoped local deletion requests.
Unknown existing models, including earlier evidence-first and advanced records,
require an explicit migration decision. The advanced material is archived
outside the installed package, not a supported runtime alternative.

Preserve attributable evidence, no trait labels, and learner ownership. Stop
writes when ownership or contract semantics are unclear. Skills are not a
storage backend or sandbox. Both runtime skills are pinned to `clew-skills`
revision `9c8fb3b3754716c4cbf7c961c4a5f269cd003c15`; restore the matching package
rather than editing generated files to simulate it.
Until PR #9 merges, use its checkout as described
in [student setup](README.md#student-setup), not an older `main` checkout.

## Hosted Copilot

Ordinary student tasks permit bounded task-relevant reads into hosted Copilot/
model context without a new opt-in ritual. Retrieve both source and model
context cheapest-first and stop when enough is available. Course-only lookup
does not require learner records. Never bulk-upload the model, read unrelated
vaults, introduce passive telemetry, publish private records, or grant teacher/
institutional access. Normal tool permissions still apply.

Local storage does not imply local-only inference. Local corrections or
deletions do not erase previously sent hosted context. Make no provider
retention, training, deletion, or encryption promises or claims of complete
network auditing.

## Architecture and dependencies

Use the APM-managed
[ADR skill](.agents/skills/create-architectural-decision-record/SKILL.md) and
[template](docs/adr/template.md). New records start Proposed; lifecycle changes
require explicit human approval. Do not infer others' agreement. Keep index
and relationship links consistent. ADR-0001 remains unchanged; Proposed
ADR-0004 is an intended replacement default, not an accepted supersession.

Runtime skills are only `course-content` and `learner-model`. Skill-creator,
ADR, Defuddle, Bases, and Obsidian Canvas/Markdown/optional CLI are direct
upstream dependencies at existing pins, not a development package.
Use **APM 0.28.0** and `apm install --frozen` with both manifest targets
`copilot` and `agent-skills`. Never narrow to `--target copilot` alone, which
silently skips hybrid skills. Preserve LF deployment line endings, immutable
pins, regenerated lockfiles, and license notices. Do not hand-edit generated
`.agents/skills` or lock hashes.

Keep the optional `.github/extensions/red-markdown` extension unchanged.
Use synthetic original notes and disposable test vaults, never real learner
records, to test configuration and behavioral scenarios.
