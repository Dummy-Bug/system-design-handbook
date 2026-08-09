#python #type-hints #typing #mypy #python-utils


Two of the three readers have already been seen working. An editor pulled annotations out of a file that could not run. A web framework turned `"5"` into `5` before a function body executed. The third — a checker — has been named twice and demonstrated never.

Before showing it, it has to earn its place. What is left that the other two can't do?

## A bug neither of them catches

```python
def get_discount(price: float, pct: int) -> float:
    return price * (pct / 100)


def checkout(cart: list[float]) -> float:
    total = sum(cart)
    if total > 10_000:
        return get_discount(total, "10")
    return total
```

Line 8 passes `"10"` — a string — where `pct: int` was promised.

Three things about **where** that bug sits, all of which matter:

- It's on a branch that only runs for large carts. Ordinary use never touches it.
- The bad value wasn't supplied by a user. **You wrote it**, inside your own function.
- It never crosses a boundary. The incoming cart is perfectly valid.

Run it:

```
$ python3 cart_check.py
small cart : 350.0
big cart   : TypeError: unsupported operand type(s) for /: 'str' and 'int'
```

The small cart is fine. The large one dies — in production, on a real customer, on the order you least wanted to lose.

Now check the two readers you already have.

**The runtime validator does nothing**, and is right not to. Validation guards boundaries — data arriving from outside the program. Nothing arrived from outside here; the string was invented internally and handed from one of your functions to another. No boundary was crossed, so nothing was watching.

**The editor is unreliable for this.** It could underline line 8 — if that file is open, and if you happen to look at that line. It won't tell you the other four hundred files are clean, and it won't stop the commit.

## What's left

```
$ mypy cart_check.py
cart_check.py:8: error: Argument 2 to "get_discount" has incompatible type
"str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Exact line, exact argument, before any cart existed.

A **static type checker** is a separate program that reads your source without running it, follows your annotations through the code, and reports where the values flowing around don't match what you claimed. `mypy` is the reference implementation; `pyright` is what VS Code's Pylance runs underneath.

"Static" is the whole distinction: it analyses the code **at rest**, as text, rather than watching it work.

## Why isn't this just part of Python?

The obvious question, especially coming from a language where the compiler refuses to produce a runnable file. Four reasons, and the last is the one that settles it.

**It would have broken everything.** Annotations arrived in 2015, into a language already twenty-four years old and carrying an enormous body of untyped code. Enforcing them would have broken essentially every program then in existence.

**Partial adoption is the design, not a compromise.** You are meant to annotate one function, or ten thousand, and mix freely. If the interpreter enforced annotations, a half-annotated codebase would be an error rather than a perfectly normal waypoint — and nobody would ever get started, because the first useful result would require converting everything.

**It would cost time on every call, forever.** Verifying `get_discount`'s arguments at runtime means verifying them on *every* invocation, in production, for the lifetime of the service. A separate program does it once, offline, and then never again.

**And the interpreter could not have caught this bug anyway.** Line 8 didn't execute for the small cart. The interpreter, by definition, only ever sees code that runs — so a runtime check on that line stays unreachable until a customer triggers it, which is precisely the situation you were trying to avoid.

> [!important] **To catch a mistake on a branch that never runs, you have to read the text rather than execute it.** That is a fundamentally different activity from interpreting, and it belongs in a different program. This is not Python being lax — it's the recognition that "run this" and "reason about this without running it" are two jobs, and one tool doing both would do neither well.

## Where a checker goes blind

The limit is sharp, and it is the most important thing in this note.

Same bug, in two files that differ by one annotation. The cart now comes from somewhere:

```python
def fetch_cart(order_id):               # ← no annotations
    return ["9000", "5000"]


def checkout(cart: list[float]) -> float:
    return sum(cart)


checkout(fetch_cart(42))
```

```
$ mypy reach_a.py
Success: no issues found in 1 source file
```

Annotate the source function, change nothing else:

```python
def fetch_cart(order_id: int) -> list[str]:     # ← annotated
    return ["9000", "5000"]
```

```
$ mypy reach_b.py
reach_b.py:9: error: Argument 1 to "checkout" has incompatible type
"list[str]"; expected "list[float]"  [arg-type]
```

One annotation is the entire difference between a precise error and silence. And the first file still crashes when you run it:

```
$ python3 reach_a.py
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

> [!warning] **`Success: no issues found` is not a statement about your code. It's a statement about the claims you gave the checker.** On the unannotated version it is a false all-clear over code that provably crashes — which makes that version *worse* than having no checker at all, because you'd have run it feeling covered.

A checker has no crystal ball. It knows what you told it, propagates that as far as the code lets it, and where you told it nothing it stops — quietly, reporting success. Its reach is exactly the reach of your annotations.

## Telling the two kinds of error apart

Since two different programs are now producing messages about the same file, it's worth being able to tell at a glance which one is talking. **Every output block in these notes shows the command that produced it** — `$ mypy file.py` or `$ python3 file.py` — but the messages themselves are also distinguishable by shape.

**A checker error** starts with the filename and line, and ends with a bracketed code:

```
cart_check.py:8: error: Argument 2 to "get_discount" has incompatible type "str"; expected "int"  [arg-type]
                                                                                                  ^^^^^^^^^^
```

`[arg-type]`, `[attr-defined]`, `[return-value]`, `[assignment]`, `[index]`, `[call-arg]`, `[union-attr]`, `[list-item]` — **Python never prints bracketed codes.** They're mypy's identifier for the rule that fired, and you can silence one specifically by name.

**A Python runtime error** is a traceback ending in an exception class:

```
Traceback (most recent call last):
  File "cart_check.py", line 8, in checkout
    return get_discount(total, "10")
TypeError: unsupported operand type(s) for /: 'str' and 'int'
^^^^^^^^^
```

The word `Traceback`, a stack of frames showing how execution got there, and a name ending in `Error`. **A checker never prints a traceback of your program**, because it never runs your program.

| output | who said it | when |
|---|---|---|
| `file.py:8: error: ... [arg-type]` | **the checker** | when you run `mypy` |
| `note: Revealed type is "..."` | **the checker** | `reveal_type()`, checker only |
| `SyntaxError: invalid syntax` | **Python, compiling** | before any line runs |
| `Traceback ... TypeError: ...` | **Python, executing** | when it reached that line |

The third row is the odd one — it's Python, but it happens before execution, which is why nothing prints at all. That's the `bad_syntax.py` case in `00-How-Python-Runs-Code/01-Compile-Then-Execute`.

## What this concept claims

**A static type checker is a separate program that compares your claims against your code before any of it runs — and its reach is bounded by how much you've claimed.**

That gives it a capability nothing else has: finding a mistake in a function you never called, on a branch that fires once a year, in a file nobody has opened. And it gives it a failure mode nothing else has: reporting success over code it simply couldn't see into.

Both halves are worth holding at once. The value is real, and it is not automatic — it is proportional to how much of your program you have described.
