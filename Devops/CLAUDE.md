# Devops Folder — Context for Claude Sessions

This folder is the notes vault for a **live DevOps course** the user is enrolled in. Classes are
recorded with OBS, transcribed locally, and turned into permanent notes here.

> **The rig that produces these notes is documented elsewhere.** Read
> `~/Desktop/Transcribe/PROMPT-FOR-CLAUDE.md` (how the transcription pipeline works) and
> `~/Desktop/Transcribe/tracks/devops.md` (this track's status and transcription profile).
> **This file is about the notes**: what they're for, how they must read, how the folder is laid out.

**Scope of a DevOps session:** this folder and the DevOps track only. RAG, AlgoCamp, Python-Utils,
LLD, HLD and the interview-prep tracks are other sessions' work — do not read their files, do not
cross-reference them, do not let their status distract this one.

## The course

| | |
|---|---|
| **Provider / instructor** | *fill on first session* |
| **Format** | Live cohort class with student Q&A |
| **Language** | ~95% Hindi, ~5% English |
| **Modules** | *fill once the syllabus is known* |
| **Started** | 2026-08-05 |
| **Course repo / lab files** | `github.com/Rohitnegi9/Thunder` → `04 Devops/Lecture <nn>/`. Per-lecture `Notes.pdf` and an Excalidraw export. **Read the caveats in `~/Desktop/Transcribe/tracks/devops.md` before trusting it** — it is a lesson plan rather than a record, and its PDF text layer eats the spaces in commands. |

## Who the notes are for

**The notes are the product.** They get published and read by strangers with zero context — not by
someone who attended the class. That single fact drives every rule below.

The user is a backend engineer (Java/Spring, Python/FastAPI) with ~2.6 years' experience, preparing
for interviews at a higher band. So the notes have two jobs at once: **teach the thing properly**,
and **be defensible in an interview**. A note that lets him say "I set up X" but not "here's why X
and not Y, and here's what it cost" has failed at the second job.

---

## Folder layout

```
Devops/
├── CLAUDE.md                    ← this file
├── 00-Syllabus.md               ← the course's module list, once known
├── 01-<Module-Name>/
│   ├── 00-Syllabus.md           ← that module's concept list
│   ├── 01-<Concept>.md
│   ├── 02-<Concept>.md
│   └── Images/
└── 02-<Module-Name>/
```

- **Folders are numbered by course order** (unlike `AI-Engineering/`, which numbers by learning
  order). A live course arrives in sequence; there is no reason to reorder it.
- **Concept notes are numbered to match their module syllabus item** — concept 7 → `07-Name.md`.
- A folder is created when its module starts. Gaps in numbering mean a module not yet reached.
- **Images are embedded by absolute vault path** — `![[Devops/01-Module/Images/file.png]]`. Any
  folder rename must rewrite every embed in the same operation.

---

## House style

Match the vault's existing style — see `~/Desktop/wiki/AI-Engineering/07-RAG/00-Fundamentals/` for
the reference implementation.

- **No H1 headings.** Open directly with prose; Obsidian shows the filename as the title.
- **No "Next:" trailer lines.** Each note ends on its own content.
- **Problem before solution.** Never open with "X is a tool that…". Open with the situation that
  makes X necessary, show the naive approach, then break it. *Motivate a tool by first showing a
  simpler tool suffices on the easy case, then breaking it on a harder case.*
- **Justify with scale numbers, not adjectives.** Not "this is slow" — "this took 40 minutes per
  deploy across 12 services". If the lecture gave a number, the note keeps it.
- **Plain English. No jargon before it's introduced.** Every term gets explained at first use.
- **One concept per note.** Split when the content justifies it, not before — folder economy matters.
- Obsidian callouts: `> [!info]`, `> [!important]`, `> [!danger]`, `> [!tip]`.
- **Mermaid over screenshots** for pipelines, architectures, request flows and state machines.
- **"Guarantees / doesn't guarantee"** framing wherever a tool makes a promise with an edge to it.
- **Full capture** — every example, number, distinction, analogy and warning from the class. But
  **lecture depth only**: don't bolt on material the class didn't cover. If you add something
  beyond it, mark it clearly and flag it to the user.

---

## DevOps-specific rules

These are the ones that don't come from the general house style, and they exist because DevOps notes
fail differently from concept notes.

### 1. Command provenance — the load-bearing rule

> [!danger] **Never write a command, flag, path or config key that came out of the transcript.**
>
> The instructor types commands rather than dictating them. That typing is silence, and silence is
> exactly what makes whisper hallucinate. Anything command-shaped in the transcript is either
> garbled or invented.
>
> Every command in a note comes from **the course repo, the official docs, or a legible frame grab
> of the terminal** — and then gets sanity-checked. A wrong flag in a published note is worse than a
> missing one, because the reader runs it.

If a command can't be recovered from any of those sources, **say so in the note** rather than
guessing — a `> [!info] The class ran a command here that the recording didn't capture cleanly`
callout is honest and costs the reader nothing.

### 2. Version and currency

DevOps tooling moves faster than anything else in this vault, and the class will teach whatever
version it teaches. So:

- **State the version** for anything version-sensitive — Kubernetes API versions, Docker Compose v1
  vs v2 syntax, GitHub Actions runner images, Terraform providers.
- Each module's `00-Syllabus.md` carries a **currency check dated at time of writing**, noting what
  is likely to drift.
- If the class teaches something already deprecated, note the current form **and** keep the class's
  version — the reader may be following along with the same course.

### 3. Show the failure, not just the happy path

A DevOps note that only shows the working command teaches nothing durable. Where the class shows an
error, a broken build, a pod that won't schedule, a permission denied — **that is the most valuable
content in the lecture**. Keep the error text, keep the diagnosis, keep the fix.

### 4. Config blocks are code blocks

YAML, Dockerfiles, HCL, shell — always fenced code blocks with the language tag, never screenshots.
Copyable, greppable, and they render properly on the published site. Terminal *output* is also a
code block. Screenshots are for **dashboards, architecture drawings and UI**, where the picture is
the point.

### 5. Live-class hygiene

- **Student names are stripped; questions and answers are kept.** The Q&A is genuinely good
  content — keep all of it, attribute none of it. **Grep before finishing.**
- **Neutralise named examples** — if the instructor demos with a personal account, real company
  name, real repo URL, real IP or real domain, rewrite it to a placeholder that behaves the same way
  for the point being made.
- **Never publish a credential, token, key, or account ID that appears on screen**, even a demo one.

---

## How to work here

**Derive before writing.** Never create or edit a file until it's explicitly asked for. Propose the
note structure in chat, wait for approval, then write. Auto-writing and auto-advancing are the
failure mode.

**Read the transcript in full before proposing anything.** Under-reading has been called out before.

**Socratic by default** outside of note-writing — the user answers first, then gets pushed on the
assumption that's actually load-bearing.

**Correctness checks are one word** — "correct" or "incorrect", no explanation unless asked.

**Never run git.** The user owns version control, including read-only commands.

**Never launch a background job without explicit consent** — including `transcribe`. Default to
telling him the command.

---

## Status

**Three folders written**, through class 4 (2026-08-16):

- `01-Introduction-To-DevOps/` — 8 notes
- `Linux/` — 7 notes, 2,723 lines. **Done.**
- `Git/` — 6 notes, 2,221 lines. **Class 4 complete** (5 parts, ~2h 6m).
  `01` why Git exists + Git vs GitHub · `02` the local loop (`init`→`add`→`commit`→`log`) ·
  `03` remotes (`push`, `clone`, `pull` vs `fetch`, tokens) · `04` content addressing + blobs ·
  `05` tree and commit objects · `06` the index and the rest of `.git`.
  Note `03` spans parts 2–3; part 5 produced two notes. Otherwise one note per part.

> [!tip] **Hashes in the internals notes are real and reproducible — keep doing this.**
> Object IDs in notes `04`–`06` were computed, not invented: `sha1("blob <len>\0<content>")` for blobs,
> and the real binary tree format (`<mode> <name>\0<20-byte sha>`, entries sorted by name) for trees.
> A reader can run `git hash-object` / `git ls-tree` and get the same strings, which is what makes
> "same content → same ID" demonstrable instead of asserted.
> **Commit IDs cannot be reproduced** — they hash the author and timestamp too, so those are marked
> illustrative in the notes. Say so rather than implying otherwise.

**Git is being taught well past developer level**, and the internals are the most interview-valuable
material in the vault so far. Still to come, named at the end of class 4: **branches, merge, rebase,
cherry-picking**, then monorepo vs polyrepo and Git Flow.

> [!danger] **Class 4's recordings carry real credentials and PII — check before any frame grab.**
> Part 2 shows the instructor's name and email in `git log` output and in `git config user.name`, plus
> his GitHub username spoken aloud. **Part 3 is a live personal-access-token walkthrough with the token
> on screen.** All of it was placeholdered on the way into the notes; none of it may be screenshotted.

All mermaid, no images yet. Classes run **Wednesday and Saturday, 9:00 pm, 2–2½ hours**.

> [!important] **`Linux/` is flat and unnumbered by design, and it is the pattern to follow from here.**
>
> It replaced three numbered folders (`02-Linux-Fundamentals`, `03-Linux-Filesystem-And-Deployment`,
> `04-Users-Permissions-And-Processes`) totalling 19 small notes, merged on 2026-08-14 into 7 substantial
> ones. **The user's standing preferences, learned here:**
>
> - **One folder per subject, not per class.** Three classes of Linux is one subject.
> - **No `00-Syllabus.md` files.** He deleted them. Put currency checks and scope caveats inside the notes
>   they belong to.
> - **Merge rather than split.** A 500–700 line note is fine; a 60-line one is not. "500 is not that much
>   to read."
> - **Notes are numbered in CLASS ORDER, not learning order — until he says otherwise.** He needs to be
>   able to map a note back to the recording it came from while he is still revising. Every note carries
>   a `*Source: class N — date, recording parts X–Y.*` footer for exactly that reason. **Resequencing for
>   pedagogy is a separate, later decision, and it is his to make** — do not pre-empt it.
> - **When merging, remove duplication only.** Never compress an explanation to save space — breadth and
>   depth must survive the merge intact.

Running status, the per-part transcript table, the course-repo caveats and the **playback-speed
rules** (recording at 2× destroys a transcript, and the usual density check misses it) live in
`~/Desktop/Transcribe/tracks/devops.md`. **Read that file before transcribing anything.**
