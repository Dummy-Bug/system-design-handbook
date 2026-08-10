#python #type-hints #typing #dataclass #typeddict #python-utils


`11-TypedDict` left a decision open: it works, it costs nothing at runtime, and it never validates anything. Several other ways exist to say "an object with these fields", and choosing between them is a real decision rather than a style preference.

## Where `TypedDict` stops

The record from `11-TypedDict`, a retrieved chunk with a relevance score:

```python
1  class RetrievedDoc(TypedDict):
2      url: str
3      text: str
4      score: float
5
6
7  doc: RetrievedDoc = {"url": "u1", "text": "...", "score": 0.9}
8  print(doc["score"])
```

Per-key types, typos caught, zero runtime cost. It's the right answer until you need something that isn't a key.

Say the relevance threshold — `doc["score"] >= 0.7` — is now written in eleven places, and you want it on the record itself:

```python
 1  from typing import TypedDict
 2
 3
 4  class RetrievedDoc(TypedDict):
 5      url: str
 6      text: str
 7      score: float
 8
 9      def is_relevant(self) -> bool:
10          return self["score"] >= 0.7
11
12
13  doc: RetrievedDoc = {"url": "u1", "text": "...", "score": 0.9}
14  print(doc)
15  print(doc.is_relevant())
```

```
$ mypy sd0.py
sd0.py:9: error: Invalid statement in TypedDict definition; expected "field_name: field_type"  [misc]
sd0.py:15: error: "RetrievedDoc" has no attribute "is_relevant"  [attr-defined]
```

```
$ python3 sd0.py
{'url': 'u1', 'text': '...', 'score': 0.9}
Traceback (most recent call last):
  File "sd0.py", line 15, in <module>
    print(doc.is_relevant())
AttributeError: 'dict' object has no attribute 'is_relevant'
```

**Line 9** — `Invalid statement in TypedDict definition`. The body may contain field declarations and nothing else.

**The runtime error names the real reason:** `'dict' object has no attribute 'is_relevant'`. Concept 11 established that instances are plain dicts — `RetrievedDoc.__mro__` is `(RetrievedDoc, dict, object)`. There is nowhere for a method to live, because the class you wrote never becomes the type of the object.

> [!important] A `TypedDict` describes **the shape of a dict**. The moment you want something that isn't a key — a method, a computed value, a check — you need an object rather than a dict.

## A plain class, and what it costs

```python
 1  class RetrievedDoc:
 2      def __init__(self, url: str, text: str, score: float) -> None:
 3          self.url = url
 4          self.text = text
 5          self.score = score
 6
 7      def is_relevant(self) -> bool:
 8          return self.score >= 0.7
 9
10
11  a = RetrievedDoc("u1", "hello", 0.9)
12  b = RetrievedDoc("u1", "hello", 0.9)
13
14  print(a.is_relevant())
15  print(a)
16  print(a == b)
```

```
$ python3 sd1.py
True
<__main__.RetrievedDoc object at 0x100be1d30>
False
```

The method works and `a.score` reads cleanly. Three things are wrong anyway.

**The repetition.** Lines 2–5 name each field three times — parameter, assignment target, assignment source. Nine mentions for three fields, and a fourth field means editing three places.

**Line 15 prints an address.** `<__main__.RetrievedDoc object at 0x100be1d30>`. Print ten of these while debugging a retrieval step and you learn nothing.

**Line 16 is `False`**, with identical field values. By default `==` compares **identity**, not contents — two constructions are two objects. Which quietly breaks `doc in seen_docs`, deduplication, and every assertion in a test.

## `@dataclass` writes the boilerplate

```python
 1  from dataclasses import dataclass
 2
 3
 4  @dataclass
 5  class RetrievedDoc:
 6      url: str
 7      text: str
 8      score: float
 9
10      def is_relevant(self) -> bool:
11          return self.score >= 0.7
12
13
14  a = RetrievedDoc("u1", "hello", 0.9)
15  b = RetrievedDoc("u1", "hello", 0.9)
16
17  print(a.is_relevant())
18  print(a)
19  print(a == b)
20  print(a.score)
```

```
$ python3 sd2.py
True
RetrievedDoc(url='u1', text='hello', score=0.9)
True
0.9
```

