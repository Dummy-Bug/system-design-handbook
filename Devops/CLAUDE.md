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

- **Folders are numbered in READING order — the order he should study them in.** He renumbered them himself on 2026-08-20 (`01-Introduction-To-DevOps/`, `02-Linux/`, `03-Git/`) for exactly that reason: the number tells him what to read first. So far reading order and course order agree; **if the course ever teaches a subject out of the order it should be learned, the folder number follows the reading order and the class mapping lives in this file rather than in the note.**
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

**Seven folders written**, through class 14 (2026-09-25). **Networking is complete**, CI/CD covers both Jenkins and GitHub Actions, deployment strategies is complete as its own folder, and Docker now carries the whole conceptual half of the subject with the practical walkthrough still to come.

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
  **Reviewed end to end as a stranger on 2026-09-12, and eleven findings were fixed.** Three were correctness errors, and they are the ones worth remembering. **A JWT was described as held server-side** in note `06`, inside the very section arguing that a stored session breaks under a load balancer — a token is held by the client and is in fact a third answer to that problem, so the note now gives all three. **Note `11` described RSA key transport while naming TLS 1.3**, which removed that mechanism outright; the seven steps are kept because the failure they lead to motivates Diffie–Hellman, but the note now states plainly that this is the pre-1.3 form and shows the real one-round-trip sequence. And **note `05` used a live Google IPv6 address**, replaced with the documentation range `2001:db8::/32` from RFC 3849, with `::` compression now explained in note `01` where eight groups is first claimed. The other eight were clarity: a missing whole-architecture diagram, a status code used before introduction, a term used a note before its definition, an uncounted number, an SSH port mapped to a web app, and a code-block header naming a file that did not exist.

  **Note `02` was rewritten and renamed by class 8** — class 7 promised forward-versus-reverse proxy and never reached it, so note `02` carried a marked beyond-lecture callout. Class 8 taught it properly, so the callout was replaced with real lecture material and the file became `02-Forward-And-Reverse-Proxies.md`. **Merging into the existing note rather than adding a new one is the right call when a later class returns to the same concept.**
