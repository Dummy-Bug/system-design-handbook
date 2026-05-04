#langgraph #hitl #resume #idempotency #re-execution

---

# The Node Re-runs From the Top — What Are the Consequences?

> Prerequisite: [[what-interrupt-actually-is]] — establishes that the node re-runs from line 1 on resume.

You know LangGraph re-executes the interrupted node from line 1 on resume. That sounds alarming. In practice it's mostly fine — but only if you understand exactly what fine means and where it stops being fine.

---

## The Setup

A node with this shape:

```python
async def run(state):
    # work before interrupt
    result = await roster_service.find_students(state["student_name"])  # I/O call
    emit_progress("Searching...")                                        # side effect

    selected = interrupt({"options": result.matches})                   # pause

    # work after interrupt
    emit_progress(f"Fetching marks for roll no {selected}...")
    marks = await marks_service.fetch(selected)
    emit_result(marks)
    return {**state, "marks": marks}
```

On resume, everything above `interrupt()` runs again. Ask the question for each line: **is repeating this safe?**

---

## Line by Line — What Re-runs and Whether It Matters

### `roster_service.find_students()` — a read

It hits the school roster with the same name, gets the same list of matching students back. The data hasn't changed. The cost is one extra network round-trip.

> [!success] Safe. Reads are naturally idempotent — calling them twice with the same input produces the same result.

### `emit_progress("Searching...")` — a streaming side effect

This fires again and lands on the queue of the **resume request's** `RequestContext`. The frontend on the resume request sees Searching... briefly.

Is this a problem? In most UIs, no — the next event (Fetching marks for roll no 42...) arrives so quickly after that the Searching... message barely registers before being replaced.

> [!warning] It is technically a lie — you're not actually searching, you already have the result. But it's a cosmetic lie with no functional consequence. Acceptable trade-off.

### `interrupt()` — the pause point

On the resume run, this line does **not** pause. It returns the human's selected value directly. This is the key mechanic — covered in detail in [[interrupt-pause-vs-return]].

### Everything after `interrupt()` — runs for the first time

The work below `interrupt()` never ran on the first request (the node stopped at the interrupt). On resume, it runs for the first time. No duplication here.

---

## The Rule: Reads Before, Writes Never

> [!important] Operations before `interrupt()` will run twice — once on the original request, once on resume. This is only safe if those operations are **reads** (idempotent by nature). Never put a write operation before an `interrupt()`.

What a write before `interrupt()` looks like:

```python
# bad — write before interrupt
async def run(state):
    await notification_service.send_email(state["student"], "Your marks are being reviewed")
    selected = interrupt({"options": matches})
    ...
```

On resume, the email sends again. The student gets two emails. If this is a payment or a database write, it's worse.

The fix is either:
- Move the write to **after** `interrupt()`
- Make the write idempotent (deduplicate by a key, check before write)

---

## What About Progress Events Firing Twice?

You might see this in the network tab on the resume request:

```
progress  → Searching for 'alice'...                    ← re-execution, fires again
progress  → Fetching marks for roll no 42...            ← new, fires for the first time
```

The first event is the re-emitted one. Why doesn't the frontend show it visibly?

Two reasons:
1. The re-execution is fast — no actual slow I/O since the result comes back instantly on a warm cache or fast service. Both events land on the queue within milliseconds of each other.
2. The frontend likely renders the latest progress message, overwriting the previous one immediately.

> [!tip] If re-emitted progress messages become visually jarring in your UI, guard the emit with a state flag: `if not state.get("already_searched"): ctx.emit(...)`. But only do this if it's actually a problem — the default re-execution is usually invisible.

---

## Mental Model To Remember

> [!info] Re-execution on resume is safe when everything before `interrupt()` is a read. Reads are idempotent — running them twice with the same input produces the same output. The only real danger is writes: they must be moved after the interrupt or made idempotent.
