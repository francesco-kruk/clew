import { createHash, randomUUID } from "node:crypto";
import { readFile, realpath, stat, mkdir, writeFile, link, unlink } from "node:fs/promises";
import { dirname, extname, isAbsolute, join, relative, sep } from "node:path";
import { appendQuizEvidence, evidenceError, evidenceStatus } from "./evidence.mjs";

const text = (maxLength) => ({ type: "string", minLength: 1, maxLength });
export const inputSchema = {
    type: "object",
    properties: {
        sourcePath: text(4096),
        vaultRoot: { ...text(4096), description: "Only supply a user-confirmed root when automatic .obsidian discovery fails." },
        quizId: { type: "string", pattern: "^[a-zA-Z0-9][a-zA-Z0-9_-]{7,79}$" },
        topic: text(200),
        questions: {
            type: "array", minItems: 3, maxItems: 3,
            items: {
                type: "object",
                properties: {
                    concept: text(200), prompt: text(4000),
                    sourceExcerpt: text(4000), suggestedAnswer: text(8000),
                },
                required: ["concept", "prompt", "sourceExcerpt", "suggestedAnswer"],
                additionalProperties: false,
            },
        },
    },
    required: ["sourcePath", "quizId", "topic", "questions"],
    additionalProperties: false,
};

function requireText(value, label, limit) {
    if (typeof value !== "string" || !value.trim() || value.length > limit) {
        throw new Error(`${label} must be nonempty text of at most ${limit} characters.`);
    }
}

function inside(root, path) {
    const child = relative(root, path);
    return child !== "" && child !== ".." && !child.startsWith(`..${sep}`) && !isAbsolute(child);
}

async function maybeStat(path) {
    try {
        return await stat(path);
    } catch (error) {
        if (error.code === "ENOENT") return null;
        throw error;
    }
}

export async function resolveSource(sourcePath, explicitRoot) {
    if (typeof sourcePath !== "string" || !isAbsolute(sourcePath)) throw new Error("Source path must be absolute.");
    const source = await realpath(sourcePath);
    if (![".md", ".markdown"].includes(extname(source).toLowerCase()) || !(await stat(source)).isFile()) {
        throw new Error("Source must be a Markdown file.");
    }
    let detected;
    for (let candidate = dirname(source); ; candidate = dirname(candidate)) {
        if ((await maybeStat(join(candidate, ".obsidian")))?.isDirectory()) {
            detected = candidate;
            break;
        }
        if (dirname(candidate) === candidate) break;
    }
    let root = detected;
    if (explicitRoot !== undefined) {
        if (!isAbsolute(explicitRoot)) throw new Error("Confirmed vault root must be absolute.");
        const confirmed = await realpath(explicitRoot);
        if (detected && confirmed !== detected) throw new Error("Confirmed root conflicts with the detected Obsidian vault.");
        root = confirmed;
    }
    if (!root) throw new Error("No .obsidian vault root found. Ask the user to confirm this note's vault root, then pass vaultRoot.");
    if (!inside(root, source)) throw new Error("Source is outside the confirmed vault.");
    return { source, root, relativeSource: relative(root, source).split(sep).join("/") };
}

function hash(value) {
    return createHash("sha256").update(value).digest("hex");
}

