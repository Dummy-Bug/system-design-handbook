# Coder Army Spring lecture notes — working rules

Turning the Coder Army *Spring Framework & Spring Boot* YouTube series into Obsidian notes in this
folder. Style reference: `~/Desktop/wiki/Java/DURGA/**` — same conventions, adapted below.

**The transcripts are Hindi** and arrive from the user **one video at a time, pasted into chat**.
There is no playlist fetch step and no transcription rig involved in this track.

---

## Rule 1 — Never drop anything from the transcript

**Everything in the transcript goes into the notes. Nothing is omitted unless the user explicitly says
to omit it.**

This includes:

- every worked example and program he walks through, with its output
- every analogy and aside — the MySQL connector, WhatsApp/Chrome/Spotify fighting over ports, the
  "programmer's laziness" line. These are not filler; they are how the concept is taught and how it
  will be recalled in an interview.
- every definition, in the words he gives it
- every list, every "how many types", every enumerated case

### The one standing exception: agendas and meta-framing

**Skip, without asking:**

- the syllabus run-through at the start — *"is series mein hum ye cover karenge, bahut maza aayega"*
- channel meta — *"notes GitHub pe daal dunga, link description mein hai"*, *"video pasand aayi toh
  like kar dena, comment chhod dena"*, *"aapse milte hain next video mein"*
- pure course navigation — *"ye hum aage dekhenge"* as a standalone aside with no content attached

