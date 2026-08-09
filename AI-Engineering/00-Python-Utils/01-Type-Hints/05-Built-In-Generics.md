#python #type-hints #typing #generics #python-utils


Every annotation so far has been a single word — `int`, `str`, `Node`. That's enough while the thing being described is a single value. It stops being enough the moment the value is a container, because a container has an inside.

## A claim that is true and useless

```python
def average(scores: list) -> float:
    return sum(scores) / len(scores)


print(average([90, 80, 70]))
print(average(["90", "80", "70"]))
```

Nothing is missing here. The parameter is annotated, the return is annotated. Compare that with the blind spot from `03-Static-Type-Checkers`, where the checker went quiet because a function had **no** annotations at all — that excuse isn't available now.

Run it:

```
$ python3 bare.py
80.0
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

The second call dies, for the reason `sum` always dies on strings: it starts from `0`, and `0 + "90"` has nowhere to go.

Now check it:

```
$ mypy bare.py
Success: no issues found in 1 source file
```

Silence over code that provably crashes — the same false all-clear as before, arrived at a completely different way. **The annotation isn't missing. It's too coarse.**

And the checker is right. `["90", "80", "70"]` *is* a list. You claimed the argument would be a list, a list is what arrived, and the claim was satisfied. It didn't fail to check; you gave it a weak question and it answered honestly.

`list` rules out a string and an integer and stops there. Any list, holding anything, in any combination.

## The brackets

Say what's inside:

```python
def average(scores: list[int]) -> float:
    return sum(scores) / len(scores)


print(average([90, 80, 70]))
print(average(["90", "80", "70"]))
```

```
$ mypy param.py
param.py:6: error: List item 0 has incompatible type "str"; expected "int"  [list-item]
param.py:6: error: List item 1 has incompatible type "str"; expected "int"  [list-item]
param.py:6: error: List item 2 has incompatible type "str"; expected "int"  [list-item]
```

One error per element, pointing at the exact items, before anything ran.

Square brackets after a container type give it a **parameter** — the type of what it holds. `list` is *"a list"*; `list[int]` is *"a list of integers"*. Same word, strictly stronger claim.

## Four shapes

```python
names:  list[str]       = ["alice", "bob"]
ages:   dict[str, int]  = {"alice": 30, "bob": 25}
tags:   set[str]        = {"python", "backend"}
point:  tuple[int, int] = (10, 20)
```

Each one holds afterwards:

```python
names.append(42)
ages["carol"] = "thirty"
tags.add(99)
```

```
$ mypy four.py
four.py:6: error: Argument 1 to "append" of "list" has incompatible type "int"; expected "str"  [arg-type]
four.py:7: error: Incompatible types in assignment (expression has type "str", target has type "int")  [assignment]
four.py:8: error: Argument 1 to "add" of "set" has incompatible type "int"; expected "str"  [arg-type]
```

Worth noticing what those errors are *about*. You annotated three variables. Nobody annotated `append` or `add` — yet both got checked, because once the checker knows `names` is a `list[str]`, it knows what `names.append` will accept. **One annotation reaches into every operation on that object**, which is the actual return on the brackets. A bare `list` leaves all of it unchecked.

`dict` is the only one of the four taking two things, and the order is fixed: **keys first, then values.** `dict[str, int]` is names-to-ages. `dict[int, str]` would be a different container entirely.

Two is also all it takes:

```python
bad: dict[str, str, str | None] = {}
```

```
$ mypy dictarity.py
dictarity.py:1: error: "dict" expects 2 type arguments, but 3 given  [type-arg]
```

A dictionary has exactly two kinds of thing in it — keys and values — so there are exactly two slots to describe. It does not matter how many *entries* the dictionary has, and there is no way to describe individual keys separately here.

## What a tuple actually is

The fourth shape needs a detour, because tuples come up less often than lists in day-to-day code.

A tuple is an ordered sequence, written with `()` instead of `[]`. In the ways that matter for reading data, it behaves exactly like a list:

```python
lst = [10, 20, 30]
tup = (10, 20, 30)

print(lst[0], tup[0])       # 10 10
print(len(lst), len(tup))   # 3 3
```

The difference is that **a tuple cannot be changed after it is made**:

```python
lst[0] = 99
print(lst)                        # [99, 20, 30]

tup[0] = 99                       # TypeError: 'tuple' object does not
                                  # support item assignment

lst.append(40)                    # fine
print(hasattr(tup, "append"))     # False
```

No item assignment, and no `append` — the method doesn't exist, because there is nothing it could do.

That single restriction is what tuples are for, and it buys something concrete:

```python
d = {}
d[(10, 20, 30)] = "works"
print(d)                    # {(10, 20, 30): 'works'}

