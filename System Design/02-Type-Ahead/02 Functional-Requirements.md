
### 1. Autocomplete Suggestions

- System must return typeahead suggestions for a given prefix.

- Suggestions should update as the user types.

---

### 2. Ranking by Popularity

- Return **top 10 results** sorted by query frequency.
    
- Ranking based on:
    
    - Historical search count.
       
    - Recency boost(out of scope).
      
    - Optional personalization weight(out of scope).
      

---

### 3. Prefix Length Constraints

- Autocomplete should trigger only when:
    

```
3 <= prefix length <= 20
```

Reasons:
- Avoid useless single-character queries.
- Prevent excessive backend load.
- Improve signal quality.

---

### 4. Personalized Suggestions (Optional Advanced Feature)

- Results should adapt to user context:
    
    - Location.
      
    - Search history.
      
    - Language.
      
    - Device signals.
      

Note:  
This is primarily an ML ranking problem layered on top of base retrieval.

---

### 5. Query Types

There are two distinct request types:

---

#### Typeahead Query (Read Path)

Triggered when user types in search box.

Example:

```
"par"
```

Purpose:

- Fetch suggestions.
- Read-heavy.
- Latency sensitive.

---

#### Search Submission Query (Write Path)

Triggered when user clicks a suggestion or submits search.

Example:

```
"paris city cost of living"
```

Purpose:

- Update popularity counters.
- Feed ranking pipeline.
- Write-heavy.

---

## Client-Side Optimization

---

### Debouncing

To avoid sending requests on every keystroke:

- Client must debounce input events.

Example policy:

```
Debounce interval: 250ms
```

Behavior:

- User types continuously → no request sent.
- User pauses typing → request triggered.

Benefits:

- Reduces QPS.
- Prevents backend overload.
- Improves perceived responsiveness.

---

### Additional Client Guards

- Cancel in-flight requests when new keystroke arrives.
- Do not send request if prefix length < 3.
- Cache last prefix response locally.
---
