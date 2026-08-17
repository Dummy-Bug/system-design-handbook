#python #type-hints #typing #newtype #python-utils


Two tools that look almost identical and do opposite things. One gives a type a second name. The other creates a genuinely different type. Confusing them produces a bug that runs perfectly and returns the wrong answer.

## The readability problem

A return annotation that's accurate but unreadable:

```python
def create_user(first_name: str, age: int | None = None
                ) -> dict[str, str | int | None]:
    ...
```

That type will now be repeated at every function that accepts or returns a user. Give it a name:

```python
type User = dict[str, str | int | None]

def create_user(first_name: str, age: int | None = None) -> User:
    ...
```

This is a **type alias**. The `type` statement creates one, and the name is the only new thing — the type underneath is unchanged:

```python
type User = dict[str, str | int | None]
print(User.__value__)
# dict[str, str | int | None]
```

Aliases work for anything, and are worth it the moment a type appears twice:

```python
type RGB = tuple[int, int, int]
type Handler = Callable[[str], None]
type Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
```

> [!info] Older code writes `User: TypeAlias = dict[...]`, or just `User = dict[...]` with no annotation at all. Both still work. The `type` statement is the current form and has one practical advantage: the right-hand side isn't evaluated until something asks for it, so an alias can refer to a class defined further down the file without quoting gymnastics.

## Where an alias isn't enough

Colours. RGB is three numbers; HSL — hue, saturation, lightness — is a different way of describing a colour, and also three numbers.

```python
type RGB = tuple[int, int, int]
type HSL = tuple[int, int, int]

def set_color(c: RGB) -> None: ...

set_color((206, 10, 48))     # a raw tuple

h: HSL = (206, 10, 48)
set_color(h)                 # an HSL where RGB was asked for
```

```
Success: no issues found in 1 source file
```

**No complaint about either line.** The second one is a real bug — those numbers mean something different in the two systems, so the colour comes out wrong — and it will run, produce output, and never raise.

The reason is exactly what an alias is: a second name for the same type. `RGB` **is** `tuple[int, int, int]`. So is `HSL`. To a checker they're not two types that happen to look alike; they're one type with two spellings, so there is nothing to object to.

## `NewType`

`NewType` makes a type that is genuinely distinct, while the value at runtime stays exactly what it was:

```python
from typing import NewType

RGB = NewType('RGB', tuple[int, int, int])
HSL = NewType('HSL', tuple[int, int, int])

def set_color(c: RGB) -> None: ...

set_color((206, 10, 48))          # raw tuple
set_color(HSL((206, 10, 48)))     # an HSL
set_color(RGB((206, 10, 48)))     # correct
```

```
error: Argument 1 to "set_color" has incompatible type
"tuple[int, int, int]"; expected "RGB"  [arg-type]

error: Argument 1 to "set_color" has incompatible type "HSL";
expected "RGB"  [arg-type]

Found 2 errors in 1 file
```

Both mistakes caught, and the correct line passes silently. The bare tuple is now rejected too — which is the point rather than a side effect. A plain triple of numbers **isn't** an RGB colour until somebody says it is, and `RGB(...)` is where that gets said, in the source, where it can be reviewed.

## What it actually costs at runtime

Nothing. That's the part worth seeing:

```python
c = RGB((206, 10, 48))

print(c)                    # (206, 10, 48)
print(type(c).__name__)     # tuple
print(RGB is HSL)           # False
```

`RGB(...)` returns the tuple it was handed, unchanged. There is no wrapper class, no new object, no per-call overhead — the distinction exists only for the checker. `RGB is HSL` being `False` is the whole mechanism: two separate marker objects that a checker refuses to interchange, sitting on top of one runtime representation.

> [!warning] Because the distinction is invisible at runtime, nothing enforces it once the program starts. `isinstance(c, RGB)` is not merely useless, it's an error — `NewType` has no class to test against. If you need the guarantee while running, that's a validating class, not `NewType`.

## Choosing

| | Type alias | `NewType` |
|---|---|---|
| Creates a new type? | no — a second name | yes |
| Interchangeable with the original? | yes, freely | no, needs an explicit wrap |
| Runtime cost | none | none |
| Use when | the type is long, repeated, or hard to read | two values share a representation but must not be mixed |

The test that settles it: **would swapping the two by accident be a bug?** Two `str`s that are a user ID and an email address, two `int`s that are cents and dollars, two triples that are RGB and HSL — those want `NewType`. A long `dict[...]` you're tired of retyping wants an alias.
