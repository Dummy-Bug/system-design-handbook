#python #type-hints #typing #generics #typevar #python-utils


Some functions work on any type at all, and every honest attempt to annotate them with the tools so far either lies or throws away information. A helper that picks a random item from a list is the smallest example.

## Too narrow

```python
import random

def random_choice(items: list[User]) -> User:
    return random.choice(items)
```

Fine, until the same helper is wanted for something else:

```python
emails: list[str] = ['a@b.com']
random_choice(emails)
```

```
error: Argument 1 to "random_choice" has incompatible type "list[str]";
expected "list[User]"  [arg-type]
```

The error is correct and the annotation is the problem. Nothing in the function body cares what's in the list — `random.choice` picks an element and hands it back. The signature invented a restriction the code doesn't have.

There's a second, quieter cost. Because the signature promises a `User`, the editor believes it — even when the value is plainly a string:

![[AI-Engineering/00-Python-Utils/01-Type-Hints/Images/01-Narrow-Annotation-Wrong-Autocomplete.png]]

`rando_email` holds an email address, and the completions offered are `age`, `email`, `fav_color`, `first_name`, `last_name` — the fields of a user. Every one of them would fail at runtime. A wrong annotation doesn't merely fail to help; it actively misinforms the tooling built on top of it.

## Too wide

The obvious escape is to say "anything":

```python
from typing import Any

def random_choice(items: list[Any]) -> Any:
    return random.choice(items)
```

No errors. It also destroys the thing you were annotating for. A checker can be asked what it thinks a result is:

```python
reveal_type(random_choice(emails))
# Revealed type is "Any"
```

`Any` means *stop checking here*. The caller passed a list of strings and got back something the checker knows nothing about — no error if it's used as a number, no error if a method is called that doesn't exist. And because the unknown value flows onward into whatever it's assigned to, the blindness spreads outward from this one call.

The editor goes quiet too. Same variable, same dot, nothing offered:

![[AI-Engineering/00-Python-Utils/01-Type-Hints/Images/02-Any-No-Autocomplete.png]]

This is the trade people miss when they reach for `Any` to make an error go away. The error goes away because **the checker stopped having opinions**, and the help it was giving you stops with it.

Both attempts fail for the same reason. The real rule is not *"takes users"* and not *"takes anything"* — it is **"whatever type is in the list, that's the type that comes out"**. Neither annotation can express a relationship between the input and the output.

## Saying "the same type"

```python
def random_choice[T](items: list[T]) -> T:
    return random.choice(items)
```

The `[T]` after the name introduces a **type variable** — a placeholder standing for a type that isn't decided until somebody calls the function. It's used twice, and that repetition is the entire content of the annotation: the `T` going in and the `T` coming out are the same `T`.

```python
reveal_type(random_choice(emails))   # Revealed type is "str"
reveal_type(random_choice(users))    # Revealed type is "TypedDict(User, ...)"
```

Called with strings, it returns a `str`. Called with users, a `User`. The checker works this out per call site, from the argument, and the information survives — so a mistake made with the result is still caught.

The editor recovers, and this is the payoff worth looking at twice. **One function, two call sites, correct at both.** On a user:

![[AI-Engineering/00-Python-Utils/01-Type-Hints/Images/03-TypeVar-Knows-User.png]]

and on a string:

![[AI-Engineering/00-Python-Utils/01-Type-Hints/Images/04-TypeVar-Knows-Str.png]]

`fav_color` / `first_name` / `last_name` in the first, `center` / `count` / `encode` / `endswith` / `find` in the second. Nothing about `random_choice` changed between them — the placeholder resolved to whatever the caller passed in, and both call sites got the real type back.

> [!important] The contrast in one line. `Any` says **"I don't know what this is"** and stops. A type variable says **"I don't know what this is yet, but it's the same thing on both sides"** and keeps checking. That difference is why `Any` is a last resort and a type variable is the normal answer for anything that passes values through.

Nothing changes at runtime — the placeholder is recorded and otherwise ignored:

```python
def random_choice[T](items: list[T]) -> T: ...

print(random_choice.__type_params__)   # (T,)
```

## The older spelling

Plenty of code declares the variable separately, before the function:

```python
from typing import TypeVar

T = TypeVar('T')

def random_choice(items: list[T]) -> T:
    return random.choice(items)
```

Identical meaning. Worth being able to read, since it's what most existing code and most written material uses. The `[T]` form scopes the placeholder to the one function that uses it, rather than leaving a module-level name floating around, and needs no import.

## Where this shows up

Anything that passes values through without inspecting them, which is a larger category than it first sounds: a cache wrapper, a retry helper, `first()` / `last()` / `pluck()`, a function that unwraps a result, a decorator returning the function it was given.

The tell is a function whose body never looks at *what* the value is. If the code only moves a value from one place to another, the signature should say so — and a type variable is how it says so without lying in either direction.

> [!tip] A useful sanity check on any signature you write: **if `Any` appears in it, ask what you actually meant.** Sometimes you genuinely don't know and can't — unvalidated JSON, a plugin interface. Far more often you meant "the same type as that other one", and a type variable will say it precisely while keeping every downstream check alive.
