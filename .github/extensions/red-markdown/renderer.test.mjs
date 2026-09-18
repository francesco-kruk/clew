import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { renderDocument, resolveDocument, readAsset } from "./renderer.mjs";

test("opens arbitrary paths, resolves each document's images, and reports failures", async () => {
    const root = await mkdtemp(join(tmpdir(), "red-markdown-test-"));
    try {
        const image = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1sAAAAASUVORK5CYII=", "base64");
        await mkdir(join(root, "assets"));
        await writeFile(join(root, "assets", "my image.png"), image);
        const first = join(root, "First note.md");
        await writeFile(first, '# First\n\nInline $x^2$.\n\n$$\\frac{1}{2}$$\n\n![Diagram](assets/my%20image.png)\n\n![[assets/my image.png]]\n\n[[note|Label]]\n\n```md\n![[literal]]\n```\n\n<script>alert(1)</script>\n');
        assert.equal(await resolveDocument(first), first);
        const html = await renderDocument(first);
        assert.match(html, /<title>First note<\/title>/);
        assert.match(html, /border: 4px solid red/);
        assert.match(html, /katex-display/);
        assert.equal((html.match(/src="data:image\/png;base64,/g) ?? []).length, 2);
        assert.match(html, /!\[\[literal\]\]/);
        assert.doesNotMatch(html, /alert\(1\)|Image warnings/);
        assert.equal((html.match(/<script/g) ?? []).length, 1);
        assert.match(html, /<script src="quiz-button.mjs" type="module"><\/script>/);
        assert.match(html, /id="quiz-button"[^>]*aria-label="Quiz me on this content"/);
        assert.match(html, /#quiz-button \{ position: fixed; top: 12px; right: 12px/);
        assert.match(html, /id="quiz-status" role="status" aria-live="polite" hidden/);
        const interactive = await renderDocument(first, { quizToken: 'quote"test', quizEnabled: true });
        assert.match(interactive, /content="quote&quot;test"/);
        assert.doesNotMatch(interactive, /id="quiz-button"[^>]* disabled/);

        const second = join(root, "Second.MARKDOWN");
        await writeFile(second, "# Second\n\n![Missing](absent.png)\n\n![Remote](https://example.com/image.png)\n\n$\\notACommand$\n");
        await resolveDocument(second);
        const secondHtml = await renderDocument(second);
        assert.match(secondHtml, /<h1>Second<\/h1>/);
        assert.match(secondHtml, /Image warnings/);
        assert.match(secondHtml, /mathcolor="#cc0000"/);
        assert.match(secondHtml, /\\notACommand/);
        assert.doesNotMatch(secondHtml, /src="https:/);
        assert.doesNotMatch(secondHtml, /<h1>First<\/h1>/);

        await assert.rejects(resolveDocument("relative.md"), /absolute/);
        await assert.rejects(resolveDocument(join(root, "file.txt")), /\.md/);
        await assert.rejects(resolveDocument(join(root, "missing.md")), /ENOENT/);
        await mkdir(join(root, "folder.md"));
        await assert.rejects(resolveDocument(join(root, "folder.md")), /must identify a file/);
        await assert.rejects(renderDocument(join(root, "missing.md")), /ENOENT/);
        await assert.rejects(resolveDocument(undefined), /absolute/);
        await assert.rejects(renderDocument(), /path/i);
    } finally {
        await rm(root, { recursive: true, force: true });
    }
});

test("loads KaTeX assets through package resolution and rejects other paths", async () => {
    const css = await readAsset("katex.min.css");
    assert.equal(css.type, "text/css");
    assert.match(css.data.toString(), /font-face/);
    const font = await readAsset("fonts/KaTeX_Main-Regular.woff2");
    assert.equal(font.type, "font/woff2");
    assert.ok(font.data.length > 0);
    for (const path of ["../package.json", "fonts/../../package.json", "extension.mjs", "fonts/nope.woff2"]) {
        assert.equal(await readAsset(path), null);
    }
});
