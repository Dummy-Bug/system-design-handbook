#python #type-hints #typing #unions #optional #python-utils


Every annotation so far has named one type. Real functions don't always cooperate — the commonest shape in any codebase is a lookup that might not find anything.

## A lookup that sometimes finds nothing

```python
def find_email(name: str) -> str:
    users = {"alice": "alice@example.com", "bob": "bob@example.com"}
    return users.get(name)


print(find_email("alice").upper())      # line 6
print(find_email("carol").upper())      # line 7
```

`dict.get` is the safe lookup — it hands back the value when the key is there and doesn't raise when it isn't.

```
ALICE@EXAMPLE.COM
AttributeError: 'NoneType' object has no attribute 'upper'
```

Line 6 works, line 7 dies. `"carol"` isn't in the dictionary, `.get` returned `None`, and `None` has no `.upper()`.

## What it means for an annotation to be true

Before the fix, the question the error raises: is `-> str` a true annotation? It *is* a `str` most of the time.

No — and the reason matters more than the answer.

> [!important] **An annotation is a claim about every possible run, not the typical one.** `-> str` says *"whenever this function returns, the thing coming back is a `str`."* Not usually, not when the key exists. One path returning something else makes the claim false, however rare that path is. There's no partial credit: either a checker can rely on the claim or it can't.

Worth contrasting with Java, because Java has the opposite behaviour and it's the more familiar one:

```java
String findEmail(String name) { return null; }   // legal
```

Perfectly fine there. `null` is a member of every reference type, so a method declared `String` may return `null` and the compiler says nothing — which is the hole that produces `NullPointerException`, and why `Optional<String>` was bolted on later.

Python's type system does not have that hole:

```python
isinstance(None, str)   # False
type(None)              # <class 'NoneType'>
```

`None` is the single value of its own type, `NoneType`. It is not a `str`, not an `int`, not a member of anything else. So a function that sometimes returns `None` and sometimes a `str` returns **two different types**, and `-> str` is a straightforwardly false description.

And the checker says so:

```
find1.py:3: error: Incompatible return value type (got "str | None", expected "str")  [return-value]
```

Notice **where**. Line 3 — the `return` statement — not line 7 where it crashes, and not the call sites at all. It caught the *lie*, and the lie is visible without any caller existing.

Notice also `got "str | None"`. Nobody wrote that. mypy ships descriptions of the built-ins, which is how it already knows what `dict.get` gives back — it worked out the honest type by itself, and it's the exact type you're about to write.

## Saying "or"

```python
def find_email(name: str) -> str | None:
```

The pipe reads as **or**: *"a `str`, or `None`."* That's a **union** — a type made of several types, where a value is one of them.

```
find2.py:6: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
find2.py:7: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
```

Line 3 has gone quiet — the annotation is true now. And the complaint moved to **both** call sites, including line 6, which works perfectly when you run it.

That's the worst-case assumption again, the same one that made a record-shaped `dict[str, str | int | None]` unusable. The checker doesn't know `"alice"` is in the dictionary and `"carol"` isn't; it knows the function returns `str | None`, so `.upper()` might land on `None`. Both lines get flagged.

**That is the union working, not failing.** The errors now sit on the two lines that genuinely aren't safe, and they arrived before anyone ran anything.

## Narrowing

The way out is to handle the case:

```python
email = find_email("carol")

if email is None:
    print("no such user")
else:
    print(email.upper())
```

```
Success: no issues found in 1 source file

no such user
```

Nothing was annotated differently. `email` is still `str | None`, and `.upper()` is still invalid on one of those — but inside the `else`, mypy has worked out that `None` is impossible, because the branch above it caught that case. In there, the variable is a `str` and nothing else.

> [!important] **Narrowing** — the checker following your control flow and tracking which members of a union are still possible at each point. It is the whole reason unions are usable rather than exhausting: you write the check you were going to write anyway, and the error disappears because the code genuinely became safe. An `if` that eliminates a case is information, and the checker reads it.

`is None` is the narrowing you'll write most. `isinstance` does the same job for unions that don't involve `None`, and there are ways to teach the checker about your own predicate functions — a rung of its own.

