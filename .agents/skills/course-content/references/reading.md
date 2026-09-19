# Portable Markdown reading

Start with the configured vault and selected bundle/note, not a mandatory
directory layout. A bundle can contain an index, README, hub, or none of them.
Read only bounded relevant content. Ordinary Markdown with no frontmatter is
valid; absence of domains/concept IDs is unknown metadata, not a reason to
generate a catalog or classify the learner.

## Local links

- Resolve `[text](chapter.md#an-anchor)` and `![caption](images/figure.png)`
  relative to the file containing the link. Respect angle-bracket destinations,
  URL-encoded spaces and reference-style links (`[text][ref]` plus the relevant
  definition). A fragment-only link addresses the current note.
- Decode URI escapes for path resolution without treating query/fragment text
  as a filename. Confirm the resulting local destination remains in authorized
  scope. Do not follow absolute paths, network paths, symlinks/junctions or `..`
  beyond the boundary just because a note links there.
- Markdown heading slugs depend on the renderer. Match against actual heading
  text using the source's known convention, retaining the exact heading text
  in citations. For a simple unambiguous slug, confirm the actual heading;
  for duplicates, unknown slug rules or mismatches report ambiguity and ask for
  the intended section. Never silently choose the first repeated heading.
- Keep relevant source qualifications and nearby captions with excerpts.
  Resolve asset references but say whether the image was actually inspected.
  A missing figure is a limitation, not a license to reconstruct its contents.
- External URLs are citations, not local targets or permission to fetch.
  PDF `#page=N` denotes physical page N; printed page labels remain separate.

## Wikilinks and embeds

Retain `[[Note]]`, `[[Note|alias]]`, `[[Note#Heading]]`,
`[[Note#^block-id]]` and `![[asset.png]]`. The alias is display text, not target
identity. Heading text/block ID must actually exist. Resolve explicit
vault-qualified paths only inside the authorized course scope. Resolve bare
basenames by an unambiguous match inside the selected bundle; do not scan the
whole vault to resolve a generic `[[hub]]`. Ask if two courses/notes match.

Copying a complete relative-link bundle generally preserves its internal
links. Legacy vault-qualified links and Canvas file paths may depend on the
original prefix; flag mismatches, do not rewrite source paths on read.
Filesystem paths passed to tools on Windows use `\`; serialized Markdown
destinations use `/`.

## Citations and factual limits

Cite `bundle/note.md` plus the exact heading, block or exercise identifier used.
No heading means a whole-note citation, not a fabricated anchor. Preserve source
page references when present but do not invent them. A statement from the note
can be attributed to that note even when original-source provenance is missing;
say that source provenance is unknown rather than declaring the statement
independently verified.

Source concept/domain mappings are optional. Reuse explicit bindings only with
their source context; same text in different domains is not shared identity.
A request depending on ambiguous identity needs clarification, while an exact
note lookup need not wait for classification. No course content is evidence
that a learner has seen, mastered or misunderstood it.
