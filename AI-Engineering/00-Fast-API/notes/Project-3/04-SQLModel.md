Every model built so far has been pure Pydantic — validating data in memory, nothing more. SQLModel is the next layer: the same class definition can also **be** a database table. Worth building up from the actual problem before looking at any syntax.

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

Worth building the pre-SQLModel version properly here, because the exact shape of its problem is what SQLModel was made to fix. SQLAlchemy defines the table:

```python
class ReviewORM(Base):
    __tablename__ = "reviews"
    id            = Column(Integer, primary_key=True)
    play_name     = Column(String)
    reviewer_name = Column(String)
    rating        = Column(Integer)
    comment       = Column(String)
    created_at    = Column(DateTime)
```

Six columns, and `id` is the database's to assign — a client never picks its own row id.

Now a request arrives at `POST /reviews` carrying a play name, a reviewer name, a rating and a comment. Something has to check that body, and SQLAlchemy will not: that needs a Pydantic class, holding exactly the four fields a client is allowed to send.

```python
class ReviewCreateSchema(BaseModel):
    play_name: str
    reviewer_name: str
    rating: int
    comment: str
```

Declaring it on the route is what puts it in the request's path:

```python
@app.post("/reviews")
def create_review(review: ReviewCreateSchema):
    row = ReviewORM(**review.model_dump())
    ...                      # save it
```

The annotation is the entire mechanism. FastAPI reads `review: ReviewCreateSchema`, builds one from the incoming body, and rejects the request with a `422` before `create_review` runs at all if the body doesn't fit. A client sending an `id` gets nowhere, because the class it is being checked against has no such field.

Then the route finishes and the new review goes back out, and the response has to include the `id` — the caller needs it to fetch this review again later — plus the `created_at` the database filled in. Six fields, not four, so that is a third class:

```python
class ReviewReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    play_name: str
    reviewer_name: str
    rating: int
    comment: str
    created_at: datetime
```

That `from_attributes` line is not decoration. A Pydantic class normally builds itself from a dictionary, and what the route has in hand is a `ReviewORM` **object**. Without the flag, handing one over fails outright — Pydantic refuses to read attributes off an arbitrary object unless it has been told it may. So the read schema needs a config switch whose only purpose is to let it accept the thing the ORM produces.

Which completes the route — the same one from a moment ago, now with its outgoing half declared too:

```python
@app.post("/reviews", response_model=ReviewReadSchema)
def create_review(review: ReviewCreateSchema):
    row = ReviewORM(**review.model_dump())
    ...                      # save it; the database assigns id and created_at
    return row
```

Three classes, three jobs, one request. `ReviewCreateSchema` guards what comes **in** — four fields, so an `id` cannot be sent. `ReviewORM` is what actually gets **stored**. `ReviewReadSchema` shapes what goes **out**, now carrying the two fields the database filled in. The route body does almost nothing; the classes at either end are doing the work.

### One schema for both directions, and why it fails

The obvious economy is to write **one** Pydantic class for both jobs, with the two database-owned fields marked optional so an incoming request can leave them out:

```python
class ReviewSchema(BaseModel):
    id: Optional[int] = None
    play_name: str
    reviewer_name: str
    rating: int
    comment: str
    created_at: Optional[datetime] = None
```

It breaks on the first request that abuses it:

```json
{"play_name": "Hamlet", "reviewer_name": "Asha", "rating": 5,
 "comment": "Loved it", "id": 1, "created_at": "1999-01-01T00:00:00"}
```

That body **passes validation**, because optional means **allowed to be absent** — never **forbidden**. The client just handed you a row id of its choosing and a timestamp from 1999, and the schema raised nothing. Whether that overwrites an existing review or simply plants a lie in the database depends on the code downstream, and neither outcome is acceptable.

So the two directions genuinely need two classes. Not for tidiness — because the **absence** of `id` from the incoming schema is the only thing making it impossible to send one.

### Which leaves three classes, two of them identical

```python
class ReviewORM(Base):                 # SQLAlchemy — 6 columns
    id, play_name, reviewer_name, rating, comment, created_at

class ReviewCreateSchema(BaseModel):   # Pydantic — 4 fields, what a client may send
    play_name, reviewer_name, rating, comment

class ReviewReadSchema(BaseModel):     # Pydantic — 6 fields, what goes back out
    id, play_name, reviewer_name, rating, comment, created_at
```

The first and the third are **mirrors**. Same six fields, same six meanings, written twice — once in SQLAlchemy's `Column(...)` syntax and once in Pydantic's annotation syntax — for no reason other than that neither library can read the other's classes.

