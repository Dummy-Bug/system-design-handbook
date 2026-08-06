#python #type-hints #typing #unions #python-utils


A parameter that may be a number or may be missing needs a way to say "either". The syntax is one character, and the confusion around it is worth clearing once because the word *optional* is used for two different ideas.

## The problem, as a checker sees it

```python
def create_user(first_name: str, age: int = None) -> dict:
    ...
```

Perfectly ordinary code. A checker rejects it:

```
error: Incompatible default for parameter "age"
(default has type "None", parameter has type "int")  [assignment]
note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed
its default to no_implicit_optional=True
```

The complaint is exact: you said this is an `int`, then supplied a default that isn't one. `None` is not a number — it's a separate value of a separate type — so the annotation and the default contradict each other on line one.

## Saying "either"

A pipe means *or*:

```python
def create_user(first_name: str, age: int | None = None) -> dict:
    ...
```

Read it as "an `int`, or `None`". The contradiction is gone because the annotation now admits the default it was given.

This composes anywhere a type goes, and with as many members as you like:

```python
value: int | str | None
def handler(x: int | float) -> str | bytes: ...
items: list[int | str]
```

> [!info] Older code writes this as `Optional[int]`, imported from `typing`, which means exactly `int | None` and nothing more. You'll meet it constantly in codebases predating the pipe syntax. The name is the problem — see below.

## The trap the name causes

**"Optional" gets used for two unrelated ideas**, and mixing them up produces bugs a checker will happily let through.

| What you mean | How you say it |
|---|---|
| the caller may leave it out | give it a **default** |
| the value may be `None` | annotate it `X \| None` |

These are independent. All four combinations are legal and mean different things:

```python
def a(age: int): ...                # required, never None
def b(age: int = 0): ...            # may be omitted, never None
def c(age: int | None): ...         # required, but may be None
def d(age: int | None = None): ...  # may be omitted, may be None
```

`c` is the one people write by accident. Leaving it out is an error:

```python
c()
```

```
error: Missing positional argument "age" in call to "c"  [call-arg]
```

You made the *value* nullable without making the *argument* skippable. `Optional[int]` reads like it should have covered both. It covers neither on its own — only `= None` makes it skippable.

## What a union costs you afterwards

Saying "either" moves the work rather than removing it. The checker now holds you to *both* possibilities:

```python
def a(age: int | None = None) -> None:
    print(age + 1)
```

```
error: Unsupported operand types for + ("None" and "int")  [operator]
note: Left operand is of type "int | None"
```

Nothing is wrong with the annotation. The error is real: `age` might be `None` at that line, and `None + 1` raises at runtime. The checker found a crash that only happens when the caller omits the argument — the branch least likely to be covered by a quick manual test.

The fix is to handle the case, which then narrows the type for the rest of the block:

```python
def a(age: int | None = None) -> None:
    if age is None:
        return
    print(age + 1)      # here, age is an int
```

> [!important] This is the honest trade. A union is not a way to make the checker quieter — it's a promise that **every place you use the value, you've dealt with all of its possibilities.** Reaching for `int | None` to silence the default-value error, then using the value as though it were always an `int`, converts one obvious error into a scattering of subtler ones.
