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

- **Folders are numbered in READING order — the order he should study them in.** He renumbered them himself on 2026-08-20 (`01-Introduction-To-DevOps/`, `02-Linux/`, `03-Git/`) for exactly that reason: the number tells him what to read first. So far reading order and course order agree; **if the course ever teaches a subject out of the order it should be learned, the folder number follows the reading order and the note footers still record the class.**
- **Notes INSIDE a folder stay in class order** — see the `[!important]` block near the end of this file. Folder number = what to read first; note number = which class it came from.
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

### Never hard-wrap a paragraph

**This vault renders a single newline as a line break.** Obsidian's *Strict line breaks* setting is off, so a paragraph hard-wrapped at ~100 columns in the source shows up in reading view with ragged breaks mid-sentence — a break after "with", a break after "any of this".

**Write one paragraph as one source line, however long it runs.** The same goes for list items, callout lines and blockquote lines — a `>` line is wrapped by the reader's window, never by you. Code fences, tables and mermaid blocks keep their own line structure and are never touched.

**When reflowing a file that is already wrapped, watch the seam.** A join that loses its space produces `gets packaged.The`, `verifying,installing`, `not inyour code`. Grep `[a-z][.,;][A-Za-z]` outside code blocks afterwards, and prove the reflow changed nothing by comparing token streams with whitespace and `>` markers stripped before writing anything back.

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

**Four folders written**, through class 8 (2026-09-02). **Networking is complete** — CI/CD starts with the next class.

- `01-Introduction-To-DevOps/` — 8 notes
- `02-Linux/` — 7 notes, 2,723 lines. **Done.**
- `03-Git/` — **18 notes, 4,903 lines. Done.** Classes 4, 5 and 6 all complete.
  **Class 4** (5 parts, ~2h 6m) — `01` why Git exists + Git vs GitHub · `02` the local loop (`init`→`add`→`commit`→`log`) · `03` remotes (`push`, `clone`, `pull` vs `fetch`, tokens) · `04` content addressing + blobs · `05` tree and commit objects · `06` the index and the rest of `.git`.
  **Class 5** (4 parts, ~2h 15m) — `07` branches (`refs/heads`, `HEAD`, `switch`) · `08` merging: fast-forward, three-way, conflicts · `09` rebase and force-push · `10` cherry-pick and stash · `11` `log`/`show`/`diff` and `reset`/`restore`/`revert` · `12` `git bisect`.
  **Class 6** (3 parts, ~2h 8m) — `13` pull requests and code review · `14` Git Flow · `15` GitHub Flow · `16` trunk-based development, feature flags, deploy vs release · `17` monorepo and polyrepo · `18` signed commits.
  Note `03` spans class 4 parts 2–3, note `08` spans class 5 parts 1–2, and notes `13` and `15` span class 6 parts 1–3 and 2–3. Class 4 part 5 produced two notes, class 5 part 4 produced three, and class 6 part 3 fed four.
- `04-Networking/` — **13 notes, 2,002 lines, 55 mermaid diagrams. Done.** Classes 7 and 8, both recorded on 2026-09-02.
  **Class 7** (2 parts, ~1h 55m) — `01` how a request finds a server: methods, endpoints, IPv4/IPv6, one server hosting many applications, ports, well-known ports, listening, sockets, MAC vs IP · `02` reverse proxy: the 443-to-8080 gap, the mapping table, nginx wearing several hats · `03` TCP, UDP and the layer model: OSI, three-way handshake, guarantees, the payment failure, packet loss, connection lifetime · `04` DNS resolution: browser cache → resolver → root → TLD → authoritative, TTL, registrar vs authoritative · `05` DNS records: A, AAAA, CNAME, TXT, MX, NS, subdomains, `www` is not the apex, where each record is written · `06` scaling and load balancers: vertical vs horizontal, public/private IP, routing algorithms, sticky sessions vs a shared session store, health checks, layer 4 vs layer 7.
  Note `05` spans both parts; part 2 fed `05` and `06`.
  **Class 8** (1 part, ~2h 27m) — `07` API gateway: microservices, routing by endpoint, gateway versus load balancer, authentication and rate limiting · `08` HTTPS and what it guarantees: HTTP is plaintext, man-in-the-middle, confidentiality/integrity/authentication · `09` symmetric and asymmetric keys: the speed-versus-secret trade, the key-exchange problem · `10` certificates and trust: the public-key substitution attack, digital signatures, certificate authorities, chaining, the root store · `11` the TLS handshake: seven steps end to end · `12` Diffie-Hellman key exchange: the colour analogy, the arithmetic, ECDHE and ephemeral keys · `13` certificate management: Let's Encrypt, ACME, Certbot, and TLS termination at the reverse proxy.
  **Note `02` was rewritten and renamed by class 8** — class 7 promised forward-versus-reverse proxy and never reached it, so note `02` carried a marked beyond-lecture callout. Class 8 taught it properly, so the callout was replaced with real lecture material and the file became `02-Forward-And-Reverse-Proxies.md`. **Merging into the existing note rather than adding a new one is the right call when a later class returns to the same concept.**