**Everything from the moment he starts teaching is in scope**, including throwaway analogies, which
are exactly what must never be cut. A forward reference that carries information (*"iske andar se
Hibernate JDBC use karta hai, jo hum aage dekhenge"*) is content, not navigation — keep it.

Before claiming a part is complete, **read the transcript end to end** against the note.

### Hindi quotes: translate into English (ruled 2026-08-16)

**The notes are written entirely in English. Every quote is translated — never transliterated into Latin-script Hindi.**

```markdown
> A client can be anything at all.
```

**Not** `> Client toh koi bhi ho sakta hai.` — that was the original convention and it was reversed. The notes are read to study from, and switching scripts mid-sentence makes them slower to read, not more authentic.

**Translate faithfully, keeping his register.** He is informal and direct, and the English should be too — "you know that a server is nothing but a computer", not "a server may be understood as a computing device". **Keep the rhetorical shape**: his questions stay questions, his asides stay asides, and the emphasis he puts on a word stays bold in the same place.

**The blockquote is what marks it as his sentence** — no quotation marks, no italics. If you are compressing several sentences into one idea, that is prose — take it out of the blockquote.

### No italics anywhere, and no quotation marks anywhere (ruled 2026-08-16)

**Italics are not used in these notes at all.** Not for his quoted speech, not for emphasis on a single word. Emphasis is carried by **bold**, and a word that would have been italicised is simply left plain. `` `inline code` `` stays code.

| Write this | Not this |
|---|---|
| `> A client can be anything at all.` | `> *"A client can be anything at all."*` |
| `**Where you create the object is the problem.**` | `**Where you create the object is the problem.**` with `*where*` italicised inside the bold |
| `an invented tag gives \`Invalid content was found\`` | `an invented tag gives *"Invalid content was found"*` |

**A literal string from a log, an error or the screen goes in backticks**, not in quotation marks — it is a string, and backticks say so.

**Quotation marks do not survive anywhere outside a code block or inline code.** Not around his speech, and not around a word being quoted in prose either — write `they assume client means browser`, not `they assume "client" means "browser"`.

**Where a bare removal would read badly, reword rather than leave the quotes.** The phrase gets hyphenated into a compound — `the just-read-the-lines approach` — or the sentence takes the small word it needs — `the fix is not to remove the dependency`.

---

## Rule 2 — There is no companion PDF

**Unlike the Durga track, this chapter has no second written source.** The transcript plus measured
behaviour is all there is, so **measurement carries more weight here** — see Rule 3.

He mentions notes and practice questions on a GitHub repo. **If the user ever supplies those, they
become a second source to merge, not a fallback.**

---

## Rule 3 — Verify by running it

**Claims about how Spring behaves are checked by building and running a real project, not recalled.**

### The environment

| | |
|---|---|
| JDK | **25.0.1 only** — `/Users/home/Library/Java/JavaVirtualMachines/openjdk-25.0.1/Contents/Home` |
| Maven | `/opt/homebrew/bin/mvn` — **`JAVA_HOME` must be exported first**, or it fails with *"JAVA_HOME is not defined correctly"* |
| Gradle | **not installed** |
| Network | available — `start.spring.io` and Maven Central both reachable |
| Scratchpad | build throwaway projects there, never in this folder |

### How to check a Spring fact

```bash
export JAVA_HOME=/Users/home/Library/Java/JavaVirtualMachines/openjdk-25.0.1/Contents/Home
curl -s "https://start.spring.io/starter.zip?type=maven-project&...&dependencies=web" -o demo.zip
mvn -q clean package -DskipTests
java -jar target/demo-0.0.1-SNAPSHOT.jar
curl -s -i http://localhost:8080/hello
```

> [!warning] **Initializr writes a version id Maven cannot resolve.** The `starter.zip` API puts
> `<version>4.0.7.RELEASE</version>` in the pom, and Maven Central has **`4.0.7`**. The build fails
> with *"Non-resolvable parent POM"* until the `.RELEASE` suffix is stripped. **Strip it before
> building** — this is an artefact of the download API, not something the video's user would hit.

### Two things worth measuring every time

- **The actual startup log**, pasted verbatim — Tomcat version, port, boot time. It dates the note
  and it is what he will compare his own console against.
- **The response with headers** (`curl -i`), not just the body. Content type and status code are
  where Spring's behaviour is visible, and where it differs from what the video shows.

### Send a browser `Accept` header when the video uses a browser

**`curl` sends `Accept: */*` and gets different responses than Chrome does.** When the lecture
demonstrates something in a browser, reproduce it with the browser's header or the measurement is
about a different code path:

```bash
curl -s -i -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" http://localhost:8080/hello
```

---

## Rule 4 — State the current truth, never the old one

**The notes are read to learn from. Wherever the video is out of date or simply wrong, the main text
states what is true today** — not *"he says X, it is actually Y"*. Just Y.

**Record the versions actually measured**, since this series is being written against a moving target:

| | |
|---|---|
| Spring Boot | **4.0.7** (4.1.0 is also GA) |
| Java | **25** |
| Tomcat | **11.0.22**, embedded |

**The old behaviour still goes in, but demoted and reframed**, because he will meet it in older
tutorials, StackOverflow answers, and existing codebases. Put it in an `[!important]` written as
*"older material uses X"* — a fact about the ecosystem, never a correction of the note above it.

**Known drifts already found, which will keep recurring:**

- the Initializr *Spring Web* dependency resolves to **`spring-boot-starter-webmvc`** in Spring Boot 4;
  every older tutorial says `spring-boot-starter-web`
- **`jakarta.servlet`**, not `javax.servlet` (Jakarta EE 9, 2020)
- an unmapped path returns **JSON** to an API client and the **Whitelabel HTML page** to a browser —
  the video only ever shows the browser half

**`[!warning]` is reserved for danger**, not for currency — things that will actually bite. A version
change is not a danger; use `[!important]` or `[!info]`.

---

## Rule 5 — One video, one file

**One video = one transcript = one note file.** Do not split a video across several files, and do not
merge two videos into one.

- **Flat, numbered, kebab-case** at the top of this folder: `02-Building-Your-First-Spring-Boot-App.md`
- The number is the video's position in the playlist. **Leave a number unused rather than renumbering**
  if a video is skipped — a gap is how a missing part stays visible.
- **Grouping into chapter folders comes later**, once the whole series is in and the seams are
  obvious. Do not pre-emptively invent a folder hierarchy.

**These files are deliberately long — 400–900 lines is normal and fine.** Never trim content to hit a
line count.

---

## Rule 6 — File shape

- **Open with prose, not a heading.** The filename already names the topic; the first line should be a
  sentence that sets up what the part is for. (Established on `01` by the user.)
- **`#` marks a major topic within the video**; `##` and below are its sections. The H1s are what make
  the Obsidian outline usable.
- Mermaid diagrams, comparison tables, `---` separators between major topics.
- Callouts: `[!important]`, `[!info]`, `[!question]-` and `[!example]-` (collapsible), `[!warning]`
  for genuine danger only.
- **Keep code together with the analysis of its output.** He reads linearly and will not scroll back
  and forth to match a program to the discussion of its results.
- **Close every file with a `# What this part established` summary table** — one row per fact, in the
  order the note taught them. This is the revision surface.

### Never hard-wrap a paragraph (ruled 2026-08-16)

**This vault renders a single newline as a line break.** Obsidian's *Strict line breaks* setting is off, so a paragraph hard-wrapped at ~100 columns in the source shows up in reading view with ragged breaks mid-sentence — a break after "with", a break after "any of this".

**Write one paragraph as one source line, however long it runs.** The same goes for list items, callout lines and blockquote lines — a `>` line is wrapped by the reader's window, never by you. Code fences, tables and mermaid blocks keep their own line structure and are never touched.

**When reflowing a file that is already wrapped, watch the seam.** A join that loses its space produces `gets packaged.The`, `verifying,installing`, `not inyour code`. Grep `[a-z][.,;][A-Za-z]` outside code blocks afterwards, and prove the reflow changed nothing by comparing token streams with whitespace and `>` markers stripped before writing anything back.

---

## Rule 7 — Deep dives go in a collapsible callout

Anything that is **mechanism, evidence or background rather than the thing being taught** goes in a
collapsed callout, so he can read the note straight through and open the depth only when he wants it.

```markdown
> [!question]- **Deep dive — <what is inside>.** <one clause on why he might open it>
> …the whole thing, every line prefixed with `>` …
```

- **`[!question]-`** for *why does it work this way*. **`[!example]-`** for *here is it happening* —
  a demo, a thing broken on purpose, measured output. The trailing `-` is what makes it collapse.
- **The title must say what is inside**, so he can decide without opening.
- **The visible layer must stand alone.** Collapse it and the section still teaches the topic.
- **Never nest a collapsible inside a collapsible.** Flatten inner callouts to `#####` sub-heads.
- **Never leave a heading outside pointing at collapsed content** — it shows up in the outline and
  leads nowhere.

**What earns a deep dive:** the mechanism behind a rule, a startup or request trace, a multi-step
failure. **What does not:** the definition, the rule itself, the summary table, anything he would be
asked directly in an interview.

---

## Rule 8 — Write only after confirmation

**Do not create or edit note files until the user has explicitly asked for it.** Pasting a transcript
with "make notes out of this" is that ask; discussing a topic is not.

**External edits to note files are the user's own refinements — never revert them.** If a file changed
underneath you, read the change and follow the convention it establishes.
