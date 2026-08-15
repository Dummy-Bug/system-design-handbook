Constraints (the previous note) cover ranges and lengths. A step above that is validation with real *domain* knowledge baked in — is this actually a well-formed email address, a valid URL, a value that should never appear in a log. Writing that from scratch means regular expressions and edge cases that are easy to get subtly wrong. Pydantic ships ready-made types for the common cases instead.

## Installing the extras

The core `pydantic` package is deliberately lean. A few of these special types need extra dependencies, installed via optional extras:

```bash
uv add "pydantic[email]"
```

(`"pip install "pydantic[email]"` if using pip.) Without the extra installed, importing `EmailStr` raises an `ImportError` explaining exactly which package to add.

## `EmailStr` — real email validation, zero regex written by hand

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
```

`email="not-an-email"` fails validation with a clear message; a well-formed address passes. All the actual format-checking logic lives inside the `email-validator` package that the `email` extra pulls in — nothing to write or maintain.

## `HttpUrl` — validated, normalized URLs

```python
from pydantic import BaseModel, HttpUrl

class User(BaseModel):
    website: HttpUrl | None = None
```

`HttpUrl` requires a proper scheme — `website="coreyms.com"` fails, because there's no `http://` or `https://` to anchor it as a URL rather than a bare domain string:

```
1 validation error for User
website
  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='coreyms.com', input_type=str]
```

`website="https://coreyms.com"` passes and comes back as a real `HttpUrl` object, not a plain string — one with its own `.scheme`, `.host`, etc. If the raw string is genuinely all that's needed downstream, `str(user.website)` converts it back.

## `SecretStr` — for values that shouldn't leak into logs

```python
from pydantic import BaseModel, SecretStr

class User(BaseModel):
    password: SecretStr

user = User(password="secret123")
print(user)
```

```
password=SecretStr('**********')
```

Printing the model — or dumping it with `model_dump()` / `model_dump_json()` — shows asterisks, never the real value. That's the entire point: it's far too easy to accidentally `print(user)` in a debug log and leak a password otherwise. The real value is still there when it's genuinely needed, reached explicitly rather than by accident:

```python
user.password.get_secret_value()  # "secret123"
```

## `UUID` — unique identifiers, generated automatically

```python
from uuid import uuid4
from pydantic import BaseModel, Field

class User(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
```

Paired with `default_factory` (previous note), this gives every new instance a fresh, unique ID with zero caller involvement — genuinely the common case for a primary identifier, since the *caller* creating a new user almost never has an ID to hand it themselves.

---

These barely scratch the surface of what ships in `pydantic.types` and `pydantic.networks` — positive/negative numeric shorthands, file paths, IP addresses, and more all exist as ready-made types following the same idea: encode a real-world constraint once, in the library, instead of re-deriving it per project.
