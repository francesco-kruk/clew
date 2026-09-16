import { createServer } from "node:http";
import { randomUUID } from "node:crypto";
import { renderDocument, readAsset } from "./renderer.mjs";

export async function startServer(path) {
    const entry = { path };
    const prefix = `/${randomUUID()}/`;
    const server = createServer(async (req, res) => {
        res.setHeader("Cache-Control", "no-store");
        res.setHeader("X-Content-Type-Options", "nosniff");
        res.setHeader("Content-Security-Policy", "default-src 'none'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'");
        try {
            if (req.method !== "GET") {
                res.writeHead(405, { Allow: "GET" }).end("Method not allowed");
                return;
            }
            if (req.url === prefix) {
                const html = await renderDocument(entry.path);
                res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }).end(html);
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
