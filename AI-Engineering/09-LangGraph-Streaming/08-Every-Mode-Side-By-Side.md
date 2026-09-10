#langgraph #graphs #streaming #lab

**Six modes have been met one at a time, each against whatever graph made its point clearest.** None of those comparisons were fair, because the graph kept changing underneath them. This note runs one graph and asks all six the same five questions.

# Lab — Every Mode, Side By Side

> [!info] Nothing here is new. Everything here is measured against the same three nodes, so the numbers can be compared to each other rather than to memory.

## One graph, held still

The value of this note is entirely in the controls. One graph, one input, one machine, one afternoon — so that when `debug` costs nineteen times what `updates` costs, that ratio means something.

Three nodes, half a second of work each, and writer calls in the first and third so `custom` has something to carry.

```mermaid
flowchart LR
    S([START]) --> L[look_up_priya] --> C[check_balance] --> W[write_answer] --> E([END])
    style L fill:#1f4f7a,color:#fff
    style C fill:#7a5a1f,color:#fff
    style W fill:#1f6f3f,color:#fff
    style S fill:#2d333b,color:#fff
    style E fill:#2d333b,color:#fff
```

`src/langgraph_lab/note08/a_every_mode.py`:

```python
import json
import time
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.types import StreamMode


class DeskState(TypedDict):
    asked_by: str
    answer: str


class DeskUpdate(TypedDict, total=False):
    answer: str


def look_up_priya(state: DeskState) -> DeskUpdate:
    writer = get_stream_writer()
    writer({"status": "opening the record"})
    time.sleep(0.5)
    writer({"status": "reading the leave balance"})
    time.sleep(0.5)
    return {"answer": "Priya has 12 days left"}


def check_balance(state: DeskState) -> DeskUpdate:
    time.sleep(0.5)
    return {"answer": state["answer"] + ", 3 already taken"}


def write_answer(state: DeskState) -> DeskUpdate:
    writer = get_stream_writer()
    writer({"status": "writing the reply"})
    time.sleep(0.5)
    return {"answer": state["answer"] + ", and that is the most in her team"}


builder = StateGraph(DeskState)  # ty: ignore[invalid-argument-type]
builder.add_node("look_up_priya", look_up_priya)
builder.add_node("check_balance", check_balance)
builder.add_node("write_answer", write_answer)
builder.add_edge(START, "look_up_priya")
builder.add_edge("look_up_priya", "check_balance")
builder.add_edge("check_balance", "write_answer")
builder.add_edge("write_answer", END)
graph = builder.compile(checkpointer=InMemorySaver())

START_STATE: DeskState = {"asked_by": "reception", "answer": ""}


def report(mode: StreamMode, thread_id: str) -> None:
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    started = time.perf_counter()
    first_at = 0.0
    count = 0
    on_the_wire = 0
    for item in graph.stream(START_STATE, stream_mode=mode, config=config):
        count = count + 1
        if count == 1:
            first_at = time.perf_counter() - started
        on_the_wire = on_the_wire + len(json.dumps(item, default=str))
    last_at = time.perf_counter() - started
    print(f"    {mode:<12} {count:>3} {first_at:>8.2f}s {last_at:>8.2f}s {on_the_wire:>8,}")


if __name__ == "__main__":
    print("--- one graph, three nodes, two seconds of work, run once per mode")
    print(f"    {'mode':<12} {'items':>3} {'first':>9} {'last':>9} {'bytes':>8}")
    report("values", "t1")
    report("updates", "t2")
    report("custom", "t3")
    report("tasks", "t4")
    report("checkpoints", "t5")
    report("debug", "t6")
```

Each run gets its own `thread_id`, so no run is reading state another run left behind.

## When each mode speaks, and what it costs

```
--- one graph, three nodes, two seconds of work, run once per mode
    mode         items     first      last    bytes
    values         4     0.00s     2.02s      290
    updates        3     1.02s     2.02s      232
    custom         3     0.00s     2.02s      102
    tasks          6     0.00s     2.03s    1,068
    checkpoints    5     0.00s     2.02s    2,429
    debug         11     0.00s     2.02s    4,528
```

Every mode finishes at the same moment, because they are all watching the same two seconds of work. Everything else differs.

**The `first` column is the one that decides what a user sees.** `updates` says nothing for a full second — it has nothing to say until a node returns, and the first node sleeps for one. Every other mode has something on the wire before the first node has done anything: `values` has the start state, `custom` has the first writer call, and the three operator modes have a task or checkpoint record.

That second of silence is not a lab artefact. It is the exact shape of a real first turn, where the first node is the slow one.