That is the duplication worth being angry about. It carries no information and it decays: add a column to the table, forget the read schema, and the API quietly stops returning a field the database is storing. The `Create` schema, by contrast, differs from the table **on purpose**, and would still need to exist in a perfect world.

## What SQLModel actually is

**SQLModel is one class that is genuinely both at once** — a real SQLAlchemy-mapped table **and** a real Pydantic validation model, simultaneously, because **it's built by combining both libraries under the hood** rather than picking one or reimplementing either. Built specifically to simplify working with SQL databases inside FastAPI applications, by the same author as FastAPI itself.

```python
class ReviewTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rating: int = Field(ge=1, le=5)
```

This single class definition:

- **Is a SQLAlchemy-mapped class** — SQLAlchemy's query engine, session, and everything database-side treats it as a real table definition, because underneath, it genuinely is one.
- **Is built on Pydantic** — the same `Field()` syntax, the same type annotations, the same class the earlier projects' models were written in.

It works against any relational database — SQLite, Postgres, MySQL, MariaDB — through Python objects and type annotations, without hand-written SQL for ordinary operations.

> [!important] The core idea worth holding onto: **SQLModel isn't a separate, new thing — it's SQLAlchemy and Pydantic merged into one class**, so a table no longer has to be described **twice, in two libraries' syntaxes**. Exactly how much that saves is worked out below — it is a real win, and a narrower one than it first sounds. 


### Which of the three classes disappears

Go back to the three the old way needed. `ReviewORM` and `ReviewReadSchema` were mirrors of each other, so the moment one class can be both, the mirror has nothing left to do:

```python
@app.post("/reviews", response_model=ReviewTable)
def create_review(review: ReviewCreate):
    ...
```

The same route as before, with one word changed. `ReviewReadSchema` is gone and the table class has taken its place on the way out. The create schema stays exactly where it was — still four fields, still the thing stopping a client from sending an `id`.

FastAPI accepts the table class directly as a `response_model`, publishes all its fields to the generated docs, and **serialises instances** of it exactly like any other Pydantic model — because it **is** one. Three classes become two, and the one that vanished is the one that carried no information.

The `from_attributes` switch goes with it. That flag existed only to grant a Pydantic class permission to read values off an object built by a different library. A table class needs no such permission — the object and the schema are the same class.

That holds only while the read shape and the stored shape genuinely match. Add a column the public must never see — an internal `moderation_flag`, a `reviewer_email` — and `response_model=ReviewTable` will happily publish it. At that point a separate read schema earns its place again, and the class count is back to three.

> [!important] Which is the honest size of the win, and it is smaller than it first sounds. **SQLModel does not reduce the number of classes you need. It removes the class you never needed.**
>
> | | Nothing to hide | A column to hide |
> |---|---|---|
> | **Old way** | 3 classes — the read schema is a pure mirror, carrying no information | 3 classes — the read schema now earns its place |
> | **SQLModel** | **2 classes** — the mirror is deleted | 3 classes — all three earn their place |
>
> The counts only match in the case where a read schema has something real to say. When it has nothing to say, the old way made you write it anyway.

There is a second difference that matters more day to day than the count does. In the old way, `ReviewReadSchema` mirrored the table **whether anyone wanted it to or not**, so the two drifted apart the moment someone edited one and forgot the other. Now, a read schema differs from the table **because somebody decided it should**, and that difference is the documentation — read the class and you know exactly what a caller is allowed to see. Two classes accidentally the same and rotting, versus two classes deliberately different where the difference is the whole point.

> [!note] Worth holding this loosely rather than as a verdict. Whether the win justifies adopting a library is a real debate — plenty of production Python runs SQLAlchemy plus Pydantic on purpose, and SQLModel is a far smaller project with a far smaller ecosystem behind it. The defensible summary is that it removes accidental duplication and not meaningful duplication, and that the gain is real but modest.

---

## `table=True` — the one flag that changes everything

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class ReviewTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    play_name: str = Field(index=True)
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.now)
```

The same class from the previous section, now carrying every field this project actually stores.

Two completely different behaviors come out of the exact same base class, depending on one keyword:

- **`table=True`** — this class becomes an actual **database table**. Every field becomes a column, and its type annotation is what defines that column's SQL type and whether it accepts null. **Rows in the table correspond to instances of this class**. **Validation is off**.
- **No `table=True`** — the class behaves like ordinary Pydantic: a validation shape, nothing persisted, every constraint enforced. This is the same `BaseModel`-style behavior seen in every earlier project.

That single flag is what makes SQLModel double as both halves of the job — the same import, the same field syntax, radically different behavior depending on one keyword argument.

### The surprise hiding in that flag

The last three words of the first bullet — **validation is off** — are the single most consequential thing in this note, and they sound like a typo the first time you read them. They are not. Two classes one keyword apart behave completely differently:

```python
class ReviewCreate(SQLModel):                 # no table=True
    rating: int = Field(ge=1, le=5)


