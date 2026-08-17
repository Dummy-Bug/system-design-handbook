#python #type-hints #typing #python-utils


## The gap they fill

A function with nothing written down about its inputs:

```python
1  def add(a, b):
2      return a + b
```

Reading this, you cannot answer a basic question: **what is `add` for?** Numbers, presumably. But `a + b` also joins two strings, also concatenates two lists, also works on anything that has decided what `+` means for itself. The code doesn't say which of those was intended, so a reader has to guess, and the editor can't offer any help — it has nothing to go on either.

The author knew. That knowledge just never made it into the file.

## The syntax

A **type hint** is that knowledge, written down. A colon after a parameter, an arrow before the return:

```python
1  def add(a: int, b: int) -> int:
2      return a + b
```

Read it as a sentence: **takes two ints, gives back an int.** Nothing else about the function changed.

Variables can carry one too, though it's rarely worth it when the value is sitting right there:

```python
1  count: int = 0
2  name: str = 'Corey'
```

That's the entire feature at surface level. Now the question that decides everything else about this folder.

## Does Python enforce it?

The function says `int`. Give it strings:

```python
1  def add(a: int, b: int) -> int:
2      return a + b
3
4  print(add("hello", "world"))
```

```
$ python3 add.py
helloworld
```

No error. No warning. It ran to completion and produced an answer.

That result is worth sitting with, because the natural conclusion from it is wrong. The tempting explanation is **Python is relaxed about types.** It isn't. Watch:

```python
add("hello", "world")   # 'helloworld'
add(5, "world")         # TypeError: unsupported operand type(s) for +: 'int' and 'str'
add(5, 5)               # 10
```

The middle call **raised**. Python is perfectly willing to refuse on grounds of type — it does it constantly, and `len(5)` or `None.upper()` will too.

So the puzzle sharpens. The annotation says `int, int`. The first two calls both violate it. One runs; one raises. **If the annotation were what Python consulted, both would have failed identically.**

## What Python was actually doing

Delete the hints entirely and run the same broken call:

```python
1  def add(a, b):          # no hints at all
2      return a + b
3
4  add(5, "world")
```

```
$ python3 add.py
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

The identical error, from a file containing no annotation anywhere. The hint contributed nothing to it — removing the hint changed nothing, because Python never looked at it in the first place.

> [!important] **Python checks types at the level of operations, not declarations.**
> When it reaches `a + b`, the question it asks is **can these two objects, the ones I am actually holding, be added?** Two strings — yes, join them. An int and a string — no, raise. It never asks **what did somebody write after the colon on line 1?**
>
> So `add("hello", "world")` succeeds not because Python is lax, but because **that operation is genuinely valid**. Joining two strings is a perfectly good thing to do. The annotation being wrong is irrelevant to a question nobody asked.

The return annotation goes unchecked for the same reason:

```python
1  def get_name(user: dict) -> str:
2      return user["name"]
3
4  r = get_name({"name": 42})
5
6  print(r)                    # 42
7  print(type(r).__name__)     # int
```

Annotated `-> str`, returns an `int`, and nothing anywhere objects. The claim was simply false and no one was checking.

Push on it further and the pattern holds — every failure comes from the operation, never from the declaration:

```python
get_name({"nope": 1})   # KeyError: 'name'
get_name(["name"])      # TypeError: list indices must be integers
                        #            or slices, not str
```

The second is the telling one. A list **was** passed where `dict` was annotated — and the complaint that came back was not **you promised me a dict.** It was **you can't index a list with a string.** Python hit the real operation, found it invalid for the real object, and reported ***that*.**

## So where does the hint go?

Not nowhere. This is the part that's easy to get backwards.

When Python executes a `def`, it builds a function object and files the annotations in a dictionary attached to it. That dictionary is still sitting there while the function runs:

```python
print(get_name.__annotations__)
# {'user': <class 'dict'>, 'return': <class 'str'>}
```

Printed **after** the call that returned an `int` from a `-> str` function. **The hints were never removed. They were filed and left unread.**

And Python does no vetting on the way in. Whatever you write after the colon is evaluated and stored, whether or not it is a type at all:

```python
1  def nonsense(x: 'banana', y: 12345) -> ['not', 'a', 'type']:
2      return x
3
4  print(nonsense.__annotations__)
5  # {'x': 'banana', 'y': 12345, 'return': ['not', 'a', 'type']}
6
7  print(nonsense(999, 'whatever'))   # 999
```

Three things that are not types, all filed without comment, and the function runs normally. Write 
`x: 2 + 2` and the dictionary holds `4`.

> [!warning] **Kept and ignored is not the same as removed, and the difference is load-bearing.** 
> If annotations really were discarded, nothing could read them once the program is running — no runtime validation, no framework reading a function's signature to work out what to hand it. They survive in full precisely so that other tools can pick them up. Nothing **has** to; Python itself doesn't.

One consequence, since `def` is an instruction that runs rather than a declaration read ahead:

```python
1  def outer():
2      def inner(x: str) -> bool:
3          return True
4      return inner
```

Until `outer()` is called, that inner `def` never **executes** — so no function object exists and no annotations dictionary exists, even though the annotation is sitting in the source in plain sight.

## What this concept claims

**A type hint is a claim you wrote down, not a constraint the language enforces.**

Everything else in this folder follows from that one sentence. A hint that is never checked is worth writing anyway — but **why** it's worth writing is a separate question with a real answer, and it needs asking rather than assuming.

The failure mode to guard against is the quiet assumption that writing `age: int` has made something safe. It has made something **legible**. Whether anything is checking is a question about your tooling, and the answer is not automatically yes.
