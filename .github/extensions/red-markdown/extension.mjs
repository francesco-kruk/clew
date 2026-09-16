import { basename, extname } from "node:path";
import { joinSession, createCanvas, CanvasError } from "@github/copilot-sdk/extension";
import { DOCUMENT_BORDER, readDocument, resolveDocument } from "./renderer.mjs";
import { startServer } from "./server.mjs";

const servers = new Map();

await joinSession({
    canvases: [createCanvas({
        id: "red-markdown",
        displayName: "Red-bordered Markdown",
        description: "Display a local Markdown file by absolute path, with equations, local images, and a red border.",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string", minLength: 1, description: "Absolute path to a local .md or .markdown file." },
            },
            required: ["path"],
            additionalProperties: false,
        },
        actions: [{
            name: "get_document",
            description: "Read the displayed Markdown and presentation settings.",
            inputSchema: { type: "object", properties: {}, additionalProperties: false },
            handler: async (ctx) => {
                const entry = await servers.get(ctx.instanceId);
                if (!entry) throw new CanvasError("document_not_open", "Open a Markdown file first.");
                return {
                    path: entry.path,
                    markdown: await readDocument(entry.path),
                    border: DOCUMENT_BORDER,
                };
            },
        }],
        open: async (ctx) => {
            let path;
            try {
                path = await resolveDocument(ctx.input.path);
            } catch (error) {
                throw new CanvasError("document_unavailable", error.message);
            }
            // Cache startup too, so concurrent opens cannot leak a second server.
            if (!servers.has(ctx.instanceId)) {
                const pending = startServer(path).catch((error) => {
                    servers.delete(ctx.instanceId);
                    throw error;
                });
                servers.set(ctx.instanceId, pending);
            }
            const entry = await servers.get(ctx.instanceId);
            entry.path = path;
            return { title: basename(path, extname(path)), url: entry.url };
        },
        onClose: async (ctx) => {
            const pending = servers.get(ctx.instanceId);
            if (!pending) return;
            servers.delete(ctx.instanceId);
            const { server } = await pending;
            await new Promise((resolve, reject) => {
                server.close((error) => error ? reject(error) : resolve());
                server.closeIdleConnections();
            });
        },
    })],
});
