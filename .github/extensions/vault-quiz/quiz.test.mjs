import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, readFile, readdir, rm, symlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { openQuiz, resolveSource } from "./quiz.mjs";
import { startServer, closeServer } from "./server.mjs";
import { appendQuizEvidence, evidenceStatus, quizObservation } from "./evidence.mjs";

async function fixture(t, marker = true) {
    const root = await mkdtemp(join(tmpdir(), "clew-quiz-"));
    t.after(() => rm(root, { recursive: true, force: true }));
    if (marker) await mkdir(join(root, ".obsidian"));
    await mkdir(join(root, "Lessons"));
    const sourcePath = join(root, "Lessons", "Angles.md");
    await writeFile(sourcePath, "# Angles\nA right angle is 90 degrees.\nA straight angle is 180 degrees.\nA full turn is 360 degrees.\n");
    const input = {
        sourcePath, quizId: "synthetic-quiz-001", topic: "Angles",
        questions: [
            { concept: "Right angle", prompt: "How many degrees are in a right angle?", sourceExcerpt: "A right angle is 90 degrees.", suggestedAnswer: "90 degrees." },
            { concept: "Straight angle", prompt: "How many right angles make a straight angle?", sourceExcerpt: "A straight angle is 180 degrees.", suggestedAnswer: "Two, since 180 / 90 = 2." },
            { concept: "Full turn", prompt: "How many right angles make a full turn?", sourceExcerpt: "A full turn is 360 degrees.", suggestedAnswer: "Four, since 360 / 90 = 4." },
        ],
    };
    return { root, input };
}

test("discovers source vault, hides solutions and saves exactly three verbatim answers", async (t) => {
    const { root, input } = await fixture(t);
    const original = await readFile(input.sourcePath, "utf8");
    const quiz = await openQuiz(input);
    const before = await quiz.state();
    assert.equal(before.vaultRoot, root);
    assert.equal(before.questions.length, 3);
    assert.equal(before.questions[0].suggestedAnswer, undefined);
    assert.equal((await readdir(root)).includes("Quizzes"), false);
    assert.equal((await readdir(root)).includes("model"), false);
    const answers = ["  90°\nwith working  ", "```json\n{\"test\": true}\n```\n[[untrusted]]", "四\n</textarea><script>alert(1)</script>"];
    const state = await quiz.submit(answers);
    assert.equal(state.submitted, true);
    assert.deepEqual(state.questions.map((q) => q.answer), answers);
    assert.equal(state.questions[0].suggestedAnswer, "90 degrees.");
    assert.equal(state.assessment, "ungraded");
    assert.equal(state.learnerModel.status, "recorded");
    const ledger = await readFile(state.learnerModel.ledgerPath, "utf8");
    const observation = JSON.parse(ledger.trim());
    assert.deepEqual(Object.keys(observation), ["id", "timestamp", "session", "type", "tier", "context", "content", "informs", "tombstoned", "tombstone_reason"]);
    assert.equal(observation.id, `obs-quiz-${input.quizId}`);
    assert.equal(observation.type, "supplied-work");
    assert.equal(observation.tier, 1);
    assert.equal(observation.session, null);
    assert.equal(observation.context.artifact, `[[Quizzes/quiz-${input.quizId}]]`);
    assert.deepEqual(observation.informs, []);
    assert.equal(observation.tombstoned, false);
    assert.equal(ledger.includes(answers[0]), false);
    assert.deepEqual(await readdir(join(root, "model")), ["provenance"]);
    assert.equal((await quiz.status()).answers, undefined);
    const saved = await readFile(state.savedPath, "utf8");
    assert.match(saved, /\[\[Lessons\/Angles\]\]/);
    assert.match(saved, /submitted_at:/);
    assert.match(saved, /sourceSha256/);
    assert.equal(await readFile(input.sourcePath, "utf8"), original);
    const reopened = await openQuiz(input);
    assert.deepEqual((await reopened.state()).questions.map((q) => q.answer), answers);
    await reopened.submit(answers);
    assert.equal(await readFile(state.learnerModel.ledgerPath, "utf8"), ledger);
    assert.equal((await readdir(join(root, "Quizzes"))).length, 1);
    await assert.rejects(reopened.submit(["changed", "2", "4"]), /already submitted/);
    await assert.rejects(openQuiz({ ...input, topic: "Different" }), /conflicts/);
});

test("requires confirmed roots when marker is absent and rejects mismatched vaults", async (t) => {
    const { root, input } = await fixture(t, false);
    await assert.rejects(openQuiz(input), /No .obsidian/);
    assert.equal((await (await openQuiz({ ...input, vaultRoot: root })).status()).vaultRoot, root);
    await assert.rejects(resolveSource(input.sourcePath, join(root, "Lessons", "Angles.md")), /outside/);
    await mkdir(join(root, ".obsidian"));
    await assert.rejects(openQuiz({ ...input, vaultRoot: join(root, "Lessons") }), /conflicts/);
    await assert.rejects(resolveSource("relative.md"), /absolute/);
});

