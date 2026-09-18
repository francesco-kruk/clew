# Quality, linking, and portability reference

## Select the structure owner

For Clew course exports, use the
[`course-content` structure contract](../../course-content/references/structure.md).
It owns the hub, metadata, one-complete-file-per-chapter rule, supporting-note
roles, and course link/destination conventions. The standalone layout below is
not a second course format. Apply this reference's PDF coverage, fidelity,
verification-report, and packaging gates in addition to the shared course
structural checks.

In course-mode checks below, "index" means the canonical course `hub.md`. Its
backlinks must be course-qualified; unique-basename guidance never permits
`[[hub]]`. Multiple source sections may map to headings in the same chapter
file in the conversion manifest.

Digest is the editable conversion/recovery route. The separate optional
`content-ingest` skill retains the image-first workflow. Do not apply digest's
editable-prose requirements to erase that route or call an image-first result a
verified editable transcription. If the requested image-first skill is not
installed, report that limitation instead of silently changing routes.

## Standalone non-course bundle structure

```text
Book-Obsidian\
  00 - Index.md
  Concept Map.md
  Concept Overview.canvas
  01 - First section.md
  02 - Second section.md
  Exercises.md
  Answers.md
  Concepts\
    Book - First concept.md
  Attachments\
    Book - Original.pdf
    Book - Figure 01.png
```

Names and counts are illustrative, not a fixed schema. Preserve actual source
section identifiers. Use Windows-safe filenames without reserved device names,
trailing periods, or characters that collide with wikilink syntax (`#`, `^`, `|`,
`[` or `]`). Apply one deterministic naming policy before creating links.
Check names case-insensitively, including collisions with existing destination
notes when authorized access to the destination is available.

## Native Obsidian links

- Prefer unique basename wikilinks for notes and assets when a bundle may be
  inserted anywhere: `[[Book - First concept|first concept]]`.
- Heading links must match an authored heading:
  `[[02 - Second section#Worked example 3|worked example 3]]`.
- Use explicit block IDs only when heading granularity is insufficient:
  `[[Exercises#^exercise-3b|Exercise 3(b)]]`.
- Use aliases after `|` to keep sentences readable. YAML aliases are optional
  discovery aids, not a substitute for resolvable link targets.
- Embed images with `![[Book - Figure 01.png]]` and a nearby source caption.
  Link a source page with `[[Book - Original.pdf#page=7|PDF page 7]]`;
  PDF page fragments refer to physical pages, not printed labels.
- Avoid bare mathematical expressions inside wikilink targets or aliases.
  Link a readable concept phrase adjacent to math instead.
- Use tags sparingly for classification. Explain semantic relationships in text
  and links; a shared tag does not establish a conceptual relationship.
- Link only relevant exercise subparts. Do not imply that an exercise tests a
  concept merely because both occur in the same chapter.

Concept notes should be compact and useful:

```markdown
# Concept title

A concise, source-grounded definition.

## In the textbook

- [[02 - Second section#Definition|Definition and assumptions]]
- [[02 - Second section#Worked example 3|Worked example]]

## Connections

- Requires [[Book - Prerequisite]] because ...
- Contrasts with [[Book - Related concept]] in ...

## Practice

[[Exercises#Exercise 3|Exercise 3]] applies this concept to ...
```

Omit empty sections. Never retain template ellipses or placeholder links.
Do not duplicate a chapter wholesale into its concept note.

## Canvas portability