class ReviewTable(SQLModel, table=True):      # table=True
    rating: int = Field(ge=1, le=5)
```

`ReviewCreate(rating=99)` raises a `ValidationError` saying the input should be less than or equal to 5. `ReviewTable(rating=99)` builds without complaint and holds a rating of 99. Same constraint, same syntax, opposite outcome.

### Why the author switched it off on purpose

This looks like a mistake — validation disabled on exactly the class where bad data does the most damage. It isn't, and the reason is about what a table object **is**.

A Pydantic model is built **once, complete, from data that arrived from outside**, and then never changes. Validate it at construction and the job is finished. That describes a request body exactly, which is what Pydantic was designed for.

A table object does not live like that. It is mutable, and it spends most of its life **incomplete**:

- Build one to insert and it has no `id` yet — the database has not assigned one. At **that moment the object does not satisfy its own declared shape**.
- **SQLAlchemy writes attributes directly, one at a time** — when it loads a row, refreshes after a commit, or re-fetches a field it had discarded. Every one of those is a **partial state**.
- **Updating a row means setting a single attribute on an object that already exists**. If assignment triggered full validation, changing one field would have to satisfy the entire schema.

> [!important] Pydantic validates a **snapshot**, and a table object is never a snapshot. It is a long-lived thing the ORM keeps modifying, so the guarantee Pydantic offers does not fit it. Validation therefore lives at the **boundary** instead, on the non-table schemas, which genuinely are one-shot snapshots of data arriving from outside. That is not a workaround for a limitation — it is the pattern SQLModel's own documentation recommends.

One tempting explanation is worth ruling out, because it sounds right and isn't: that validation is off so rows read back from the database don't have to be re-checked.

**What `__init__` is.** When you write `ReviewTable(rating=5)`, Python runs a function called `__init__` on the new object. That is the setup function — and it is where Pydantic's validation happens. Validation is code sitting inside `__init__`.

**Two ways an object gets made.**

- You write `ReviewTable(rating=5)` yourself. `__init__` runs, so validation would run there.
- SQLAlchemy reads a row from disk and turns it into an object. It does **not** write `ReviewTable(rating=5)`. It makes an empty object and pushes the values straight into it, skipping `__init__` completely.

That second path goes underneath the setters too. Give the class a `__setattr__` and watch: building one yourself fires it for every field, while loading a row fires it for nothing at all — the values are simply written into the object's attribute dictionary directly. Setters work normally afterwards; it is specifically the loading step that bypasses everything.

**So what?** Validation lives in `__init__`. SQLAlchemy never calls `__init__` when loading. Therefore rows coming back from the database were **never** being validated — not before the flag, not after. The flag changed nothing about reading, which is why the reason for it has to be the **write** path, where your own code is holding a half-built row.

### If the annotations are not validating, what are they doing?

> [!note] They are **defining the columns**. The annotations are precisely what SQLModel hands to SQLAlchemy to build the table with:
>
> ```
> CREATE TABLE reviewtable (
> 	id INTEGER NOT NULL, 
> 	play_name VARCHAR NOT NULL, 
> 	reviewer_name VARCHAR NOT NULL, 
> 	rating INTEGER NOT NULL, 
> 	comment VARCHAR NOT NULL, 
> 	created_at DATETIME NOT NULL, 
> 	PRIMARY KEY (id)
> )
> ```
>
> `play_name: str` became `VARCHAR NOT NULL`, `rating: int` became `INTEGER`, `created_at: datetime` became `DATETIME`. Those `NOT NULL` constraints came from the annotations not being optional, and the database genuinely enforces them — `ReviewTable(play_name=None)` builds fine in Python and then fails at commit with `IntegrityError: NOT NULL constraint failed: reviewtable.play_name`. Enforcement didn't disappear; it moved to a later moment and a different layer.
>
> Which is exactly why `rating=99` survives and `play_name=None` doesn't. A type annotation has somewhere to go in SQL, so it becomes a column and keeps its teeth. `ge=1, le=5` has nowhere to go, so it evaporates. The same annotation therefore means two different things depending on one keyword: a **validation rule** without `table=True`, a **column definition** with it.

---

## Reference — two things to look up, not to read straight through

Both of these are mechanical rather than conceptual. They interrupt the argument above if read in sequence, so they live here.

> [!note]- `Field(...)` — one function serving two different jobs
> `Field` carries two kinds of information at once, because SQLModel's fields are genuinely Pydantic fields underneath. Which of the two actually does anything depends on `table=True`.
>
> **Database-level metadata**, which only means something when `table=True`:
>
> ```python
> id: Optional[int] = Field(default=None, primary_key=True)
> play_name: str = Field(index=True)
> ```
>
> - `primary_key=True` — marks this column as the table's primary key
> - `index=True` — creates a database index on this column, so filtering or searching on it is fast
> - `default=...` — the column's default value if none is provided
>
> **Validation constraints**, the same Pydantic power seen in earlier field-validator work, just expressed differently here:
>
> ```python
> rating: int = Field(ge=1, le=5)
> ```
>
> `ge` (greater than or equal) and `le` (less than or equal) enforce a numeric range directly through `Field`, without writing a custom `@field_validator` — for a constraint this simple, `Field` alone is enough.
>
> The two halves are not equally alive. Per the `table=True` section above, the validation half enforces nothing on a class **with** `table=True`; written on the table class, `ge=1, le=5` is documentation of intent and nothing more. On a class without the flag, it is the real check.

> [!note]- `default` vs. `default_factory` — a real, easy-to-miss gotcha
> ```python
> created_at: datetime = Field(default_factory=datetime.now)
> ```
>
> `default_factory` takes a **callable**, not a value — `datetime.now` here, not `datetime.now()`. The distinction matters a great deal.
>
> Writing `Field(default=datetime.now())` — calling the function immediately, with parentheses — would evaluate `datetime.now()` **once**, at the moment the class body executes, when the module is first imported. That single frozen timestamp then becomes the default for every row ever created afterwards, so every review would show the same **created at** time: whenever the server happened to start up.
>
> `default_factory=datetime.now` — no parentheses — hands SQLModel the function itself, to be called **fresh, every time a new row needs a default**, producing a genuinely different timestamp per row.
>
> This is the same category of trap as Python's well-known mutable-default-argument gotcha (`def f(x, lst=[])`), just showing up in a different place.

---

## Recall

Answers hidden. Try to produce each one before opening it.

> [!question]- Before SQLModel, why did one table need three class definitions — and which two of them were describing the same thing?
> A SQLAlchemy table class, a Pydantic create schema, and a Pydantic read schema. The table class and the **read** schema were mirrors — same six fields, same six meanings, written once in `Column(...)` syntax and once in annotation syntax, purely because neither library can read the other's classes. The create schema was different on purpose and would exist in any world.

> [!question]- Why can't one Pydantic class handle both the request and the response by marking `id` and `created_at` optional?
> Because **optional means allowed to be absent, never forbidden.** A request carrying `"id": 1` and a 1999 timestamp would pass validation, letting a client pick its own row id and fabricate a creation time. The **absence** of `id` from the incoming schema is the only thing making it impossible to send one.

> [!question]- What exactly does SQLModel remove, and what does it not remove?
> It removes the **accidental** duplication — one table described twice in two libraries' syntaxes and hand-synced forever. It does not remove the **meaningful** duplication, because storage shape and API shape genuinely differ. Concretely: when the read shape matches the stored shape, three classes become two; when a column has to be hidden, it stays at three. SQLModel doesn't reduce the classes you need — it removes the one you never needed.

> [!question]- `ReviewCreate(rating=99)` and `ReviewTable(rating=99)` carry the identical `Field(ge=1, le=5)`. What happens on each line?
> `ReviewCreate` raises a `ValidationError`. `ReviewTable` builds without complaint and holds a rating of 99, because `table=True` switches validation off.

> [!question]- Why is validation switched off on a table class? Give the reason, not just the fact.
> Because a table object is **mutable and usually incomplete**: it has no `id` before insert, the ORM writes its attributes one at a time while loading and refreshing, and updating a row means setting a single attribute on an object that already exists. Pydantic validates a **snapshot**, and a table object is never a snapshot — so validation moves to the boundary schemas, which genuinely are one-shot snapshots of data arriving from outside.

> [!question]- If the annotations on a table class aren't validating anything, what are they doing — and why does `rating=99` get through while `play_name=None` doesn't?
> They are **defining the columns**. `play_name: str` becomes `VARCHAR NOT NULL`, `rating: int` becomes `INTEGER`. A type annotation has somewhere to go in SQL, so it becomes a column and keeps its teeth — the database rejects `play_name=None` at commit with an `IntegrityError`. `ge=1, le=5` has nowhere to go in SQL (SQLModel emits no `CHECK` constraint), so it evaporates entirely.

> [!question]- Where is a rating of `99` actually stopped, then?
> At the door and nowhere else — `POST /reviews` accepts a `ReviewCreate`, and that class validates. Write one route that builds a `ReviewTable` straight from raw input and there is nothing left to stop it: no error, no warning, a `99` in the database. The table class is storage; the schemas are the validation.
