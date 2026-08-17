Every model built so far has been pure Pydantic — validating data in memory, nothing more. SQLModel is the next layer: the same class definition can also **be** a database table. Worth building up from the actual problem before looking at any syntax.

---

## The problem, before any tooling

A database like SQLite or Postgres speaks exactly one language: SQL. Storing a review means, at bottom, something like:

```sql
INSERT INTO reviews (play_name, reviewer_name, rating, comment, created_at)
VALUES ('Hamlet', 'Asha', 5, 'Loved it', '2026-08-04 10:00:00');
```

Doing this directly from Python means writing SQL as raw strings, manually inserting values into that string — risky, since building queries by concatenating strings is literally how SQL injection happens if done carelessly — and manually converting whatever comes back from a query (plain tuples of raw values) into something usable. No type checking, no autocomplete, no validation. Strings in, tuples out.

## An ORM removes that friction

An **ORM — Object-Relational Mapper** — exists to translate between two different worlds: the database's world (tables, rows, columns) and Python's world (classes, objects, attributes). Instead of writing SQL by hand:

```python
session.add(Review(play_name="Hamlet", reviewer_name="Asha", rating=5, comment="Loved it"))
```

and the ORM generates the actual `INSERT` behind the scenes. **SQLAlchemy** is the dominant, most mature ORM in the Python ecosystem, and it's the library actually doing the database work underneath SQLModel.

## A second, separate problem: validating what comes in over the API

An ORM solves **talk to the database using Python objects.** It says nothing about **validating incoming API requests** — is this rating actually between 1 and 5, is this field actually a string. That's a genuinely different concern, and it's Pydantic's job, not SQLAlchemy's.

Before SQLModel existed, a typical FastAPI app needed **two separate class definitions** for what is conceptually one thing:

```python
# SQLAlchemy — defines the actual database table
class ReviewORM(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    ...

# Pydantic — defines the API validation shape
class ReviewSchema(BaseModel):
    rating: int
    ...
```

Two classes describing the same **review** concept, kept in sync entirely by hand. Add a field to one and forget the other, and the API and the database quietly disagree with each other — a real, common source of bugs.

## What SQLModel actually is

**SQLModel is one class that is genuinely both at once** — a real SQLAlchemy-mapped table **and** a real Pydantic validation model, simultaneously, because it's built by combining both libraries under the hood rather than picking one or reimplementing either. Built specifically to simplify working with SQL databases inside FastAPI applications, by the same author as FastAPI itself.

```python
class ReviewTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rating: int = Field(ge=1, le=5)
```

This single class definition:

- **Is a SQLAlchemy-mapped class** — SQLAlchemy's query engine, session, and everything database-side treats it as a real table definition, because underneath, it genuinely is one.
- **Is built on Pydantic** — the same `Field()` syntax, the same type annotations, the same class the earlier projects' models were written in.

> [!important] The core idea worth holding onto: **SQLModel isn't a separate, new thing — it's SQLAlchemy and Pydantic merged into one class**, so **the shape of my data** only has to be written once instead of twice. Everything below — `table=True`, `Field()`, the `Create`/`Read`/`Update` split — is really just **how** that merged class gets used differently in different situations, now that the core idea is in place.

> [!warning] A `table=True` class does **not** validate anything when you construct it. This is the single biggest surprise in SQLModel, and it is deliberate on SQLModel's part, not a bug — a table class has to be constructible from whatever the database hands back, so validation is switched off for it. Checked directly against the installed version:
>
> ```
> sqlmodel 0.0.39 | sqlalchemy 2.0.51 | pydantic 2.13.4
> TABLE  rating=99 accepted -> 99
> TABLE  wrong types accepted -> 12345 'not-a-number'
> CREATE rating=99 REJECTED: ValidationError
> ```
>
> `ReviewTable(play_name=12345, rating="not-a-number")` builds happily. The identical constraint on `ReviewCreate` — no `table=True` — raises. And `ge=1, le=5` doesn't reach the database either; SQLModel emits no `CHECK` constraint, so the generated `CREATE TABLE` carries the column types and nothing more.
>
> The consequence is worth stating plainly, because it is what makes the several-classes pattern below **necessary rather than tidy**: the only thing standing between a caller and a rating of `99` in the database is that every write goes through a non-table schema first. The table class is storage. The schemas are the validation.