- `05-CI-CD/` — **26 notes, 3,601 lines, plus an `Images/` folder. Classes 9, 10, 11 and 12.** The subject is one folder covering two tools, because the whole of class 11 is built on comparing them.
  **Class 9** (3 parts) — `01` the manual way · `02` the pipeline · `03` build versus deploy · `04` continuous integration · `05` delivery versus deployment · `06` a pipeline run · `07` orchestration and tools · `08` controller and agents · `09` executors and workspace · `10` pipeline as code · `11` declarative and scripted.
  **Class 10** (3 parts) — `12` installing Jenkins · `13` preparing the server · `14` the demo application · `15` a real Jenkinsfile · `16` a pipeline in action.
  **Class 11** (2 parts, 2026-09-20, ~1h 19m) — `17` why GitHub Actions · `18` events and schedules · `19` jobs, steps and actions · `20` runners · `21` testing pull requests · `22` deploying to your server. Three answers to student questions were folded into existing notes rather than made new ones: parallel stages and concurrent builds into `15`, how many pipeline files a set of microservices needs into `13`, and a webhook being an ordinary HTTP request rather than a message queue into `16`.
  **Class 12** (1 part, 2026-09-20, ~1h 20m) — `23` matrix builds · `24` secrets and environments · `25` short-lived credentials · `26` build caches and artifacts. The class's fifth topic, **deployment strategies, was cut off mid-setup when the recording ended** and is taught as its own lecture next, so no note was written for it. The load-balancer and instances material at the tail of the recording is the opening of that note, held back deliberately rather than stranded at the end of `26`.

  **Notes `12`–`16` and `17`–`21` were both executed on the user's own machine, not just written.** A Multipass VM running Ubuntu, Jenkins, a multibranch pipeline, then a self-hosted GitHub Actions runner on the same VM — every command, output and error in those notes came from a real run or a legible frame grab. **This is the standard for this folder: nothing in it is recalled.**

  > [!important] **The whole of class 11 was dictated, so every command came from frames or docs.**
  > The two workflow files in note `21` were read off the video frame by frame. Everything else — workflow and event syntax, cron's five fields and its UTC default, `actions/checkout@v7`, `actions/setup-java@v6`, the Jenkins `parallel` and `failFast` syntax, `svc.sh` — came from official documentation. **One thing is knowingly unsourced: `RUNNER_TRACKING_ID=""`**, which detaches a process from the Actions runner so it survives the job ending. It is visibly used in the file on screen and works, but GitHub does not document it, and the note recommends systemd over it anyway.

  > [!danger] **Class 11 is taught entirely on the instructor's personal GitHub account.**
  > His username and repository are in the browser address bar for most of part 2, and his name and hostname are in every terminal prompt in both parts. **No frame from either recording may be embedded.** The demo endpoints also return the course's brand name in their response bodies. All of it was replaced on the way into the notes — the running example is the same calculator on 8081 that the Jenkins notes deploy, chosen so the folder carries one application throughout rather than two.

  > [!important] **Class 12 was dictated too, and every command in notes `23`–`26` came from GitHub's documentation.**
  > Nothing was typed on screen except clicks through the repository settings UI. `strategy`/`matrix`, `${{ matrix.x }}`, `${{ secrets.X }}`, the job-level `environment` key, `permissions: id-token: write` and the OIDC subject claims were all taken from GitHub's docs and checked. **Two verifications are worth keeping.** The cache key he derived on the board — operating system plus a hash of `pom.xml` — is character-for-character the Maven example in `actions/cache`: `${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}`. And the four things he said OIDC proves are literally the fields of the subject claim: `repo:<org>/<repo>:ref:refs/heads/<branch>` and `repo:<org>/<repo>:environment:<name>`. Current versions confirmed on 2026-09-20: `actions/checkout@v7`, `actions/setup-java@v6`, `actions/cache@v6`.

  > [!danger] **Class 12 names the instructor's former employer and uses the course brand as an example organisation.**
  > He gives the company he worked at for two and a half years, along with when he was granted production credentials and why — the same employment-history exposure as class 6, and out under the neutralise rule. The OIDC walkthrough uses the course's own brand as the organisation and repository, replaced with `bookcart/calculator-service` to match the screenshot already in note `22`. Six or seven student names across the part. **The repository settings pages are on his personal account, so no frame from this recording may be embedded either.**

  > [!tip] **`24` borrows a larger application on purpose, and says so in the note.**
  > The calculator has no database and no cloud account, so it is a poor vehicle for credentials. Rather than invent a second pipeline — the drift that had to be undone in class 11 — note `24` states plainly that the examples assume an ordinary application with a database behind the same pipeline. **Say it in the note rather than quietly switching examples.**

