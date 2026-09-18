import { joinSession, createCanvas, CanvasError } from "@github/copilot-sdk/extension";
import { openQuiz, inputSchema } from "./quiz.mjs";
import { startServer, closeServer } from "./server.mjs";

const servers = new Map();

await joinSession({
    canvases: [createCanvas({
        id: "vault-quiz",
        displayName: "Obsidian note quiz",
        description: "Answer three questions about an Obsidian note and save your answers in its vault.",
        inputSchema,
        actions: [{
            name: "get_status",
            description: "Read quiz topic, source, submission status and saved path, without exposing learner answers.",
            inputSchema: { type: "object", properties: {}, additionalProperties: false },
            handler: async (ctx) => {
                const entry = await servers.get(ctx.instanceId);
                if (!entry) throw new CanvasError("quiz_not_open", "Open a quiz first.");
                return entry.quiz.status();
            },
        }],
        open: async (ctx) => {
            if (!servers.has(ctx.instanceId)) {
                const pending = openQuiz(ctx.input).then(startServer).catch((error) => {
                    servers.delete(ctx.instanceId);
                    throw new CanvasError("quiz_unavailable", error.message);
                });
                servers.set(ctx.instanceId, pending);
            }
            const entry = await servers.get(ctx.instanceId);
            return { title: `Quiz: ${entry.quiz.topic}`, url: entry.url };
        },
        onClose: async (ctx) => {
            const pending = servers.get(ctx.instanceId);
            if (!pending) return;
            servers.delete(ctx.instanceId);
            await closeServer((await pending).server);
        },
    })],
});
