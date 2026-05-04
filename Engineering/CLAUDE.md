---
name: Engineering Wiki Writing Guide
description: How to write notes in this wiki — Socratic method, school theme, link-driven knowledge graph
---

# CLAUDE.md — How to Write Notes in This Wiki

This file tells you how to write notes in `Engineering/`. Read it before writing anything here.

---

## The One Rule That Overrides Everything Else

**Never mention any real company, product, codebase, team, or internal system by name.**

Not as an example. Not as a "e.g." Not in passing. Not even in a diagram label.

Real-world learning always comes from working on something concrete — a real pipeline, a real refactor, a real bug. That's fine. But the note must strip the origin completely. No company names, no product names, no service names, no internal API names, no domain-specific terminology that identifies the employer.

The test: could this note have been written by someone at any company, working on any system? If not, rewrite it until it passes.

> [!danger] If you are tempted to write "in our pipeline..." or "at our company, we had..." — stop. Use the school/teacher/student theme instead, or a plain generic code example with placeholder names.

**The default theme for all examples in this wiki is: a teacher querying a school pipeline to look up student marks.**

- The human actor = the teacher
- The data subject = the student
- The identifier = roll number
- The data = marks / report card
- Disambiguation = multiple students share the same name, teacher picks by roll number
- The pipeline = a LangGraph workflow the teacher interacts with

This theme maps cleanly onto any agentic workflow where a human operator queries or acts on records about other people. Use it for all HITL examples, streaming examples, and node behavior examples.

For non-AI / pure-systems notes (asyncio, networking, queues, databases), the school theme is optional — generic placeholder names are fine when the school analogy would be a stretch.

Wrong:
```python
# exposes internal domain
await profile_service.get_employee_profile(employee_id)
```

Right:
```python
# generic, using the school theme
marks = await marks_service.fetch(roll_no)
```

The note should be permanently shareable. Treat every note as something you might post publicly or hand to someone at any company.

---

## Three Principles That Govern What Gets Written

These replace any "daily note" or calendar-driven framing. Notes here are concept-driven, not chronology-driven.

### 1. A note exists because a concept demanded it, not because today is a new day.

A new note appears when you encountered a real concept gap and resolved it — not on a schedule. If you have nothing to add today, write nothing. Calendar guilt produces shallow notes. Concept hunger produces deep ones.

### 2. Every note links to its prerequisites and to notes that build on it.

Wikilinks are mandatory, not decorative. A note without a prerequisite breadcrumb is either a true root concept (rare) or you forgot. Use the format:

```markdown
> Prerequisite: [[note-name]], [[other-note]] — one-line description of what they establish.
```

When you finish a note, search the wiki for any existing note this one builds on — add backlinks both ways. The graph view should never be empty.

### 3. When a folder reaches 4+ notes, write a Map of Content (MOC).

A MOC lives in `_maps/` and curates a reading order through related notes. It's the syllabus you build *yourself* once you've explored the cluster — not a plan you set in advance. A note has one home (its folder), but can appear in many MOCs.

MOCs are pure navigation: ordered wikilinks with light section headers. No content of their own.

---

## The Teaching Method: Socratic, Not Declarative

Notes here do not state facts and move on. They make the reader discover the answer themselves by constructing the problem first.

The shape of every note is:

```
1. Why does this problem exist?
2. What is the obvious (wrong) solution?
3. What breaks?
4. What is the right solution?
5. Why does it work?
6. When does it not apply?
```

Steps 1–3 are non-negotiable. If a reader can skip straight to the answer without understanding why the wrong answer fails, the note is incomplete.

### Concretely: lead with a scenario, not a definition

Bad opening (declarative):
> `asyncio.Queue` is an in-process, non-blocking queue that can be used to pass events between coroutines.

Good opening (Socratic):
> You need two coroutines to share events. The obvious data structure is a list. What breaks if you just use a list?

The bad version tells you what to remember. The good version makes you reason. By the time the definition arrives, the reader already built it in their head.

### Show the naive/wrong approach first

Every note should contain at least one "here is the thing that looks right but isn't." Label it clearly. Then walk through exactly what breaks and why. Only then introduce the correct approach.

This is not negative teaching. It is the only way a concept sticks — the reader has to see the failure mode before the fix means anything.

### Ask the question before you answer it

Before any key point, ask the question that leads to it:

> What happens when `get()` is called on an empty queue?

