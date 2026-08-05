A field's type doesn't have to be a primitive like `str` or `int` — it can be **another Pydantic model**. Once that's true, models can be composed: a `BlogPost` that contains a full `User` as its author, and a list of `Comment` objects, each of which is its own validated model.

## Why not just a dict or a string?

Consider an address. The tempting shortcut is a single string: `"123 Main St, Gurgaon, Haryana, 122001"`. That works until something downstream needs just the city, or just the pin code — now it's string-parsing a loosely-structured blob every time, with no guarantee the format is even consistent across records. The better shape is a model of its own:

```python
class Address(BaseModel):
    city: str
    state: str
    pin_code: str
```

...used as a field type on whatever model needs an address:

```python
class Patient(BaseModel):
    name: str
    address: Address
```

## Nested models validate recursively

```python
class Comment(BaseModel):
    content: str
    author_email: EmailStr
    likes: int = 0

class BlogPost(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    content: Annotated[str, Field(min_length=10)]
    author: User
    comments: list[Comment] = Field(default_factory=list)
```

Constructing a `BlogPost` means every nested model gets checked too — the `author` field has to pass every validation rule the `User` model declares (constraints, custom validators, everything from the earlier notes), and every item in `comments` has to independently pass `Comment`'s rules. One `model_validate(...)` call, full validation top to bottom:

```python
post_data = {
    "title": "Hello, World",
    "content": "This is my very first blog post.",
    "slug": "hello-world",
    "author": {
        "username": "coreyms",
        "email": "CoreyMSchafer@gmail.com",
        "password": "secret123",
        "age": 39,
    },
    "comments": [
        {"content": "Great post!", "author_email": "reader@example.com", "likes": 3},
    ],
}

post = BlogPost(**post_data)
```

`BlogPost.model_validate(post_data)` does the identical thing without unpacking — both forms exist; `model_validate` reads more clearly when the data is already a dict rather than being assembled inline.

The dumped output (`post.model_dump_json(indent=2)`) mirrors the input's nested shape exactly — `author` comes back as a full nested `User` object (password still masked as `SecretStr`, any computed fields on `User` present too), `comments` as a list of full `Comment` objects — not references or IDs, but the complete validated sub-models.

## What this buys over one flat model

- **Structure matches the actual data.** An address, a comment, an author aren't flat key-value pairs conceptually — modeling them as their own type keeps the shape honest.
- **Reuse.** `Address` written once works for a `Patient`, an `Employee`, a `Shipment` — anything that has one.
- **Validation composes for free.** Nothing extra is written to validate the nested pieces — declaring the field as `Address` (or `User`, or `list[Comment]`) is the entire validation rule for that piece of the structure.
