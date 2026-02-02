#backend #json #serialization #api-design #data-encoding #engineering-principles


### First understand the core problem

Python has types that **JSON does not understand**.

Example:

```python
datetime
UUID
Decimal
set
```

JSON only supports:

- string
    
- number
    
- boolean
    
- null
    
- list
    
- object (dict)
    

So this FAILS:

```python
import json
json.dumps(datetime.now())
```

Error:

```
TypeError: Object of type datetime is not JSON serializable
```

This is the root problem.

---

### What `mode="json"` actually does

It **converts Python-only objects into plain JSON-friendly values**.

Think of it as:

> "Make everything safe to send over the internet."

---

### Example without `mode="json"`

#### Code

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class Event(BaseModel):
    time: datetime
    event_id: UUID

e = Event(
    time=datetime(2026, 1, 20, 10, 30),
    event_id=UUID("12345678123456781234567812345678")
)

data = e.model_dump()
print(data)
```

#### Output

```python
{
 'time': datetime.datetime(2026, 1, 20, 10, 30),
 'event_id': UUID('12345678-1234-5678-1234-567812345678')
}
```

These are **real Python objects**, not strings.

Now try sending this as JSON:

```python
import json
json.dumps(data)
```

#### Result

CRASH:

```
TypeError: Object of type datetime is not JSON serializable
```

Because JSON has no idea what `datetime` or `UUID` is.

---

### Same example WITH `mode="json"`

#### Code

```python
data = e.model_dump(mode="json")
print(data)
```

#### Output

```python
{
 'time': '2026-01-20T10:30:00',
 'event_id': '12345678-1234-5678-1234-567812345678'
}
```

Now notice:

- datetime → string
    
- UUID → string
    

Now this works:

```python
json.dumps(data)
```

No crash.

---

### Simple mental model

#### Without json mode

You get:

```
Python objects
```

#### With json mode

You get:

```
Internet-safe primitives
```

---

## Production Rule

Never pass raw Pydantic dumps with datetime or UUID directly into json.dumps().
Always use mode="json" or model_dump_json() before crossing network or storage boundaries.