d[[10, 20, 30]] = "?"       # TypeError: unhashable type: 'list'
```

A tuple can be a dictionary key; a list cannot. A dictionary has to remember where it filed something, and a container that can change out from under it makes that impossible. Being unchangeable is exactly what qualifies a tuple.

The usage difference follows from all this. **A list is a bag of like things** — ten users, three hundred users, however many arrive. **A tuple is usually a fixed record** — a coordinate is always `(x, y)`, a database row is always `(name, age, email)`. Different positions carrying different meanings, and a count that doesn't vary.

## Why tuple's brackets read differently

Which is where the annotation diverges from the other three:

```python
point:  tuple[int, int] = (10, 20, 30)
person: tuple[str, int] = ("alice", 30)
wrong:  tuple[str, int] = (30, "alice")
```

```
$ mypy tuples.py
tuples.py:1: error: ... expression has type "tuple[int, int, int]", variable has type "tuple[int, int]"
tuples.py:4: error: ... expression has type "tuple[int, str]",       variable has type "tuple[str, int]"
```

Read the two failures together.

**The first failed on count.** Every element was the right type — there was one too many.

**The second failed on order.** A `str` and an `int`, same as the line above it, the other way round.

So the brackets mean two different things depending on the container:

| | what the brackets say |
|---|---|
| `list[str]` | **every** element is a `str`, however many there are |
| `set[str]` | same |
| `dict[str, int]` | every key is a `str`, every value an `int` |
| `tuple[str, int]` | **position 0** is a `str`, **position 1** is an `int`. Exactly two. |

`list[str]` is *one type for all elements*. `tuple[str, int]` is *one type per position*, read left to right — a layout, not a description of a typical element.

> [!important] **Length is part of a tuple's type, and of no other container's.** It isn't a separate rule bolted on; it falls out of naming a type per position. Name three, you've said there are three. `list[int]` has nothing to say about how many, and there is no way to make it say anything — which matches what the two containers are for.

## The trap

Because `tuple[int, int]` describes positions rather than elements, the obvious shortcut means the opposite of what it looks like:

```python
a: tuple[int] = (10, 20, 30)
b: tuple[int] = (10,)
c: tuple[int] = (10, 20)
```

```
$ mypy tuple1.py
tuple1.py:1: error: ... expression has type "tuple[int, int, int]", variable has type "tuple[int]"
tuple1.py:3: error: ... expression has type "tuple[int, int]",      variable has type "tuple[int]"
```

Only `(10,)` passes. **`tuple[int]` means a tuple of exactly one integer** — one position named, one position allowed.

Set them side by side, because they look like the same syntax and disagree completely:

- `list[int]` — any number of integers
- `tuple[int]` — precisely one integer

When you genuinely want "any number", there's separate syntax for it:

```python
scores: tuple[int, ...] = (90, 80, 70, 60)
```

The `...` is literal — three dots, typed as they appear. It reads *"an `int`, then any number more of them"*, and it makes no claim about length. That is the `list[int]` equivalent, and without it whatever you write is a fixed-length layout.

## Where the brackets run out

Everything so far has been the brackets working. The last rung is the shape they cannot describe, and it's a shape you write constantly.

A function returning a user record:

```python
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age, "email": None}
```

`-> dict` is bare, and by now that's obviously too coarse. Tighten it. The name is a string, the age is a number, the email might be nothing — so the only accurate parameterisation admits all three:

```python
def create_user(name: str, age: int) -> dict[str, str | int | None]:
```

That is correct. mypy accepts it. Now be a caller:

```python
 1  def create_user(name: str, age: int) -> dict[str, str | int | None]:
 2      return {"name": name, "age": age, "email": None}
 3
 4
 5  user = create_user("alice", 30)
 6
 7  print(user["name"].upper())
 8
 9  user["age"] = "thirty"
10
11  print(user["emial"])
```

Line 7 is correct code. Line 9 puts a string in the age. Line 11 misspells a key.

```
$ mypy record.py
record.py:7: error: Item "int" of "str | int | None" has no attribute "upper"  [union-attr]
record.py:7: error: Item "None" of "str | int | None" has no attribute "upper"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
```

```
$ python3 record.py
ALICE
KeyError: 'emial'
```

Both complaints land on **line 7**, and neither of the other two lines is mentioned.

**Line 7 — flagged, and it works.** It printed `ALICE`. But the annotation gave *one* type to *all* values, so the checker has no way to know that the `"name"` key in particular holds a string. It sees `str | int | None` and has to assume the worst, and neither `int` nor `None` has `.upper()`.

**Line 9 — silent.** Putting `"thirty"` in the age is a real bug. It passes because `str` is in the union, and the union applies to every key equally.

**Line 11 — silent.** `user["emial"]` raises `KeyError` when it runs. The annotation says keys are strings; `"emial"` is a string. Nothing to object to.

> [!warning] **The annotation complains about the only correct line and says nothing about either bug.** That's the worst possible arrangement — and the damage isn't just the missed bugs. Line 7's error pushes you toward wrapping working code in `isinstance` checks to satisfy a complaint that was never about a real problem.

None of that is a defect in `dict[K, V]`. It describes a mapping where **all values are alike**, which is what a dictionary is for — `dict[str, int]` holding a hundred names-to-ages is exactly right, and the brackets do real work there.

What `create_user` returns is a different thing wearing a dictionary's clothes. It's a **record**: a fixed set of keys, each holding its own type. Three fields, three types, and one slot to describe them all in.

There is no bracket syntax for *"the `name` key holds a `str` and the `age` key holds an `int`"*. That needs a different tool — `TypedDict` — and that's a rung of its own.

## What this concept claims

**A container annotation without brackets is a claim about the box and not the contents** — true, checkable, and almost always weaker than you intended.

Four things to carry:

1. `list` accepts every list ever made. `list[int]` accepts one kind. The brackets are the entire difference, and they cost four characters.
2. The parameter flows outward: annotate the variable and every method call on it becomes checkable, including methods you never wrote.
3. `list`, `set` and `dict` describe a *typical* element — one type covering all of them, however many there are. `tuple` describes *positions*, left to right, which is why its length is fixed by the annotation.
4. `tuple[int]` is not the tuple version of `list[int]`. It means exactly one. `tuple[int, ...]` is the version you wanted.
5. The brackets describe a *uniform* container. A record — fixed keys, each with its own type — is not one, and forcing it into `dict[K, V]` produces an annotation that flags working code and misses real bugs.
