# Obsidian note quiz

Project-local companion to the [canvas-quiz skill](../../skills/canvas-quiz/SKILL.md).
Ask "Quiz me on this note" while an Obsidian Markdown reader is active.
The agent reads the live document action, composes exactly three grounded
written-answer questions, and opens a separate quiz canvas.

## Setup and use

This extension uses Node built-ins and the host-provided Copilot SDK; no npm
installation is needed. Reload extensions after installation. If a running
agent has not discovered the new skill, start a new session.

Answer all three fields and select **Submit and save answers**. The button
saves one Markdown note to `Quizzes/quiz-<quizId>.md` inside the source vault
and appends a linked `supplied-work` observation to
`model/provenance/<year>/<month>.jsonl` in that same vault. It then reveals
suggested answers. Responses are ungraded: no concepts, misconceptions,
preferences, goals, or review schedules are updated. Recording uses local
filesystem code, not an AI evaluator. Submitted answers are never sent to
the agent. `get_status` exposes metadata, not answers or ledger content.

The note includes exact responses, three prompts, concepts, source excerpts,
suggested answers, a source link/hash, and a timestamp. A final JSON block in
the same Markdown note supports exact round trips and reopening; leave it
intact. New attempts get new IDs. Repeated identical submissions are idempotent;
existing attempts are never overwritten. Do not commit these private records
or upload them to an external service.

The ledger contains one observation per quiz with ID `obs-quiz-<quizId>`,
the original submission timestamp, and an artifact link to the exact answers.
It records submission only; answers remain in the quiz note rather than being
duplicated in JSONL. Unknown session and canonical concept/item fields are
`null`; `informs` is empty. Tier 1 identifies this unassessed intake.
See [the intake contract](../../../docs/LEARNER_MODEL.md#361-basic-quiz-intake).

The quiz note is saved first. If the ledger append fails, the form reports
partial completion and offers **Retry learner-model recording**. A retry uses
the original ID and UTC submission month, does not overwrite the quiz, and
does not append a duplicate observation. Metadata distinguishes `recorded`,
`pending`, `error`, and legacy `not-requested`; `submitted` alone only
confirms the quiz file.

Local writers serialize through a per-vault queue and an exclusive
`model/provenance/.quiz-evidence.lock` file. Other writers must cooperate with
this lock. Crashes may leave a lock requiring manual investigation; it is
never removed automatically as stale. Invalid JSONL, conflicting IDs,
redirected directories, and hard-linked ledgers block recording without
rewriting existing history. Partial filesystem writes are not rolled back.

The vault root is discovered from the canonical source path's nearest
`.obsidian` ancestor. For exports or vaults with a custom configuration folder,
the agent asks for an explicit root. No vault, source, or machine-specific
absolute path is embedded in the extension or skill.

## Limitations and recovery

- Draft answers remain in the form only. Closing/reloading the panel or
  restarting the provider can lose unsaved drafts; the UI warns on navigation
  where the host supports it.
- Math is preserved as source text, not rendered LaTeX.
- The extension requires a local writable filesystem supporting hard links
  for atomic, no-overwrite publication. On an unsupported filesystem or a
  permission/sync failure, the form shows an error and retains its answers.
- `Quizzes` and attempt files cannot be redirected through symlinks or junctions.
- Previously saved version-1 attempts are not backfilled, even when reopened.
  New version-2 submissions record evidence. Reading status never appends it.
- Reopen a completed attempt using its original `quizId`, source, topic, and
  questions. A changed definition or a corrupted record produces an explicit
  error rather than silently replacing prior answers. Source excerpts must
  still exist in the current note.
- The source reader must expose its absolute Markdown path and content through
  a document action. For `red-markdown`, use `get_document`; never infer a file
  path from its localhost URL.

## Validation

From the repository root:

```powershell
node --test .github\extensions\vault-quiz\quiz.test.mjs
```

Tests use temporary synthetic vaults, never a learner's real notes. They cover
the provenance schema, append-only preservation, idempotent and concurrent
retries, partial saves, legacy attempts, private error redaction, and path guards.
The server binds only to `127.0.0.1` with random capability paths, validates
Host/Origin and a per-instance submission token, bounds request size, and
does not load remote assets. Learner input is rendered using DOM text values.
