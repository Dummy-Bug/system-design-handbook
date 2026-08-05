Python has no static typing. A variable declared to hold a string can just as easily hold an integer, a list, or `None` later on, and nothing in the language stops that. For a script that's a non-issue. For a function that inserts data into a database, it's a real problem: nothing enforces that a `username` is actually a string or an `age` is actually a number before that data lands in storage.

**Pydantic** is a Python library that closes this gap — it validates data *at runtime*, using the type hints you already write, and raises a clear error the moment something doesn't match.

---

## Writing the validation by hand first

Before reaching for Pydantic, it's worth seeing what the problem looks like without it — a plain function that's supposed to receive a username, an email, and an age, and manually checks each one:

```python
def create_user(username, email, age):
    if not isinstance(username, str):
        raise TypeError("Username must be a string")
    if not isinstance(email, str):
        raise TypeError("Invalid email format")
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")

    return {"username": username, "email": email, "age": age}


user1 = create_user("coreyms", "CoreyMSchafer@gmail.com", 38)
print(user1)

user2 = create_user("johndoe", None, "old")
print(user2)
```

`user1` is valid and prints fine. `user2` has **two** problems at once — `email` is `None` instead of a string, and `age` is the string `"old"` instead of an integer. Running this:

![[AI-Engineering/00-Python-Utils/09-Pydantic/Images/00-manual-validation-single-error.png]]

Only one error shows up: `TypeError: Invalid email format`. The `age` problem exists too, but the function crashes on the first `raise` it hits and never gets far enough to check `age`. Whoever's calling this function fixes the email, reruns it, and *then* discovers the age problem — one round-trip at a time, for however many fields have issues.

> [!important] This isn't a Pydantic quirk on the manual side — it's just how a chain of `if ... raise` statements behaves. Each `raise` stops execution immediately, so only the first failing check is ever seen. The real problem this exposes is that hand-written validation reports errors one at a time and requires this much boilerplate *per field* — multiply it by every field a real model has (and real models have far more than three), and the function becomes mostly validation code with the actual logic buried inside it.

---

## The same thing with Pydantic

```python
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    age: int


user1 = User(username="coreyms", email="CoreyMSchafer@gmail.com", age=38)
print(user1)

user2 = User(username="johndoe", email=None, age="old")
print(user2)
```

The type hints (`str`, `int`) aren't just documentation the way they'd be on a plain class or a `dataclass` — Pydantic reads them and actively validates incoming data against them the moment an instance is created. `user1` builds and prints normally. `user2` raises immediately:

![[AI-Engineering/00-Python-Utils/09-Pydantic/Images/01-pydantic-multiple-validation-errors.png]]

**Both** problems are reported in a single error — `email` and `age` — with the exact reason for each. Nothing about the class definition mentions error handling; the three-line class *is* the whole validation logic, for every field, all at once.

That's the sentence-length version of what the rest of these notes go into more depth on: less boilerplate per field, and every problem in the data surfaces together instead of one round-trip at a time.

---

## Where this shows up

Pydantic isn't a niche tool — once a codebase has real data flowing through it, this pattern (parse untrusted input → validate → work with a guaranteed-correct object) shows up constantly:

- **FastAPI** uses Pydantic models to validate every request body and shape every response.
- **SQLModel** builds its table models on top of Pydantic.
- Config loading (env vars, YAML/JSON settings files), data pipelines, and structured-output AI agents (PydanticAI and others) all lean on the same validate-on-construction idea.

Version matters here: **Pydantic V2** (a near-total rewrite, with the core validation logic implemented in Rust) is what's covered throughout — noticeably faster than V1, and the version actually in wide use today. V1 code looks similar but uses different method names (`.dict()` instead of `.model_dump()`, for example) — a tell for which version an older tutorial is written against.
