#python #type-hints #typing #generics #python-utils


Annotating a parameter `dict` looks like a real claim. It mostly isn't.

## What a bare container promises

```python
def f(d: dict) -> None:
    d['anything'] = object()
```

A checker finds nothing wrong here, and it's right not to. `dict` says *"some dictionary"* — nothing about what's in it. Any key, any value, any combination. You've ruled out a list and a string and stopped.

Add the pieces and it becomes a claim worth making:

```python
def g(d: dict[str, str]) -> None:
    d['k'] = 5
```

```
error: Incompatible types in assignment
(expression has type "int", target has type "str")  [assignment]
```

The square brackets say **keys are strings, values are strings**. Now assigning an `int` is a contradiction, and it's caught without running anything.

Same shape for the rest:

```python
nums: list[int] = [1, 2, 3]
nums.append('four')
```

```
error: Argument 1 to "append" of "list" has incompatible type "str";
expected "int"  [arg-type]
```

That error is worth reading twice. Nobody annotated `append`. The checker worked out that `nums` is a `list[int]`, went and looked at what `append` accepts on a `list[int]`, and found `str` doesn't fit. **One annotation propagated into a method call you never touched** — that's what a parameterised container buys over a bare one.

## The shapes you'll actually use

```python
list[int]              # any number of ints
set[str]
dict[str, int]         # keys, then values
tuple[int, int, int]   # exactly three ints, in order
tuple[int, ...]        # any number of ints
```

The two tuple forms are different claims, and the fixed one is genuinely fixed:

```python
pair: tuple[int, int, int] = (1, 2)
```

```
error: Incompatible types in assignment
(expression has type "tuple[int, int]",
 variable has type "tuple[int, int, int]")  [assignment]
```

A tuple's length is part of its type, which no other container can say. `list[int]` has nothing to say about how many. That's the difference between "a coordinate" and "some numbers" — and the `...` form is how you say the second one deliberately.

## Where it stops being enough

A function returning a user record, annotated honestly:

```python
def create_user(first_name: str, age: int | None = None) -> dict:
    ...
```

`-> dict` tells a caller almost nothing. Tighten it:

```python
-> dict[str, str]
```

Except the age isn't a string, so that's now false. The only accurate version admits everything a value could be:

```python
-> dict[str, str | int | None]
```

Correct, and immediately unsatisfying. **Every value now shares one type.** The dictionary has a first name that must be a string and an age that must be a number, and this annotation cannot express the difference — it says each value is one of three things, without saying which key gets which.

That's not a flaw in the syntax. `dict[K, V]` describes a mapping where all values are alike, which is what a dictionary *is* for. A record with fixed, differently-typed fields is a different thing wearing a dictionary's clothes, and it needs `TypedDict` — which is where the crack in this annotation gets demonstrated properly.

> [!tip] The habit: **parameterise every container you annotate.** A bare `list` or `dict` in a signature is nearly always someone who stopped one step early — it costs nothing to write `list[str]`, and it's the difference between an annotation that documents and one that also checks.
