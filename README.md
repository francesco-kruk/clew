# clew

Clew is a student-facing Copilot workspace for learning from your own course
notes. Bring a portable notes-and-assets bundle, keep it in your local Obsidian
vault, and ask for explanations or practice grounded in that material. Personal
artifacts and genuine learning evidence support continuity across sessions;
having a file in the vault is not evidence that you understand it.

Every challenge is its own labyrinth. Clew takes its name from the ball of
thread that guided Theseus through the maze. The thread is not the hero: you
are. Clew helps you see a way forward; the choices, effort, and discoveries
remain yours.

## Repository roles

| Repository | Owns |
| --- | --- |
| [clew](https://github.com/francesco-kruk/clew) | Student setup, vault location, tutoring instructions, architecture documentation, optional Markdown canvas |
| [clew-skills](https://github.com/francesco-kruk/clew-skills) | Reusable course-reading and learner-model skills and their canonical contracts |
| [clew-content](https://github.com/francesco-kruk/clew-content) | Teacher authoring and `digest` conversion into portable notes/assets bundles |

This workspace does not convert PDFs or distribute courses. Obtain a bundle
from your teacher through their chosen handoff. This repository grants no
redistribution rights or guarantee that a particular teacher bundle is available.

## Student setup

Use **Python 3.11+**, Git, GitHub Copilot, and **APM 0.28.0**. The vault CLI uses
only Python's standard library and the Git executable to inspect private-tracking
metadata; no pip install or requirements file is needed. Obsidian is optional
for viewing notes.

**Availability:** this setup is part of
[PR #9](https://github.com/francesco-kruk/clew/pull/9), not yet merged into `main`.
To test it before merge, clone the repository and check out the PR head:

```powershell
git clone https://github.com/francesco-kruk/clew.git
Set-Location clew
git fetch origin pull/9/head
git switch --detach FETCH_HEAD
```

After PR #9 merges, a current default-branch clone can omit the last two commands.

1. Create your own external vault folder, outside the Clew clone.
2. Manually copy the **entire portable notes/assets bundle as-is** into a folder
   of your choosing within that vault. Keep its internal paths, names, links,
   and assets together. There is no required `courses` directory, hub, catalog,
   manifest, or schema migration.
3. From the Clew clone, restore the pinned skills and tell Clew the absolute
   path of the existing vault once:

```powershell
apm --version
apm install --frozen
python -m src.vault.cli configure --vault "C:\Users\Student\Documents\My Learning Vault"
python -m src.vault.cli status
```

Alternatively, start Copilot in the clone and simply tell it the absolute vault
path; the agent can run configure/status for you. The host's normal tool and
filesystem access permissions still apply—supplying a path does not bypass them.

`apm install --frozen` uses both manifest targets, `copilot` and `agent-skills`.
Both are required for hybrid skill packages. **Do not override with
`--target copilot` alone:** that silently skips first-party skill deployment.

`configure` requires an **absolute, existing external vault**. It does not create
the vault or any learner records. The clone's ignored `.clew.local.json` stores
`version: 1` and the canonical vault path, for example:

```json
{"version": 1, "vault": "C:\\Users\\Student\\Documents\\My Learning Vault"}
```

Both command outputs retain a stable `vault` JSON field. An explicit `configure`
with a valid supplied path can replace a malformed local setting; `status`
never repairs or updates configuration or ignore rules.

There is no home-directory fallback, and the clone is not a vault. Start Copilot
in the **Clew clone**; open the external vault in Obsidian if desired. Tell
Copilot which copied notes or topic you want to work on. It need not rename or
reorganize the bundle before reading it.

### What configuration does—and does not do

- `configure` and `status` do not read learner records or course-file contents.
  They retain Git index checks and warn about existing reserved root names
  `model` and `artifacts`, including files and case variants, without reading
  inside them or determining ownership.
- Only `configure` adds relevant `.gitignore` exclusions additively. `status`
  is read-only. Neither command initializes or pushes a vault Git repository.
  Already tracked private paths require attention; ignore rules neither
  untrack data nor encrypt it.
  If saving the local configuration later fails, the additive ignore update
  may remain; configure is not a transaction across those two files.
- A bundle might already use the names `model` or `artifacts`. Their presence
  does not prove they belong to Clew. The agent must ask before writing when
  ownership or the intended destination is uncertain.
- The setting locates the selected vault. It does not bypass tool permissions,
  authorize unrelated access, or turn an instructional agent into a sandbox
  or storage backend. There is no automatic backup or cross-device sync.

## Learning from your notes

Ask, for example: “Use the notes I copied into `Maths\Trigonometry` to explain
this example, then give me a similar problem.” The course-content skill reads
only relevant notes and linked context, cites the source, and reports ambiguity
or missing assets rather than silently repairing the bundle. It does not infer
domains or require a metadata migration.

Teacher notes are read-only unless you explicitly request a change. Explanations,
practice, and your working belong in `artifacts` once its destination is clear.
The learner-model skill can retain genuine evidence from the interaction:
goals, supplied work, observed errors, and confirmed preferences. Copying notes,
configuring a path, or generating practice is not evidence of learning.

The default **`evidence-first-v1`** profile (`schema_version: 1`) uses readable records with
`model/profile.md` identifying the profile and `model/index.md` supporting bounded
lookup. It does not assign numerical confidence/mastery scores or schedules.
Configure/status never read or create the profile marker. A path-only exchange
asks what you want to learn; the skill initializes records at the first genuine
intake, once ownership and intent are clear.
An existing unmarked model requires clarification, not automatic initialization,
conversion, or migration. The advanced profile remains separate; do not mix its
rules into the default. See the [canonical contract pointer](docs/LEARNER_MODEL.md).
Skills provide operating instructions, not an enforced learner-model backend.

## Local files, hosted Copilot

Learner records persist in the selected local vault. During ordinary student
tasks, bounded, task-relevant contents can enter **hosted GitHub Copilot/model
processing**. There is no additional per-workspace opt-in ritual; local storage
does not mean local-only inference or machine-boundary isolation.

Retrieve source material and learner context cheapest-first and stop when the
request has enough context. Course-only lookup does not need learner records.
Never bulk-upload the model, inspect another learner's vault, introduce passive
telemetry, publish learner records, or grant teachers/institutions access.
Keep evidence attributable, distinguish observed errors from unsupported
conclusions, avoid trait labels, and honor learner inspection and correction
under the selected profile.

Local correction, deletion, or tombstoning cannot erase context already sent
to a host. Clew makes no provider retention, training, deletion, or encryption
promises. Advanced-profile adaptation-decision records are not complete
network audits. Undefined operations remain clarification gates, not permission
to invent storage or statistical rules.

## Agent skills

[Microsoft APM](https://github.com/microsoft/apm) **0.28.0** restores the versions
recorded in `apm.yml` and `apm.lock.yaml` with `apm install --frozen`. Keep both
`copilot` and `agent-skills` targets and preserve the deployment's LF line endings.

The student runtime consists of **`course-content`** and **`learner-model`**.
Course-content v2 supports portable bounded reading; learner-model v2 supplies
the evidence-first default and a separate advanced profile. Both are pinned to
`clew-skills` revision `16f727da7bbffbb9f905eb9a9ac40fa6d12ca27f`.
Restore that matching pin before using these profiles; an older deployment is
not the redesigned contract. Student CLI availability remains subject to the
PR #9 checkout/merge guidance above.

Contributor and Obsidian tools are direct upstream dependencies at their
existing immutable pins, not a development package:

| Source | Tools |
| --- | --- |
| [Anthropic](https://github.com/anthropics/skills) | `skill-creator` |
| [GitHub Awesome Copilot](https://github.com/github/awesome-copilot) | `create-architectural-decision-record` |
| [Kepano's Obsidian skills](https://github.com/kepano/obsidian-skills) | `defuddle`, `obsidian-bases`, `json-canvas`, `obsidian-markdown`, optional-use `obsidian-cli` |

Obsidian CLI use requires the appropriate local application/tool; it is not
required to configure a vault or read Markdown. Contributor tools do not
authorize access to learner data.

`.agents/skills/` contains generated deployments, not another source of truth.
Change first-party sources in `clew-skills`, then regenerate deployments and
lockfiles with APM. Do not hand-edit generated skills or invent lock hashes.
Preserve upstream pins, `THIRD_PARTY_NOTICES.txt`, and bundled licenses.
`apm_modules/` is an ignored cache. Software licenses do not license textbooks.

## Markdown canvas

The optional [Red-bordered Markdown extension](.github/extensions/red-markdown/README.md)
previews local Markdown files with equations and images in a canvas-capable
Copilot host. Its code lives in `.github/extensions/red-markdown/`; restore its
npm dependencies and reload extensions as described in its installation guide.
It is not required for student setup.

## Architecture decisions

[Architecture Decision Records](docs/adr/README.md) explain the rationale and
trade-offs. ADR-0002/0003 remain Proposed and are revised for the student-only
workflow. Proposed ADR-0004 describes portable bounded reading and its intended
replacement of ADR-0001's default; Proposed ADR-0005 describes evidence-first
continuity. ADR-0001 remains Accepted and unchanged pending an explicit human
lifecycle decision. Implementation approval does not imply ADR acceptance.
Use the [ADR template](docs/adr/template.md) and preserve historical records.
