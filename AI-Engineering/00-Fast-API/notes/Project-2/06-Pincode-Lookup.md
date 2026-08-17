The field-validator pattern applied to this project's actual request and response shapes — a single-lookup pair and a bulk-lookup pair.

```python
from pydantic import BaseModel, field_validator


class PinCodeRequest(BaseModel):
    pin_code: str

    @field_validator("pin_code")
    @classmethod
    def validate_pin_code(cls, value: str) -> str:
        if len(value) != 6 or not value.isdigit():
            raise ValueError("Pin code must be exactly 6 digits")
        return value


class LocationResponse(BaseModel):
    pin_code: str
    city: str
    state: str
    district: str
```

`PinCodeRequest` is the incoming shape — one field, validated by exactly the pattern from the previous note. `LocationResponse` is what comes back on a successful lookup: no validation logic of its own, since this data is coming **out** of the trusted `PINCODE_DB` dictionary rather than arriving untrusted from a caller — there's nothing here that needs checking, only declaring.

---

## Bulk lookup

```python
class BulkRequest(BaseModel):
    pin_codes: list[str]

    @field_validator("pin_codes")
    @classmethod
    def validate_pin_codes(cls, values: list[str]) -> list[str]:
        if len(values) == 0:
            raise ValueError("At least one pin code is required")
        if len(values) > 20:
            raise ValueError("Maximum 20 pin codes allowed per request")

        for code in values:
            if len(code) != 6 or not code.isdigit():
                raise ValueError("Each pin code must be exactly 6 digits")

        return values


class BulkResponse(BaseModel):
    status: str = "success"
    found: int
    not_found: int
    results: list[LocationResponse]
    missing: list[str]
```

The 20-item cap in `BulkRequest`'s validator is an arbitrary limit, not derived from any real capacity constraint — picked the same way a lot of list/page-size limits get picked in practice, as a round number that feels reasonable rather than one backed by a specific measurement.

`BulkResponse` is where the **some found, some not** reality of a bulk request actually gets represented:

| Field | What it holds |
|---|---|
| `status` | Defaults to `"success"` — the request as a whole succeeded, independent of whether every individual pin code was found |
| `found` | Count of pin codes that matched something in `PINCODE_DB` |
| `not_found` | Count that didn't |
| `results` | The actual `LocationResponse` data for every pin code that **was** found |
| `missing` | The raw pin codes that weren't — so the caller knows exactly which ones to investigate, not just how many |

This is the bulk equivalent of the single-lookup 404: rather than one bad pin code failing an entire batch request, the response separates what succeeded from what didn't and reports both, in full, in one response. A caller sending 20 pin codes where only 15 exist gets all 15 results **and** the exact 5 that came up empty, in the same call.