- `06-Deployment-Strategies/` — **5 notes, 672 lines. Class 13, both parts. Done.** `01` how a service is deployed: monolith, microservices, API gateway and service discovery, instances, a load balancer per service, static against dynamic algorithms, regions, Geo DNS and what a CDN cannot do · `02` rolling deployment: blast radius, one instance at a time, halting time, monitoring and rollback · `03` blue-green: the cost of undoing a rolling deployment, two fleets, the router, rollback as a routing decision, the fleets swapping roles · `04` canary: the percentage ladder, the same thing expressed as pool composition, why it is the affordable answer to blue-green, and rolling versus canary as a difference of intent rather than mechanism · `05` feature flags: two paths in one build, the flag as configuration, the internal-only instance and alpha versus beta testing, and the probability form.
  **The folder is ordered as one argument rather than as four techniques.** Each note opens on the previous one's weakness: rolling caps exposure but takes a full deployment to reverse, so `03` buys instant reversal and pays with total exposure, so `04` controls exposure directly and pays with time, and `05` drops the requirement for a second server altogether. **Keep that spine if any of these notes are ever rewritten** — the techniques are not independent and reading them as a list loses the whole point.

  > [!important] **Class 13 part 2 was dictated too, and three things in notes `03`–`05` came from outside it.**
  > The Java in note `05` was written here and executed on JDK 25, not taken from the recording — the bucket logic, the widening list and the measured spread (twelve batches of 100 users at one bucket in ten gave 6, 14, 17, 8, 10, 7, 15, 8, 11, 11, 7, 10) are real output, and that spread is the evidence behind the note's expected-not-guaranteed callout. **The Spring binding was verified against the documentation and corrected as a result:** `@Value` supports a default with `${key:default}` and binds scalars, but it does **not** bind a comma-separated value to a `List`, so the bucket list uses `@ConfigurationProperties` with YAML sequence syntax instead. The canary etymology — Haldane, 1896, a Welsh colliery explosion, retired in Britain in 1986 for electronic detectors — was researched and added at the user's request, because the recording never explains the word.

  > [!tip] **Blue-green is taught twice in the recording and the second version corrects the first — only the correct one is in the note.**
  > It is first drawn as a gradual traffic shift (50/50, then 75/25), then retracted: real blue-green switches all traffic in one step, and the gradual form is canary. **Note `03` teaches only the instant cutover**, at the user's instruction, and closes with a short callout that the two names get used interchangeably in the wild and that the discriminating question is whether traffic moves all at once. The gradual-shift material lives in `04` where it belongs.

  > [!danger] **Class 13 part 2 names the course brand, a second platform, and another instructor.**
  > The brand is used as the example company for the internal-only testing walkthrough and again in an answer about when he would dismiss someone; a second platform of his is named alongside it; another instructor is named by name when a student compares them. Three student names. All out. The running example stays the `bookcart` shop and its order service, carried from `04-Networking/` and `01`–`02` of this folder.

  > [!important] **Why this is a separate folder rather than notes `27`+ of `05-CI-CD/`.**
  > The decision was made after reading class 13 part 1, not before. **The first thirteen minutes are not about pipelines at all** — monoliths, gateways, service discovery, regions and CDNs are the shape of a deployed system, and they are established because the strategies are meaningless without them. That is a subject opening. `05-CI-CD/` was also already the largest folder in the track at 26 notes, this material gets leaned on again when Kubernetes arrives, and reading order still holds: you need a pipeline before strategies make sense.
  > **The cost of the split is real and was accepted deliberately.** A folder must stand alone, so `06` may not lean on `04-Networking/` for load balancers and API gateways — it has to re-establish them. The recording does exactly that, so note `01` carries it honestly rather than padding. **If a later class returns to networking proper, that still belongs in `04`, not here.**

  > [!danger] **Class 13 names the instructor's former employer again, and tells a real company's production bug.**
  > The employer appears when he describes whole teams being dismissed over a production incident — out, same as classes 6 and 12, and the point survives without it. **The food delivery payment bug is kept but the company is not named**: the story is excellent teaching, but asserting a specific payment defect against a named business is an unverifiable factual claim about them, and the lesson is identical told as a food delivery app in its early days. Student names stripped as usual. The running example is the `bookcart` shop, carried over from `04-Networking/`.

