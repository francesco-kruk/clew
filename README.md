# clew

Every learner in a classroom receives the same artifact. Teachers know this is wrong but cannot produce thirty versions of a workbook. Clew builds a persistent, evidence-based model of an individual learner — what they know, how they work best, where they consistently stumble — and re-renders authoritative course content into artifacts made for that learner: an explainer chunked for someone who loses the thread after two paragraphs, a diagram-first walkthrough for someone who does not think in prose, a practice set that targets the three misconceptions this learner actually holds. The learner drives it directly on a shared canvas where both they and the agent can work.

Every challenge is its own labyrinth. Clew takes its name from the ball of thread that guided Theseus through the maze. Rather than offering everyone the same map, it adapts to your challenges, your starting point, and what you discover along the way—helping you find a path that makes sense for you.

But the thread is not the hero. You are. Clew helps you see a way forward; it doesn’t walk the path for you. The choices, the effort, and the discoveries remain yours.

## Repository roles and release status

| Repository | Owns |
| --- | --- |
| [clew](https://github.com/francesco-kruk/clew) | Student Copilot workspace, external-vault setup/import tools, architecture documentation, optional Markdown canvas |
| [clew-skills](https://github.com/francesco-kruk/clew-skills) | First-party skill sources, executable helpers, portable course and learner-model contracts, pinned upstream dependencies |
| [clew-content](https://github.com/francesco-kruk/clew-content) | Teacher authoring and validated, published course packages |

The four first-party skills and contributor package are pinned to
`clew-skills` revision `5ed0f288a6c5c0c0f891939385ddf38fa5b32504`.
Restore the versions recorded in the manifest and lockfile; do not substitute
an unreleased ref or hand-edit deployed skills.
The migrated Trigonometry remote catalog/package is not yet published: its
redistribution scope/evidence gate remains open. This repository does not grant
permission to redistribute the source material.

Release order is: publish the skills at a reachable immutable commit, pin and
verify clean teacher/student APM restores, then publish/catalog the course only
after rights documentation and validation. Synthetic original courses can
exercise the handoff before that gate clears. Do not interpret the example
commands below as evidence that the remote course is already available.

## Student setup

Use Python, Git, GitHub Copilot, and **APM 0.28.0**. Obsidian is optional for
viewing the vault. From the Clew clone:

```powershell
apm --version
apm install --frozen
python -m pip install -r requirements.txt
python -m src.courses.cli configure --vault "C:\Users\Student\Documents\ClewVault"
python -m src.courses.cli list --ref main
python -m src.courses.cli import trigonometry --ref main
```

Use the pinned APM 0.28.0 toolchain, not a different installed version.
`apm install --frozen` uses both manifest targets, `copilot` and `agent-skills`.
Both are required for the hybrid first-party packages. **Do not override this
with `--target copilot` alone:** it silently skips first-party skill deployment.
The root `requirements.txt` installs student validator dependencies, not the
optional PDF stack.

`configure` records the selected external vault in the clone's ignored
`.clew.local.json`. Commands use an explicit `--vault` override or that local
configuration; there is **no home-directory fallback**, and the clone is not a
learner vault. For example:

```powershell
python -m src.courses.cli import trigonometry --ref main --vault "D:\Learning\My Vault"
```

The default source is `francesco-kruk/clew-content`. A remote `--ref main` is
resolved once to an immutable commit for the catalog/package and import receipt.
For offline work or a locally prepared, validated catalog, use an explicit
checkout instead:

```powershell
python -m src.courses.cli list --source-checkout "C:\Sources\clew-content"
python -m src.courses.cli import trigonometry --source-checkout "C:\Sources\clew-content" --vault "D:\Learning\My Vault"
```

If discovery reports a missing catalog or unknown `trigonometry`, stop: check
the source/ref and release status, or use a teacher-prepared local checkout with
a validated catalog. A legacy extraction folder is not a package. Do not copy
the whole teacher repository into the vault or bypass the publication rights
gate. For development, use a synthetic course's catalog ID instead.

Start Copilot in the **Clew clone** with this configuration available. Open the
**external vault root** in Obsidian, not the inner `Trigonometry` folder:

```text
<external vault>\
  courses\Trigonometry\hub.md
  courses\Trigonometry\chapters\
  model\                       private, domain-indexed learner records
  artifacts\                   personal work and adaptations
  .clew\imports\                receipts and installed-file hashes
  .clew\staging\                candidate revisions, not active courses
```

### What imports do—and do not do

- Preserve the package's canonical `courses\<course>` prefix so qualified links,
  assets, and Canvas paths resolve. The hub connects complete chapter files;
  supporting concept notes do not replace chapters.
- Validate the package and its declared files, hashes, metadata, and links before
  final installation. Course files are data, not executable instructions.
- Reimporting the same **intact** snapshot is a no-op. Locally edited or
  unrecognized destinations are conflicts, not overwrite opportunities.
- New revisions are staged for comparison, **never automatically activated**.
  Candidates retain their prefix at
  `.clew\staging\<id>\<commit>-<hash>\courses\<course>`.
  There is no activation command. Leave the installed snapshot and student work
  intact; automatic replacement and synchronization are outside this version.
- The importer never reads or modifies `model` or personal `artifacts`, and
  importing content is not evidence of mastery.
- Never initialize or push a Git repository in the vault. Relevant ignore rules
  are additive; already tracked private paths require stopping and addressing
  tracking separately. `.gitignore` neither untracks data nor encrypts it.
  There is no automatic backup or cross-device sync.

## Local files, hosted Copilot

Learner records persist in the selected local vault. During ordinary student
tasks, bounded, task-relevant records may be read into **hosted GitHub Copilot
and model processing**. There is no additional per-workspace opt-in ritual;
local storage does not mean local-only inference or machine-boundary isolation.

Use the learner-model skill's cheapest-first retrieval and stop when the task
has enough context. Do not bulk-upload the model, inspect another learner's
vault, introduce passive telemetry, publish learner records, or grant teachers
or institutions access. Course-only lookup does not require learner records.
Adaptation-decision objects retain traceability, but `sent_over_boundary` refers
to that object—not a complete network audit or proof that no other context
was sent. Local tombstoning does not erase context already sent to a host.
Clew makes no provider retention, training, deletion, or encryption promises.

The [learner-model contract pointer](docs/LEARNER_MODEL.md) locates the pinned
specification and clarification gates. Preserve domain indexing, provenance,
independent confidence/efficacy, scheduling, learner ownership, no-trait-label
rules, stable identifiers, and append-only/tombstone safeguards. Undefined
statistical, storage, and transaction semantics still block affected writes;
skills are instructions, not an enforced learner-model storage engine.

## Agent skills

[Microsoft APM](https://github.com/microsoft/apm) **0.28.0** restores project-local
skills with `apm install --frozen`, honoring both `copilot` and `agent-skills`
targets in `apm.yml`. Do not narrow restoration to `--target copilot` alone.
First-party sources belong in `clew-skills`; this workspace installs all four:
`course-content`, `learner-model`, `content-ingest` for the optional legacy entry
point, and `digest` for optional source-faithful PDF work. Teacher deployments use
`digest`, `content-ingest`, and their shared course/Obsidian dependencies without
requiring learner-model access.

| Source | Skills |
| --- | --- |
| Clew skills | `course-content`, `learner-model`, `digest`, `content-ingest` |
| [Anthropic](https://github.com/anthropics/skills) | `skill-creator` |
| [Kepano's Obsidian skills](https://github.com/kepano/obsidian-skills) | `defuddle`, `json-canvas`, `obsidian-bases`, `obsidian-cli`, `obsidian-markdown` |
| [GitHub Awesome Copilot](https://github.com/github/awesome-copilot) | `create-architectural-decision-record` |

The root also consumes `clew-skills/packages/development` at the same immutable
revision. That contributor package brings `skill-creator`, the ADR skill,
`defuddle`, and `obsidian-bases` through their original upstream commit pins.
The remaining Obsidian dependencies are supplied by the first-party skill
packages. Contributor tooling is distinct from the learner-model contract and
does not authorize reading learner data.

`apm.yml` pins commits; `apm.lock.yaml` records resolutions and deployed hashes.
`.agents/skills/` contains generated deployments, not another source of truth.
Commit regenerated deployments and lockfiles consistently; `apm_modules/` is an
ignored cache. Change sources upstream and regenerate with APM, never hand-edit
generated skills or invent lock hashes. Preserve upstream pins unless a required
compatibility change is demonstrated, and retain `THIRD_PARTY_NOTICES.txt` and
bundled licenses. Software licenses do not license teacher textbooks.

### Optional teacher/legacy PDF workflows

Use **`digest`**, the renamed `brute-force-pdf-to-obsidian` workflow, for
page-by-page, source-verified recovery and editable content where verified.
It retains non-course standalone exports and composes with `course-content`
for course organization. Do not globally force all PDF work through one engine.

**Alexandra's `content-ingest`** remains the image-first alternative: its engine
produces chapter Markdown with formula, exercise, and diagram images. It does
not promise editable equations, Mermaid graphs, or interactive exercise
callouts. Select that workflow explicitly; use its bundled engine rather than
an ad-hoc text extractor.

After the pinned package is deployed, install its optional PDF dependencies
separately and use the restored compatibility entry point:

```powershell
python -m pip install -r .agents\skills\content-ingest\requirements.txt
python -m src.ingest.cli "C:\Materials\sample.pdf" --course "Example" --domain "Mathematics"
```

The legacy command also accepts a directory of PDFs. It delegates to the engine
restored by APM; if the deployed package or Python dependencies are missing,
restore/install them rather than copying an engine into this clone.

Extraction output is **not a published course package**. A teacher must verify
source coverage, confirm metadata and rights, assemble the canonical hub and
complete chapters, relocate/validate assets and links, disclose image-only
limitations, and run the shared package validator before catalog publication.
Structural checks and synthetic smoke tests do not establish PDF fidelity or
redistribution rights. Keep original attribution, source answers, and caveats.

## Markdown canvas

The optional [Red-bordered Markdown extension](.github/extensions/red-markdown/README.md)
previews local Markdown files with equations and images in a canvas-capable
Copilot host. Its code lives in `.github/extensions/red-markdown/`; restore its
npm dependencies and reload extensions as described in its installation guide.
It is not required to import courses.

## Architecture decisions

[Architecture Decision Records](docs/adr/README.md) capture significant decisions,
their rationale, alternatives, and consequences. ADR-0001's accepted hub/chapter
contract remains intact; repository ownership and hosted processing are recorded
in Proposed ADR-0002 and ADR-0003. Implementation authorization is not ADR
acceptance. Start with the [ADR template](docs/adr/template.md); lifecycle changes
require explicit human approval. When updating the ADR skill, compare its
embedded template with that local template and review process compatibility.