test("rejects wrong question counts, unsupported grounding, invalid IDs and incomplete answers", async (t) => {
    const { root, input } = await fixture(t);
    await assert.rejects(openQuiz({ ...input, questions: input.questions.slice(0, 2) }), /exactly three/);
    await assert.rejects(openQuiz({ ...input, quizId: "../escape" }), /Invalid quiz ID/);
    await assert.rejects(openQuiz({ ...input, questions: input.questions.map((q) => ({ ...q, sourceExcerpt: "Not in the note" })) }), /verbatim/);
    const quiz = await openQuiz(input);
    await assert.rejects(quiz.submit(["1", "2"]), /all three/);
    await assert.rejects(quiz.submit(["1", " ", "3"]), /nonempty/);
    await assert.rejects(quiz.submit(["x".repeat(16001), "2", "3"]), /16000/);
    assert.equal((await readdir(root)).includes("Quizzes"), false);
});

test("concurrent submissions and independent quiz attempts never overwrite answers", async (t) => {
    const { root, input } = await fixture(t);
    const first = await openQuiz(input);
    const second = await openQuiz(input);
    const results = await Promise.allSettled([first.submit(["90", "2", "4"]), second.submit(["wrong", "wrong", "wrong"])]);
    assert.equal(results.filter((r) => r.status === "fulfilled").length, 1);
    assert.equal(results.filter((r) => r.status === "rejected").length, 1);
    const newAttempt = await openQuiz({ ...input, quizId: "synthetic-quiz-002" });
    await newAttempt.submit(["90", "2", "4"]);
    assert.equal((await readdir(join(root, "Quizzes"))).length, 2);
});

test("does not follow a Quizzes junction outside the vault or replace corrupt records", async (t) => {
    const { root, input } = await fixture(t);
    const outside = await mkdtemp(join(tmpdir(), "clew-quiz-outside-"));
    t.after(() => rm(outside, { recursive: true, force: true }));
    await symlink(outside, join(root, "Quizzes"), process.platform === "win32" ? "junction" : "dir");
    await assert.rejects(openQuiz(input), /not a symlink/);
    assert.deepEqual(await readdir(outside), []);
    await rm(join(root, "Quizzes"));
    await mkdir(join(root, "Quizzes"));
    const target = join(root, "Quizzes", `quiz-${input.quizId}.md`);
    await writeFile(target, "Existing unrelated note");
    await assert.rejects(openQuiz(input), /not readable/);
    assert.equal(await readFile(target, "utf8"), "Existing unrelated note");
});

test("HTTP serves accessible quiz UI, guards submission, and exposes suggestions only after saving", async (t) => {
    const { input } = await fixture(t);
    const entry = await startServer(await openQuiz(input));
    t.after(() => closeServer(entry.server));
    const html = await (await fetch(entry.url)).text();
    assert.match(html, /aria-live="polite"/);
    assert.match(html, /Submit and save answers/);
    const token = /name="quiz-token" content="([^"]+)"/.exec(html)[1];
    const initial = await (await fetch(`${entry.url}state`)).json();
    assert.equal(initial.questions[0].suggestedAnswer, undefined);
    const headers = { "Content-Type": "application/json", "X-Quiz-Token": token };
    const body = JSON.stringify({ answers: ["90", "2", "4"] });
    assert.equal((await fetch(`${entry.url}submit`, { method: "POST", body })).status, 403);
    assert.equal((await fetch(`${entry.url}submit`, { method: "POST", headers: { ...headers, Origin: "https://example.com" }, body })).status, 403);
    assert.equal((await fetch(`${entry.url}submit`, { method: "POST", headers, body: "{" })).status, 400);
    assert.equal((await fetch(`${entry.url}submit`, { method: "POST", headers, body: JSON.stringify({ answers: ["one"] }) })).status, 400);
    assert.equal((await fetch(new URL("/state", entry.url))).status, 404);
    const response = await fetch(`${entry.url}submit`, { method: "POST", headers, body });
    assert.equal(response.status, 200);
    const saved = await response.json();
    assert.equal(saved.submitted, true);
    assert.equal(saved.learnerModel.status, "recorded");
    assert.equal(saved.questions[0].suggestedAnswer, "90 degrees.");
    assert.equal((await fetch(`${entry.url}submit`, { method: "POST", headers, body })).status, 200);
});

test("simultaneous identical submissions append one observation only", async (t) => {
    const { input } = await fixture(t);
    const first = await openQuiz(input);
    const second = await openQuiz(input);
    const results = await Promise.all([first.submit(["90", "2", "4"]), second.submit(["90", "2", "4"])]);
    assert(results.every((result) => result.learnerModel.status === "recorded"));
    const lines = (await readFile(results[0].learnerModel.ledgerPath, "utf8")).trim().split("\n");
    assert.equal(lines.length, 1);
});

