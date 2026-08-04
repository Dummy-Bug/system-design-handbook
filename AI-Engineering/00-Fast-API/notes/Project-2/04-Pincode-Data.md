The same constraint as project 1 — no database — so a data file stands in for one again.

```python
PINCODE_DATA = {
    "110001": {"city": "New Delhi", "state": "Delhi", "district": "Central Delhi"},
    "400001": {"city": "Mumbai", "state": "Maharashtra", "district": "Mumbai City"},
    # ...a handful more, covering a few states
}
```

One deliberate structural difference from project 1's menu data: this is a **dictionary keyed by pin code**, not a list of dictionaries. That choice isn't arbitrary — it's what makes the lookup itself trivial. Finding a pin code is `PINCODE_DATA.get("110001")`, a constant-time dictionary lookup, rather than looping through a list checking each entry's `id` field the way `/menu/{item_id}` had to. The shape of the data was chosen specifically because of how it's going to be searched.

Coverage is intentionally partial — a handful of real Indian pin codes across a few states and cities, not a complete national dataset. This is the same "file instead of database" stand-in as before: in a real version of this service, this data would come from an external pin code API or a proper database table, queried rather than hardcoded. The point of the file is to prove the lookup logic works, not to be exhaustive.

That partial coverage is also *why* the "not found" case matters as much as it does here — asking for a real, valid-looking pin code that simply isn't in this small dataset is the expected common case, not an edge case.
