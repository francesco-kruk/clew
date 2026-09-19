# Legacy Clew course structure contract (explicit export)

This preserved format applies only when the caller explicitly selects legacy
Clew authoring/export or package validation. It is not the default student read
contract: [portable navigation](reading.md) accepts ordinary copied Markdown
without a hub, metadata or catalog. Within this legacy format the hub is the
stable interface. Source-specific importers own recovery and fidelity. The
examples are synthetic, not supplied material or a concept-ID registry.

## Layout and granularity

```text
<vault>\
  courses\
    Mechanics\
      hub.md
      chapters\
        MECH - 01 - Motion.md
        MECH - 02 - Forces.md
      concepts\                     (optional)
        MECH - Average speed.md
      supplements\                  (optional)
        MECH - Supplied answer key.md
      attachments\                  (when needed)
        MECH - Source.pdf
        MECH - Figure 01.png
      MECH - Concept Map.md         (optional)
      MECH - Concept Overview.canvas (optional)
```

- `courses\<course>\hub.md` is the one canonical main file. Do not also create
  `00 - Index.md`, a second course hub, or a required learning-plan file.
- Each chapter has exactly one Markdown file in `chapters\`. Preserve chapter
  identifiers and meaningful titles; section numbers become headings, not
  separate files. Long chapters remain one file even when processed in batches.
- Keep the chapter's definitions, explanations, examples, exercises, supplied
  in-chapter answers, footnotes, and citations together. A summary or a file
  that only embeds section shards is not a complete chapter.
- Separate front matter, appendices, or an answer key may have their own
  `supplements\` notes when they are genuinely separate in the source. If an
  appendix is itself a source chapter, give it one chapter file instead.
  Do not use supplements to evade the one-file-per-chapter rule or duplicate
  in-chapter exercises and answers.
- For chapterless material, establish the intended logical chapter units with
  the author when grouping is ambiguous. Do not invent a textbook hierarchy.
- Concepts and maps are optional navigation/synthesis aids. The chapter remains
  authoritative. A course requires neither a concept-note quota, Canvas,
  Obsidian plugin, dashboard, nor learner model.
- Keep raw extraction, scripts, environments, and bulky debug output outside
  reader-facing course content. Conversion support reports are not chapters.

## Hub

Required frontmatter:

| Property | Meaning |
| --- | --- |
| `type` | `course`. |
| `course` | Stable course name used to join course metadata to the learner model's course-name values. |
| `primary_domains` | List of home knowledge domains taught by the course. |
| `prerequisite_domains` | List of prerequisite knowledge domains, not a list of learner weaknesses. |
| `sources` | List of original-source wikilinks or external source URLs; `[]` for explicitly original authored material. |

Do not equate a course name with a domain. Preserve established names rather
than silently renaming them. Missing domain/source information is not an empty
list: ask the author before declaring a new course's metadata complete. Legacy
readers report missing fields without manufacturing values.

Required body sections:

- `# <Course title>` and a short, source-grounded overview.
- `## Chapters`: an ordered list of direct links to every chapter, exactly
  once. This list is the authoritative reading order, not filesystem sorting.
  Do not maintain a competing order in a second file or property.
- `## Concept index`: a table with **Concept ID**, **Concept**, **Domain**, and
  **Location** columns. Locations link to exact chapter headings/blocks, not
  just to summaries. An optional concept note can be linked in the Concept
  column without replacing its authoritative Location.
- `## Resources` when supporting notes/assets are present: link supplements,
  maps, source files, and other entry points. All reader-facing notes and
  needed assets must be reachable from the hub, directly or through its links.
- `## Content notes` when there are missing source regions, unclassified
  concepts, or other known limits. Do not hide incomplete import status.

Reuse established domain-scoped concept IDs from the content/index when
available. Use `null` in a Concept ID cell when no established ID is supplied,
and explain unmapped concepts in Content notes; assigning a new global ID is
not a side effect of import or reading. A concept may have several grounded
locations. Do not infer an entire course's concepts from its title, or add
mastery, confidence, review dates, or observed misconceptions to this index.
If there are no identified concepts yet, retain the table headers and state
that limitation instead of fabricating entries.

This abbreviated synthetic hub demonstrates the syntax:

```markdown
---
type: course
course: Mechanics
primary_domains: [Physics]
prerequisite_domains: [Algebra]
sources:
  - "[[MECH - Source.pdf]]"
---

# Mechanics

Motion and forces, with algebraic worked examples.

## Chapters

1. [[MECH - 01 - Motion|1. Motion]]
2. [[MECH - 02 - Forces|2. Forces]]

## Concept index

| Concept ID | Concept | Domain | Location |
| --- | --- | --- | --- |
| PHY.KIN.SPEED | Average speed | Physics | [[MECH - 01 - Motion#1.1 Average speed]] |

## Resources

- [[MECH - Source.pdf]]
- [[MECH - Supplied answer key]]
- [[MECH - Concept Map]]
```