test("an unavailable ledger leaves a durable quiz and supports retry after reopening", async (t) => {
    const { root, input } = await fixture(t);
    await writeFile(join(root, "model"), "Blocking fixture file");
    const entry = await startServer(await openQuiz(input));
    t.after(() => closeServer(entry.server));
    const html = await (await fetch(entry.url)).text();
    const token = /name="quiz-token" content="([^"]+)"/.exec(html)[1];
    const response = await fetch(`${entry.url}submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Quiz-Token": token },
        body: JSON.stringify({ answers: ["90", "2", "4"] }),
    });
    assert.equal(response.status, 400);
    const failure = await response.json();
    assert.equal(failure.quizSaved, true);
    assert.match(failure.error, /answers are saved/);
    const reopened = await openQuiz(input);
    const partial = await reopened.state();
    assert.equal(partial.submitted, true);
    assert.equal(partial.learnerModel.status, "error");
    const original = await readFile(partial.savedPath, "utf8");
    await rm(join(root, "model"));
    const retried = await reopened.submit(["90", "2", "4"]);
    assert.equal(retried.learnerModel.status, "recorded");
    assert.equal(await readFile(retried.savedPath, "utf8"), original);
    await reopened.submit(["90", "2", "4"]);
    assert.equal((await readFile(retried.learnerModel.ledgerPath, "utf8")).trim().split("\n").length, 1);
});

test("ledger appends preserve history, use submission month and reject collisions or malformed private data", async (t) => {
    const { root } = await fixture(t);
    const record = { version: 2, quizId: "year-boundary-quiz", submittedAt: "2025-12-31T23:59:59.000Z" };
    const target = join(root, "model", "provenance", "2025", "12.jsonl");
    await mkdir(join(root, "model", "provenance", "2025"), { recursive: true });
    const prior = JSON.stringify({ id: "existing-observation", content: "Existing evidence" });
    await writeFile(target, prior);
    await appendQuizEvidence(root, record);
    const text = await readFile(target, "utf8");
    assert(text.startsWith(`${prior}\n`));
    assert.equal(text.trim().split("\n").length, 2);
    assert.deepEqual(JSON.parse(text.trim().split("\n")[1]), quizObservation(record));
    await appendQuizEvidence(root, record);
    assert.equal(await readFile(target, "utf8"), text);
    assert.equal((await evidenceStatus(root, record)).ledgerPath, target);
    await writeFile(target, `${prior}\n${JSON.stringify({ ...quizObservation(record), tombstoned: true })}\n`);
    await assert.rejects(appendQuizEvidence(root, record), /conflicts/);
    await writeFile(target, '{"id":"private","content":"DO-NOT-EXPOSE');
    const invalid = await evidenceStatus(root, record);
    assert.equal(invalid.status, "error");
    assert.equal(invalid.error.includes("DO-NOT-EXPOSE"), false);
    await assert.rejects(appendQuizEvidence(root, record), /invalid JSONL/);
    assert.equal(await readFile(target, "utf8"), '{"id":"private","content":"DO-NOT-EXPOSE');
});

test("does not follow model junctions, duplicate cross-month IDs, or remove someone else's lock", async (t) => {
    const { root } = await fixture(t);
    const outside = await mkdtemp(join(tmpdir(), "clew-ledger-outside-"));
    t.after(() => rm(outside, { recursive: true, force: true }));
    const record = { version: 2, quizId: "ledger-safety-quiz", submittedAt: "2026-09-18T12:00:00.000Z" };
    await symlink(outside, join(root, "model"), process.platform === "win32" ? "junction" : "dir");
    await assert.rejects(appendQuizEvidence(root, record), /symlinks/);
    assert.deepEqual(await readdir(outside), []);
    await rm(join(root, "model"));
    const provenance = join(root, "model", "provenance");
    await mkdir(join(provenance, "2026"), { recursive: true });
    const lock = join(provenance, ".quiz-evidence.lock");
    await writeFile(lock, "Other writer");
    await assert.rejects(appendQuizEvidence(root, record), /locked/);
    assert.equal(await readFile(lock, "utf8"), "Other writer");
    await rm(lock);
    const otherMonth = join(provenance, "2026", "08.jsonl");
    await writeFile(otherMonth, `${JSON.stringify(quizObservation(record))}\n`);
    await assert.rejects(appendQuizEvidence(root, record), /outside its submission month/);
    assert.equal((await evidenceStatus(root, record)).status, "error");
});

test("older saved attempts are readable but are never automatically backfilled", async (t) => {
    const { root, input } = await fixture(t);
    const quiz = await openQuiz(input);
    const state = await quiz.submit(["90", "2", "4"]);
    const markdown = await readFile(state.savedPath, "utf8");
    await writeFile(state.savedPath, markdown.replace('"version": 2', '"version": 1').replace(/\n/g, "\r\n"));
    await rm(join(root, "model"), { recursive: true });
    const legacy = await openQuiz(input);
    assert.equal((await legacy.status()).learnerModel.status, "not-requested");
    await legacy.submit(["90", "2", "4"]);
    assert.equal((await readdir(root)).includes("model"), false);
});