**The `bytes` column ranks them in the opposite order to usefulness on a screen.** `custom` is the cheapest thing here at 102 bytes and it is also the only mode carrying words written for a human. `debug` costs 44 times that, and 19 times what `updates` costs, for the same two seconds.

## What one item looks like

Counting items says nothing about what a consumer has to write. The other half is the shape.

`src/langgraph_lab/note08/b_one_item_each.py`:

```python
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamMode

from langgraph_lab.note08.a_every_mode import START_STATE, graph


def first_item(mode: StreamMode, thread_id: str) -> Any:
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    for item in graph.stream(START_STATE, stream_mode=mode, config=config):
        return item
    return None


def describe(mode: StreamMode, thread_id: str) -> None:
    item = first_item(mode, thread_id)
    keys = ", ".join(item.keys())
    print(f"    {mode:<12} {type(item).__name__:<6} {keys}")


if __name__ == "__main__":
    print("--- the first item each mode produces, by container and top-level keys")
    print(f"    {'mode':<12} {'type':<6} keys")
    describe("values", "t1")
    describe("updates", "t2")
    describe("custom", "t3")
    describe("tasks", "t4")
    describe("checkpoints", "t5")
    describe("debug", "t6")

    print("\n--- the same first item printed whole, for the three client modes")
    print(f"    values   {first_item('values', 'u1')}")
    print(f"    updates  {first_item('updates', 'u2')}")
    print(f"    custom   {first_item('custom', 'u3')}")
```

```
--- the first item each mode produces, by container and top-level keys
    mode         type   keys
    values       dict   asked_by, answer
    updates      dict   look_up_priya
    custom       dict   status
    tasks        dict   id, name, input, triggers
    checkpoints  dict   config, parent_config, values, metadata, next, tasks
    debug        dict   step, timestamp, type, payload
```

**All six are a `dict`, and that is the entire similarity.** The keys are the mode.

`values` is keyed by state field, so its keys are yours and they never change. `updates` is keyed by node name, so its keys are also yours but a different set of yours, and only one arrives at a time. `custom` is keyed by whatever the writer was handed, so its keys are yours in a third sense — you invented them at the call site.

The other three are keyed by the framework, and their keys are fixed. That is the real division: three modes whose shape you designed, three whose shape you receive.

```
--- the same first item printed whole, for the three client modes
    values   {'asked_by': 'reception', 'answer': ''}
    updates  {'look_up_priya': {'answer': 'Priya has 12 days left'}}
    custom   {'status': 'opening the record'}
```

Read those three together and the choice between them stops being about mechanics. The first is a state, the second is an event, the third is a sentence.

## What needs a checkpointer

The setup requirement is not uniform across the six, and the way it fails is not uniform either.

`src/langgraph_lab/note08/c_what_needs_a_checkpointer.py`:

```python
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.types import StreamMode


class DeskState(TypedDict):
    answer: str


class DeskUpdate(TypedDict, total=False):
    answer: str


def look_up_priya(state: DeskState) -> DeskUpdate:
    get_stream_writer()({"status": "opening the record"})
    return {"answer": "Priya has 12 days left"}


def write_answer(state: DeskState) -> DeskUpdate:
    return {"answer": state["answer"] + ", and that is the most in her team"}


builder = StateGraph(DeskState)  # ty: ignore[invalid-argument-type]
builder.add_node("look_up_priya", look_up_priya)
builder.add_node("write_answer", write_answer)
builder.add_edge(START, "look_up_priya")
builder.add_edge("look_up_priya", "write_answer")
builder.add_edge("write_answer", END)

bare = builder.compile()
checkpointed = builder.compile(checkpointer=InMemorySaver())

START_STATE: DeskState = {"answer": ""}


def compare(mode: StreamMode, thread_id: str) -> None:
    without = len(list(bare.stream(START_STATE, stream_mode=mode)))
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    with_one = len(list(checkpointed.stream(START_STATE, stream_mode=mode, config=config)))
    print(f"    {mode:<12} {without:>10} {with_one:>13}")


if __name__ == "__main__":
    print("--- the same graph compiled twice, items per mode")
    print(f"    {'mode':<12} {'no saver':>10} {'with a saver':>13}")
    compare("values", "t1")
    compare("updates", "t2")
    compare("custom", "t3")
    compare("tasks", "t4")
    compare("checkpoints", "t5")
    compare("debug", "t6")

    print("\n--- the graph without a saver still ran to completion")
    print(f"    {bare.invoke(START_STATE)}")
```