function fenced(value, language = "") {
    const lengths = [...value.matchAll(/`+/g)].map((match) => match[0].length);
    const fence = "`".repeat(Math.max(3, ...lengths.map((length) => length + 1)));
    return `${fence}${language}\n${value}\n${fence}`;
}

function renderRecord(record) {
    const sourceLink = record.source.replace(/\.markdown$|\.md$/i, "");
    // Obsidian reserves these characters in wikilinks; use an encoded relative link if needed.
    const linkText = /[\[\]|#\n\r]/.test(sourceLink)
        ? `[Source note](../${record.source.split("/").map(encodeURIComponent).join("/")})`
        : `[[${sourceLink}]]`;
    return [
        "---", "type: quiz-attempt", `quiz_id: ${JSON.stringify(record.quizId)}`,
        `topic: ${JSON.stringify(record.topic)}`, `submitted_at: ${JSON.stringify(record.submittedAt)}`,
        'assessment: "ungraded"', `source: ${JSON.stringify(record.source)}`, "---", "",
        "# Quiz attempt", "", `Topic: ${record.topic}`, "", `Source: ${linkText}`, "",
        "These are written responses, not an assessment of mastery. Suggested answers are AI-generated study aids.", "",
        `Learner evidence ID: \`obs-quiz-${record.quizId}\`. The canvas reports whether ledger recording completed.`, "",
        ...record.questions.flatMap((question, index) => [
            `## Question ${index + 1}`, "", `Concept: ${question.concept}`, "",
            question.prompt, "", "### Your answer", "", fenced(record.answers[index]), "",
            "### Suggested answer", "", question.suggestedAnswer, "",
            "### Source excerpt", "", fenced(question.sourceExcerpt), "",
        ]),
        "## Machine-readable attempt", "",
        "This copy preserves exact response text and supports reopening this completed quiz.", "",
        "```json", JSON.stringify(record, null, 2).replace(/`/g, "\\u0060"), "```", "",
    ].join("\n");
}

export async function openQuiz(input) {
    requireText(input.topic, "Topic", 200);
    if (!/^[a-zA-Z0-9][a-zA-Z0-9_-]{7,79}$/.test(input.quizId ?? "")) throw new Error("Invalid quiz ID.");
    if (!Array.isArray(input.questions) || input.questions.length !== 3) throw new Error("A quiz needs exactly three questions.");
    const questions = input.questions.map((question) => {
        for (const [key, max] of Object.entries({ concept: 200, prompt: 4000, sourceExcerpt: 4000, suggestedAnswer: 8000 })) {
            requireText(question[key], key, max);
        }
        return { concept: question.concept, prompt: question.prompt, sourceExcerpt: question.sourceExcerpt, suggestedAnswer: question.suggestedAnswer };
    });
    const { source, root, relativeSource } = await resolveSource(input.sourcePath, input.vaultRoot);
    const markdown = await readFile(source, "utf8");
    for (const question of questions) {
        if (!markdown.includes(question.sourceExcerpt)) throw new Error("Each source excerpt must occur verbatim in the displayed Markdown.");
    }
    const definition = { quizId: input.quizId, topic: input.topic, source: relativeSource, questions };
    const fingerprint = hash(JSON.stringify(definition));
    const directory = join(root, "Quizzes");
    const recordPath = join(directory, `quiz-${input.quizId}.md`);

    async function checkDirectory(create = false) {
        if (create) await mkdir(directory, { recursive: true });
        if (await maybeStat(directory)) {
            if (await realpath(directory) !== directory) throw new Error("Quizzes must be a real folder inside the source vault, not a symlink.");
        }
    }

    async function readRecord() {
        await checkDirectory();
        let content;
        try {
            if (await realpath(recordPath) !== recordPath) throw new Error("Quiz record must not be a symlink.");
            content = await readFile(recordPath, "utf8");
        } catch (error) {
            if (error.code === "ENOENT") return null;
            throw error;
        }
        content = content.replace(/\r\n/g, "\n");
        const match = /^\n```json\n([\s\S]*)\n```\n$/.exec(content.slice(content.lastIndexOf("\n```json\n")));
        if (!match) throw new Error("Existing quiz record is not readable; it will not be overwritten.");
        let record;
        try {
            record = JSON.parse(match[1]);
        } catch {
            throw new Error("Existing quiz record has invalid metadata; it will not be overwritten.");
        }
        if (!record || typeof record !== "object") throw new Error("Existing quiz record has invalid metadata.");
        if (record.fingerprint !== fingerprint || hash(JSON.stringify({
            quizId: record.quizId, topic: record.topic, source: record.source, questions: record.questions,
        })) !== fingerprint || !Array.isArray(record.answers) || record.answers.length !== 3 ||
            record.answers.some((answer) => typeof answer !== "string" || !answer.trim()) ||
            ![1, 2].includes(record.version) || typeof record.submittedAt !== "string") {
            throw new Error("Quiz ID conflicts with an existing or edited record. Create a new quiz ID.");
        }
        return record;
    }
    await readRecord();

    async function status() {
        const record = await readRecord();
        return {
            quizId: input.quizId, topic: input.topic, sourcePath: source, vaultRoot: root,
            questionCount: 3, submitted: record !== null,
            savedPath: record ? recordPath : null, assessment: "ungraded",
            learnerModel: await evidenceStatus(root, record),
        };
    }

    async function state() {
        const record = await readRecord();
        return {
            ...(await status()), source: relativeSource,
            questions: questions.map((question, index) => ({
                concept: question.concept, prompt: question.prompt,
                ...(record ? { suggestedAnswer: question.suggestedAnswer, answer: record.answers[index] } : {}),
            })),
        };
    }

    async function submit(answers) {
        if (!Array.isArray(answers) || answers.length !== 3) throw new Error("Answer all three questions.");
        answers.forEach((answer) => requireText(answer, "Each answer", 16000));
        const existing = await readRecord();
        if (existing) {
            if (JSON.stringify(existing.answers) !== JSON.stringify(answers)) throw new Error("This quiz is already submitted; existing answers will not be overwritten.");
            return completeSubmission(existing);
        }
        await checkDirectory(true);
        const record = {
            ...definition, version: 2, fingerprint, sourceSha256: hash(markdown),
            submittedAt: new Date().toISOString(), assessment: "ungraded", answers,
        };
        const tempPath = join(directory, `.quiz-${randomUUID()}.tmp`);
        try {
            await writeFile(tempPath, renderRecord(record), { flag: "wx", encoding: "utf8" });
            try {
                // Publish the complete file without ever overwriting another attempt.
                await link(tempPath, recordPath);
            } catch (error) {
                if (error.code !== "EEXIST") throw error;
                const concurrent = await readRecord();
                if (!concurrent || JSON.stringify(concurrent.answers) !== JSON.stringify(answers)) {
                    throw new Error("Another submission already saved this quiz; it will not be overwritten.");
                }
            }
        } finally {
            await unlink(tempPath).catch((error) => {
                if (error.code !== "ENOENT") throw error;
            });
        }
        return completeSubmission(await readRecord());
    }

    async function completeSubmission(record) {
        try {
            await appendQuizEvidence(root, record);
        } catch (error) {
            const failure = new Error(`Quiz answers are saved, but learner-model recording was not confirmed. ${evidenceError(error)}`);
            failure.quizSaved = true;
            throw failure;
        }
        return state();
    }
    return { topic: input.topic, status, state, submit };
}
