import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { validateMap, multiply, grade } from "./validate.mjs";

const original = JSON.parse(await readFile(new URL("./map.json", import.meta.url), "utf8"));
async function rejects(change, expected) {
    const map = structuredClone(original);
    change(map);
    const errors = await validateMap(map);
    assert.ok(errors.some(error => expected.test(error)), `Expected ${expected}, got ${JSON.stringify(errors)}`);
}

test("the entire exported bundle validates", async () => {
    assert.deepEqual(await validateMap(original), []);
    assert.equal(original.nodes.length, 14);
    assert.equal(original.categories.length, 4);
    assert.equal(original.edges.length, 15);
    assert.equal(original.nodes.reduce((sum, node) => sum + node.presets.length, 0), 12);
    assert.ok(original.edges.every(edge => edge.type === "suggested-next"));
});
test("all original products and checkpoint answers are preserved", () => {
    const expected = [
        [[12]], [[9]], [[4, 5], [10, 11]], [[4], [7]], [[10, 4], [6, -1]],
        [[2, 1], [1, 1]], [[2, -1, 4], [3, 5, 0]], [[2, 6], [-2, -4]],
        [[3, 4], [1, 2], [5, 6]], [[-1], [2]], [[4], [11]], [[1, 0], [0, 1]],
        [[11]], [[3, 4], [6, 8], [-3, -4]],
    ];
    const answers = [-10, 0, "3 × 4", "[2, 1]ᵀ", -1, "Only AB exists", "I₃ (3 × 3)", 12, "I₂", "[0, 2]ᵀ", "CᵀBᵀAᵀ", "No", "(AB)C = A(BC)", "4 × 3"];
    original.readingOrder.forEach((id, i) => {
        const node = original.nodes.find(item => item.id === id);
        assert.deepEqual(multiply(node.example.A, node.example.B), expected[i]);
        assert.equal(node.checkpoint.answer, answers[i]);
        assert.ok(grade(node.checkpoint, answers[i]));
        assert.equal(grade(node.checkpoint, ""), false);
    });
    for (const answer of [" ", "Infinity", "NaN", null, [], false, {}]) assert.equal(grade(original.nodes[1].checkpoint, answer), false);
    assert.equal(grade(original.nodes[1].checkpoint, "0.0000000001"), true);
    assert.equal(grade(original.nodes[1].checkpoint, "0.01"), false);
});
test("schema rejects incomplete maps and accidental personal state", async () => {
    await rejects(map => { map.schemaVersion = 2; }, /constant/);
    await rejects(map => { delete map.categories; }, /categories/);
    await rejects(map => { map.nodes[0].progress = { passed: true }; }, /additional properties/);
    await rejects(map => { map.readingOrder.push("one"); }, /duplicate items/);
    await rejects(map => { map.edges[0].type = "unknown"; }, /allowed values/);
});
test("IDs, categories, reading order, and edges are checked", async () => {
    await rejects(map => { map.nodes[1].id = "one"; }, /Duplicate node ID/);
    await rejects(map => { map.categories[1].id = "the-rule"; }, /Duplicate category ID/);
    await rejects(map => { map.nodes[0].categoryId = "missing"; }, /Unknown category/);
    await rejects(map => { map.startNode = "missing"; }, /Unknown startNode/);
    await rejects(map => { map.readingOrder.pop(); }, /missing from readingOrder/);
    await rejects(map => { map.edges[0].to = "missing"; }, /Unknown edge endpoint/);
    await rejects(map => { map.edges.push(map.edges[0]); }, /Duplicate edge/);
    await rejects(map => { map.edges[0].to = "one"; }, /Self-edge/);
    await rejects(map => { map.edges = []; }, /unreachable/);
    await rejects(map => {
        map.edges.push({ from: "one", to: "dot", type: "prerequisite" }, { from: "dot", to: "one", type: "prerequisite" });
    }, /Prerequisite edges contain a cycle/);
});
test("related edges are undirected, not prerequisites", async () => {
    const map = structuredClone(original);
    map.edges.push({ from: "diagonal", to: "geometry", type: "related" });
    assert.deepEqual(await validateMap(map), []);
    await rejects(next => {
        next.edges.push({ from: "diagonal", to: "geometry", type: "related" }, { from: "geometry", to: "diagonal", type: "related" });
    }, /Duplicate edge/);
});
test("content references are local, nonempty, and resolve to the right lesson", async () => {
    await rejects(map => { map.nodes[0].content = "../outside.md"; }, /pattern/);
    await rejects(map => { map.nodes[0].content = "https://example.com/lesson.md"; }, /pattern/);
    await rejects(map => { map.nodes[0].content = "lessons/missing.md"; }, /Cannot read/);
    await rejects(map => { map.nodes[0].content = "lessons/dot.md"; }, /mismatched lesson title/);
});
test("matrix and checkpoint corruption fails explicitly", async () => {
    await rejects(map => { map.nodes[0].example.expectedProduct = [[13]]; }, /Incorrect expectedProduct/);
    await rejects(map => { map.nodes[2].example.A[0].pop(); }, /Ragged/);
    await rejects(map => { map.nodes[0].example.A[0][0] = Infinity; }, /must be number/);
    await rejects(map => { map.nodes[2].presets[2].expectedProduct = [[0]]; }, /Incorrect expectedProduct/);
    await rejects(map => { map.nodes[2].checkpoint.answer = "5 × 5"; }, /Answer is not an option/);
    await rejects(map => { map.nodes[0].checkpoint.tolerance = 0; }, /must be >/);
    await rejects(map => { map.nodes[0].interactions.push("coordinate-view"); }, /coordinate-view requires/);
});
test("layout is optional and ordering does not depend on array positions", async () => {
    const map = structuredClone(original);
    delete map.layout;
    map.nodes.forEach(node => { delete node.layout; });
    map.categories.forEach(category => { delete category.layout; });
    map.nodes.reverse();
    map.categories.reverse();
    assert.deepEqual(await validateMap(map), []);
});