It works against any relational database — SQLite, Postgres, MySQL, MariaDB — through Python objects and type annotations, without hand-written SQL for ordinary operations.

---

## `table=True` — the one flag that changes everything

```python
from sqlmodel import SQLModel, Field


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None
```

Two completely different behaviors come out of the exact same base class, depending on one keyword:

- **`table=True`** — this class becomes an actual **database table**. Every field becomes a column. Rows in the table correspond to instances of this class. Validation is off.
- **No `table=True`** — the class behaves like ordinary Pydantic: a validation shape, nothing persisted, every constraint enforced. This is the same `BaseModel`-style behavior seen in every earlier project.

That single flag is what makes SQLModel double as both halves of the job — the same import, the same field syntax, radically different behavior depending on one keyword argument.

---

## `Field(...)` — column metadata, layered onto Pydantic validation

`Field` does two jobs at once, because SQLModel's fields are genuinely Pydantic fields underneath:

**Database-level metadata**, relevant when `table=True`:

```python
id: int | None = Field(default=None, primary_key=True)
play_name: str = Field(index=True)
```

- `primary_key=True` — marks this column as the table's primary key
- `index=True` — creates a database index on this column, so filtering or searching on it is fast
- `default=...` — the column's default value if none is provided

**Validation constraints**, the same Pydantic power seen in earlier field-validator work, just expressed differently here:

```python
rating: int = Field(ge=1, le=5)
```

`ge` (greater than or equal) and `le` (less than or equal) enforce a numeric range directly through `Field`, without writing a custom `@field_validator` — for a constraint this simple, `Field` alone is enough. Per the warning above, this only actually enforces anything on a class **without** `table=True`; written on the table class it is documentation of intent, nothing more.

---

## `default` vs. `default_factory` — a real, easy-to-miss gotcha

```python
created_at: datetime = Field(default_factory=datetime.now)
```

`default_factory` takes a **callable**, not a value — `datetime.now` here, not `datetime.now()`. The distinction matters a great deal:

> [!important] Writing `Field(default=datetime.now())` — calling the function immediately, with parentheses — would evaluate `datetime.now()` **once**, at the moment the class body executes (when the module is first imported), and reuse that exact same frozen timestamp as the default for every single row ever created afterward. Every review would show the same **created at** time: whenever the server happened to start up. `default_factory=datetime.now` — no parentheses — instead hands SQLModel the function itself, to be called **fresh, every time a new row needs a default**, producing a genuinely different timestamp per row. This is the same category of trap as Python's well-known mutable-default-argument gotcha (`def f(x, lst=[])`), just showing up in a different place.

---

## Why one concept needs several classes

The `Hero` example above conflates two things that are usually kept apart on purpose: what actually gets **stored**, and what a **client is allowed to send or receive** at each stage of interacting with it. In a real application, those are rarely identical, and SQLModel's pattern is to define them as separate classes:

| Class | `table=True`? | Purpose |
|---|---|---|
| The table model | Yes | The full column set — everything actually stored, including database-assigned fields like an auto-generated `id` or a server-set `created_at` |
| A **create** schema | No | Only the fields a client should be allowed to submit when creating a new row — deliberately **excludes** fields the database itself is responsible for assigning |
| A **read** schema | No | The shape returned to a caller reading data back — now includes the database-assigned fields, since they exist by this point |
| An **update** schema | No | Every field **optional**, since an update might only touch one of them |

That last row connects directly back to the very first distinction drawn between `PUT` and `PATCH`: a `PATCH` request should be able to send just the one field being changed, leaving everything else untouched. An **update** schema with every field optional is the concrete Pydantic-level mechanism that makes that possible — a client sending only `{"rating": 4}` validates cleanly, because every other field is allowed to simply be absent.

The reason this needs several separate classes, rather than one class reused everywhere: a client creating a review should never be able to set its own `id` or fabricate a `created_at` timestamp — those are the database's job. Excluding those fields from the **create** schema isn't an oversight; it's the actual mechanism enforcing that boundary.
