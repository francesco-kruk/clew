import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { request as httpRequest } from "node:http";
import { startServer } from "./server.mjs";
import { createQuizRequester } from "./quiz-request.mjs";

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
    assert.match(response.headers.get("content-security-policy"), /script-src 'self'; connect-src 'self'/);
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
    const script = await fetch(new URL("quiz-button.mjs", entry.url));
    assert.equal(script.status, 200);
    assert.match(script.headers.get("content-type"), /javascript/);
    assert.match(await script.text(), /fetch\("\.\/quiz"/);
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

test("quiz button dispatches only the selected document and deduplicates a page's requests", async (t) => {
    const root = await mkdtemp(join(tmpdir(), "red-markdown-quiz-"));
    const entries = [];
    t.after(async () => {
        await Promise.all(entries.map(({ server }) => new Promise((resolve) => {
            server.close(resolve);
            server.closeAllConnections();
        })));
        await rm(root, { recursive: true, force: true });
    });
    const first = join(root, "first.md");
    const second = join(root, "second.md");
    await writeFile(first, "# First\n\nDO_NOT_SEND_NOTE_CONTENT");
    await writeFile(second, "# Second");
    const messages = [];
    const session = { send: async (message) => { messages.push(message); return `message-${messages.length}`; } };
    const request = (instanceId) => createQuizRequester(() => session, { extensionId: "project:red-markdown", instanceId });
    entries.push(
        await startServer(first, { onQuizRequested: request("reader-first") }),
        await startServer(second, { onQuizRequested: request("reader-second") }),
    );
    const [entry, other] = entries;
    const token = async (item) => /name="quiz-token" content="([^"]+)"/.exec(await (await fetch(item.url)).text())[1];
    const firstToken = await token(entry);
    const otherToken = await token(other);
    assert.equal(messages.length, 0);
    const post = (item, key, extra = {}) => fetch(new URL("quiz", item.url), {
        method: "POST", headers: { "X-Quiz-Token": key, ...extra },
    });
    assert.equal((await post(entry, "wrong")).status, 403);
    assert.equal((await post(entry, otherToken)).status, 403);
    assert.equal((await post(entry, firstToken, { Origin: "https://example.com" })).status, 403);
    const wrongHost = await new Promise((resolve, reject) => {
        const request = httpRequest(new URL("quiz", entry.url), {
            method: "POST", headers: { Host: "example.com", "X-Quiz-Token": firstToken },
        }, (response) => {
            response.resume();
            resolve(response.statusCode);
        });
        request.on("error", reject);
        request.end();
    });
    assert.equal(wrongHost, 403);
    assert.equal(messages.length, 0);
    const results = await Promise.all([post(entry, firstToken), post(entry, firstToken)]);
    assert(results.every((response) => response.status === 202));
    assert.equal(messages.length, 1);
    assert.equal(messages[0].mode, "immediate");
    assert.match(messages[0].prompt, /"canvas-quiz" skill/);
    assert.match(messages[0].prompt, /get_document/);
    assert.equal(messages[0].attachments, undefined);
    assert.equal(messages[0].prompt.includes("DO_NOT_SEND_NOTE_CONTENT"), false);
    const selected = JSON.parse(messages[0].prompt.split("\n")[2]);
    assert.deepEqual(selected, { extensionId: "project:red-markdown", canvasId: "red-markdown", instanceId: "reader-first", sourcePath: first });
    assert.equal((await post(other, otherToken)).status, 202);
    assert.equal(JSON.parse(messages[1].prompt.split("\n")[2]).sourcePath, second);
    const refreshed = await token(entry);
    assert.equal((await post(entry, firstToken)).status, 403);
    entry.path = second;
    assert.equal((await post(entry, refreshed)).status, 409);
    assert.equal(messages.length, 2);
    assert.equal((await post(entry, await token(entry))).status, 202);
    assert.equal(JSON.parse(messages[2].prompt.split("\n")[2]).sourcePath, second);
});

test("failed quiz dispatch is explicit and retryable, without claiming creation", async (t) => {
    const root = await mkdtemp(join(tmpdir(), "red-markdown-quiz-error-"));
    const path = join(root, "note.md");
    await writeFile(path, "# Note");
    let session;
    const errors = t.mock.method(console, "error", () => {});
    const entry = await startServer(path, { onQuizRequested: createQuizRequester(() => session, { extensionId: "project:red-markdown", instanceId: "reader" }) });
    t.after(async () => {
        await new Promise((resolve) => {
            entry.server.close(resolve);
            entry.server.closeAllConnections();
        });
        await rm(root, { recursive: true, force: true });
    });
    const html = await (await fetch(entry.url)).text();
    const token = /name="quiz-token" content="([^"]+)"/.exec(html)[1];
    const post = () => fetch(new URL("quiz", entry.url), { method: "POST", headers: { "X-Quiz-Token": token } });
    const failure = await post();
    assert.equal(failure.status, 500);
    assert.match((await failure.json()).error, /Could not send/);
    assert.equal(errors.mock.callCount(), 1);
    session = { send: async () => undefined };
    assert.equal((await post()).status, 500);
    session = { send: async () => "confirmed-message-id" };
    assert.equal((await post()).status, 202);
    assert.equal((await post()).status, 202);
    assert.equal(errors.mock.callCount(), 2);
});