## Two older spellings

```python
def a(x: str | None) -> None: ...
def b(x: Optional[str]) -> None: ...
def c(x: Union[str, None]) -> None: ...
```

```
opt.py:9:  note: Revealed type is "def (x: str | None)"
opt.py:10: note: Revealed type is "def (x: str | None)"
opt.py:11: note: Revealed type is "def (x: str | None)"
```

Three spellings, **one type**. (`reveal_type` is a question you ask mypy — it prints what the checker believes something is, and is the fastest way to settle an argument about a type.)

- **`str | None`** — 3.10+, what you write in new code.
- **`Optional[str]`** — imported from `typing`, means exactly `str | None`. Nothing more.
- **`Union[str, None]`** — the oldest form. `Union[int, str, None]` is how a three-way union was written before the pipe existed.

All three still work and all three appear in real codebases, so you need to read them. Only the first is worth writing.

## Optional does not mean optional

`Optional` is a badly chosen name, and it causes a specific, extremely common confusion: **"optional" meaning *the caller may omit it* is not the same as "optional" meaning *the value may be `None`*.**

Four functions, all legal, all different:

```python
def w(name: str) -> None: ...
def x(name: str = "friend") -> None: ...
def y(name: str | None) -> None: ...
def z(name: str | None = None) -> None: ...
```

Call each one twice — once omitting the argument, once passing `None`:

```
four.py:6:  error: Missing positional argument "name" in call to "w"  [call-arg]
four.py:7:  error: Argument 1 to "w" has incompatible type "None"; expected "str"  [arg-type]
four.py:10: error: Argument 1 to "x" has incompatible type "None"; expected "str"  [arg-type]
four.py:12: error: Missing positional argument "name" in call to "y"  [call-arg]
```

| | `f()` — omit it | `f(None)` — pass nothing-ish |
|---|---|---|
| `name: str` | **error** | **error** |
| `name: str = "friend"` | fine | **error** |
| `name: str \| None` | **error** | fine |
| `name: str \| None = None` | fine | fine |

> [!important] **Two independent switches.**
> - **A default** decides whether the caller may *omit* the argument. It has nothing to do with types.
> - **`| None`** decides whether `None` is an *allowed value*. It has nothing to do with defaults.
>
> Four combinations, each meaning something different, and each one you will need.

The row people never think of is the third. **`name: str | None` with no default** means the caller *must* pass an argument, and `None` is a legitimate thing to pass. `y()` is an error; `y(None)` is fine.

That's a genuinely useful signature — *"tell me explicitly, even if the answer is nothing"* — and it's invisible the moment you collapse the two switches into one word. A field that must be stated but may be empty is not the same as a field you can forget about, and only one of the four rows says each.

## The trap that falls out

```python
def greet(name: str = None) -> None:
    print(name)
```

```
badefault.py:1: error: Incompatible default for parameter "name" (default has type "None", parameter has type "str")  [assignment]
badefault.py:1: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
```

Very common, and wrong on its face: the annotation says `str` and the default on the same line is `None`. The two contradict each other. The fix is to write what was meant:

```python
def greet(name: str | None = None) -> None:
```

The note about *implicit Optional* is history worth knowing. Older mypy silently rewrote `str = None` into `str | None = None` for you. That guessing was removed precisely because it erased the difference between the second and fourth rows of the grid — the reader could no longer tell whether `None` was a meaningful value or just a placeholder default.

## What this concept claims

**A union says a value is one of several types, and `X | None` is the union you will write most — because "this might not be there" is the commonest thing a real function has to express.**

Four things to carry:

1. An annotation is a claim about **every** run. "True except when the key is missing" is false, and a checker treats it as false.
2. `None` is its own type in Python, not a member of every other type as in Java. A function that may return `None` genuinely returns two types and has to say so.
3. Once a value is a union, the checker assumes the worst member — and **narrowing** is how you get out of it. An `if` that eliminates a case is information the checker reads.
4. **A default and `| None` are independent switches.** One controls whether the argument may be omitted, the other whether `None` is a legal value. All four combinations exist and mean different things.