> [!tip] **Hashes in the internals notes are real and reproducible — keep doing this.**
> Object IDs in notes `04`–`06` were computed, not invented: `sha1("blob <len>\0<content>")` for blobs,
> and the real binary tree format (`<mode> <name>\0<20-byte sha>`, entries sorted by name) for trees.
> A reader can run `git hash-object` / `git ls-tree` and get the same strings, which is what makes
> "same content → same ID" demonstrable instead of asserted.
> **Commit IDs cannot be reproduced** — they hash the author and timestamp too, so those are marked
> illustrative in the notes. Say so rather than implying otherwise.

**Git was taught well past developer level**, and the internals are the most interview-valuable material in the vault so far. Class 6 changed register completely: no new plumbing, all team process — branching strategies, review etiquette, repository layout. The notes carry that by deriving each strategy from the one before it rather than listing three of them, with the single idea underneath stated explicitly: **integration difficulty grows with the time two branches stay apart.** Git Flow pays that cost deliberately, GitHub Flow shortens it, trunk-based development attacks it — and feature flags are what make attacking it survivable.

**Networking is taught deliberately narrow, and the notes hold that line.** The framing given at the top of class 7 is that a DevOps engineer needs enough networking to deploy and debug, not a network engineer's education — and four topics are explicitly pushed to system design: API gateway internals, consistent hashing, how balancer health monitoring really works, and distribution mechanics. The notes stop where he stopped and say so rather than filling the gap. The spine underneath them is a single question asked repeatedly: **an address gets you to the machine, and then what?** Ports answer it for one machine hosting several applications, a reverse proxy answers it when the public port and the application's port differ, DNS answers it when all you have is a name, and a load balancer answers it once one machine is not enough — at which point hiding the machines becomes the whole benefit, and anything a server remembers privately becomes a bug.

> [!tip] **The course repo's `Notes.pdf` is worth reading before writing, not after.**
> For class 6 it was a 40-page written guide covering the whole subject properly, and it supplied things the recording did not carry cleanly: the full pull-request command sequence, what a release branch is for beyond testing, the review-comment labels, and `git commit -S`. **It is still a lesson plan rather than a record** — it went further than the class did in several places — so everything from it was checked against the transcript before being used, and anything the class did not reach stays out or gets marked. Ask for the lecture folder link if it has not been shared.

> [!tip] **Notes 07–12 carry more marked additions than any earlier class, and every one is load-bearing.**
> `git merge --abort` · `git rebase --continue`/`--abort` · `--force-with-lease` over `-f` · `git stash list` and `apply` vs `pop` · `git restore --staged` · `git revert` · `git bisect reset` · `git bisect run <script>`.
> The pattern worth repeating: **the class teaches the happy path of a dangerous command and omits the escape hatch.** Every one of those additions is what a reader needs at the moment the command goes wrong, so they are marked as beyond-lecture and kept.

> [!danger] **Class 5 part 4 shows a `reset --soft` followed by a force push to `master`.**
> That is precisely the shared-history rewrite note `09` warns against. It was kept in note `11` with a callout tying it back, rather than being shown as routine or silently dropped. **Where the instructor contradicts an earlier note, say so and reconcile it — do not quietly pick one.**

> [!danger] **Classes 4, 5 and 6 all carry real credentials or PII — check before any frame grab.**
> **Class 4 part 2** shows the instructor's name and email in `git log` output and in `git config user.name`, plus his GitHub username spoken aloud. **Class 4 part 3 is a live personal-access-token walkthrough with the token on screen.** **Class 5 part 1 shows him pasting that token again from his notes**, about four minutes in, to push. All of it was placeholdered on the way into the notes; none of it may be screenshotted.
> **Class 6 adds his employment history** — he names both companies he has worked for, in part 2, answering a student. That is his personal information, not course material, and it is out under the neutralise-named-examples rule. Student names appear in all three parts of class 6, roughly a dozen of them.
> **Classes 7 and 8 are taught entirely on his own live domains** — the course site and a second site of his, used as the running example for DNS, subdomains, ports and load balancing across roughly 200 lines of transcript, plus example mail addresses at them. All of it was replaced with an invented brand on the way into the notes. Student names appear in both parts, about a dozen again, and he is addressed by an honorific throughout — all stripped.


> [!tip] **The placeholder conventions settled for `04-Networking/` — reuse them, do not reinvent them.**
> Every domain in these notes is one invented brand with its subdomains (`api.`, `admin.`, `manager.`, `blog.`), chosen so the notes read as one continuous example rather than a different placeholder per note. Example IP addresses keep the shape used on the board but with **legal octets** — the ones taught had values above 255, which is a real error to publish. Ports came from `/etc/services` rather than the recording, because the spoken numbers included at least one slip. **A later networking class continues this subject, so the same brand and the same addresses must carry over.**

All mermaid, no images yet. Classes run **Wednesday and Saturday, 9:00 pm, 2–2½ hours**.

> [!important] **One flat folder per subject, and it is the pattern to follow from here.**
>
> `02-Linux/` replaced three numbered folders (`02-Linux-Fundamentals`, `03-Linux-Filesystem-And-Deployment`,
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
