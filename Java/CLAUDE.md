# Durga Java lecture notes — working rules

Turning Durga Sir's Core Java YouTube lectures into Obsidian notes under `DURGA/<NN>-<Topic>/`.
Style reference: `~/Desktop/Camp/*.md`.

## Rule 1 — Never drop anything from the transcript

**Everything in the transcript goes into the notes. Nothing is omitted unless the user explicitly says to omit it.**

This includes:

- every worked example and program the tutor walks through, with its output
- every analogy and story he tells — the school admission, the 70 mm screen, the kid asking to
  restart his life cycle, the classroom student. These are not filler; they are how the concept is
  taught and how it will be recalled in an interview.
- every definition, dictated word for word as he gives it
- every list, every "how many types", every case number

### Stale facts: state the current truth, never the old one (ruled 2026-08-15)

**Reversed from the original rule.** The notes are read to *learn from*, and learning a fact then
scrolling into a callout that invalidates it is double work — he has to learn it twice.

**So: wherever the video is out of date or simply wrong, the main text states what is true today.**
Not "he says 73, it is now 151" — just **"`String` has 151 methods"**. Not "as taught this fails, but
Java 16 allows it" — just show it compiling. Tables, summary rows, code samples and error messages
all carry the measured JDK 25 behaviour, with no `❌ as taught` / `✅ now` split columns.

**The old behaviour still goes in, but demoted and reframed**, because he will meet it in exam papers
and older material. Put it in an `[!important]` written as *"older material says X; that was true
through Java N"* — a fact about the ecosystem, never a correction of the note above it. Keep it only
where it is genuinely still encountered; drop it where the change was cosmetic (a reworded compiler
message that nobody will be quizzed on).

**`[!warning]` is now reserved for danger, not for currency.** *"Never call a wrapper constructor",*
*"a `return` inside `finally` swallows exceptions"*, *"assertions are off unless you pass `-ea`"* —
things that will bite. A version change is not a danger; use `[!important]` or `[!info]`.

**Everything asserted as current must be run on JDK 25 first** (Rule 3). Restating a fact means owning
it.

Only the user decides what gets cut. If something seems not worth including, **ask** — do not decide
unilaterally. (Precedent: he ordered the multithreading agenda file deleted, and separately told me
to keep the multitasking definition, classroom example and process-vs-thread diagram. Those calls
are his.)

### The one standing exception: agendas and meta-framing

Ruled twice (multithreading 2026-08-10, JVM part 1 2026-08-10). **Skip, without asking:**

- the syllabus / agenda run-through at the start of a chapter — "first I will cover X, then Y, then
  Z, this will take 10–15 hours"
- meta-framing about the topic rather than the topic — "this is not programming", "you only need
  the overview", "don't write this down", "very important for the interview room" as a standalone
  aside

This is about **course navigation**, not subject matter, and the note's own structure already says
what it covers. Everything the moment he starts teaching is in scope again — including throwaway
analogies and asides, which are exactly what must never be cut.

Before claiming a chapter is complete, **read the transcript end to end** and check it against the
notes. A keyword grep is not an audit — it misses exactly the stories and examples that matter.

## Rule 2 — Read the companion PDF for the chapter

`DURGA/pdfs/` holds Durga Sir's own written notes, one PDF per chapter:

| PDF | Chapter |
|---|---|
| `01 JVMDurga.pdf` | JVM architecture |
| `02 MultithreadingDurga.pdf` | Multithreading |
| `03 MultiThreadingEnhancementsDurga.pdf` | Multithreading enhancements |
| `04 CollectionsDurga.pdf` | Collections |
| `05 ExceptionHandlingDurga.pdf` | Exception handling |
| `06 Java.LangPackageDurga.pdf` | `java.lang` package |
| `07 GenericDurga.pdf` | Generics |
| `08 LambdaExpressionsDurga.pdf` | Lambda expressions |
| `09 GarbageCollectionDurga.pdf` | Garbage collection |

**Read the matching PDF before writing any note in that chapter.** It carries the exact definition
wording and contains full programs with their outputs that the video only gestures at. It is a
second source that must be merged with the transcript, not a fallback.