- `07-Docker/` — **5 notes, 994 lines. Class 13 part 3 and the whole of class 14.** `01` why containers exist: it works on my machine, an application being far more than its code, the two machines that disagree, one staging server holding one configuration, virtual machines and why they are the wrong size, containers, containerization, and the correction that a container is not a virtual machine · `02` images and containers: what Docker contributed and what its alternative is, image against container as program/process and as class/object, the read-only template and why a code change forces a new image, what an image holds, the writable layer and copy-on-write, disposability, and volumes · `03` the Dockerfile: derived from the manual handover, what building carries out and what it deliberately leaves for the container, `FROM` and base images and Docker Hub, `WORKDIR`/`COPY`/`CMD`/`ENV`, CMD against ENTRYPOINT, why images are layered, the build cache, and the three best practices · `04` building and running a container: the whole sequence, two containers from one image, and the edit that stays local to one of them · `05` namespaces and cgroups: what may I see against how much may I use, the flats and the lunch box, the PID, network and mount namespaces, port publishing and the rewrite, the memory leak, and why this still is not a virtual machine.
  **The folder is ordered as one argument, like `06`.** `01` establishes that an application is more than its code and that a virtual machine is the wrong size for the problem; `02` names what you are actually handling; `03` is how you describe what you want; `04` does it; `05` explains why the isolation holds. **Keep that spine** — `04` exists to raise the question `05` answers, and reading `05` before the demonstration loses the motivation entirely.
  **Still to come:** the practical walkthrough of the commands, which the next class does properly, and volumes beyond the short treatment in `02`.

  > [!danger] **The wrong analogy is in this note on purpose, labelled wrong.**
  > A container described as a lightweight virtual machine is how nearly everyone first understands it, and it is false — no private kernel, no private file system, no private memory, only a view of the host that makes it look that way. The instructor gives the analogy and flags it as incorrect in the same breath, twice, answering two separate student questions that both come from believing it. **Note `01` keeps both halves and uses `[!warning]` for the correction, which is one of the few genuine traps in this vault.** Do not let a later note quietly restate the analogy as true.

  > [!important] **Three things were corrected on the way in from class 13 part 3, and the pattern is the usual one.**
  > **The Java compatibility direction was stated backwards** — the class says Java 21 code is not backward compatible with Java 8, when the real rule is that old code runs on new runtimes and not the reverse; the example and the conclusion were both right, only the label was inverted. **The port numbers were invented aloud** (8080 offered for a database, 9090 picked for Redis on the spot), so the note uses the real defaults: MySQL 3306, confirmed in `/etc/services`, and Redis 6379, confirmed in Redis's own configuration documentation. **Six student names were used as the example developers** and are all out.

  > [!important] **Class 14 carried three more errors, and all three are written as corrected fact with no trace of the taught version — at the user's explicit instruction.**
  > **Containers do not copy the image's layers.** The class says a container first copies the layers and then adds a writable one; Docker's storage documentation says containers share the underlying image and copying happens per file, on write. This one is load-bearing rather than pedantic — if each container really copied 500 MB, containers would cost what the virtual machines in note `01` were rejected for costing, and the folder's whole argument would collapse. **CMD against ENTRYPOINT** was answered as CMD being preferred because it accepts more parameters, which is not the distinction: arguments given to `docker run` are appended to an exec-form ENTRYPOINT and **override CMD entirely**. **The default memory limit** was asked about and left unanswered with a suggestion to look it up; the real answer is that a container has **no resource constraint at all** by default and can take as much as the host's kernel allows, with 6 MB the floor when a limit is set — which strengthens the class's own memory-leak argument rather than weakening it.

  > [!tip] **Everything command-shaped in class 14 came from Docker's documentation, and nothing in `04` was executed.**
  > Both parts were whiteboard work apart from one six-minute terminal demonstration, so `docker build -t` and the build context, `docker run -it --name`, `-p` in host-then-container order, `--memory`, `ps -a`, the Dockerfile instructions and the volume flag were all taken from the docs. **The four base image tags were checked to exist rather than assumed** — `eclipse-temurin:21-jre`, `node:21`, `python:3.13` and `alpine` all resolve on Docker Hub. **Note `04` is the one note in this track written from documentation without a run**, at the user's decision, because the next class walks the commands through properly and the experimentation belongs there. It fabricates no output — the commands and their effects are documented, and nothing is presented as captured. **When that class is transcribed, `04` is the note to extend with real runs rather than a place to add a second note.**

  > [!danger] **Class 14 uses seven student names as the example developers, and one of them is inside the demo output.**
  > The file edited in the live demonstration is changed to read `hello from <name>`, so the string would have gone into a note verbatim if it were copied across. Part 1 also puts **two real routable IP addresses** on the board as example container addresses; they are replaced with `192.0.2.0/24` from RFC 5737's documentation range. Database ports were invented aloud again (8393, 8191, 9181). The terminal work is on the same Ubuntu VM as the Jenkins notes, with the hostname in every prompt, **so no frame may be embedded without cropping**.

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

> [!important] **Every example is Java, never Node.js — set 2026-09-19, at his instruction.**
> He knows Java, and a Node.js example is one more thing to decode before the concept lands. The running application is a Spring Boot bookshop at `bookcart.in`, built with Maven: sources under `src/main/java`, tests under `src/test/java`, `pom.xml` at the root, test classes named `*Test.java` so Surefire picks them up. **When the class demonstrates in Node.js, translate the example to Java and Maven rather than carrying the Node version**, and verify every Maven command against the lifecycle docs before writing it. Node.js was removed from every folder on that date. JavaScript mentioned as the language of the browser front end is a different thing and stays.

Classes run **Wednesday and Saturday, 9:00 pm, 2–2½ hours**.

