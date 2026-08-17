#python #type-hints #typing #collections #python-utils

## An annotation that rejects working code

```python
1  def shout(names: list[str]) -> None:
2      for n in names:
3          print(n.upper())
4
5
6  shout(["alice", "bob"])                    # a list
7  shout(("alice", "bob"))                    # a tuple
8  shout({"alice", "bob"})                    # a set
9  shout(n for n in ["alice", "bob"])         # a generator
```

The parameter is properly parameterised — `list[str]`, exactly as the previous note taught. Four callers pass four different containers.

Run it:

```
$ python3 shout.py
ALICE
BOB

ALICE
BOB

ALICE
BOB

ALICE
BOB
```

**All four worked.** Four identical pairs — the tuple, the set and the generator behaved no differently from the list. A `for` loop doesn't care which of them it was handed.

Check it:

```
$ mypy shout.py

shout.py:7: error: Argument 1 to "shout" has incompatible type "tuple[str, str]"; expected "list[str]"  [arg-type]

shout.py:8: error: Argument 1 to "shout" has incompatible type "set[str]";        expected "list[str]"  [arg-type]

shout.py:9: error: Argument 1 to "shout" has incompatible type "Generator[str, None, None]"; expected "list[str]"  [arg-type]
```

**Three errors on a program with no bugs in it.**

This is the mirror image of where the previous note ended. There, an over-loose annotation flagged the one correct line and missed both real bugs. Here an over-tight one flags three correct lines when there are no bugs at all.

And the checker is right both times. It is enforcing the claim it was given. `list[str]` means **a list** — a tuple is not a list, a set is not a list, a generator is not a list. Nothing about the errors is wrong; the claim was.

## What the body actually needs

```python
1  def shout(names: list[str]) -> None:
2      for n in names:
3          print(n.upper())
```

Read the two lines and ignore what you happen to call it with. The function loops over `names`, and calls `.upper()` on whatever comes out.

That's the entire requirement: **something you can loop over, yielding strings.** It never indexes, never takes a length, never sorts, never asks whether the order is stable. **Being a list** was never part of the job.

## Saying the requirement instead

```python
 1  from collections.abc import Iterable
 2
 3
 4  def shout(names: Iterable[str]) -> None:
 5      for n in names:
 6          print(n.upper())
 7
 8
 9  shout(["alice", "bob"])
10  shout(("alice", "bob"))
11  shout({"alice", "bob"})
12  shout(n for n in ["alice", "bob"])
13  shout({"alice": 1, "bob": 2})      # a dict
14  shout("xyz")                       # a plain string
```

```
$ mypy shout2.py
Success: no issues found in 1 source file
```

Six callers, one annotation, nothing to report. `Iterable[str]` says **anything that can be looped over, producing strings** — which is what the body asked for, stated exactly.

Two of those callers are new, and both are worth looking at.

**The dict passed.** Looping over a dictionary yields its **keys**, and these keys are strings. `shout({"alice": 1, "bob": 2})` prints `ALICE BOB`; the values are never touched. Anything that reads a dict by looping is reading its keys.

**The plain string passed too**, and this one is a trap:

```
$ python3 shout2.py
X
Y
Z
```

`"xyz"` is iterable, and looping over it yields one-character strings — which are strings. So a `str` genuinely **is** an `Iterable[str]`.

> [!warning] Pass one name where a collection of names was meant and it will be shouted a letter at a time, with no complaint from the checker and no error at runtime. `Iterable[str]` cannot rule this out, because the claim is true. It's the standard cost of the loosest annotation, and worth remembering whenever a function takes `Iterable[str]` and the caller might hold a single string.

## Where these types live

`Iterable` is imported from **`collections.abc`** — the modern home for the abstract collection types. Older code imports the same names from `typing`; those are deprecated aliases for exactly these, kept working for compatibility.

Nothing about the import is magic. It brings in a name to write after the colon, and — as concept 1 established — the interpreter files it away and moves on. `shout` behaves identically with the annotation deleted.

## Weakest is a floor, not a race

Different body, same annotation. This one indexes instead of looping:

```python
1  from collections.abc import Iterable
2
3
4  def first_and_last(names: Iterable[str]) -> str:
5      return f"{names[0]} ... {names[-1]}"
```

```
$ mypy firstlast.py

firstlast.py:5: error: Value of type "Iterable[str]" is not indexable  [index]
```

The complaint is about the **definition**, not any caller — there aren't any yet. 
`Iterable` **promises one thing, looping, and the body is doing something else**.\

Which iterables actually break on `names[0]`? Feed it seven:

