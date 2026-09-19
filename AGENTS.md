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
profile, or destination is uncertain. Never infer that an existing `model` or
`artifacts` directory belongs to Clew from its name or a status report.

## Read, tutor, and retain genuine evidence

Use `course-content` v2 for bounded reading of the selected portable notes.
Follow only relevant links and cite exact source locations. Stop at ambiguity
or missing context; do not automatically rename, migrate, reorganize, or infer
domains. Teacher notes are read-only except for an explicit user request.

Create tutoring artifacts in the agreed `artifacts` destination. Use
`learner-model` v2 for continuity grounded in actual goals, supplied work,
observed errors, and confirmed preferences—not the presence of course files
or an explanation the agent generated.

The default profile is `evidence-first-v1`. Its `model/profile.md` marker and
`model/index.md` guide bounded access to readable records. It does not introduce
numerical confidence/mastery scores or schedules. Consult the installed
specification for exact record semantics; do not invent fields or algorithms.
Its schema version is 1. Configure/status must not read or create the marker.
For a path-only exchange, ask the learner's goal rather than initializing records.
The skill initializes at the first genuine intake once ownership and intent
are clear.
An existing unmarked model requires asking, not migration or replacement.
Keep the separate `advanced-v1` profile's rules and unresolved gates separate;
do not apply advanced numerical/scheduling rules to default records.

Preserve provenance, no-trait-label rules, learner ownership, and the selected
profile's correction/history safeguards. Stop affected writes when the contract
is missing or unclear. An agent skill is not a storage backend or enforcement
sandbox. The new immutable package pin is pending; do not edit generated files
to simulate a matching deployment.

## Hosted Copilot

Ordinary student tasks permit bounded task-relevant reads into hosted Copilot/
model context without a new opt-in ritual. Retrieve both source and model
context cheapest-first and stop when enough is available. Course-only lookup
does not require learner records. Never bulk-upload the model, read unrelated
vaults, introduce passive telemetry, publish private records, or grant teacher/
institutional access. Normal tool permissions still apply.

Local storage does not imply local-only inference. Local corrections or
tombstones do not erase previously sent hosted context. Make no provider
retention, training, deletion, or encryption promises. Advanced adaptation
objects and `sent_over_boundary` do not constitute complete network audits.

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