## Chapter notes

Required frontmatter:

| Property | Meaning |
| --- | --- |
| `type` | `course-chapter`, distinct from a learner-model concept or session. |
| `course` | The hub's exact course-name value. |
| `chapter` | Stable source chapter identifier as a string, such as `"1"` or `"A"`; preserve an established identifier for an unnumbered chapter. |
| `hub` | Quoted, vault-qualified wikilink to this course's `hub.md`. |
| `sources` | Source references for this chapter; `[]` only for explicitly original authored material. Finer citations belong with the relevant section or item. |

Use one title heading, stable numbered section headings where supplied, and
exact source example/exercise identifiers. Add a visible backlink to the hub.
Make repeated headings distinguishable; use a stable explicit block ID when
an item cannot be linked unambiguously by heading. Preserve anchors on revisions
or repair all affected inbound links in the authorized destination.

This synthetic chapter fragment illustrates those conventions, not a complete
transcription:

```markdown
---
type: course-chapter
course: Mechanics
chapter: "1"
hub: "[[courses/Mechanics/hub]]"
sources:
  - "[[MECH - Source.pdf]]"
---

# 1. Motion

[[courses/Mechanics/hub|Mechanics]]

## 1.1 Average speed

Average speed is distance travelled divided by elapsed time:
$\bar v = d / \Delta t$, with $\Delta t > 0$.

### Worked example 1

Travelling 120 m in 10 s gives an average speed of 12 m/s.

### Exercise 1

A walker travels 150 m in 30 s. Find the average speed in m/s.
```

Keep answers where the source puts them. Link an exercise to its supplied
answer and that answer back to the exact exercise, including subparts. Do not
invent an answer key. A separate answer-key supplement is valid only when the
source supplies one separately.

## Supporting content

- Optional course concept notes use `type: course-concept`, the course name,
  home `domain`, and established `concept_id` (or `null`). Include a compact
  definition, exact source chapter/heading links, and explained relationships.
  Mark added explanatory synthesis. Link them from a relevant chapter or hub;
  do not duplicate chapters into them.
- A concept map groups meaningful relationships with native wikilinks and
  labels such as "requires" or "used to solve". It is not a second chapter
  index or a substitute for the hub's Concept index.
- Embed needed assets with descriptive captions and source references. Keep
  image-only/unverified transcription labels next to the affected material.
  An attachment resolves a missing transcription only as a source image, not
  as verified editable text.
- Learner records live outside the course in the explicitly selected external
  vault, as separate personal memory under the installed `learner-model`
  contract (`references/learner-model-spec.md` in that skill). Teacher course
  authoring and validation do not require that package. Course concepts
  describe subject matter; learner concepts describe a person's evidence and
  state. Do not copy one into the other or put personal progress in the hub.
  Local storage does not imply local-only inference: relevant content used
  during a task enters hosted GitHub Copilot processing.

## Links, names, and destination

Use Windows-safe filenames, preserving source identifiers in metadata/headings
when a filename must be sanitized. Avoid reserved device names, trailing
periods/spaces, and characters that collide with wikilinks (`#`, `^`, `|`, `[`,
`]`). Check collisions case-insensitively against the declared destination.

Use a short, stable course prefix for chapter, concept, supplement, and asset
basenames. Unique basenames such as `[[MECH - 01 - Motion]]` are convenient
within the course. If uniqueness cannot be established, use an explicit
vault-relative link. A generic `hub.md` always needs its course-qualified
target, such as `[[courses/Mechanics/hub|Mechanics]]`; never author `[[hub]]`.
Aliases are display aids, not a fix for ambiguous targets.

Filesystem operations on Windows use `\`. Serialized Obsidian vault paths
inside wikilinks and Canvas JSON use `/`; these are not shell paths.
Match heading links to actual heading text, and block links to authored
`^block-id` values. Escape alias pipes in Markdown tables. Resolve embeds,
source references, and local Markdown links too; classify external URLs as
citations rather than local file targets.

PDF `#page=N` fragments refer to physical pages. Preserve printed labels as
separate caption text when supplied; do not infer a fixed page-label offset.
The PDF importer, not a reader, establishes page coverage and verification.

For a standalone course vault, package the `courses\<course>\` tree inside
the vault root. For an existing vault, target that exact course path and obtain
authorization before installation. A staged course folder is not by itself
the final vault root: do not recommend opening it as a vault when its hub
links assume the enclosing `courses\` tree.

Optional Canvas file-node paths are vault-root-relative, not relative to the
Canvas file. Use the actual `courses/<course>/...` prefix. If the destination
is unknown, omit Canvas until it can be resolved or clearly label a fixed
standalone-root layout. Moving a course to a different prefix requires an
explicit migration of qualified links and Canvas paths, not a portability
claim. Validate the chosen destination, not only the staging directory.