```
$ python3 indexprobe.py

list      | Sequence? True  | alice ... carol

tuple     | Sequence? True  | alice ... carol

str       | Sequence? True  | x ... z

range     | Sequence? True  | 0 ... 2

set       | Sequence? False | TypeError: 'set' object is not subscriptable

generator | Sequence? False | TypeError: 'generator' object is not subscriptable

dict      | Sequence? False | KeyError: 0
```

All seven are iterable — `for n in x` works on every one. Only four survive indexing, and one column predicts it exactly.

### What a sequence is

Not a class you create. **A category, defined by what you can do to the thing.**

Something is a sequence when its items sit at **numbered positions**, starting at 0, in an order that stays put. Three abilities come with that, always together:

- `x[0]`, `x[-1]` — get an item by position
- `len(x)` — how many
- looping returns them in the **same order every time**

The word is ordinary Python vocabulary, not a typing invention. The built-in sequences are 
`list`, `tuple`, `str`, `range` and `bytes` — all familiar, they just never had a collective name.

Read the three failures against that definition:

**`set` → `TypeError: 'set' object is not subscriptable`.** A set has no positions. It records what is in it, not where anything sits, so **the first one** doesn't mean anything.

**`generator` → `TypeError: 'generator' object is not subscriptable`.** A generator produces items one at a time, forward only. The second item doesn't exist yet while you hold the first, and the first is gone once you move past it — there is nothing to index into.

**`dict` → `KeyError: 0`**, and the **different** error is the interesting part. A dict **is** subscriptable; `d["alice"]` works. But the thing in brackets is a **key**, not a position. `d[0]` went looking for a key called `0` and didn't find one. Nothing in a dict is addressed by position.

### Saying it

```python
1  from collections.abc import Sequence
2
3
4  def first_and_last(names: Sequence[str]) -> str:
5      return f"{names[0]} ... {names[-1]}  (of {len(names)})"
6
7
8  print(first_and_last(["alice", "bob", "carol"]))
9  print(first_and_last(("alice", "bob", "carol")))
```

```
$ mypy seq.py
Success: no issues found in 1 source file

$ python3 seq.py
alice ... carol  (of 3)
alice ... carol  (of 3)
```

List and tuple both accepted — the `list[str]` annotation would have thrown the tuple away for nothing. And the two that genuinely cannot do it:

```python
1  from collections.abc import Sequence
2
3
4  def first_and_last(names: Sequence[str]) -> str:
5      return f"{names[0]} ... {names[-1]}  (of {len(names)})"
6
7
8  first_and_last({"alice", "bob"})                 # a set
9  first_and_last(n for n in ["alice", "bob"])      # a generator
```

```
$ mypy seq_bad.py

seq_bad.py:8: error: Argument 1 to "first_and_last" has incompatible type "set[str]"; expected "Sequence[str]"  [arg-type]

seq_bad.py:9: error: Argument 1 to "first_and_last" has incompatible type "Generator[str, None, None]"; expected "Sequence[str]"  [arg-type]
```

Rejected, and correctly this time — `names[0]` on either would be a real error, caught before it happened.

**Every sequence is iterable; most iterables are not sequences.** So `Sequence[str]` is asking for more than `Iterable[str]`, and it's only justified when the body indexes, measures, or leans on the order — which this one does, on both counts.

## Reading versus changing

Inside a function taking `names: Sequence[str]`:

```python
1  from collections.abc import Sequence
2
3
4  def add_one(names: Sequence[str]) -> None:
5      names.append("dave")
```

```
$ mypy mutate.py
mutate.py:5: error: "Sequence[str]" has no attribute "append"  [attr-defined]
```

The reason is already on the table:

```python
print(hasattr([], 'append'))    # True
print(hasattr((), 'append'))    # False
print(hasattr('', 'append'))    # False
```

A tuple is a sequence. A string is a sequence. Neither has `append`. So `append` **cannot** be part of what `Sequence` promises, or the promise would be false for two of its most common members.

**`Sequence` is read-only — look, count, loop.** Changing is a stronger promise with its own name:

```python
1  from collections.abc import MutableSequence
2
3
4  def add_two(names: MutableSequence[str]) -> None:
5      names.append("dave")     # accepted
```

The dictionary family works the same way. `Mapping[str, int]` promises key lookup, `len`, and looping the keys, and nothing about modification:

```python
1  from collections.abc import Mapping
2
3
4  def add_person(ages: Mapping[str, int]) -> None:
5      ages["dave"] = 40
```

