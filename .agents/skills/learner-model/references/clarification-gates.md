# Evidence-first-v1 clarification gates

Use [the default specification](learner-model-spec.md). Only an affected operation
is blocked, not unrelated read-only course lookup. The old full model's
[advanced gates](advanced-clarification-gates.md) apply only to advanced-v1;
missing posteriors, schedules or seven-dimensional decisions do not block a
real goal/attempt in this profile.

| Situation | Required behavior |
| --- | --- |
| Unknown vault or ambiguous selected note | Ask for the explicit root/target; never infer the clone is a vault or scan everything. |
| Vault path only, no learning input | Ask the goal; no marker, session or fabricated observation yet. |
| Genuine goal or attempted work with no mappings | Record the actual input, session and evidence; `mapping_refs: []` is valid. |
| Existing unmarked/advanced/unknown-version model, reserved-dir collision | Ask about ownership/profile and explicit migration choice. No automatic adoption, schema coercion or overwrite. |
| Malformed record, missing support, duplicate IDs, index disagreement | Report the specific problem, stop affected writes and ask for recovery. Preserve data/history. |
| Ambiguous domain/concept identity | Retain unresolved literal evidence. Ask before a dependent lookup, binding, merge or cross-course reuse; labels alone do not establish identity. |
| Unchecked answer or unclear source | Record supplied work as an observation; do not assert a factual mistake or diagnose a misconception without grounding. |
| Current presentation request only | Apply for this task if appropriate; do not persist a standing preference, infer its scope, or claim efficacy. |
| Missing adaptation | `adaptation: none` is valid; no scored decision schema needed. |
| Concurrent modification or partial write | Stop and report exact changes already persisted; re-read and reconcile, no overwrite or rollback claim. |
| Correction | Use documented append-only change with exact replacement and any superseded overlay IDs; no history rewrite. |
| Forgetting/shared evidence | Explain and confirm target-scoped logical suppression; preserve contributions to unrelated records. |
| Physical erasure, hosted deletion or an unspecified deletion rule | Stop for separate explicit handling. Do not act or claim erasure; a tombstone is not physical or provider deletion. |

No gate allows whole-vault upload, unrelated record collection, teacher access,
invented performance, scoring or automatic scheduling. Ordinary bounded hosted
processing is disclosed, not blocked behind an extra consent screen.
