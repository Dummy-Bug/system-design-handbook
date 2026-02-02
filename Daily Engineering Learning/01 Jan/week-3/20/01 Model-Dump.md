#backend #pydantic #serialization #api-design #data-validation #engineering-principles


`model_dump` is a **Pydantic method** used to convert a Pydantic model instance into a **plain Python dictionary**.

It exists in **Pydantic v2**. In v1 this was called `dict()`.

### What it does

It takes your validated model object and serializes it into native Python types:

- `BaseModel` → `dict`
    
- Nested models → nested dicts
    
- Enums → values
    
- Datetime → datetime objects (or strings if you ask for JSON mode)
    

### Basic example

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

u = User(id=1, name="Laxy")

data = u.model_dump()
print(data)
```

Output:

```python
{'id': 1, 'name': 'Laxy'}
```

Type:

```python
type(data)  
```

### Why it exists

Pydantic models are not normal dicts. Many libraries expect raw Python objects:

- JSON serialization
    
- Database inserts
    
- API payloads
    
- Logging
    
- Caching
    

`model_dump()` gives you a clean, dependency-free structure.


---

# 1. `exclude_unset=True`

**Meaning**  
Removes fields that were **not provided during object creation**. Defaults do not count as “set”.

### Example

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str = "anonymous"
    age: int | None = None

u = User(id=1)
```

### Normal dump

```python
u.model_dump()
```

Output:

```python
{
    'id': 1,
    'name': 'anonymous',
    'age': None
}
```

### With `exclude_unset=True`

```python
u.model_dump(exclude_unset=True)
```

Output:

```python
{
    'id': 1
}
```

### Why this matters

PATCH APIs only send fields the user updated.

Client sends:

```json
{ "name": "Laxy" }
```

You don't want to overwrite `age` or `id`.  
So you dump only what was explicitly set.

---

# 2. `exclude_none=True`

**Meaning**  
Removes fields whose value is `None`.  
Does NOT care whether field was set or defaulted.

### Example

```python
u = User(id=1, name="Laxy", age=None)
```

### Normal dump

```python
u.model_dump()
```

Output:

```python
{
    'id': 1,
    'name': 'Laxy',
    'age': None
}
```

### With `exclude_none=True`

```python
u.model_dump(exclude_none=True)
```

Output:

```python
{
    'id': 1,
    'name': 'Laxy'
}
```

### Brutal truth

- `exclude_unset` = remove fields not provided
    
- `exclude_none` = remove fields whose value is None
    
- They solve **different problems**
    

---

# Combine both (common in production)

```python
u.model_dump(exclude_unset=True, exclude_none=True)
```

This gives you:

- Only fields user touched
    
- No null garbage
    

---

# 3. `by_alias=True`

**Meaning**  
Uses external field names instead of Python variable names.

### Example

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: int = Field(alias="userId")
    full_name: str = Field(alias="fullName")

u = User(userId=10, fullName="Laxy Dev")
```

### Normal dump

```python
u.model_dump()
```

Output:

```python
{
    'user_id': 10,
    'full_name': 'Laxy Dev'
}
```

### With alias

```python
u.model_dump(by_alias=True)
```

Output:

```python
{
    'userId': 10,
    'fullName': 'Laxy Dev'
}
```

### Why this exists

Python style:

```python
user_id
```

JSON / frontend style:

```json
userId
```

This avoids manual mapping. It is essential for REST APIs.

