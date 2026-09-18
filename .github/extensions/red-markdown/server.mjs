import { createServer } from "node:http";
import { randomUUID } from "node:crypto";
import { readFile } from "node:fs/promises";
import { renderDocument, readAsset } from "./renderer.mjs";

export async function startServer(path, { onQuizRequested } = {}) {
    const entry = { path };
    const prefix = `/${randomUUID()}/`;
    const script = await readFile(new URL("./quiz-button.mjs", import.meta.url));
    let pageRequest;
    const server = createServer(async (req, res) => {
        res.setHeader("Cache-Control", "no-store");
        res.setHeader("X-Content-Type-Options", "nosniff");
        res.setHeader("Content-Security-Policy", "default-src 'none'; script-src 'self'; connect-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'");
        const json = (code, body) => res.writeHead(code, { "Content-Type": "application/json; charset=utf-8" }).end(JSON.stringify(body));
        try {
            const host = `127.0.0.1:${server.address().port}`;
            if (req.headers.host !== host || (req.headers.origin && req.headers.origin !== `http://${host}`)) {
                json(403, { error: "Only same-origin local requests are allowed." });
                return;
            }
            if (req.method === "POST" && req.url === `${prefix}quiz`) {
                const request = pageRequest;
                if (!request || req.headers["x-quiz-token"] !== request.token) {
                    json(403, { error: "Invalid or expired quiz request. Refresh this reader." });
                    return;
                }
                if (request.path !== entry.path) {
                    json(409, { error: "The displayed document changed. Refresh this reader before requesting a quiz." });
                    return;
                }
                if (!onQuizRequested) {
                    json(503, { error: "Quiz requests are unavailable in this reader." });
                    return;
                }
                // One dispatch per rendered page, including concurrent clicks and network retries.
                if (!request.pending) {
                    request.pending = Promise.resolve().then(async () => {
                        await onQuizRequested(request.path);
                    }).catch((error) => {
                        request.pending = null;
                        throw error;
                    });
                }
                await request.pending;
                json(202, { status: "requested" });
                return;
            }
            if (req.method !== "GET") {
                res.writeHead(405, { Allow: "GET" }).end("Method not allowed");
                return;
            }
            if (req.url === prefix) {
                const request = { path: entry.path, token: randomUUID(), pending: null };
                const html = await renderDocument(request.path, { quizToken: request.token, quizEnabled: Boolean(onQuizRequested) });
                pageRequest = request;
                res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }).end(html);
                return;
            }
            if (req.url === `${prefix}quiz-button.mjs`) {
                res.writeHead(200, { "Content-Type": "text/javascript; charset=utf-8" }).end(script);
                return;
            }
            if (req.url?.startsWith(prefix)) {
                const asset = await readAsset(req.url.slice(prefix.length));
                if (asset) {
                    res.writeHead(200, { "Content-Type": asset.type }).end(asset.data);
                    return;
                }
            }
            res.writeHead(404).end("Not found");
        } catch (error) {
            console.error("Markdown canvas request failed:", error);
            if (req.method === "POST") {
                json(500, { error: "Could not send the quiz request to Copilot. Try again; see the extension log if it keeps failing." });
                return;
            }
            res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
            res.end("Unable to render the document. See the extension log for details.");
        }
    });
    await new Promise((resolve, reject) => {
        server.once("error", reject);
        server.listen(0, "127.0.0.1", () => {
            server.removeListener("error", reject);
            resolve();
        });
    });
    return Object.assign(entry, { server, url: `http://127.0.0.1:${server.address().port}${prefix}` });
}