No PDF text extractor is installed. A pure-Python `zlib` + regex pass over the FlateDecode streams
works fine — do not install anything.

## Rule 3 — Verify by running the code

The videos are ~Java 6/7 era. JDK 25 is at `/usr/bin/java`; JDK sources are at
`~/Library/Java/JavaVirtualMachines/openjdk-25.0.1/Contents/Home/lib/src.zip`.

Compile and run the examples in the scratchpad and put the **measured** output in the notes, not the
remembered one. Where reality has moved, add a `[!warning]` naming the JDK version checked.

## Rule 4 — One file per transcript

**One video = one transcript = one note file.** Do not split a video across several files.

This is how he tracks which video he still has to transcribe: the file numbers line up with the
videos, so a gap in the numbering is a gap in the source. Where a video's transcript is not
available yet, **leave its number unused** rather than renumbering (e.g. `JVM-ARCHITECTURE/01-*` is
reserved for the first JVM video).

These files are deliberately long — 400–700 lines is normal and fine. **Splitting comes later**, once
the whole topic is finished and he decides where the seams go. Do not pre-emptively thin them, and
never trim content to hit a line count.

## Rule 5 — File shape

- Prose-first opening. Mermaid diagrams, comparison tables, `---` separators.
- Obsidian callouts: `[!important]`, `[!info]`, `[!question]-` (collapsible), `[!warning]` for
  anything outdated.
- Numbered kebab-case filenames.
- **H1 (`#`) marks a major topic within the video**; `##` and below are its sections. (Camp's
  no-H1 convention assumed one topic per file; a per-video file usually holds several, and the H1s
  are what make the Obsidian outline usable.)
- **Keep code together with the analysis of its output.** He reads linearly and will not scroll back
  and forth to match a program to the discussion of its results.

### Never hard-wrap a paragraph (ruled 2026-08-16)

**This vault renders a single newline as a line break.** Obsidian's *Strict line breaks* setting is off, so a paragraph hard-wrapped at ~100 columns in the source shows up in reading view with ragged breaks mid-sentence — a break after "with", a break after "any of this".

**Write one paragraph as one source line, however long it runs.** The same goes for list items, callout lines and blockquote lines — a `>` line is wrapped by the reader's window, never by you. Code fences, tables and mermaid blocks keep their own line structure and are never touched.

**When reflowing a file that is already wrapped, watch the seam.** A join that loses its space produces `gets packaged.The`, `verifying,installing`, `not inyour code`. Grep `[a-z][.,;][A-Za-z]` outside code blocks afterwards, and prove the reflow changed nothing by comparing token streams with whitespace and `>` markers stripped before writing anything back.

## Rule 6 — Deep dives go in a collapsible callout

Anything that is **mechanism, evidence or background rather than the thing being taught** goes in a
collapsed callout, so he can read the note straight through and open the depth only when he wants it.

```markdown
> [!question]- **Deep dive — <what is inside>.** <one clause on why he might open it>
> …the whole thing, every line prefixed with `>` …
```

- **`[!question]-`** for *why does it work this way* — mechanism, derivation, background.
  **`[!example]-`** for *here is it happening* — a demo, a thing broken on purpose, measured output.
  The trailing `-` is what makes it start collapsed. Without it the callout is always open.
- **The title must say what is inside**, so he can decide without opening. Not "Deep dive"; rather
  "Deep dive — why *these* five default values, and why the default `char` is not a space."
- **The visible layer must stand alone.** Collapse it and the section still teaches the topic —
  the must-know sentence stays outside, in the table or a short `[!important]`.
- **Never nest a collapsible inside a collapsible.** Flatten inner callouts to `#####` sub-heads or
  bold lead-ins.
- **Never leave a heading outside pointing at collapsed content** — an `###` above a collapsed block
  shows up in the Obsidian outline and leads nowhere. Put the heading inside, or drop it.

What earns a deep dive: the bit-level reason behind a rule, a startup/ordering trace, a
multi-step failure mechanism, a "two objections that make this sound impossible" walk-through.
What does not: the definition, the rule itself, the summary table, anything he would be asked directly.

## Rule 7 — Write only after confirmation

Do not create or edit note files until the user has explicitly asked for it.
