# Clew student workspace

Follow [AGENTS.md](../AGENTS.md) and the [student setup](../README.md#student-setup).
This repository is the student-facing Copilot workspace, not a global Content
Ingestion Agent and not the learner vault.

## Locate only the selected external vault

- Resolve an explicit `--vault` or ignored `.clew.local.json`; configure with
  `python -m src.courses.cli configure --vault "C:\Path\To\Vault"`.
  Never guess a home-directory location or use the clone as the vault.
- Use `course-content` to read the hub and only relevant chapter sections.
  Preserve the canonical `courses\<course>` prefix, source citations, and
  read-only snapshots. Put personal work in external-vault `artifacts`.
- Use `python -m src.courses.cli list --ref main` and
  `python -m src.courses.cli import trigonometry --ref main` for the default
  `francesco-kruk/clew-content` source; `--source-checkout` selects a local
  prepared catalog. `--vault` overrides configured destination selection.
  The migrated remote catalog remains unavailable pending rights documentation;
  report that clearly rather than copying a legacy bundle or bypassing checks.
- Intact identical imports are no-ops; new revisions are staged, not activated.
  Candidates preserve their course prefix at
  `.clew\staging\<id>\<commit>-<hash>\courses\<course>`; no activation command exists.
  Dirty/unrecognized destinations are conflicts. Imports never inspect or
  change `model` or personal `artifacts` and never generate mastery records.
- Never initialize or push a vault Git repository. `.gitignore` is neither
  encryption nor untracking; already tracked private paths require a stop and
  actionable guidance, not a claim that the data is now private.

## Local storage does not mean local inference

Ordinary student tasks permit bounded task-relevant learner-model reads into
hosted GitHub Copilot/model processing, without a new per-workspace opt-in.
Load `learner-model` and its specification/clarification gates, retrieve
cheapest-first, and stop when enough context is available. Never bulk-upload
the model, access another learner's vault, add passive telemetry, publish
private records, or grant teacher/institutional access. Course-only lookup
does not require model access.

Preserve domain indexing, no trait labels, provenance, independent confidence
and efficacy, scheduling, learner ownership, stable IDs, and append-only/
tombstone safeguards. Stop affected writes when statistical, tombstone, storage,
or transaction rules are undefined. Skills do not implement an enforced model
engine. `sent_over_boundary` concerns the adaptation-decision object, not a
complete network audit. Local tombstoning cannot erase already-sent hosted
context; do not promise provider retention, training, deletion, or encryption.

The [contract pointer](../docs/LEARNER_MODEL.md) identifies the pinned
package specification. Missing specification or old local-only deployed guidance
must be resolved by restoring the released package before learner-model work,
not by inventing rules or editing generated skill files.

## Optional teacher workflows and repository maintenance

First-party skills are sourced in `clew-skills`; teacher packages are authored
in `clew-content`. Select `digest` (formerly `brute-force-pdf-to-obsidian`) for
source-verified, page-by-page recovery or Alexandra's image-first `content-ingest`.
Do not force all PDF tasks through the latter. When it is explicitly selected,
use its bundled engine through the restored `python -m src.ingest.cli` wrapper,
not ad-hoc raw extraction. Its chapter Markdown embeds formula/exercise/diagram
images; do not promise editable equations, Mermaid graphs, or exercise callouts.
PDF dependencies are optional and installed from the deployed
`.agents\skills\content-ingest\requirements.txt`, separate from student imports.

Extraction is not publication: assemble the shared hub/chapter contract,
validate assets/links, verify fidelity separately, preserve attribution and
source caveats, and satisfy the rights gate. Release immutable skills first,
pin and restore consumers, then publish validated courses with documented
rights. Use synthetic original material for tests, never real learner records.

Use **APM 0.28.0** with pinned dependencies and regenerated lockfiles/deployments.
Run `apm install --frozen` with both manifest targets, `copilot` and
`agent-skills`. Never override with `--target copilot` alone: hybrid first-party
skills would be silently skipped. The root installs `course-content`,
`learner-model`, `content-ingest`, `digest`, and `packages/development` from
`clew-skills` revision `5ed0f288a6c5c0c0f891939385ddf38fa5b32504`.
The development package retains the original upstream pins for skill-creator,
ADR, Defuddle, and Bases tooling.
Do not edit `.agents/skills/` by hand or discard license notices. Preserve the
optional `.github/extensions/red-markdown` extension. Read the
[ADR process](../docs/adr/README.md) before architecture changes; new records
start Proposed and require explicit human approval for lifecycle changes.