Then answer it. The question primes attention. An answer without a question is just information density — forgettable.

---

## Note Structure

Every note follows this skeleton:

```markdown
#tag1 #tag2 #tag3

---

# Title — phrased as a question or a problem, not a topic name

> Prerequisite: [[other-note]] — what it establishes (omit only if this is a true root concept)

Opening paragraph: the problem the reader is about to solve. One or two sentences. 
No background, no preamble, straight into the conflict.

---

## The Setup / The Problem

Concrete scenario. Naive code if relevant. No jargon yet.

---

## What Breaks

Walk through why the naive approach fails. 
> [!danger] callout for dangerous consequences
> [!important] callout for key constraints

---

## The Right Approach

Show the fix.
> [!success] callout for what is now solved

---

## Edge Cases / When This Doesn't Apply

One or two cases where the rule inverts or doesn't hold. 
This is what separates "knows the rule" from "understands the rule."

---

## Mental Model To Remember

> [!info] One-liner summary. The sentence someone would say in a code review.
```

---

## Callout Types

Use Obsidian-style callouts. Each has a specific job — do not use them interchangeably.

| Callout | Use for |
|---------|---------|
| `> [!info]` | Neutral principles, mental models, decision rules |
| `> [!important]` | Constraints you must hold in your head to avoid bugs |
| `> [!danger]` | What breaks, what leaks, what crashes, what silently lies |
| `> [!success]` | What the correct approach fixes, confirmed behaviors |
| `> [!tip]` | One-liner shortcuts, decision rules, "when to reach for X" |
| `> [!warning]` | Tricky edge cases, gotchas, things that look safe but aren't |

---

## Code Examples

All code examples use generic placeholder names. No real service names, no real table names, no real endpoint paths that identify a real product.

Good placeholder names: `UpstreamService`, `EventQueue`, `StreamingEndpoint`, `MyNode`, `pipeline`, `worker`, `ctx`, `handler`.

Bad names: anything that names a real company's internal concept.

Code examples must do one of two things:
- Show the **wrong** approach so the failure is visible (label with `# bad` or `# naive`)
- Show the **right** approach (label with `# correct` or just leave unlabelled)

Never show code that is "medium" — half right, half wrong. That just creates confusion.

---

## Analogies

Use one concrete analogy per note, maximum. The analogy should map directly to the thing being explained and should be discardable once the concept lands. If the analogy becomes load-bearing (the reader needs to keep thinking about it to understand the concept), it is too complex — simplify it.

Good: "An `asyncio.Queue` is a phone line between two people in the same room. You can't mail a phone line to a database."

Bad: a multi-paragraph extended metaphor that has its own sub-parts and special cases.

---

## Diagrams

Use Mermaid. Diagrams are optional but strongly preferred for:
- sequence diagrams (things happening in time order)
- flows with branching (decision trees, state machines)
- multi-component interactions (producer / queue / consumer)

Do not use diagrams to repeat information already in a table or code block.

---

## Tags

The first line of every note is tags: `#topic1 #topic2 #topic3`.

Tags should be:
- **technology** (`#asyncio`, `#langgraph`, `#python`, `#fastapi`)
- **concept** (`#queues`, `#streaming`, `#backpressure`, `#architecture`)
- **pattern** (`#sentinel-pattern`, `#funnel-pattern`, `#inversion`)
- **source** (`#source` for notes walking through primary sources — cpython, RFCs, papers)

Do not tag with company names, product names, or project names.

---

## Tone

- Second person (`you`) throughout. The reader is the protagonist discovering the answer.
- No academic passive voice ("it can be seen that..."). Direct.
- No filler transitions ("Now that we understand X, let's move on to Y..."). Cut them all.
- Short paragraphs. If a paragraph is more than 4 lines, it probably contains two ideas — split it.
- Bold the key phrase in a sentence, not the whole sentence.

---

## What a Finished Note Passes

Before considering a note done, check:

- [ ] Zero mentions of any real company, product, codebase, or internal system
- [ ] Opens with the problem, not the answer
- [ ] Contains at least one "wrong approach" with a clear failure walkthrough
- [ ] Key insight arrives via question-then-answer, not statement
- [ ] Has a "Mental Model To Remember" callout at the end
- [ ] Code examples use generic names
- [ ] Tags are on the first line
- [ ] Has a `Prerequisite:` breadcrumb with wikilinks (or is a true root concept)
- [ ] Existing notes that build on this one have backlinks added
