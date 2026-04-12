## What Is a DAG

DAG = **Directed Acyclic Graph**.

It's the recipe of your job represented as a graph of steps with dependencies.

```
load → filter → count → sort
```

- **Directed** — arrows go one way, steps have a fixed order
- **Acyclic** — no loops, you never go back to a previous step

---

## How Spark Uses the DAG

Before executing anything, Spark builds the full DAG of your job and **optimizes it globally**.

You write:
```
load → filter by ERROR → count → filter count > 100 → sort
```

Spark sees the whole graph and asks: "Can I do this more efficiently?"

It merges the two filter steps into one pass:

```
Before optimization:
  pass 1: filter lines starting with ERROR
  pass 2: filter results where count > 100

After optimization:
  pass 1: filter ERROR AND count > 100 — combined into one pass
```

Less passes = less work = faster execution.

---

## Why MapReduce Can't Do This

MapReduce has a rigid structure: Map → Reduce. That's it.

It executes steps one by one with no global view. It can't look ahead and merge operations.

```
MapReduce:  Map runs → done → Reduce runs → done
            No optimization possible between phases

Spark:      Builds full DAG → optimizes → executes
            Can reorder, merge, and skip steps
```

---

## Practical Impact

| | MapReduce | Spark |
|---|---|---|
| Execution model | Rigid Map → Reduce | Flexible DAG |
| Optimization | None | Merges passes, reorders steps |
| Multi-step pipelines | Each step = one full job | All steps = one optimized job |
| Iterative algorithms (ML) | Very slow — disk after every iteration | Fast — stays in RAM, optimized graph |

---

## One-Line Summary

> Spark builds a DAG of your entire job before running, optimizes it globally, then executes — unlike MapReduce which runs Map and Reduce rigidly with no global view.
