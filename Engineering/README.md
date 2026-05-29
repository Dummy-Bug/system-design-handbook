# Engineering Wiki

Concept-driven engineering notes. No daily framing, no calendar guilt — notes appear when a real concept demanded one.

See [[System Design/CLAUDE]] for the writing rules (Socratic method, school theme, mandatory wikilinks, MOCs at 4+ notes).

---

## Concept Folders

Each folder holds atomic notes for one concept area. A note has exactly one home, but may appear in multiple reading paths via MOCs.

- **[asyncio/](asyncio/)** — coroutines, event loop, queues, backpressure
- **[langgraph/](langgraph/)** — interrupts, HITL, state, checkpointing
- **[streaming/](streaming/)** — event queues in long-running workflows, driver/consumer pattern, NDJSON, SSE
- **[http-clients/](http-clients/)** — shared HTTP client statefulness, cookie jar pollution, CSRF mechanics

A new top-level folder appears when 3+ notes for it exist. No speculative empty folders.

---

## Maps of Content

Curated reading paths through the atomic notes. The syllabus you build *yourself* once you've explored a cluster.

- **[[streaming-in-langgraph]]** — full reading path from async fundamentals to driver/consumer architecture (14 notes)

---

## Open Questions

Active investigations — things you're chasing, even before you have answers. Lives in [`_questions/`](_questions/).

Writing down confusion explicitly is what separates depth-first learning from journaling. If you have an open thread, it goes here as a note titled with the question.

---

## Navigating This Wiki

- **By topic:** open the concept folder.
- **By reading path:** open a MOC in `_maps/`.
- **By graph:** Obsidian's graph view shows the wikilink network. Every note links to its prerequisites.
- **By open question:** browse `_questions/` for active threads.

---

## When You Add a Note

1. Place it in the right concept folder (or create a new one if 3+ notes will live there).
2. Add the `Prerequisite:` breadcrumb at the top with wikilinks.
3. Search the wiki for notes that should now link *to* this one — add the backlinks.
4. If the folder reaches 4+ notes and has no MOC, write one in `_maps/`.
5. If this note answers an open question in `_questions/`, delete the question or convert it into a `Mental Model` callout in the new note.