Obsidian Canvas `file` paths are **vault-root-relative**, not Canvas-file-relative.
Serialized Canvas paths use `/`, even when filesystem operations use Windows `\`.

Choose and document one valid destination strategy:

1. Standalone vault: file paths are relative to the bundle root. Instruct the user
   to open that folder as a vault, or copy its contents directly into a vault root.
2. Known vault subfolder: prefix every file-node path with that exact subfolder.
   Validate against a virtual vault root or the authorized real destination.
3. Unknown existing-vault subfolder: keep notes portable with unique-basename
   wikilinks. Either omit Canvas until the destination is known, or label a supplied
   Canvas as standalone-root-only. Do not suggest it works unchanged in any subfolder.

A Canvas is JSON with `nodes` and `edges` arrays. File nodes need unique string IDs,
`type: "file"`, a vault-relative `file`, and numeric `x`, `y`, `width`, `height`.
Edges need unique IDs and valid `fromNode`/`toNode` IDs; add meaningful `label` values.
Optional `fromSide`/`toSide` values are `top`, `right`, `bottom`, or `left`.
If using `subpath`, validate its heading or block target too. Group nodes use
`type: "group"` and a label; they do not replace file links in the notes.

Use comfortable node spacing and a limited overview. A structurally valid Canvas
does not prove a readable layout; inspect it in Obsidian when available. Otherwise
report that live rendering was not checked.

## Source coverage manifest

Maintain structured fields equivalent to:

- Source filename, SHA-256, total physical pages, and printed-page mapping.
- Each section's stable ID, note path, source pages, and boundary rectangles where
  pages are shared. Do not assume a constant cover-page offset.
- Each page's classification and review state, including deliberately omitted blank
  pages or repeated running headers with a reason.
- Example/exercise/answer identifiers, subpart counts, and destination headings.
- Each figure or fallback's asset path, physical page, crop rectangle, caption,
  and whether it is an original raster, rendered vector crop, or untranscribed region.
- Unresolved fidelity issues and clearly labeled source-error annotations.

Every source page must be accounted for, but coverage is not merely a count of page
images. A page assigned to a note is not proof that its content survived.

## Required acceptance gates

### Fidelity

- Compare every section with its source. Verify no prose, meaningful footnotes,
  tables, examples, exercise subparts, or supplied answers disappeared at boundaries.
- Check formula semantics, not just balanced delimiters: signs, denominators,
  radicals, superscripts, limits, domains, units, and rounding.
- Preserve legible source crops for unresolved math. Caption the limitation.
- Check diagrams for clipped labels, legends, arrows, axes, and missing captions.
- Scan for `(cid:...)`, replacement characters, NULs, mojibake, repeated headers,
  meaningless tables, and unreplaced generation placeholders. Investigate matches;
  do not delete them indiscriminately.
- Check balanced math delimiters outside code and escaped literals. Parser success
  is only structural evidence, not proof of mathematical accuracy.
- Do not silently "fix" a source answer to agree with a derived answer. Preserve the
  original, explicitly annotate a verified discrepancy, and retain its source link.

### Links and graph

- Parse wikilinks with embeds, aliases, headings, and block IDs; ignore fenced and
  inline code. Handle Markdown inline and reference links too if authored.
- Resolve note names with and without `.md`, relative paths, vault paths, and unique
  basenames. Reject ambiguity instead of accepting the first filename match.
- Decode URL-encoded local paths where appropriate. Validate local destinations,
  while classifying external links separately rather than treating them as files.
- Check actual target headings and explicit block IDs. Wikilink heading text and
  Markdown URL heading slugs need different normalization.
- Validate PDF page fragments against the PDF's page count; check every embed exists.
- Ensure every study note is reachable from the index. Each concept needs a source
  chapter link and a meaningful inbound link, with concept-to-concept relationships
  where supported. For course exports, check the hub's ordered chapter inventory,
  required metadata, and chapter backlinks using `course-content`; optional concept
  notes need checking only when authored. Do not manufacture edges to satisfy an
  arbitrary minimum.
- Validate Canvas JSON, unique IDs, finite geometry with positive dimensions,
  edge endpoints, file-node targets, and fragments using the declared vault root.
- Exclude machine-readable reports and supporting documentation from orphan-note
  gates unless intentionally included in the reader-facing knowledge graph.

### Preservation and packaging

- On revisions, capture an initial inventory/hash baseline. Compare attachment
  hashes and original-source hashes after editing.
- Verify chapter-content preservation beyond byte comparison: links and metadata
  legitimately change bytes. Compare normalized prose and mathematical content,
  exercise identifiers, section coverage, and source-error annotations.
- For a course export, verify the archive/import root preserves the declared
  `courses\<course>\` prefix and that source chapter IDs map to exactly one
  complete chapter file each. Section-batch output is intermediate, not a
  delivered substitute for a chapter. Keep the generic standalone-root advice
  separate from course installation instructions.
- Validate ZIP members use safe relative paths without traversal or absolute paths.
  Compare archive contents and file hashes with the finalized importable folder.
- Test validators using small fixtures containing both valid links and deliberate
  failures (missing file, ambiguous basename, invalid anchor, orphan, broken Canvas
  edge, and wrong destination prefix). A validator that always passes proves nothing.
- Save actual outcomes, counts, unresolved regions, and validation limitations.
  Do not claim OCR was verified visually, formulas were checked, or Obsidian was
  launched unless those actions occurred.

### Storage and processing

- Keep output and working files under explicitly authorized external roots, not
  the skill clone. Do not infer or access a learner-model root for PDF conversion.
- Use bounded page/section reads for hosted GitHub Copilot task processing. Local
  storage is not a local-inference promise; no additional processing opt-in is
  required. Never bulk-upload a vault or unrelated learner records.
- Do not add separate cloud OCR/vision uploads, passive telemetry, teacher access,
  or provider retention/training guarantees. Report actual tool capabilities and
  any source regions left untranscribed.

## Efficiency and recovery

Use a small representative extraction probe to select the workflow, then process
bounded sections. Cache page text/geometry and only render changed or uncertain
regions. Recheck affected notes and inbound links after edits; run the complete
graph/package check once final. Avoid re-extracting the entire PDF after link edits.

A failed extractor is not a failed conversion: try coordinate-aware text extraction,
local OCR, and visual source transcription in that order as appropriate. If all
fail, retain the region as a clearly identified source image. Password protection,
unreadable pages, missing local OCR, or destination conflicts must remain explicit
limitations rather than silent omissions or fabricated text.
