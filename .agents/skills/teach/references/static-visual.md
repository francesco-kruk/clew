# Static visual procedure

The required visual is a relevant, visibly rendered **static raster image** with
readable explanatory text, not just a link, written file or textual description.
Prefer PNG. This procedure defines no canvas/tool API: discover the actual host
capabilities, schemas and actions before calling them.

## Discover and authorize

1. Inspect the available host preview/display capability and its documentation,
   supported raster formats, Markdown/math behavior and asset boundary.
   Establish renderer readiness; an installed extension is not necessarily
   running or able to render. Use only real available tools and their discovered
   input schemas. A missing capability is a limitation, not an invitation to
   invent a tool call or silently install an extension.
2. Identify a relevant source-grounded raster supplied with the selected notes,
   or another explicitly authorized asset. Inspect its content and caption
   before using it; resolving its path is not visual review. Retain its source
   note/heading, original asset location and rights/provenance limitations.
   A reused or copied image is not a generated image.
3. Generate a raster only when a genuinely available approved tool can do so.
   Check its actual local capability before relying on it. Do not add a required
   generator, image service, runtime library or silently install one. Sending
   source or learner data to another service needs separate authorization;
   ordinary tutoring scope is not permission to upload it there. Review generated
   content against the selected source, label it agent-generated and record the
   actual tool/method, source grounding and uncertainty. Generation does not
   establish correctness or source fidelity.
4. Establish an authorized output directory outside teacher source notes and
   repository commits. For retained useful work, follow `learner-model`'s
   ownership checks for the personal artifact destination. Permission to read an
   image is not permission to copy it. If copying is authorized, place a display
   copy beside the explanation Markdown without changing the original.
   Do not assume that tutoring, a configured vault or declined memory authorizes
   new files. Respect the exact no-save scope: use an existing authorized display
   or a genuinely non-persistent host capability if available, otherwise report
   the visual limitation. Temporary files are not a no-save workaround.

## Prepare a self-contained explanation

Keep explanation Markdown and every copied/generated raster it uses in the
**same authorized directory**, with ordinary relative Markdown image links.
Use collision-safe descriptive names and check existing ownership before any
write. Put accessible alt text, a caption and a short adjacent text explanation
of the image's relevant relationships, labels and takeaway; do not rely on color
alone. Cite the actual source note/heading and image provenance, distinguish a
source figure from an agent illustration, and preserve known source uncertainty.
Do not replicate the learner's complete original answer in this artifact.

Filesystem tool paths use the host's conventions (backslashes on Windows);
serialized Markdown links use forward slashes and URI-encoded spaces as needed.
Check actual relative targets. Do not widen asset security rules, use traversal
to reach sibling/parent assets, or fetch remote assets just because they are
linked. Do not alter the source bundle to fit the renderer.

The existing Clew `red-markdown` preview is a possible host, not a mandatory
portable API. It supports Markdown, math and supported raster images, not
arbitrary SVG, Mermaid, HTML or interactive teaching controls. Discover its
current schema rather than assuming action names. Do not introduce a renderer,
watcher, automatic-refresh mechanism or new asset policy for this loop.

## Display, observe, and report

1. Read back any written explanation and verify its image file/link exists.
   This proves file availability only, not successful rendering.
2. Open the actual explanation using the discovered host preview action. Use
   available host observation, or a human visual check, to confirm that the
   **image is visible, relevant and legible and explanatory text is readable**.
   Confirm labels are not clipped or unreadable. An open-panel response,
   renderer unit test, Markdown source view or successful file write alone is
   insufficient evidence. If observation is unavailable, say display is
   unverified; do not claim the visual step passed.
3. After an authorized saved edit, reopen the existing preview if needed and
   check the changed output, not stale display. Do not promise automatic refresh.
4. Report missing assets, unsupported formats, unavailable generation tools,
   permission/ownership problems and render failures explicitly. Correct within
   existing authorization or pause that operation; never disguise failure with
   a placeholder or claim text is a rendered visual.

Text-only explanation may keep tutoring going, but **cannot pass visual-demo
acceptance**. Preserve that limitation with any authorized session evidence.
The supplied-image and generated-image paths are separate claims: a successful
supplied-image display does not prove generation works. Record the observation
method and actual outcome when reporting acceptance; leave an unobserved check
pending, not passed.