```
$ mypy mapping_bad.py

mapping_bad.py:5: error: Unsupported target for indexed assignment 
("Mapping[str, int]")  [index]
```

`MutableMapping[str, int]` is the version that allows it.

So there are two families, three rungs each:

| loop only     | + read by position/key | + change it            |
| ------------- | ---------------------- | ---------------------- |
| `Iterable[T]` | `Sequence[T]`          | `MutableSequence[T]`   |
| `Iterable[K]` | `Mapping[K, V]`        | `MutableMapping[K, V]` |
|               |                        |                        |

> [!tip] **In practice you will never write the `Mutable*` names.** Check which built-in types they actually cover:
>
> ```
> type       Sequence  MutSeq   Mapping  MutMap
> list       True      True     False    False
> tuple      True      False    False    False
> str        True      False    False    False
> range      True      False    False    False
> bytes      True      False    False    False
> bytearray  True      True     False    False
> dict       False     False    True     True
> set        False     False    False    False
> frozenset  False     False    False    False
> ```
>
> **`MutableSequence` is `list`** — plus **`bytearray`**, which you are unlikely ever to annotate. 
> 
> **`MutableMapping` is `dict`.** So if your function modifies its argument, write `list[str]` or `dict[str, int]`: shorter, clearer, no import, and the only caller you turn away is one holding something that couldn't be modified anyway.
>
> Worth knowing the names exist, because you'll read them in library code and in older codebases. Not worth typing.

Which reduces the whole concept to four lines you'll actually use:

| the body... | annotate |
|---|---|
| only loops over it | `Iterable[T]` |
| indexes it / takes `len` / needs the order | `Sequence[T]` |
| looks things up by key, doesn't change them | `Mapping[K, V]` |
| **changes** it | `list[T]` / `dict[K, V]` |

And the everyday payoff of the middle two is not really about accepting exotic containers — it's that **the signature now says whether the function will modify what you gave it.** A caller reading `Mapping[str, int]` knows their dictionary comes back untouched; `dict[str, int]` makes no such promise. A function that reads a config and a function that rewrites one should not have the same parameter type.

## The direction flips on the way out

Everything so far has been about parameters. Now a function that builds something and hands it back:

```python
1  from collections.abc import Iterable
2
3
4  def load_names() -> Iterable[str]:
5      return ["alice", "bob", "carol"]
```

By the rule so far this looks right — `Iterable[str]` is the weakest true statement, and it **is** true. Watch what it does to the caller:

```python
 8  a = load_names()
 9
10  print(a[0])
11  print(len(a))
12  a.append("dave")
```

```
$ mypy ret.py

ret.py:10: error: Value of type "Iterable[str]" is not indexable  [index]

ret.py:11: error: Argument 1 to "len" has incompatible type "Iterable[str]"; expected "Sized"  [arg-type]

ret.py:12: error: "Iterable[str]" has no attribute "append"  [attr-defined]
```

```
$ python3 ret.py

alice
3
```

**It is a list.** It indexes, it has a length, it appends — the run proves all three. The annotation threw that away and left the caller holding the least capable description you could have written. Change the return to `list[str]` and every line is fine.

The same reasoning applies to autocomplete: an editor offers what the **annotation** permits, 
so `-> Iterable[str]` suggests one method on a value that really supports thirty.

> [!important] **Accept abstract, return concrete.**
> The rule doesn't reverse — the audience does.
> - **Parameter — weak is generous.** You're describing what you'll **accept**, so a looser type lets more callers in.
> 
> - **Return — weak is stingy.** You're describing what they **get**, so a looser type hands back less than you built.
>
> Both are the same instinct — say the true thing that serves the other side — pointed in opposite directions.

## What this concept claims

**Annotate a parameter with the weakest type the function actually needs, and return the most specific type you actually have.**

`list[str]` on a function that only loops is a claim stronger than the body justifies. The extra strength buys nothing — the loop was never going to use it — and costs you every caller holding a tuple, a set, a generator, or a dict's keys.

Four things to carry:

1. The right annotation comes from **reading the body**, not from what you currently pass in. Ask what operations the parameter is actually subjected to.
2. Over-tight and over-loose fail differently and both are worth recognising. Over-loose flags correct code **and** misses bugs. Over-tight rejects callers that would have worked perfectly — a checker reporting failure on a program that runs.
3. The abstract types form a ladder of promises: loop it, then read it by position or key, then change it. Pick the rung the body stands on. In practice the third rung is `list` and `dict`, so it doesn't need its abstract name.
4. On the way out, the reasoning inverts. `-> Iterable[str]` is honest and useless; `-> list[str]` is what the caller needed.