Lines 6–8 are annotations and nothing else — **each field named once.** No `__init__` anywhere in the file, yet line 14 constructs one.

Three methods were generated, from the annotations, at class-creation time. Taken one at a time:

**`__init__`.** In the plain class, lines 2–5 were written by hand. Here there is no `__init__` in the file at all, and `RetrievedDoc("u1", "hello", 0.9)` still works — `@dataclass` read the three annotated fields and wrote exactly that constructor, in that order.

**`__repr__`** is the method Python calls to turn an object into text; `print(a)` is really `print(a.__repr__())`. The plain class inherited `object`'s version, which knows only the class name and the address, because `object` has no idea what fields were added. `@dataclass` does know, so it wrote one that prints them.

**`__eq__`** is the method Python calls for `==`; `a == b` runs `a.__eq__(b)`. `object`'s rule is *equal only if it is literally the same object*, hence `False` for two separate constructions. `@dataclass` wrote one that compares field values — `a.url == b.url and a.text == b.text and a.score == b.score` — hence `True`.

The method on line 10 is untouched and works normally. It's an ordinary class; the decorator only filled in what you would have typed.

> [!info] Notice what it read in order to do that: **the annotations.** Same raw material `Annotated` used in `20-Annotated`, and concept 1's rule for the third time — a library choosing to read `__annotations__` at runtime and act on them. Nothing about the language changed.

## What `@dataclass` still doesn't do

```python
 1  from dataclasses import dataclass
 2
 3
 4  @dataclass
 5  class RetrievedDoc:
 6      url: str
 7      text: str
 8      score: float
 9
10      def is_relevant(self) -> bool:
11          return self.score >= 0.7
12
13
14  bad = RetrievedDoc("u1", "hello", "not a number")
15  print("constructed:", bad)
16  print("score is:", type(bad.score))
17  print(bad.is_relevant())
```

```
$ mypy sd3.py
sd3.py:14: error: Argument 3 to "RetrievedDoc" has incompatible type "str"; expected "float"  [arg-type]
```

```
$ python3 sd3.py
constructed: RetrievedDoc(url='u1', text='hello', score='not a number')
score is: <class 'str'>
Traceback (most recent call last):
  File "sd3.py", line 17, in <module>
    print(bad.is_relevant())
  File "sd3.py", line 11, in is_relevant
    return self.score >= 0.7
TypeError: '>=' not supported between instances of 'str' and 'float'
```

mypy flags line 14. **Python constructs the object anyway** — `score='not a number'`, stored, and `type(bad.score)` is `str`.

The generated `__init__` **assigns**. It read the annotation to learn each field's name and position; it never compares the value against it.

And note *where* it failed: line 17, not line 14. The bad value sat in the object until something tried to use it — which in an agent means the crash surfaces in a scoring step, several hops from the retrieval call that produced it.

> [!important] The gap only matters when there is no line 14 for mypy to check. Your own code didn't type that string — it arrived from `json.loads` on an API response, a tool call's arguments, or a config file. **The checker never saw it**, so a checked construction site is no protection at all.

## The trust boundary

The same dataclass, fed from outside:

```python
 1  import json
 2  from dataclasses import dataclass
 3
 4
 5  @dataclass
 6  class RetrievedDoc:
 7      url: str
 8      text: str
 9      score: float
10
11      def is_relevant(self) -> bool:
12          return self.score >= 0.7
13
14
15  raw = '{"url": "u1", "text": "hello", "score": "0.9"}'
16
17  payload = json.loads(raw)
18  doc = RetrievedDoc(**payload)
19
20  print("constructed:", doc)
21  print("score type:", type(doc.score))
22  print(doc.is_relevant())
```

Line 15 is a response body, with `"score": "0.9"` as a string — exactly what a real API returns. Line 18 unpacks the dict into the constructor.

```
$ mypy sd4.py
Success: no issues found in 1 source file
```

```
$ python3 sd4.py

constructed: RetrievedDoc(url='u1', text='hello', score='0.9')
score type: <class 'str'>
Traceback (most recent call last):
  File "sd4.py", line 22, in <module>
    print(doc.is_relevant())
  File "sd4.py", line 12, in is_relevant
    return self.score >= 0.7
TypeError: '>=' not supported between instances of 'str' and 'float'
```