```
--- the same graph compiled twice, items per mode
    mode           no saver  with a saver
    values                3             3
    updates               2             2
    custom                1             1
    tasks                 4             4
    checkpoints           0             4
    debug                 4             8

--- the graph without a saver still ran to completion
    {'answer': 'Priya has 12 days left, and that is the most in her team'}
```

Four of the six do not care. **`tasks` is in that group**, which is the thing most people get wrong — it is an operator mode, it reports task records, and it needs nothing.

`checkpoints` goes to zero. Not an error, not a warning, not a partial result. The loop body simply never executes, and the last line of the run proves the graph itself was fine.

`debug` halves, from 8 to 4, which is the worst of the three outcomes. It is `tasks` plus `checkpoints`, so without a saver it silently delivers the half it can still produce — a stream that works, looks right, and is missing every checkpoint record.

> [!warning] The two silent failures have opposite symptoms
> `checkpoints` gives you nothing, which is at least obvious. `debug` gives you something, which is not.

## What survives a node that throws

`src/langgraph_lab/note08/d_when_a_node_throws.py`:

```python
import json
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.types import StreamMode


class DeskState(TypedDict):
    answer: str


class DeskUpdate(TypedDict, total=False):
    answer: str


def look_up_priya(state: DeskState) -> DeskUpdate:
    get_stream_writer()({"status": "opening the record"})
    return {"answer": "Priya has 12 days left"}


def check_balance(state: DeskState) -> DeskUpdate:
    raise RuntimeError("the leave service is down")


builder = StateGraph(DeskState)  # ty: ignore[invalid-argument-type]
builder.add_node("look_up_priya", look_up_priya)
builder.add_node("check_balance", check_balance)
builder.add_edge(START, "look_up_priya")
builder.add_edge("look_up_priya", "check_balance")
builder.add_edge("check_balance", END)
graph = builder.compile(checkpointer=InMemorySaver())

START_STATE: DeskState = {"answer": ""}


def report(mode: StreamMode, thread_id: str) -> None:
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    delivered = 0
    mentions = 0
    raised = "no"
    try:
        for item in graph.stream(START_STATE, stream_mode=mode, config=config):
            delivered = delivered + 1
            if "the leave service is down" in json.dumps(item, default=str):
                mentions = mentions + 1
    except RuntimeError:
        raised = "yes"
    print(f"    {mode:<12} {delivered:>6} {mentions:>9} {raised:>8}")


if __name__ == "__main__":
    print("--- the second node raises, and every mode is asked what it saw")
    print(f"    {'mode':<12} {'items':>6} {'mentions':>9} {'raised':>8}")
    report("values", "t1")
    report("updates", "t2")
    report("custom", "t3")
    report("tasks", "t4")
    report("checkpoints", "t5")
    report("debug", "t6")

    # a step_timeout disqualifies the single-task shortcut in _runner.py, so the
    # failing task is run through the pooled path and gets to report before the raise
    graph.step_timeout = 30

    print("\n--- the same graph again, with a step_timeout set")
    print(f"    {'mode':<12} {'items':>6} {'mentions':>9} {'raised':>8}")
    report("values", "s1")
    report("updates", "s2")
    report("custom", "s3")
    report("tasks", "s4")
    report("checkpoints", "s5")
    report("debug", "s6")
```

```
--- the second node raises, and every mode is asked what it saw
    mode          items  mentions   raised
    values            2         0      yes
    updates           1         0      yes
    custom            1         0      yes
    tasks             3         0      yes
    checkpoints       3         0      yes
    debug             6         0      yes
```

**Not one mode carries the error.** Six modes, zero mentions, and the exception reaches the caller in every case.

That is the single-task shortcut from note 5. The failing node is alone in its step, so it is run directly rather than through the pool, and it commits its error and re-raises before anything gets a chance to emit a finish record.

Setting a `step_timeout` disqualifies that shortcut, and the same six runs change:

```
--- the same graph again, with a step_timeout set
    mode          items  mentions   raised
    values            2         0      yes
    updates           1         0      yes
    custom            1         0      yes
    tasks             4         1      yes
    checkpoints       3         0      yes
    debug             7         1      yes
```

`tasks` gains an item and a mention. `debug` gains an item and a mention. The three client modes do not move, and `checkpoints` does not either — a failed step produces no checkpoint to report.

> [!important] Only two modes can ever tell you what threw, and only under a condition you have to set
> `tasks` and `debug`, with a `step_timeout` on the graph. Everything else knows only that the run stopped.

## What stops at a subgraph boundary

`src/langgraph_lab/note08/e_across_the_boundary.py`:

