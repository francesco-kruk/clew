import { readFile, realpath, stat } from "node:fs/promises";
import { basename, dirname, extname, isAbsolute, relative, resolve, sep } from "node:path";
import { randomUUID } from "node:crypto";
import { Marked } from "marked";
import katex from "katex";
import sanitizeHtml from "sanitize-html";

export const DOCUMENT_BORDER = "4px solid red";
const katexRoot = new URL("./", import.meta.resolve("katex"));

export async function resolveDocument(path) {
    if (typeof path !== "string" || !isAbsolute(path)) throw new Error("Provide an absolute Markdown file path.");
    if (![".md", ".markdown"].includes(extname(path).toLowerCase())) throw new Error("Expected a .md or .markdown file.");
    const canonical = await realpath(path);
    if (!(await stat(canonical)).isFile()) throw new Error("The Markdown path must identify a file.");
    await readFile(canonical, "utf8");
    return canonical;
}

export const readDocument = (path) => readFile(path, "utf8");
const escapeHtml = (value) => value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[char]);

async function embedImage(href, documentPath) {
    if (/^data:image\/(?:png|jpeg|gif|webp);base64,[a-z0-9+/=\s]+$/i.test(href)) return href;
    if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith("//") || isAbsolute(href)) {
        throw new Error("Only document-relative raster images are loaded; remote images are not fetched.");
    }
    const root = await realpath(dirname(documentPath));
    const imagePath = await realpath(resolve(root, decodeURIComponent(href)));
    const child = relative(root, imagePath);
    if (child === ".." || child.startsWith(`..${sep}`) || isAbsolute(child)) {
        throw new Error("Image is outside the Markdown file's directory.");
    }
    const data = await readFile(imagePath);
    let mime;
    if (data.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) mime = "image/png";
    else if (data[0] === 255 && data[1] === 216 && data[2] === 255) mime = "image/jpeg";
    else if (/^GIF8[79]a$/.test(data.subarray(0, 6).toString())) mime = "image/gif";
    else if (data.subarray(0, 4).toString() === "RIFF" && data.subarray(8, 12).toString() === "WEBP") mime = "image/webp";
    else throw new Error("Supported image formats are PNG, JPEG, GIF, and WebP.");
    return `data:${mime};base64,${data.toString("base64")}`;
}

export async function readAsset(path) {
    if (path === "katex.min.css") {
        return { type: "text/css", data: await readFile(new URL(path, katexRoot)) };
    }
    if (/^fonts\/KaTeX_[A-Za-z0-9_-]+\.(woff2?|ttf)$/.test(path)) {
        return {
            type: path.endsWith(".woff2") ? "font/woff2" : path.endsWith(".woff") ? "font/woff" : "font/ttf",
            data: await readFile(new URL(path, katexRoot)),
        };
    }
    return null;
}

export async function renderDocument(path) {
    const formulas = [];
    const warnings = [];
    const marker = randomUUID();
    const mathExtension = (name, level, pattern, displayMode) => ({
        name,
        level,
        start: (source) => source.indexOf(displayMode ? "$$" : "$"),
        tokenizer(source) {
            const match = pattern.exec(source);
            if (match) return { type: name, raw: match[0], text: match[1] };
        },
        renderer(token) {
            const index = formulas.push(katex.renderToString(token.text, {
                displayMode, throwOnError: false, trust: false,
            })) - 1;
            return `<span data-formula="${marker}-${index}"></span>`;
        },
    });
    const marked = new Marked({
        async: true,
        async walkTokens(token) {
            if (token.type !== "image") return;
            try {
                token.href = await embedImage(token.href, path);
            } catch (error) {
                warnings.push(`Image "${token.text || token.href}": ${error.message}`);
                token.type = "html";
                token.text = `<span>[Image unavailable: ${escapeHtml(token.text || token.href)}]</span>`;
            }
        },
        extensions: [
            {
                name: "obsidianEmbed",
                level: "inline",
                start: (source) => source.indexOf("![["),
                tokenizer(source) {
                    const match = /^!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/.exec(source);
                    if (match) return { type: "image", raw: match[0], href: match[1], text: match[2] ?? match[1] };
                },
            },
            {
                name: "obsidianLink",
                level: "inline",
                start: (source) => source.indexOf("[["),
                tokenizer(source) {
                    const match = /^\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/.exec(source);
                    if (match) return { type: "obsidianLink", raw: match[0], text: match[2] ?? match[1] };
                },
                renderer: (token) => escapeHtml(token.text),
            },
            mathExtension("displayMath", "block", /^\$\$([\s\S]+?)\$\$(?:\r?\n|$)/, true),
            mathExtension("inlineMath", "inline", /^\$([^$\n]+?)\$/, false),
        ],
    });
    const markdown = await readDocument(path);
    const safeHtml = sanitizeHtml(await marked.parse(markdown), {
        allowedTags: [...sanitizeHtml.defaults.allowedTags, "img", "span"],
        allowedAttributes: {
            ...sanitizeHtml.defaults.allowedAttributes,
            img: ["src", "alt"],
            span: ["data-formula"],
        },
        allowedSchemesByTag: { img: ["data"] },
    });
    const body = safeHtml.replace(new RegExp(`<span data-formula="${marker}-(\\d+)"><\\/span>`, "g"), (_, index) => {
        if (!formulas[Number(index)]) throw new Error("Invalid formula placeholder");
        return formulas[Number(index)];
    });
    return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(basename(path, extname(path)))}</title>
<link rel="stylesheet" href="katex.min.css">
<style>
* { box-sizing: border-box; }
body { margin: 0; padding: 20px; background: var(--background-color-default, #fff); color: var(--text-color-default, #1f2328); font-family: var(--font-sans, system-ui, sans-serif); font-size: var(--text-body-medium, 14px); line-height: 1.7; }
main { border: ${DOCUMENT_BORDER}; border-radius: 8px; max-width: 900px; margin: auto; padding: clamp(16px, 4vw, 40px); overflow-wrap: anywhere; }
h1 { font-size: var(--text-title-large, 26px); line-height: var(--leading-title-large, 32px); }
h2 { margin-top: 1.6em; }
img { max-width: 100%; height: auto; background: white; }
blockquote { margin: 1em 0; padding-left: 16px; border-left: 3px solid var(--border-color-default, #ccc); color: var(--text-color-muted, #59636e); }
.katex-display { overflow-x: auto; overflow-y: hidden; padding: 8px 0; }
footer { color: var(--text-color-muted, #59636e); font-size: 12px; margin-top: 24px; }
</style></head><body><main>${body}
${warnings.length ? `<aside aria-label="Image warnings"><h2>Image warnings</h2><ul>${warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul></aside>` : ""}
<footer>Read-only preview of ${escapeHtml(path)}. Obsidian links are shown as text; the original file is unchanged.</footer></main></body></html>`;
}
