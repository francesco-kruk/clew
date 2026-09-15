# Matrix multiplication learning map

A portable textbook and concept graph: 14 lessons, four categories, 15 map
connections, 14 checkpoints, and 12 additional matrix presets. The data is
independent of Copilot, browser sessions, and any particular renderer.

## Files

| File | Purpose |
| --- | --- |
| `map.json` | Entry point: graph, category context, reading order, examples, presets, checkpoints, and optional presentation hints |
| `map.schema.json` | JSON Schema Draft 2020-12 for version 1 of the format |
| `lessons/*.md` | Explanations, mathematical rules, and readable worked examples |
| `CONSUMING.md` | Contract for skills and other tools reading the map |
| `validate.mjs` | Schema, reference, content, graph, and matrix-product validation |
| `validate.test.mjs` | Regression and invalid-input cases |
| `package.json`, `package-lock.json` | Reproducible Node.js validation dependencies |

Start with `map.json` and its `startNode`. The four categories are **The rule**,
**Building the product**, **Special matrices**, and **Connections**.

## Validate

The JSON and Markdown can be read without installing anything. Running the
validator requires Node.js 20 or later. From this folder:

```sh
npm ci
npm run validate
npm test
```

In Windows PowerShell, use `npm.cmd` instead of `npm` if execution policy blocks
the `npm.ps1` shim. No dependency is needed by a data-only consumer.

Validation checks the schema, unique IDs, category membership, reading order,
edge endpoints, graph reachability, prerequisite cycles, local lesson paths,
lesson titles, rectangular matrices, products, and single-choice answer
membership. It does not prove arbitrary lesson prose or newly authored quiz
answers mathematically correct; those require content review.

## Semantics

Categories provide context, not prerequisites. Their `order` establishes the
broad teaching progression. Every node references exactly one category through
`categoryId`.

`readingOrder` preserves the textbook's linear Previous/Next route. The graph's
branching connections are independent of that route. The original 15 visual
connections are exported as `suggested-next`, not inferred prerequisites.

| Edge type | Meaning |
| --- | --- |
| `suggested-next` | Directed recommendation from one concept to another; does not imply required mastery |
| `prerequisite` | Directed dependency: understand `from` before attempting `to` |
| `related` | Undirected conceptual connection; store only one orientation |

The current map has only `suggested-next` edges. The other types are supported
for deliberate future authoring. All nodes must be reachable from `startNode`
via directed `suggested-next` or `prerequisite` edges. Prerequisites must be
acyclic; optional review routes may loop.

IDs are durable keys; array indexes, display titles, canvas instance IDs, and
screen coordinates are not. The existing source concept IDs are preserved,
including `one` and `dot`. Category ID `building-the-product` uses the expanded
title "Building the product" for the canvas group formerly labeled "Build the
product".

`layout` is optional. Coordinates use a top-left origin, x increasing right,
y increasing down. Node positions indicate centers; category positions indicate
label anchors. Width and height describe a reference drawing surface, not a
required screen size. Never infer semantic connections from coordinates.

## Examples and checkpoints

Matrices are row-major arrays. `expectedProduct: null` means multiplication is
undefined because inner dimensions differ; it does not mean zero or missing
data. The validator recomputes every default and preset product.

Checkpoint prompts use fixed values, independent of learner edits to an
example. Numeric grading accepts a finite numeric answer only when its
absolute error is strictly less than `tolerance`. Single-choice answers match
an option exactly. Answers and explanations are teaching content, not learner
history; consumers should hide them until a learner requests or submits an
answer.

`interactions` describes optional renderer capabilities, not executable code.
Presets include both matrices; vector-based transformation presets use the
default vector. A renderer may retain a learner's currently edited vector when
switching transformations. A text-only skill can explain or calculate the same
examples without implementing any controls.

## Repository use

This bundle is located at `src/matrix-multiplication/` in the Clew repository.
Validate from this folder before committing. Keep the relative file layout
intact. Commit the lockfile, not `node_modules/`.

This is a standalone export, not a live link to the canvas. Editing these files
does not update the original session canvas, and canvas edits do not update
these files. A renderer can later be adapted to consume this format.

`map.json` is authoritative for graph metadata, matrices, presets, and
checkpoints; lesson Markdown is authoritative for explanatory prose. The
readable worked-example blocks in Markdown mirror the JSON. If an example
changes, update its prose and worked block as well as its JSON; the validator
checks JSON arithmetic but does not parse mathematical statements from prose.

No progress, attempts, selected lesson, custom input edits, local machine paths,
server URLs, or authentication data are included. Store learner state outside
the committed bundle, keyed by the map ID and node/checkpoint IDs. `.progress/`
is ignored if a consumer chooses to keep such state beside these files.

The bundle has been placed in the existing repository's local working tree.
This placement does not commit or push any changes.