`Success`, and this is **worse** than the previous case, not better. There, mypy at least flagged the construction. Here it has nothing to flag: `json.loads` returns `Any` — the spreading from `08-Any-Object-Never` — so `RetrievedDoc(**payload)` is unchecked by construction.

Every guarantee in the file is gone at the one place data actually enters.

## A model that validates when the object is built

Same three fields, one word different:

```python
 1  import json
 2  from pydantic import BaseModel
 3
 4
 5  class RetrievedDoc(BaseModel):
 6      url: str
 7      text: str
 8      score: float
 9
10      def is_relevant(self) -> bool:
11          return self.score >= 0.7
12
13
14  raw = '{"url": "u1", "text": "hello", "score": "0.9"}'
15  doc = RetrievedDoc(**json.loads(raw))
16
17  print("constructed:", doc)
18  print("score type:", type(doc.score))
19  print(doc.is_relevant())
```

Line 5 inherits from `BaseModel` instead of carrying `@dataclass`. Lines 6–11 are unchanged.

```
$ python3 sd5.py

constructed: url='u1' text='hello' score=0.9
score type: <class 'float'>
True
```

`score=0.9`, and `type(doc.score)` is **`float`**. The string was parsed into a number during construction, so by the time the object exists the field genuinely holds what the annotation claims — and `is_relevant()` works.

When it can't convert:

```python
21  bad = '{"url": "u1", "text": "hello", "score": "not a number"}'
22  RetrievedDoc(**json.loads(bad))
```

```
$ python3 sd5.py
ValidationError
1 validation error for RetrievedDoc
score
  Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='not a number', input_type=str]
```

It raises **at line 22**, naming the field, the reason, and the offending value.

> [!important] The dataclass crashed inside `is_relevant` with `'>=' not supported between instances of 'str' and 'float'`, several hops downstream. The model raises at the boundary the data crossed.
>
> Same bad data, same eventual failure — the difference is **where you find out**. That's a placement argument, not a correctness one, and placement is the entire value: a stack trace pointing at the retrieval response beats one pointing at whichever scoring step happened to touch the field first.

This is also the third time the same mechanism has appeared. `@dataclass` reads the annotations to *generate* code; a validating model reads them to *check values*; `Annotated` carries extra payload for either to read. The language enforces nothing in any of the three — concept 1, all the way down.

## `NamedTuple` — immutable, and therefore usable as a key

Two things the dataclass can't do:

```python
 1  from dataclasses import dataclass
 2
 3
 4  @dataclass
 5  class RetrievedDoc:
 6      url: str
 7      text: str
 8      score: float
 9
10      def is_relevant(self) -> bool:
11          return self.score >= 0.7
12
13
14  doc = RetrievedDoc("u1", "hello", 0.9)
15
16  doc.score = 999.0
17  print(doc)
18
19  seen = {doc}
```

Line 16 overwrites the score on a record that came back from a search. Line 19 puts the doc in a set — the deduplication you'd want after merging results from two retrievers.

```
$ mypy sd6.py
Success: no issues found in 1 source file
```

```
$ python3 sd6.py
RetrievedDoc(url='u1', text='hello', score=999.0)
Traceback (most recent call last):
  File "sd6.py", line 19, in <module>
    seen = {doc}
TypeError: unhashable type: 'RetrievedDoc'
```

**Line 16 succeeds everywhere.** A dataclass is an ordinary mutable object; nothing stops a field being overwritten.

**Line 19 fails** — `unhashable type`. Sets and dict keys need a hash, and a dataclass has none.

> [!info] The reason follows from the generated `__eq__`. Python's rule is that anything defining a custom `__eq__` loses the default hash: two objects that compare equal must hash equal, and once equality means "same field values", a hash based on identity would violate that. Since the fields can be reassigned at any moment, there is no safe hash to generate — so none is generated.

`NamedTuple` is the same three fields with both properties reversed:

```python
 1  from typing import NamedTuple
 2
 3
 4  class RetrievedDoc(NamedTuple):
 5      url: str
 6      text: str
 7      score: float
 8
 9
10  doc = RetrievedDoc("u1", "hello", 0.9)
11
12  print(doc)
13  print(doc.score)
14  print(doc == RetrievedDoc("u1", "hello", 0.9))
15  print({doc})
16
17  doc.score = 999.0
```