> [!important] **The visual standard for this vault — set on 2026-09-12 and applied to `04-Networking/` first.**
> The reference implementation is `~/Desktop/wiki/AI-Engineering/09-LangGraph-Streaming/04-Tasks-Checkpoints-Debug.md`. **Every mermaid flowchart carries `style` lines**, using one palette consistently so a colour means the same thing in every diagram in the vault: `#1f4f7a` blue for the mechanism being explained, `#1f6f3f` green for the working or correct outcome, `#7a1f1f` red for the broken one or the attacker, `#7a5a1f` amber for a caution or an intermediate stage, `#2d333b` dark grey for a neutral actor, `#3a3a3a` grey for something inert. Always with `color:#fff`. Sequence diagrams take no node styling and are left alone.
> **Callouts are varied rather than uniform.** The vault uses `[!important]`, `[!warning]`, `[!tip]`, `[!note]`, `[!question]`, `[!bug]`, `[!failure]` and `[!info]`. Before this pass `04-Networking/` used only two types across 49 callouts, which reads flat; a folder should spread across five or more. `[!warning]` is still reserved for genuine danger or a real trap.
> **DevOps notes carry no code blocks unless a command is genuinely being taught** — this course has almost none so far, so config and shell fences stay rare and every one must still come from a verified source.

**`04-Networking/Images/` is the first images folder in this track.** Five diagrams from Wikimedia Commons, all public domain or CC0, all downloaded locally rather than hot-linked, each opened and read before embedding, with source, author, licence and any modification recorded in `Images/CREDITS.md`. Two were edited: the proxy pair had their non-English language variants stripped and their example domain relabelled to the folder's running brand, and the Diffie–Hellman analogy had its secret colours changed to the red and blue the note text uses. **Prefer an image where it beats a diagram** — a widely reproduced standard illustration such as the OSI stack, or a real timeline with measurements on it such as the TLS 1.3 handshake — and keep mermaid for anything specific to this folder's own running example.

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
> - **Notes are numbered in CLASS ORDER, not learning order — until he says otherwise.** The number is what maps a note back to the class it came from while he is still revising. **Resequencing for
>   pedagogy is a separate, later decision, and it is his to make** — do not pre-empt it.
> - **No source footer. Removed from every note on 2026-09-12, at his instruction.** Notes used to end with `*Source: class N — date, recording parts X–Y.*`. They no longer do, and new notes must not add one. **A note ends on its last real idea and mentions no course, class, date, recording or lecture anywhere in it** — the general no-provenance rule now has no exception. Which class fed which note is recorded in this file and in the track file, where it belongs.
> - **When merging, remove duplication only.** Never compress an explanation to save space — breadth and
>   depth must survive the merge intact.

Running status, the per-part transcript table, the course-repo caveats and the **playback-speed
rules** (recording at 2× destroys a transcript, and the usual density check misses it) live in
`~/Desktop/Transcribe/tracks/devops.md`. **Read that file before transcribing anything.**

## Verify by running it, never from recall

**Any claim about how a language, library or tool behaves gets executed before it is written down.** Not recalled, not inferred from the name, not taken from a search result, and not copied from the source material. Run it, read the output, put the measured result in the note.

This applies to **definitions**, not only to code examples. A definition is a claim about behaviour and is checked the same way — the failure mode is a sentence that sounds right, reads fluently, and is wrong in a way nobody notices until it matters.

**Worked example of the failure.** `__file__` was written up as a string holding the path of the file **currently being executed**, present in **every module**. Both halves are false, and a two-file test settles it in seconds: run `main.py`, which imports `helper.py`, and inside `helper.py` the value is `helper.py` — it is the module's own file, not the entry point. Separately, `hasattr(sys, "__file__")` is `False`, because C built-ins have no file on disk. The wrong version had been written into the same note that already contained the contradicting fact two paragraphs later.

**How to check, in order of preference:**

1. **Run it in the project's own environment** — `uv run python -c ...`, or the venv's interpreter directly. The installed version is the authority, not the latest docs.
2. **Print the actual attribute** rather than grepping the source. Stale comments outlive the behaviour they describe: `transformers` still carries comments saying `max_length` defaults to 20 long after v5 removed it.
3. **Read the docs only to find out what to test**, then test it.

**Version drift is the common case, not the exception.** A recording is always older than the installed library. When the two differ, say both and name the versions — never silently pick one.

**When something genuinely cannot be run** — no API key, no hardware, code that was never pushed — say so in the note, and label what is measured versus what is reconstructed. Never present an untested claim in the same voice as a tested one.
