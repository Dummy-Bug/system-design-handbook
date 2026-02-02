#backend #pydantic #serialization #fastapi #api-design #engineering-principles


Related:
- [[01 Model-Dump]]
- [[02 Json-Dump]]

## `model_dump()`

Returns a **Python dictionary**

### Example

```python
u = User(id=1, name="Laxy")

result = u.model_dump()
print(result)
```

Output:

```python
{'id': 1, 'name': 'Laxy'}
```

Type:

```python
dict
```

You can modify it:

```python
result["id"] = 2
```

---

## `model_dump_json()`

Returns a **JSON string**

### Example

```python
result = u.model_dump_json()
print(result)
```

Output:

```json
{"id":1,"name":"Laxy"}
```

Type:

```python
str
```

You CANNOT do:

```python
result["id"] = 2   # ❌ crash
```

Because it is a string, not a dict.

---

# Relationship between them

This:

```python
u.model_dump_json()
```

Is basically:

```python
json.dumps(u.model_dump(mode="json"))
```

First convert → then encode.

---

# When to use what (real life)

---

## Case 1: FastAPI

### Code

```python
return user.model_dump()
```

Why?

Because FastAPI already converts dict → JSON.

If you use `model_dump_json()` here you DOUBLE encode and break response.

---

## Case 2: Sending HTTP request

```python
payload = user.model_dump(mode="json")

requests.post(url, json=payload)
```

Why?

Because requests expects a **dict**, not a JSON string.

---

## Case 3: Logging or saving file

```python
with open("data.json", "w") as f:
    f.write(user.model_dump_json())
```

Why?

Because file needs a string.

---

# PATCH update example (real backend case)

User sends:

```json
{
  "name": "Laxy"
}
```

Your model:

```python
class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
```

Parsed:

```python
u = UserUpdate(name="Laxy")
```

Now dump:

---

### WRONG

```python
u.model_dump()
```

Output:

```python
{
 'name': 'Laxy',
 'age': None
}
```

This will overwrite `age` in DB to NULL. Bug.

---

### CORRECT

```python
u.model_dump(exclude_unset=True, exclude_none=True)
```

Output:

```python
{
 'name': 'Laxy'
}
```

Only update what user sent.

---

# Final simple cheat sheet

Memorize this:

```
model_dump()           -> dict
model_dump_json()      -> JSON string

mode="json"            -> converts datetime, UUID, Decimal

exclude_unset=True     -> user provided fields only
exclude_none=True      -> remove nulls
by_alias=True          -> use API field names
```

---

## Common Production Mistakes

- Using model_dump_json() inside FastAPI return statements
- Passing model_dump_json() into requests.post(json=...)
- Forgetting exclude_unset on PATCH endpoints
- Accidentally nulling DB columns via default None values

