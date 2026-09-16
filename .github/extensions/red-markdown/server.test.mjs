import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { startServer } from "./server.mjs";

test("serves isolated, refreshable documents and only allowlisted assets", async (t) => {
    const root = await mkdtemp(join(tmpdir(), "red-markdown-server-"));
    const entries = [];
    t.after(async () => {
        await Promise.all(entries.map(({ server }) => new Promise((resolve, reject) => {
            server.close((error) => error ? reject(error) : resolve());
            server.closeAllConnections();
        })));
        await rm(root, { recursive: true, force: true });
    });
    const first = join(root, "first.md");
    const second = join(root, "second.md");
    await writeFile(first, "# First");
    await writeFile(second, "# Second");
    entries.push(await startServer(first), await startServer(second));
    const [entry, other] = entries;
    assert.equal(entry.server.address().address, "127.0.0.1");
    assert.notEqual(entry.url, other.url);

    const response = await fetch(entry.url);
    assert.equal(response.status, 200);
    assert.match(response.headers.get("content-type"), /text\/html/);
    assert.equal(response.headers.get("cache-control"), "no-store");
    assert.equal(response.headers.get("x-content-type-options"), "nosniff");
    assert.match(response.headers.get("content-security-policy"), /default-src 'none'/);
    assert.match(await response.text(), /<h1>First<\/h1>/);
    assert.match(await (await fetch(other.url)).text(), /<h1>Second<\/h1>/);

    await writeFile(first, "# Updated");
    assert.match(await (await fetch(entry.url)).text(), /<h1>Updated<\/h1>/);
    entry.path = second;
    assert.match(await (await fetch(entry.url)).text(), /<h1>Second<\/h1>/);

    const css = await fetch(new URL("katex.min.css", entry.url));
    assert.equal(css.status, 200);
    assert.equal(css.headers.get("content-type"), "text/css");
    const font = await fetch(new URL("fonts/KaTeX_Main-Regular.woff2", entry.url));
    assert.equal(font.status, 200);
    assert.equal(font.headers.get("content-type"), "font/woff2");
    for (const path of ["/", "/wrong-token/", "extension.mjs", "../package.json"]) {
        assert.equal((await fetch(new URL(path, entry.url))).status, 404);
    }
    const post = await fetch(entry.url, { method: "POST" });
    assert.equal(post.status, 405);
    assert.equal(post.headers.get("allow"), "GET");

    const errors = t.mock.method(console, "error", () => {});
    await rm(second);
    const failure = await fetch(entry.url);
    assert.equal(failure.status, 500);
    assert.match(await failure.text(), /Unable to render/);
    assert.equal(errors.mock.callCount(), 1);
});
