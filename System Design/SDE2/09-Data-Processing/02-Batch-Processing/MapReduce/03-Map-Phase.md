
## What Map Does

Map reads each line of its local data chunk and emits a `(key, value)` pair for it.

That's it. **No counting. No memory of previous lines. Just labeling.**

Each line is processed in isolation. Map doesn't know what other machines are doing. It doesn't know how many times a key has appeared before.

---

## Example: Error Log Count

Input file on Machine 1:
```
ERROR_404
ERROR_500
ERROR_404
ERROR_404
ERROR_500
```

Map function rule: for each line, emit `(error_code, 1)`.

```
line 1: ERROR_404  →  (ERROR_404, 1)
line 2: ERROR_500  →  (ERROR_500, 1)
line 3: ERROR_404  →  (ERROR_404, 1)
line 4: ERROR_404  →  (ERROR_404, 1)
line 5: ERROR_500  →  (ERROR_500, 1)
```

Output — 5 `(key, value)` pairs written to **local disk**.

The value is always `1` in the basic version. It means: "I saw this key once on this line."

---

## Why Not Count Locally?

Map sees line 3 (`ERROR_404`) in isolation. It doesn't know that line 1 was also `ERROR_404`. It has no shared counter.

Map just says: **"I saw ERROR_404 here."**

Think of it like survey forms — each person fills one form saying "I chose option X". Nobody tallies yet. You collect all forms first, then count. Map is filling out the form.

---

## At Scale

```
1000 machines × 1M lines each = 1 billion (key, value) pairs total
```

Each machine writes its pairs to its own local disk. Nothing is sent over the network yet.

```
Machine 1 disk:   (ERROR_404, 1), (ERROR_500, 1), (ERROR_404, 1) ...
Machine 2 disk:   (ERROR_500, 1), (ERROR_404, 1), (ERROR_503, 1) ...
Machine 3 disk:   (ERROR_404, 1), (ERROR_503, 1), (ERROR_500, 1) ...
...
```

All 1 billion pairs sit on disk, waiting for Shuffle.

---

## The Map Function (Code)

```python
def map(line):
    error_code = line.strip()
    emit(error_code, 1)
```

You write this. The framework calls it on every line, on every machine, in parallel.
