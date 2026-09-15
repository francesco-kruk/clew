import { readFile, realpath } from "node:fs/promises";
import { dirname, isAbsolute, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";

const bundleDirectory = dirname(fileURLToPath(import.meta.url));
const schema = JSON.parse(await readFile(new URL("./map.schema.json", import.meta.url), "utf8"));
const ajv = new Ajv2020({ allErrors: true, strict: true });
const validateShape = ajv.compile(schema);

export function multiply(A, B) {
    if (A[0].length !== B.length) return null;
    return A.map(row => B[0].map((_, column) => row.reduce((sum, entry, k) => sum + entry * B[k][column], 0)));
}

export function grade(checkpoint, answer) {
    if (checkpoint.type === "single-choice") return typeof answer === "string" && answer === checkpoint.answer;
    if (typeof answer !== "number" && typeof answer !== "string") return false;
    if (typeof answer === "string" && answer.trim() === "") return false;
    const numeric = Number(answer);
    return Number.isFinite(numeric) && Math.abs(numeric - checkpoint.answer) < checkpoint.tolerance;
}

function rectangular(matrix) {
    return matrix.every(row => row.length === matrix[0].length && row.every(Number.isFinite));
}
function productsEqual(actual, expected) {
    if (actual === null || expected === null) return actual === expected;
    return actual.length === expected.length && actual[0].length === expected[0].length
        && actual.every((row, i) => row.every((entry, j) => {
            const target = expected[i][j];
            return Number.isFinite(entry) && Math.abs(entry - target) <= 1e-10 * Math.max(1, Math.abs(entry), Math.abs(target));
        }));
}
function containsCycle(ids, edges) {
    const neighbors = new Map(ids.map(id => [id, []]));
    const incoming = new Map(ids.map(id => [id, 0]));
    for (const edge of edges) {
        if (!neighbors.has(edge.from) || !neighbors.has(edge.to)) continue;
        neighbors.get(edge.from).push(edge.to);
        incoming.set(edge.to, incoming.get(edge.to) + 1);
    }
    const ready = ids.filter(id => incoming.get(id) === 0);
    let visited = 0;
    for (let cursor = 0; cursor < ready.length; cursor++) {
        visited++;
        for (const next of neighbors.get(ready[cursor])) {
            incoming.set(next, incoming.get(next) - 1);
            if (incoming.get(next) === 0) ready.push(next);
        }
    }
    return visited !== ids.length;
}

export async function validateMap(map, directory = bundleDirectory) {
    if (!validateShape(map)) return validateShape.errors.map(error => `${error.instancePath || "/"}: ${error.message}`);
    const errors = [];
    function unique(values, label) {
        const seen = new Set();
        for (const value of values) {
            if (seen.has(value)) errors.push(`Duplicate ${label}: ${value}`);
            seen.add(value);
        }
        return seen;
    }
    const nodeIds = unique(map.nodes.map(node => node.id), "node ID");
    const categoryIds = unique(map.categories.map(category => category.id), "category ID");
    unique(map.categories.map(category => category.order), "category order");
    unique(map.nodes.map(node => node.content), "content path");
    unique(map.nodes.map(node => node.checkpoint.id), "checkpoint ID");
    unique(map.edges.map(edge => {
        const ends = edge.type === "related" ? [edge.from, edge.to].sort() : [edge.from, edge.to];
        return `${edge.type}:${ends.join(":")}`;
    }), "edge");
    if (!nodeIds.has(map.startNode)) errors.push(`Unknown startNode: ${map.startNode}`);
    if (map.readingOrder[0] !== map.startNode) errors.push("The first readingOrder entry must be startNode.");
    for (const id of map.readingOrder) if (!nodeIds.has(id)) errors.push(`Unknown readingOrder node: ${id}`);
    for (const id of nodeIds) if (!map.readingOrder.includes(id)) errors.push(`Node missing from readingOrder: ${id}`);
    for (const edge of map.edges) {
        if (!nodeIds.has(edge.from) || !nodeIds.has(edge.to)) errors.push(`Unknown edge endpoint: ${edge.from} -> ${edge.to}`);
        if (edge.from === edge.to) errors.push(`Self-edge: ${edge.from}`);
    }
    if (containsCycle([...nodeIds], map.edges.filter(edge => edge.type === "prerequisite"))) errors.push("Prerequisite edges contain a cycle.");
    const learningEdges = map.edges.filter(edge => edge.type !== "related");
    const reached = new Set([map.startNode]);
    const queue = [map.startNode];
    for (let cursor = 0; cursor < queue.length; cursor++) {
        for (const edge of learningEdges.filter(item => item.from === queue[cursor])) {
            if (!reached.has(edge.to)) { reached.add(edge.to); queue.push(edge.to); }
        }
    }
    for (const id of nodeIds) if (!reached.has(id)) errors.push(`Node unreachable from startNode through learning edges: ${id}`);
    const usedCategories = new Set(map.nodes.map(node => node.categoryId));
    for (const id of categoryIds) if (!usedCategories.has(id)) errors.push(`Unused category: ${id}`);
    let root;
    try { root = await realpath(directory); }
    catch (error) { return [...errors, `Cannot open bundle directory: ${error.message}`]; }
    await Promise.all(map.nodes.map(async node => {
        if (!categoryIds.has(node.categoryId)) errors.push(`Unknown category for ${node.id}: ${node.categoryId}`);
        unique(node.presets.map(preset => preset.id), `preset ID in ${node.id}`);
        if (node.checkpoint.type === "single-choice" && !node.checkpoint.options.includes(node.checkpoint.answer)) errors.push(`Answer is not an option for ${node.id}.`);
        for (const [index, item] of [node.example, ...node.presets].entries()) {
            const label = `${node.id}/${index === 0 ? "example" : item.id}`;
            if (!rectangular(item.A) || !rectangular(item.B) || item.expectedProduct !== null && !rectangular(item.expectedProduct)) {
                errors.push(`Ragged or nonfinite matrix in ${label}.`);
                continue;
            }
            if (!productsEqual(multiply(item.A, item.B), item.expectedProduct)) errors.push(`Incorrect expectedProduct in ${label}.`);
        }
        if (node.interactions.includes("coordinate-view") && (node.example.A.length !== 2 || node.example.A[0].length !== 2 || node.example.B.length !== 2 || node.example.B[0].length !== 1)) {
            errors.push(`coordinate-view requires a 2x2 matrix and a 2x1 vector in ${node.id}.`);
        }
        try {
            const path = await realpath(resolve(directory, node.content));
            const local = relative(root, path);
            if (local === ".." || local.startsWith(`..\\`) || local.startsWith("../") || isAbsolute(local)) {
                errors.push(`Content escapes the bundle: ${node.content}`);
                return;
            }
            const content = await readFile(path, "utf8");
            if (!content.startsWith(`# ${node.title}\n`) && !content.startsWith(`# ${node.title}\r\n`)) errors.push(`Missing or mismatched lesson title: ${node.content}`);
            if (content.trim().length <= node.title.length + 2) errors.push(`Empty lesson body: ${node.content}`);
        } catch (error) {
            errors.push(`Cannot read ${node.content}: ${error.message}`);
        }
    }));
    return errors.sort();
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
    try {
        const mapPath = resolve(process.argv[2] || resolve(bundleDirectory, "map.json"));
        const map = JSON.parse(await readFile(mapPath, "utf8"));
        const errors = await validateMap(map, dirname(mapPath));
        if (errors.length) {
            process.stderr.write(errors.map(error => `- ${error}`).join("\n") + "\n");
            process.exitCode = 1;
        } else {
            process.stdout.write(`Valid: ${map.nodes.length} concepts, ${map.categories.length} categories, ${map.edges.length} edges, ${map.nodes.length} lessons and checkpoints.\n`);
        }
    } catch (error) {
        process.stderr.write(`Validation failed: ${error.message}\n`);
        process.exitCode = 1;
    }
}
