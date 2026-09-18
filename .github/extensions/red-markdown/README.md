# Red-bordered Markdown canvas

A read-only preview of a local `.md` or `.markdown` file in a custom Copilot
canvas. It supports Markdown, KaTeX equations, document-relative raster images,
Obsidian image embeds, a red border, and a fixed quiz button in the upper-right
corner. It does not convert PDFs or modify the
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

## Requesting a quiz

Press the upper-right **Quiz me on this content** icon to send a request to the
current Copilot session using the `canvas-quiz` skill. It selects this reader's
instance and runtime source path, even when another panel is active. The agent
reads the selected document and opens the existing three-question `vault-quiz`
canvas; the button itself does not generate questions, submit answers, or
write learner evidence.

The button supports keyboard focus, Enter/Space activation, and a live status
message. It stays fixed while you scroll. A successful dispatch is labeled
**Quiz requested**, not quiz completed. Repeat clicks and HTTP retries from the
same page reuse that request; refresh the reader to request another quiz.
Failures are shown next to the button and can be retried. If the reader's
document changed, refresh before requesting a quiz.

The quiz skill and `vault-quiz` extension must be available to the session.
Cross-repository installations also need those companions; a missing skill or
provider must be reported by the agent rather than replaced with a fake quiz.
The request sends only panel identity and the source path, not document text,
quiz answers, or learner records. The agent reads source content through the
normal document action. No machine-specific paths are embedded in the code.

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
- Raw HTML is sanitized; document-provided scripts are removed. Only the
  extension's allowlisted local quiz-button module runs. Missing or unsupported Markdown
  images produce visible warnings. Invalid equations show KaTeX error output.
- Rendering is a snapshot on each page request, not a live file watcher.

## Development

Run `npm test` inside this folder. Tests use temporary fixtures rather than
personal documents. Keep the lockfile committed and `node_modules` excluded.
The dependency packages retain their upstream license files when installed.

`extension.mjs` registers the canvas and manages panel lifetimes, `server.mjs`
serves the preview, allowlisted assets, and token-protected quiz-request endpoint,
and `renderer.mjs` handles Markdown, math, image loading, and sanitization.
`quiz-button.mjs` handles the fixed control; `quiz-request.mjs` routes its
explicitly selected reader to `session.send`, without changing the session's
system prompt. The endpoint enforces Host/Origin checks and per-render request
tokens; it never accepts a client-supplied file path or arbitrary prompt.
