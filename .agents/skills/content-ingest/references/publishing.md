# Extraction-to-course publishing handoff

The extractor writes **staging artifacts**, not a complete course. Do not point
learners at the extraction directory as if it were already canonical.

1. Obtain authorization for the destination vault root, selected course root,
   asset placement, and any edits or overwrites. Load `course-content` and its
   current structure reference. If unavailable, stop at extraction.
2. Reconcile heuristic splits with real source chapters and preserve provenance
   and physical-page references. Retain image-only and unverified-fidelity
   labels. Report skipped front matter, unresolved grouping, missing text, or
   unsupported material; do not invent chapters, answers, concepts, or metadata.
3. Assemble the canonical `courses/<course>/hub.md` and one complete Markdown
   file per actual chapter in `courses/<course>/chapters/`, following
   `course-content`.
   Use the hub's ordered inventory, explicit chapter backlinks, real heading
   anchors, and grounded required metadata. Do not publish section shards plus
   an index instead of a complete chapter.
4. Move/copy assets only as authorized, recompute links from their final notes,
   and confirm every target. Retain authorized source attachments and citations;
   do not upload original PDFs merely to make links work.
5. Run the installed **course-content validator**, using that skill's documented
   entry point and explicit vault/course-root arguments. It owns the publishing
   schema, so this extractor does not duplicate or guess the validator's CLI.
   Capture the command, exit code, and findings. An unavailable validator,
   structural failure, or unresolved chapter grouping blocks a validated-course
   handoff; report staging-only output instead.
6. Separately report source-fidelity review and any live-rendering checks
   actually performed. A structural validator cannot establish transcription
   accuracy, image legibility, complete source coverage, or Obsidian rendering.

Handoff summary: source scope; extraction Markdown/asset roots; success and
failure counts; canonical hub and chapter paths (only if assembled); validator
command/result (only if run); fidelity limitations; remaining user decisions.
Do not create learner models, progress records, or personalized plans as part
of ingestion or publication.
