# Red-bordered Markdown canvas

A read-only preview of a local `.md` or `.markdown` file in a custom Copilot
canvas. It supports Markdown, KaTeX equations, document-relative raster images,
Obsidian image embeds, and a red border. It does not convert PDFs or modify the
source document.

## Requirements and installation

Use a Copilot CLI/runtime and host app that support SDK extension canvases.
This API is experimental; a plain terminal or a Copilot surface without a
canvas renderer cannot display the panel. A current Node.js LTS and npm are required to
restore this extension's dependencies. The runtime supplies
`@github/copilot-sdk`; do not install a separate copy.

For this repository, keep this folder at `.github/extensions/red-markdown/`.
From the repository root, run:

```sh
npm --prefix .github/extensions/red-markdown ci
```

In Windows PowerShell, use `npm.cmd` if execution policy blocks `npm.ps1`.

Then reload extensions in your Copilot session (ask the agent to call
`extensions_reload`), or start a new session. Install dependencies before
reloading; missing packages prevent the extension from loading.

For use across repositories, copy this entire folder, including `package.json`
and `package-lock.json`, into `$COPILOT_HOME/extensions/red-markdown/`
(`~/.copilot/extensions/red-markdown/` when `COPILOT_HOME` is unset). Run `npm ci`
inside that copy, then reload extensions. Do not copy `node_modules`, session
logs, or the original session's documents. Project extensions shadow personal
extensions with the same folder name.

Only install extensions you trust: they execute local Node.js code. The preview
is served over a tokenized loopback URL, not published or uploaded anywhere.

## Opening a document

Ask the agent to open a local Markdown file in the **Red-bordered Markdown**
canvas, giving its absolute path. The equivalent tool input is:

```json
{
  "canvasId": "red-markdown",
  "instanceId": "notes-preview",
  "input": { "path": "/absolute/path/to/notes.md" }
}
```

On Windows, use an absolute Windows path (escape backslashes in JSON).
`instanceId` names the panel, not the file. Use a new instance ID when opening
a different document; reopening an existing panel focuses and reloads it.
The `get_document` action returns the file path, current Markdown, and border
setting. To refresh a preview after editing its file, reopen the panel.

Files must exist and be readable on the machine running the extension.
No session ID, home directory, sample document, or repository path is embedded
in the code. The original prototype's `documentId`-only input is intentionally
removed; open old documents again using `input.path`. This does not migrate
panels owned by the original session-scoped provider.

## Rendering boundaries

- Inline `$...$` and block `$$...$$` equations are rendered locally with KaTeX.
- Markdown images and `![[image.png]]` embeds support PNG, JPEG, GIF, and WebP.
  File images must resolve within the document's directory, including after
  symlink resolution; parent-directory and remote images are not loaded.
  Supported raster data URLs are also accepted.
- `[[note|Label]]` links are displayed as text, not navigable vault links.
- Raw HTML is sanitized; scripts are disabled. Missing or unsupported Markdown
  images produce visible warnings. Invalid equations show KaTeX error output.
- Rendering is a snapshot on each page request, not a live file watcher.

## Teaching display procedure

Keep teaching in Copilot chat; this is a static, read-only explanation surface,
not an exercise UI or learner-profile editor.

1. After dependency restoration, call `extensions_reload`, inspect `red-markdown`
   with `extensions_manage`, and discover its live schema with
   `list_canvas_capabilities`. A missing dependency or unavailable canvas is an
   explicit limitation, not successful display.
2. Select a relevant supported raster, preferably PNG. With permission, copy it
   beside the explanation Markdown in the agreed external artifact directory,
   leaving the source unchanged. Cite the source and image provenance; distinguish
   supplied/copied images from genuinely generated ones. Check any local
   generation capability before relying on it; this extension generates no images.
3. Reference the same-directory file, for example
   `![Both required checks must pass](required-checks.png)`, and include readable
   explanatory text. Open that Markdown using the discovered `path` input.
   Do not work around the asset boundary with parent paths, remote images, raw
   SVG, Mermaid, or arbitrary HTML.
4. Confirm that the real canvas visibly renders a legible image and explanation
   using host observation or a human check. File existence, `get_document`, and
   successful `open_canvas` results alone do not prove visible rendering.
5. After an authorized edit and save, reopen the same `instanceId` and confirm the
   updated preview. There is no watcher. Report missing-image warnings and other
   failures; text-only fallback does not pass visual-demo acceptance.

Private artifacts and learner records stay outside Git. Use an authorized
editor, this preview, or bounded file reads to inspect records in place rather
than copying them into the repository.

## Development

Run `npm test` inside this folder. Tests use temporary fixtures rather than
personal documents. Keep the lockfile committed and `node_modules` excluded.
The dependency packages retain their upstream license files when installed.

`extension.mjs` registers the canvas and manages panel lifetimes, `server.mjs`
serves the read-only preview and allowlisted assets, and `renderer.mjs` handles
Markdown, math, image loading, and sanitization.
