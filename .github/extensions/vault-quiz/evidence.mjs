import { lstat, mkdir, open, readFile, readdir, unlink } from "node:fs/promises";
import { join } from "node:path";
import { isDeepStrictEqual } from "node:util";

const queues = new Map();

async function inspect(path) {
    try {
        const info = await lstat(path);
        if (info.isSymbolicLink()) throw new Error("Learner-model storage cannot use symlinks or junctions.");
        return info;
    } catch (error) {
        if (error.code === "ENOENT") return null;
        throw error;
    }
}

async function directory(parent, name, create = false) {
    const path = join(parent, name);
    let info = await inspect(path);
    if (!info && create) {
        try {
            await mkdir(path);
        } catch (error) {
            if (error.code !== "EEXIST") throw error;
        }
        info = await inspect(path);
    }
    if (!info) return null;
    if (!info.isDirectory()) throw new Error("Learner-model storage requires directories, not files.");
    return path;
}

async function provenanceRoot(root, create = false) {
    const model = await directory(root, "model", create);
    return model ? directory(model, "provenance", create) : null;
}

export function quizObservation(record) {
    return {
        id: `obs-quiz-${record.quizId}`,
        timestamp: record.submittedAt,
        session: null,
        type: "supplied-work",
        tier: 1,
        context: {
            artifact: `[[Quizzes/quiz-${record.quizId}]]`,
            concept: null,
            item: null,
        },
        content: "Submitted three ungraded written answers. The linked quiz artifact contains the questions, topic, and verbatim responses. No assessment or learner-attribute update was performed.",
        informs: [],
        tombstoned: false,
        tombstone_reason: null,
    };
}

function ledgerPath(root, record) {
    if (!/^\d{4}-\d{2}-\d{2}T/.test(record.submittedAt) || !Number.isFinite(Date.parse(record.submittedAt))) {
        throw new Error("Quiz submission timestamp is invalid.");
    }
    return join(root, "model", "provenance", record.submittedAt.slice(0, 4), `${record.submittedAt.slice(5, 7)}.jsonl`);
}

async function ledgerText(path) {
    const info = await inspect(path);
    if (!info) return "";
    if (!info.isFile() || info.nlink > 1) throw new Error("Provenance ledger must be a regular, unshared file.");
    return readFile(path, "utf8");
}

function entries(text) {
    const result = [];
    for (const line of text.split(/\r?\n/)) {
        if (!line.trim()) continue;
        let entry;
        try {
            entry = JSON.parse(line);
        } catch {
            // Never return a JSON parser error containing private ledger text.
            throw new Error("The provenance ledger contains invalid JSONL. It has not been rewritten; repair it before retrying.");
        }
        if (!entry || typeof entry !== "object" || Array.isArray(entry) || typeof entry.id !== "string") {
            throw new Error("The provenance ledger contains an entry without a valid ID.");
        }
        result.push(entry);
    }
    return result;
}

async function findObservation(provenance, observation) {
    let found = null;
    if (!provenance) return found;
    for (const year of await readdir(provenance)) {
        if (!/^\d{4}$/.test(year)) continue;
        const yearPath = await directory(provenance, year);
        if (!yearPath) continue;
        for (const month of await readdir(yearPath)) {
            if (!/^(0[1-9]|1[0-2])\.jsonl$/.test(month)) continue;
            const path = join(yearPath, month);
            for (const entry of entries(await ledgerText(path))) {
                if (entry.id !== observation.id) continue;
                if (found || !isDeepStrictEqual(entry, observation)) {
                    throw new Error("The quiz observation ID conflicts with existing evidence. No ledger entry was overwritten.");
                }
                found = path;
            }
        }
    }
    return found;
}

export function evidenceError(error) {
    return error.code ? `Local ledger operation failed (${error.code}).` : error.message;
}

export async function evidenceStatus(root, record) {
    if (!record) return { status: "not-submitted", observationId: null, ledgerPath: null };
    if (record.version !== 2) return { status: "not-requested", observationId: null, ledgerPath: null };
    const observation = quizObservation(record);
    const target = ledgerPath(root, record);
    try {
        const found = await findObservation(await provenanceRoot(root), observation);
        if (found && found !== target) throw new Error("Quiz evidence is stored outside its submission month; no duplicate will be appended.");
        return { status: found ? "recorded" : "pending", observationId: observation.id, ledgerPath: target };
    } catch (error) {
        return { status: "error", observationId: observation.id, ledgerPath: target, error: evidenceError(error) };
    }
}

async function append(root, record) {
    const target = ledgerPath(root, record);
    const observation = quizObservation(record);
    const provenance = await provenanceRoot(root, true);
    const lockPath = join(provenance, ".quiz-evidence.lock");
    let lock;
    try {
        lock = await open(lockPath, "wx");
    } catch (error) {
        if (error.code === "EEXIST") throw new Error("The learner ledger is locked by another writer. Retry after it finishes; a stale lock needs manual investigation.");
        throw error;
    }
    try {
        const found = await findObservation(provenance, observation);
        if (found && found !== target) throw new Error("Quiz evidence already exists outside its submission month. No duplicate was appended.");
        await directory(provenance, record.submittedAt.slice(0, 4), true);
        const previous = await ledgerText(target);
        const file = await open(target, "a");
        try {
            if (!found) {
                await file.writeFile(`${previous && !previous.endsWith("\n") ? "\n" : ""}${JSON.stringify(observation)}\n`, "utf8");
            }
            await file.sync();
        } finally {
            await file.close();
        }
        const saved = entries(await ledgerText(target)).filter((entry) => entry.id === observation.id);
        if (saved.length !== 1 || !isDeepStrictEqual(saved[0], observation)) {
            throw new Error("Learner evidence could not be verified after append. Existing bytes were preserved; inspect the ledger before retrying.");
        }
    } finally {
        await lock.close();
        await unlink(lockPath);
    }
}

export async function appendQuizEvidence(root, record) {
    if (record.version !== 2) return;
    // Serialize this provider's writers; the file lock also protects cooperating processes.
    const next = (queues.get(root) ?? Promise.resolve()).then(() => append(root, record), () => append(root, record));
    queues.set(root, next);
    try {
        await next;
    } finally {
        if (queues.get(root) === next) queues.delete(root);
    }
}
