#backend #langgraph #hitl #state-management #serialization #distributed-systems

---

LangGraph workflows support **human-in-the-loop (HITL)** interactions using `interrupt()`.

However, the return type of `interrupt()` is **not consistent across executions**:

- First execution → returns Python objects
- Resume execution → returns serialized JSON strings

If this difference is not handled correctly:

- Resume crashes occur
    
- State becomes corrupted
    
- Workflow replay becomes unstable
    

This note documents the correct handling pattern.

---

## Behavior Of interrupt()

---

### First Execution (Fresh Run)

When the graph pauses:

```python
user_inputs = interrupt(payload)
```

Return type:

```
dict[str, Any]
```

Example:

```python
{
  "username": "alex",
  "email": "alex@example.com"
}
```

This is a **direct in-memory Python object**.

---

### Resume Execution (After Pause)

When workflow resumes:

```python
Command(resume='{"values": {...}}')
```

LangGraph passes:

```
str (JSON encoded)
```

Example:

```json
"{\"values\":{\"username\":\"alex\",\"email\":\"alex@example.com\"}}"
```

This happens because:

- Resume data crosses persistence boundaries
    
- State is serialized
    
- Transport format becomes string
    

---

## Why This Happens

LangGraph execution model:

```
Live execution → Python objects
Checkpoint storage → Serialized JSON
Resume execution → Rehydrated string payload
```

This behavior is expected in resumable systems.

It is not a bug.

---

## Required Normalization Pattern

### Always Normalize interrupt Output

Immediately after:

```python
user_inputs = interrupt(payload)
```

You MUST normalize the data.

---

### Step 1 — Deserialize If String

```python
if isinstance(user_inputs, str):
    user_inputs = json.loads(user_inputs)
```

---

### Step 2 — Flatten Wrapped Resume Payload

LangGraph resume wraps values inside:

```json
{
  "values": {...}
}
```

Normalize this:

```python
if isinstance(user_inputs, dict) and "values" in user_inputs:
    user_inputs = user_inputs["values"]
```

---

### Final Invariant

After normalization:

```
user_inputs is ALWAYS dict[str, Any]
```

This invariant must hold before using the data.

## Correct Mental Model

### interrupt() Return Type Is Context Dependent

```
Fresh run    → Python object
Resume run   → Serialized string
```

Therefore:

> interrupt() output must always be normalized before use.
---

## Recommended Pattern (Canonical)

Always apply this pattern:

```python
user_inputs = interrupt(payload)

if isinstance(user_inputs, str):
    user_inputs = json.loads(user_inputs)

if isinstance(user_inputs, dict) and "values" in user_inputs:
    user_inputs = user_inputs["values"]
```

---

## Mental Model To Remember

`interrupt() Is A Serialization Boundary`

Anything crossing it must be normalized.