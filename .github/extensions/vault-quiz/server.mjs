import { createServer } from "node:http";
import { randomUUID } from "node:crypto";
import { readFile } from "node:fs/promises";

export async function startServer(quiz) {
    const prefix = `/${randomUUID()}/`;
    const token = randomUUID();
    const html = (await readFile(new URL("./ui.html", import.meta.url), "utf8")).replace("__TOKEN__", token);
    const script = await readFile(new URL("./ui.mjs", import.meta.url));
    const server = createServer(async (req, res) => {
        res.setHeader("Cache-Control", "no-store");
        res.setHeader("X-Content-Type-Options", "nosniff");
        res.setHeader("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'");
        const json = (status, body) => res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" }).end(JSON.stringify(body));
        try {
            const origin = `http://127.0.0.1:${server.address().port}`;
            if (req.headers.host !== `127.0.0.1:${server.address().port}` ||
                (req.headers.origin && req.headers.origin !== origin)) {
                json(403, { error: "Only same-origin local requests are allowed." });
                return;
            }
            if (req.method === "GET" && req.url === prefix) {
                res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }).end(html);
            } else if (req.method === "GET" && req.url === `${prefix}ui.mjs`) {
                res.writeHead(200, { "Content-Type": "text/javascript; charset=utf-8" }).end(script);
            } else if (req.method === "GET" && req.url === `${prefix}state`) {
                json(200, await quiz.state());
            } else if (req.method === "POST" && req.url === `${prefix}submit`) {
                if (req.headers["x-quiz-token"] !== token || req.headers["content-type"] !== "application/json") {
                    json(403, { error: "Invalid submission token or content type." });
                    return;
                }
                let length = 0;
                const chunks = [];
                for await (const chunk of req) {
                    length += chunk.length;
                    if (length > 300000) {
                        json(413, { error: "Submission is too large." });
                        return;
                    }
                    chunks.push(chunk);
                }
                let body;
                try {
                    body = JSON.parse(Buffer.concat(chunks).toString("utf8"));
                } catch {
                    json(400, { error: "Submission must contain valid JSON." });
                    return;
                }
                json(200, await quiz.submit(body?.answers));
            } else {
                json(404, { error: "Not found." });
            }
        } catch (error) {
            console.error("Quiz request failed:", error.message);
            json(400, { error: error.message, quizSaved: error.quizSaved === true });
        }
    });
    await new Promise((resolve, reject) => {
        server.once("error", reject);
        server.listen(0, "127.0.0.1", () => {
            server.removeListener("error", reject);
            resolve();
        });
    });
    return { quiz, server, url: `http://127.0.0.1:${server.address().port}${prefix}` };
}

export async function closeServer(server) {
    await new Promise((resolve, reject) => {
        server.close((error) => error ? reject(error) : resolve());
        server.closeIdleConnections();
    });
}