```python
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.types import StreamMode


class DeskState(TypedDict):
    answer: str


class DeskUpdate(TypedDict, total=False):
    answer: str


def find_record(state: DeskState) -> DeskUpdate:
    get_stream_writer()({"status": "opening the record"})
    return {"answer": "Priya has 12 days left"}


def add_context(state: DeskState) -> DeskUpdate:
    return {"answer": state["answer"] + ", and that is the most in her team"}


inner = StateGraph(DeskState)  # ty: ignore[invalid-argument-type]
inner.add_node("find_record", find_record)
inner.add_node("add_context", add_context)
inner.add_edge(START, "find_record")
inner.add_edge("find_record", "add_context")
inner.add_edge("add_context", END)
lookup = inner.compile()

outer = StateGraph(DeskState)  # ty: ignore[invalid-argument-type]
outer.add_node("lookup", lookup)
outer.add_edge(START, "lookup")
outer.add_edge("lookup", END)
desk = outer.compile(checkpointer=InMemorySaver())

START_STATE: DeskState = {"answer": ""}


def compare(mode: StreamMode, thread_id: str) -> None:
    closed: RunnableConfig = {"configurable": {"thread_id": thread_id + "a"}}
    opened: RunnableConfig = {"configurable": {"thread_id": thread_id + "b"}}
    without = len(list(desk.stream(START_STATE, stream_mode=mode, config=closed)))
    with_flag = len(list(desk.stream(START_STATE, stream_mode=mode, config=opened, subgraphs=True)))
    print(f"    {mode:<12} {without:>8} {with_flag:>16}")


if __name__ == "__main__":
    print("--- one subgraph of two nodes, items per mode")
    print(f"    {'mode':<12} {'default':>8} {'subgraphs=True':>16}")
    compare("values", "t1")
    compare("updates", "t2")
    compare("custom", "t3")
    compare("tasks", "t4")
    compare("checkpoints", "t5")
    compare("debug", "t6")
```

```
--- one subgraph of two nodes, items per mode
    mode          default   subgraphs=True
    values              2                5
    updates             1                3
    custom              0                1
    tasks               2                6
    checkpoints         3                7
    debug               5               13
```

**Every mode is affected, and none of them warns you.** The default column is what a parent graph reports about a subgraph doing all the work, and it is smaller in all six.

`custom` is the extreme case at 0 against 1 — the channel built specifically to report progress from inside a node reports nothing at all when that node is one graph deeper.

`debug` more than doubles, 5 to 13, which is worth knowing before turning the flag on to investigate something: the mode that already costs the most is also the one the flag inflates the most.

## The table

Everything above, in one place. This is the part to come back to.

| Mode | First item | Items | Bytes | An item is keyed by | Needs a saver | Sees inside a subgraph | Can report a crash |
|---|---|---|---|---|---|---|---|
| `values` | immediately | 4 | 290 | state field | no | only with the flag | no |
| `updates` | first return | 3 | 232 | node name | no | only with the flag | no |
| `custom` | first writer call | 3 | 102 | whatever you wrote | no | only with the flag | no |
| `tasks` | immediately | 6 | 1,068 | `id, name, input` | no | only with the flag | **yes**, with a `step_timeout` |
| `checkpoints` | immediately | 5 | 2,429 | `config, values, metadata` | **yes** | only with the flag | no |
| `debug` | immediately | 11 | 4,528 | `step, type, payload` | **half of it** | only with the flag | **yes**, with a `step_timeout` |
| `messages` | — | — | — | — | — | — | — |

`messages` is the seventh mode and it is the only one this note cannot measure, because it yields nothing unless a node calls a model. It gets its own note.

And the same six read the other way — not by what they cost, but by what question they answer:

| You want to | Reach for | Because |
|---|---|---|
| show a progress bar during slow work | `custom` | the only mode that speaks before a node returns, and the cheapest on the wire |
| rebuild a UI that survives a refresh | `values` | every item is the whole state, so a late joiner needs only the last one |
| react when one particular node finishes | `updates` | keyed by node name, and carries only what changed |
| find out which node threw, and with what input | `tasks` | the only cheap mode that carries an error, and it needs no saver |
| answer where the graph was and how it got there | `checkpoints` | the only mode carrying `parent_config` and step metadata |
| investigate one specific incident, once | `debug` | everything at once, at 19 times the bandwidth of `updates` |

**The pattern in the first table is the argument of note 5, arrived at from the other direction.** The three modes a screen wants are the three cheapest, the three keyed by names you chose, and the three that cannot tell you what threw. The three an operator wants are the three most expensive, the three keyed by the framework, and the only ones with any diagnostic content.

There is no mode that is good at both, and that is not an oversight — a mode cheap enough to send to every browser cannot also carry the input, task id and checkpoint metadata that a three in the morning investigation needs.
