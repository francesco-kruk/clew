"""Read-only course distribution v1 validation; no vault discovery or network I/O."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    yaml = None


EXTENSIONS = {
    ".md", ".json", ".canvas", ".pdf", ".png", ".jpg", ".jpeg", ".gif",
    ".svg", ".webp", ".txt", ".csv", ".mp3", ".wav", ".mp4", ".webm",
}
PRIVATE_PARTS = {
    "model", "artifacts", "sessions", "learner-model", "learner-data",
    "dashboards", "apm_modules", "node_modules", "__pycache__", "venv",
    "scripts", "evals", "tests", "raw", "staging",
}
DEVICE = re.compile(r"^(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\.|$)", re.I)
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
WIKI = re.compile(r"!?\[\[([^\]\n]+)\]\]")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.M)


def report(errors):
    return {"schema_version": 1, "ok": not errors, "errors": errors}


def error(errors, code, path, message):
    errors.append({"code": code, "path": str(path), "message": message})


def valid_path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if any(ord(c) < 32 for c in value):
        return False
    parts = value.split("/")
    return all(
        part not in {"", ".", ".."}
        and not part.startswith(".")
        and not part.endswith((" ", "."))
        and not re.search(r'[<>:"|?*#^\[\]]', part)
        and not DEVICE.match(part)
        for part in parts
    )


def private_path(value):
    return any(part.casefold() in PRIVATE_PARTS for part in value.split("/"))


def reparse(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def safe_root(path, errors):
    root = Path(os.path.abspath(path))
    try:
        for component in [root, *root.parents]:
            if reparse(component):
                error(errors, "path", root, "Symlink/reparse ancestors are not permitted.")
                return None
        if not root.is_dir():
            error(errors, "path", root, "Expected an existing package directory.")
            return None
    except OSError as exc:
        error(errors, "io", root, str(exc))
        return None
    return root


def read_json(path):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Invalid JSON: {value}")),
    )


def keys(value, required, errors, path):
    if not isinstance(value, dict) or set(value) != set(required):
        error(errors, "schema", path, f"Expected exactly these fields: {', '.join(required)}.")
        return False
    return True


def package_metadata(data, errors):
    location = "course-package.json"
    required = ("schema_version", "id", "course", "course_root", "hub",
                "files", "attribution", "rights", "reports")
    if not keys(data, required, errors, location):
        return False
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        error(errors, "schema", location, "Unsupported schema_version (expected integer 1).")
    if not isinstance(data["id"], str) or not ID.fullmatch(data["id"]):
        error(errors, "schema", location, "Invalid distribution id.")
    course = data["course"]
    if not isinstance(course, str) or not valid_path(course) or "/" in course:
        error(errors, "schema", location, "course must be one Windows-safe path component.")
    if data["course_root"] != f"courses/{course}":
        error(errors, "schema", location, "course_root must equal courses/<course>.")
    if data["hub"] != "hub.md":
        error(errors, "schema", location, "hub must be hub.md.")
    if not isinstance(data["files"], list) or not data["files"]:
        error(errors, "schema", location, "files must be a nonempty inventory array.")
    else:
        for entry in data["files"]:
            if keys(entry, ("path", "sha256"), errors, location):
                if not valid_path(entry["path"]):
                    error(errors, "path", location, "Invalid inventory path.")
                if not isinstance(entry["sha256"], str) or not HASH.fullmatch(entry["sha256"]):
                    error(errors, "schema", location, "Invalid lowercase SHA256.")
    if not keys(data["rights"], ("status", "evidence"), errors, location):
        return False
    if data["rights"]["status"] not in ("pending", "confirmed"):
        error(errors, "rights", location, "rights.status must be pending or confirmed.")
    references = [data["attribution"], data["rights"]["evidence"]]
    reports = data["reports"]
    if not isinstance(reports, list) or not reports:
        error(errors, "schema", location, "reports must be a nonempty array.")
    else:
        references.extend(reports)
        if all(isinstance(item, str) for item in reports) and len(set(reports)) != len(reports):
            error(errors, "schema", location, "Duplicate report reference.")
    for reference in references:
        if not valid_path(reference):
            error(errors, "path", location, "Invalid attribution, rights or report path.")
    return not errors


def inventory(root, data, errors):
    expected = {}
    folded = set()
    for entry in data["files"]:
        name = entry["path"]
        if name.casefold() in folded:
            error(errors, "collision", name, "Duplicate/case-insensitive inventory path.")
        folded.add(name.casefold())
        expected[name] = entry["sha256"]
        if name.casefold() == "course-package.json":
            error(errors, "inventory", name, "The manifest must exclude itself.")
        if private_path(name) or PurePosixPath(name).suffix.lower() not in EXTENSIONS:
            error(errors, "excluded", name, "Private/tooling or unsupported distribution file.")
    actual = set()
    seen = set()
    for current, directories, files in os.walk(root, followlinks=False):
        for name in list(directories) + files:
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            if reparse(path):
                error(errors, "path", relative, "Symlinks/reparse points are forbidden.")
                if name in directories:
                    directories.remove(name)
                continue
            if not valid_path(relative) or private_path(relative):
                error(errors, "excluded", relative, "Unsafe/private/tooling path.")
            if relative.casefold() in seen:
                error(errors, "collision", relative, "Case-insensitive filesystem collision.")
            seen.add(relative.casefold())
            if name in files:
                if not stat.S_ISREG(path.stat().st_mode):
                    error(errors, "path", relative, "Only regular files are permitted.")
                elif relative != "course-package.json":
                    actual.add(relative)
    for name in sorted(actual - set(expected)):
        error(errors, "inventory", name, "File is not inventoried.")
    for name in sorted(set(expected) - actual):
        error(errors, "inventory", name, "Inventoried file is missing.")
    for name in sorted(actual & set(expected)):
        with (root / name).open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != expected[name]:
            error(errors, "hash", name, "SHA256 does not match actual bytes.")
    for name in [data["attribution"], data["rights"]["evidence"], *data["reports"]]:
        if name not in expected or name not in actual:
            error(errors, "reference", name, "Metadata reference must be an inventoried file.")
        elif not (root / name).stat().st_size:
            error(errors, "reference", name, "Metadata reference must not be empty.")
    return expected


def prose(text):
    text = re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[ \t]*$", "", text)
    return re.sub(r"`+[^`\n]*`+", "", text)


def frontmatter(text, path, errors):
    if not text.startswith("---\n"):
        error(errors, "metadata", path, "Missing YAML frontmatter.")
        return {}, text
    end = re.search(r"(?m)^---[ \t]*$", text[4:])
    if not end:
        error(errors, "metadata", path, "Unclosed YAML frontmatter.")
        return {}, text
    try:
        class UniqueLoader(yaml.SafeLoader):
            pass

        def mapping(loader, node, deep=False):
            pairs = loader.construct_pairs(node, deep=deep)
            result = {}
            for key, value in pairs:
                if not isinstance(key, str) or key in result:
                    raise ValueError("Duplicate or non-string YAML property.")
                result[key] = value
            return result

        UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        metadata = yaml.load(text[4:4 + end.start()], Loader=UniqueLoader)
        if not isinstance(metadata, dict):
            raise ValueError("Frontmatter must be a mapping.")
    except (yaml.YAMLError, ValueError) as exc:
        error(errors, "metadata", path, str(exc))
        metadata = {}
    return metadata, text[4 + end.end():].lstrip("\n")


def links(text):
    """Yield (target, syntax) including reference-style Markdown links."""
    text = prose(text)
    for match in WIKI.finditer(text):
        yield match.group(1).replace("\\|", "|").split("|", 1)[0], "wiki"
    text = WIKI.sub("", text)
    definitions = {}
    for match in re.finditer(r"(?m)^ {0,3}\[([^\]]+)\]:[ \t]*(<[^>]+>|\S+)", text):
        definitions[match.group(1).casefold()] = match.group(2).strip("<>")
        yield match.group(2).strip("<>"), "markdown"
    text = re.sub(r"(?m)^ {0,3}\[[^\]]+\]:.*$", "", text)
    for match in re.finditer(r"!?\[([^\]\n]*)\](?:\[([^\]\n]*)\])?", text):
        end = match.end()
        if end < len(text) and text[end] == "(":
            start = end + 1
            if text[start:start + 1] == "<":
                close = text.find(">", start + 1)
                if close != -1:
                    yield text[start + 1:close], "markdown"
                continue
            depth, cursor = 1, start
            while cursor < len(text) and depth:
                if text[cursor] == "(" and (cursor == 0 or text[cursor - 1] != "\\"):
                    depth += 1
                elif text[cursor] == ")" and (cursor == 0 or text[cursor - 1] != "\\"):
                    depth -= 1
                cursor += 1
            if depth == 0:
                target = text[start:cursor - 1].strip()
                target = re.sub(r"""\s+["'].*["']$""", "", target)
                yield target.replace("\\(", "(").replace("\\)", ")"), "markdown"
        else:
            label = (match.group(2) or match.group(1)).casefold()
            if label in definitions:
                yield definitions[label], "markdown"
            elif match.group(2) is not None:
                yield f"UNDEFINED-REFERENCE:{label}", "markdown"
    for match in re.finditer(r"""<(?:img|a|source|video|audio)\b[^>]*?\b(?:src|href)=["']([^"']+)["']""", text, re.I):
        yield match.group(1), "markdown"


class CourseLinks:
    def __init__(self, names, texts, prefix, errors):
        self.names = set(names)
        self.texts = texts
        self.prefix = prefix
        self.errors = errors
        self.edges = {name: set() for name in names}

    def resolve(self, source, target, syntax="wiki"):
        target = unquote(target.strip())
        if target.startswith(("https://", "http://", "mailto:")):
            return None
        if urlsplit(target).scheme or target.startswith(("/", "\\")) or "\\" in target:
            error(self.errors, "link", source, f"Unsafe local target: {target}")
            return None
        path, _, anchor = target.partition("#")
        if not path:
            candidates = [source]
        elif syntax == "canvas":
            candidates = [path[len(self.prefix) + 1:]] if path.startswith(self.prefix + "/") else []
        elif path.startswith(self.prefix + "/"):
            candidates = [path[len(self.prefix) + 1:]]
        elif path.startswith("courses/"):
            candidates = []
        elif syntax == "wiki" and "/" not in path:
            candidates = [
                name for name in self.names
                if PurePosixPath(name).name == path
                or (PurePosixPath(name).suffix.lower() == ".md" and PurePosixPath(name).stem == path)
            ]
            if path in ("hub", "hub.md"):
                error(self.errors, "link", source, "A hub link must be course-qualified.")
                return None
        else:
            base = PurePosixPath(source).parent if syntax == "markdown" else PurePosixPath()
            parts = []
            for part in (base / path).parts:
                if part == "..":
                    if not parts:
                        error(self.errors, "link", source, f"Target escapes the package: {target}")
                        return None
                    parts.pop()
                elif part != ".":
                    parts.append(part)
            candidates = ["/".join(parts)]
        expanded = []
        for candidate in candidates:
            if candidate in self.names:
                expanded.append(candidate)
            elif candidate + ".md" in self.names:
                expanded.append(candidate + ".md")
        expanded = sorted(set(expanded))
        if len(expanded) != 1:
            error(self.errors, "link", source, f"Missing or ambiguous target: {target}")
            return None
        resolved = expanded[0]
        if anchor:
            self.anchor(source, resolved, anchor)
        self.edges[source].add(resolved)
        return resolved

    def anchor(self, source, target, anchor):
        if target.lower().endswith(".pdf"):
            if not re.fullmatch(r"page=[1-9]\d*", anchor):
                error(self.errors, "anchor", source, f"Invalid physical PDF page: {anchor}")
            return
        if target not in self.texts:
            error(self.errors, "anchor", source, f"Unsupported anchor on {target}: {anchor}")
            return
        text = prose(self.texts[target])
        if anchor.startswith("^"):
            matches = re.findall(r"(?m)(?:^|\s)\^" + re.escape(anchor[1:]) + r"[ \t]*$", text)
        else:
            headings = [match.group(2).strip() for match in HEADING.finditer(text)]
            matches = [heading for heading in headings if heading.casefold() == anchor.casefold()]
            if not matches:
                counts = Counter()
                slugs = []
                for heading in headings:
                    slug = re.sub(r"[^\w\s-]", "", heading.casefold()).replace(" ", "-")
                    number = counts[slug]
                    counts[slug] += 1
                    slugs.append(slug + (f"-{number}" if number else ""))
                matches = [slug for slug in slugs if slug == anchor.casefold()]
        if len(matches) != 1:
            error(self.errors, "anchor", source, f"Missing or ambiguous anchor in {target}: {anchor}")


def string_list(value, nonempty=False):
    return isinstance(value, list) and (bool(value) or not nonempty) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def validate_content(root, data, names, errors):
    texts = {
        name: (root / name).read_text(encoding="utf-8-sig")
        for name in names if name.lower().endswith(".md")
    }
    if "hub.md" not in texts:
        error(errors, "metadata", "hub.md", "Missing canonical Markdown hub.")
        return
    resolver = CourseLinks(names, texts, data["course_root"], errors)
    metadata, bodies = {}, {}
    chapters = {name for name in texts if name.startswith("chapters/")}
    concepts = {name for name in texts if name.startswith("concepts/")}
    if not chapters:
        error(errors, "metadata", "hub.md", "At least one complete chapter is required.")
    for name in {"hub.md", *chapters, *concepts}:
        meta, body = frontmatter(texts[name], name, errors)
        metadata[name], bodies[name] = meta, body
        expected_type = "course" if name == "hub.md" else (
            "course-chapter" if name in chapters else "course-concept"
        )
        if meta.get("type") != expected_type or meta.get("course") != data["course"]:
            error(errors, "metadata", name, "Incorrect type or course identity.")
        if name not in concepts and not string_list(meta.get("sources")):
            error(errors, "metadata", name, "sources must be an explicit list of references.")
        for source in meta.get("sources", []) if isinstance(meta.get("sources"), list) else []:
            if isinstance(source, str) and not (
                WIKI.fullmatch(source) or source.startswith(("https://", "http://"))
            ):
                error(errors, "metadata", name, "Source references must be wikilinks or external URLs.")
        if len([m for m in HEADING.finditer(prose(body)) if len(m.group(1)) == 1]) != 1:
            error(errors, "metadata", name, "Exactly one title heading is required.")
        if name in chapters:
            if not isinstance(meta.get("chapter"), str) or not meta["chapter"].strip():
                error(errors, "metadata", name, "chapter must be a nonempty string identifier.")
            hub = meta.get("hub")
            if not isinstance(hub, str) or not WIKI.fullmatch(hub):
                error(errors, "metadata", name, "hub must be a quoted course-qualified wikilink.")
            elif resolver.resolve(name, WIKI.fullmatch(hub).group(1).split("|")[0]) != "hub.md":
                error(errors, "metadata", name, "Chapter hub does not resolve to the canonical hub.")
            visible = [resolver.resolve(name, target, kind) for target, kind in links(body)]
            if "hub.md" not in visible:
                error(errors, "metadata", name, "Chapter needs a visible backlink to the hub.")
        if name in concepts:
            if not isinstance(meta.get("domain"), str) or not meta["domain"].strip():
                error(errors, "metadata", name, "Concept domain must be explicit.")
            if "concept_id" not in meta or not (
                meta["concept_id"] is None or isinstance(meta["concept_id"], str) and meta["concept_id"].strip()
            ):
                error(errors, "metadata", name, "Concept ID must be a known string or explicit null.")
    hub = metadata["hub.md"]
    for field in ("primary_domains", "prerequisite_domains"):
        if not string_list(hub.get(field), nonempty=field == "primary_domains"):
            error(errors, "metadata", "hub.md", f"{field} must be an explicit domain list.")
    ids = [metadata[name].get("chapter") for name in chapters]
    if len({str(value) for value in ids}) != len(ids):
        error(errors, "metadata", "hub.md", "Duplicate chapter identifiers.")
    body = bodies["hub.md"]
    section = re.search(r"(?ms)^## Chapters[ \t]*\n(.*?)(?=^## |\Z)", body)
    ordered = []
    if not section:
        error(errors, "metadata", "hub.md", "Missing Chapters section.")
    else:
        for line in section.group(1).splitlines():
            if re.match(r"^\s*\d+[.)]\s+", line):
                targets = list(links(line))
                if len(targets) != 1:
                    error(errors, "metadata", "hub.md", "Each ordered chapter item needs exactly one direct link.")
                else:
                    target, kind = targets[0]
                    if "#" in target:
                        error(errors, "metadata", "hub.md", "Chapter order links must target complete chapters.")
                    ordered.append(resolver.resolve("hub.md", target, kind))
    if Counter(ordered) != Counter(chapters):
        error(errors, "metadata", "hub.md", "Ordered Chapters must link every chapter exactly once.")
    index = re.search(r"(?ms)^## Concept index[ \t]*\n(.*?)(?=^## |\Z)", body)
    if not index or not re.search(r"\|\s*Concept ID\s*\|\s*Concept\s*\|\s*Domain\s*\|\s*Location\s*\|", index.group(1)):
        error(errors, "metadata", "hub.md", "Missing Concept index table and required columns.")
    else:
        concept_rows = []
        for line in index.group(1).splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            if cells and (cells[0] == "Concept ID" or re.fullmatch(r":?-+:?", cells[0])):
                continue
            concept_rows.append(cells)
            if len(cells) != 4 or not all(cells):
                error(errors, "metadata", "hub.md", "Concept index rows require four nonempty cells; escape alias pipes.")
                continue
            locations = list(links(cells[3]))
            if not locations:
                error(errors, "metadata", "hub.md", "Concept Location must link to a chapter heading or block.")
            for target, kind in locations:
                if "#" not in target or resolver.resolve("hub.md", target, kind) not in chapters:
                    error(errors, "metadata", "hub.md", "Concept Location must link to a chapter heading or block.")
        if (not concept_rows or any(row and row[0] == "null" for row in concept_rows)) and not re.search(r"(?m)^## Content notes\s*$", body):
            error(errors, "metadata", "hub.md", "Unmapped or missing concepts require Content notes.")
    for name, text in texts.items():
        for target, kind in links(text):
            resolver.resolve(name, target, kind)
    for name in concepts:
        if not resolver.edges[name] & chapters:
            error(errors, "metadata", name, "Concept note needs an authoritative chapter link.")
    for name in names:
        if not name.lower().endswith(".canvas"):
            continue
        canvas = read_json(root / name)
        if not isinstance(canvas, dict) or not isinstance(canvas.get("nodes"), list) or not isinstance(canvas.get("edges"), list):
            error(errors, "canvas", name, "Canvas needs nodes and edges arrays.")
            continue
        node_ids = set()
        for node in canvas["nodes"]:
            if not isinstance(node, dict) or not isinstance(node.get("id"), str) or node["id"] in node_ids:
                error(errors, "canvas", name, "Invalid or duplicate Canvas node id.")
                continue
            node_ids.add(node["id"])
            if node.get("type") == "file":
                if not isinstance(node.get("file"), str):
                    error(errors, "canvas", name, "File node needs a file path.")
                else:
                    subpath = node.get("subpath", "")
                    if not isinstance(subpath, str) or subpath and not subpath.startswith("#"):
                        error(errors, "canvas", name, "Invalid file node subpath.")
                    else:
                        resolver.resolve(name, node["file"] + subpath, "canvas")
            elif node.get("type") == "text" and isinstance(node.get("text"), str):
                for target, kind in links(node["text"]):
                    resolver.resolve(name, target, kind)
            elif node.get("type") not in ("text", "link", "group"):
                error(errors, "canvas", name, "Unknown Canvas node type.")
        edge_ids = set()
        for edge in canvas["edges"]:
            if not isinstance(edge, dict):
                error(errors, "canvas", name, "Invalid Canvas edge.")
            elif not isinstance(edge.get("id"), str) or edge["id"] in edge_ids or (
                not isinstance(edge.get("fromNode"), str)
                or not isinstance(edge.get("toNode"), str)
                or edge.get("fromNode") not in node_ids or edge.get("toNode") not in node_ids
            ):
                error(errors, "canvas", name, "Invalid Canvas edge id or endpoints.")
            else:
                edge_ids.add(edge["id"])
    reached = set()
    pending = ["hub.md", data["attribution"], data["rights"]["evidence"], *data["reports"]]
    while pending:
        name = pending.pop()
        if name not in reached:
            reached.add(name)
            pending.extend(resolver.edges.get(name, set()) - reached)
    for name in sorted(set(names) - reached):
        error(errors, "closure", name, "File is unreachable from the hub or metadata references.")


def validate_package(package_dir, mode="publish"):
    errors = []
    if mode not in ("publish", "draft"):
        error(errors, "mode", "course-package.json", "mode must be publish or draft.")
        return report(errors)
    if yaml is None:
        error(errors, "dependency", "requirements.txt", "Install course-content requirements: python -m pip install -r <skill>/requirements.txt")
        return report(errors)
    root = safe_root(package_dir, errors)
    if root is None:
        return report(errors)
    try:
        manifest = root / "course-package.json"
        if reparse(manifest):
            error(errors, "path", manifest.name, "Manifest must not be a symlink/reparse point.")
            return report(errors)
        data = read_json(manifest)
        if not package_metadata(data, errors):
            return report(errors)
        names = inventory(root, data, errors)
        if errors:
            return report(errors)
        if mode == "publish" and data["rights"]["status"] != "confirmed":
            error(errors, "rights", manifest.name, "Publication requires confirmed rights.")
        validate_content(root, data, names, errors)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        error(errors, "read", "course-package.json", str(exc))
    return report(errors)


def validate_catalog(catalog_path, packages=True):
    errors = []
    path = Path(catalog_path)
    root = safe_root(path.absolute().parent, errors)
    if root is None:
        return report(errors)
    try:
        if reparse(path):
            error(errors, "path", path.name, "Catalog must not be a symlink/reparse point.")
            return report(errors)
        data = read_json(path)
        if not keys(data, ("schema_version", "courses"), errors, path.name):
            return report(errors)
        if type(data["schema_version"]) is not int or data["schema_version"] != 1 or not isinstance(data["courses"], list):
            error(errors, "schema", path.name, "Expected schema_version 1 and courses array.")
            return report(errors)
        ids, paths = set(), set()
        for entry in data["courses"]:
            if not keys(entry, ("id", "title", "path"), errors, path.name):
                continue
            if not isinstance(entry["id"], str) or not ID.fullmatch(entry["id"]) or (
                not isinstance(entry["title"], str) or not entry["title"].strip()
            ):
                error(errors, "schema", path.name, "Invalid catalog id or title.")
                continue
            relative = entry["path"]
            if not valid_path(relative) or len(relative.split("/")) != 2 or not relative.startswith("courses/"):
                error(errors, "path", path.name, "Catalog path must be courses/<course>.")
                continue
            if entry["id"].casefold() in ids or relative.casefold() in paths:
                error(errors, "collision", path.name, "Duplicate catalog id or path.")
            ids.add(entry["id"].casefold())
            paths.add(relative.casefold())
            if relative != f"courses/{entry['title']}":
                error(errors, "identity", relative, "Catalog path must equal courses/<title>.")
            if not packages:
                continue
            result = validate_package(root / relative)
            errors.extend(result["errors"])
            if result["ok"]:
                package = read_json(root / relative / "course-package.json")
                if (entry["id"], entry["title"], relative) != (
                    package["id"], package["course"], package["course_root"]
                ):
                    error(errors, "identity", relative, "Catalog/package identity mismatch.")
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        error(errors, "read", str(path), str(exc))
    return report(errors)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, help="Explicit package directory")
    parser.add_argument("--catalog", type=Path, help="Explicit catalog JSON path")
    parser.add_argument("--catalog-only", action="store_true", help="Validate catalog structure without reading its packages")
    parser.add_argument("--mode", choices=("draft", "publish"), default="publish")
    args = parser.parse_args(argv)
    if not args.package and not args.catalog:
        parser.error("at least one of --package or --catalog is required")
    if args.catalog_only and not args.catalog:
        parser.error("--catalog-only requires --catalog")
    errors = []
    if args.package:
        errors.extend(validate_package(args.package, args.mode)["errors"])
    if args.catalog:
        errors.extend(validate_catalog(args.catalog, packages=not args.catalog_only)["errors"])
    result = report(errors)
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