```
$ mypy sd7.py
sd7.py:17: error: Property "score" defined in "RetrievedDoc" is read-only  [misc]
```

```
$ python3 sd7.py
RetrievedDoc(url='u1', text='hello', score=0.9)
0.9
True
{RetrievedDoc(url='u1', text='hello', score=0.9)}
Traceback (most recent call last):
  File "sd7.py", line 17, in <module>
    doc.score = 999.0
AttributeError: can't set attribute
```

Lines 12–14 behave exactly as the dataclass did — readable repr, dot access, equality by value. Then the two differences:

**Line 15 works.** `{doc}` builds a set, because the fields can't change, so a hash computed from them stays valid for the object's whole life.

**Line 17 fails in both tools** — `read-only` from mypy, `can't set attribute` from Python. Assignment isn't available at all.

> [!important] Those two are the same fact. **Immutable, therefore hashable.** A `NamedTuple` goes in a set or a dict key; a field in it cannot be updated.

And it is a real tuple, which is the last thing it brings:

```python
 1  from typing import NamedTuple
 2
 3
 4  class RetrievedDoc(NamedTuple):
 5      url: str
 6      text: str
 7      score: float
 8
 9
10  doc = RetrievedDoc("u1", "hello", 0.9)
11
12  url, text, score = doc
13  print(url, text, score)
14  print(doc[0])
15  print(isinstance(doc, tuple))
```

```
$ python3 sd8.py
u1 hello 0.9
u1
True
```

Unpacking and index access work on top of `doc.url`. Useful when a function returns two or three related values and you want callers to be able to write either `x, y = f()` or `result.x`.

## Choosing

Five options, and the decision is made on four questions.

| | plain `dict` | `TypedDict` | `NamedTuple` | `@dataclass` | validating model |
|---|---|---|---|---|---|
| what it is at runtime | `dict` | `dict` | `tuple` | a normal object | a normal object |
| per-field static types | no | yes | yes | yes | yes |
| methods on it | no | no | yes | yes | yes |
| mutable | yes | yes | **no** | yes | yes |
| usable in a set / as a key | no | no | **yes** | no | no |
| checks values at runtime | no | no | no | no | **yes** |
| cost to construct | none | none | none | none | validation runs |

**Is the data already a dict?** If it arrives as one and stays one — a JSON body you pass along, a state object a framework merges — describing it with a `TypedDict` costs nothing and changes no code. Converting it to an object just to describe it is work you'd pay for on every hop.

**Does it need behaviour?** A method, a computed property, a `__post_init__` — any of these rules out `TypedDict` outright, because the instance is a plain dict with nowhere to put them.

**Does it need to be a key, or must it not change?** `NamedTuple`. This is the narrowest case and the one people forget exists; the giveaway is a `set` of records or a cache keyed by one.

**Did it come from outside?** A validating model, and this question outranks the other three. Everything else in this concept trusts the values it is handed, which is fine for data your own code produced and worthless for data that crossed a boundary.

The short form: **`TypedDict` for dicts you already have, `@dataclass` for objects you create, `NamedTuple` when it must be hashable or frozen, a validating model for anything arriving from outside.**

> [!info] Mechanics beyond the choice — `field(default_factory=...)`, `frozen=True`, `__post_init__`, `NamedTuple._replace`, and what a validating model does with nested models and custom validators — belong to their own folders. What's here is the part that gets asked as a *typing* question, because all five are declared the same way: annotations in a class body, read by something at runtime.

## What this concept claims

**All five ways to say "an object with these fields" are declared identically, and the choice between them is decided by four questions, not by taste.**

Four things to carry:

1. `TypedDict` describes the shape of a **dict**. The instance is a plain dict, so it can hold no methods and no behaviour — the class you wrote never becomes the object's type.
2. `@dataclass` generates `__init__`, `__repr__` and `__eq__` from the annotations, which removes the three real costs of a hand-written class: naming each field three times, printing a memory address, and comparing by identity.
3. **Generating code from annotations is not enforcing them.** A dataclass built from `json.loads` output accepts a string into a `float` field, passes mypy because the input was `Any`, and crashes wherever the value is first used — several hops from where it entered.
4. A validating model is the answer at a trust boundary, and the argument is **placement**: both it and the dataclass fail on bad data, but only one fails at the boundary the data crossed, naming the field and the value.
