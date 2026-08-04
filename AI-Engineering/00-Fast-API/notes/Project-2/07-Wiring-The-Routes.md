Everything built across this project — the data file, the models, the exception classes and handlers — gets wired together into two working routes.

---

## Registering the handlers

```python
from fastapi import FastAPI
from exceptions import (
    PinCodeNotFoundError, pincode_not_found_handler,
    InvalidPinCodeError, invalid_pincode_handler,
)

app = FastAPI()

app.add_exception_handler(PinCodeNotFoundError, pincode_not_found_handler)
app.add_exception_handler(InvalidPinCodeError, invalid_pincode_handler)
```

This is the registration step the exceptions note ended on without resolving — the two custom exceptions and their handlers only start actually doing anything from this point on.

---

## `GET /pincode/{code}` — single lookup by path parameter

```python
from fastapi import FastAPI
from models import LocationResponse
from data import PINCODE_DB


@app.get("/pincode/{code}", response_model=LocationResponse)
def lookup_pincode(code: str):
    if len(code) != 6 or not code.isdigit():
        raise InvalidPinCodeError(code, "Pin code must be exactly 6 digits")

    if code not in PINCODE_DB:
        raise PinCodeNotFoundError(code)

    return PINCODE_DB[code]
```

> [!important] Worth being precise about *why* this manual check exists here, since it's easy to assume it's redundant with the `field_validator` already written. **It isn't.** 
> `PinCodeRequest`'s field validator only runs when a request body is validated against that model — and this route has no request body at all. `code: str` is a plain path parameter, exactly like `item_id: int` in the previous project: FastAPI extracts it and hands it over as-is, with no Pydantic model involved anywhere in that path. Nothing here has checked its shape before this line does. The manual `len(code) != 6` check isn't belt-and-suspenders caution — for this specific route, it's the *only* validation that exists.

The rest follows the same shape as `/menu/{item_id}` from the previous project: check the input is well-formed first (raising `InvalidPinCodeError` if not), then check it actually exists in the data (raising `PinCodeNotFoundError` if not), then return the match. `PINCODE_DB[code]` returns a plain dict — `response_model=LocationResponse` handles validating and shaping that dict into the declared response, the same conversion seen with `MenuResponse` in project 1.

**Tested live through Swagger's `/docs`, both outcomes:**

![[AI-Engineering/00-Fast-API/Images/pincode-single-happy.jpg]]

`GET /pincode/411001` — a valid, known pin code — comes back `200` with the full `LocationResponse` shape: city, state, district.

![[AI-Engineering/00-Fast-API/Images/pincode-single-notfound.jpg]]

`GET /pincode/999999` — well-formed but absent from `PINCODE_DB` — comes back `404`, with the exact body `pincode_not_found_handler` builds: `error`, `message`, and `pin_code` echoed back. This is `PinCodeNotFoundError` actually reaching its registered handler, not a generic FastAPI error page.

### Proof: what the exact same request looks like with no handler registered

The Foundations note on custom exceptions makes a specific claim: raising a custom exception with nothing listening for it produces a generic, unhandled `500`, not the formatted error body. Worth not taking on faith — tested directly, by temporarily commenting out both `app.add_exception_handler(...)` lines and sending the identical request as above, `GET /pincode/999999`:

![[AI-Engineering/00-Fast-API/Images/pincode-single-unhandled-500.jpg]]

Same input, same route, same `raise PinCodeNotFoundError(code)` line executing inside `lookup_pincode` — and the response is now `500 Internal Server Error`, `content-type: text/plain`, body just the literal string `Internal Server Error`. None of `pincode_not_found_handler`'s formatting — no `"error"` key, no `"message"`, no `"pin_code"` — because that function never ran. The exception was still raised correctly; there was simply nothing registered to catch that specific type and turn it into a response. The handler lines were restored immediately after, and the `404` behavior above confirmed working again before moving on.

---

## `POST /pincode/bulk` — many lookups from a request body

```python
from models import BulkRequest, BulkResponse


@app.post("/pincode/bulk", response_model=BulkResponse)
def bulk_lookup(request: BulkRequest):
    results = []
    missing = []

    for code in request.pin_codes:
        if code in PINCODE_DB:
            results.append(PINCODE_DB[code])
        else:
            missing.append(code)

    return {
        "found": len(results),
        "not_found": len(missing),
        "results": results,
        "missing": missing,
    }
```

`request: BulkRequest` is the first route in this course accepting a full **request body** rather than reading individual values off the URL. Declaring the parameter's type as `BulkRequest` is what tells FastAPI to parse the incoming JSON body against that model — `BulkRequest`'s own field validator (the 20-item cap, the empty-list check, the per-item 6-digit check) runs automatically the moment this route is hit, before a single line of `bulk_lookup`'s own body executes. Unlike the path-parameter route above, the validation genuinely has already happened here — this is the actual case the earlier assumption of "already checked by Pydantic" is true for.

Two small lists (`results`, `missing`) get built by looping once over `request.pin_codes`, and the function returns a **plain dict**, not a constructed `BulkResponse(...)` object — `response_model=BulkResponse` validates and converts that dict on the way out, the same mechanism as the single-lookup route above.

> [!important] **A route accepting a request body must be declared `@app.post(...)`, not `@app.get(...)`.** 
> The underlying reason traces back to the HTTP verbs note: 
> 
> `GET` is semantically a *read*, and isn't meant to carry a request body at all — clients and servers don't reliably support one. 
> 
> `POST` is the verb that expects a body. Getting this backwards doesn't fail loudly with an obvious message; it just quietly doesn't work the way it looks like it should.

**Tested live through Swagger's `/docs`, both outcomes:**

![[AI-Engineering/00-Fast-API/Images/pincode-bulk-happy-partial.jpg]]

`POST /pincode/bulk` with `{"pin_codes": ["411001", "560001", "999999"]}` — two real codes, one fake — comes back `200` with `found: 2`, `not_found: 1`, both real locations in `results`, and the one fake code named exactly in `missing`. No error, because a bulk request partially succeeding is the expected shape of a response here, not a failure — the client asked for three things and got told precisely which two worked and which one didn't.

![[AI-Engineering/00-Fast-API/Images/pincode-bulk-validation-error.jpg]]

`POST /pincode/bulk` with `{"pin_codes": []}` comes back `422` — **automatically**, before `bulk_lookup`'s own code ever runs. This is `BulkRequest`'s `field_validator` catching the empty-list case, exactly as described in the Pydantic field-validators note: raising `ValueError("At least one pin code is required")` inside the validator is what produces this structured `422` body, with that exact message under `"msg"`. No custom exception class or handler was involved in producing this one — it's Pydantic's own validation-error pipeline, doing its job before the route body executes at all.

---

## Path parameter vs. request body — the two ways in, side by side

| | `GET /pincode/{code}` | `POST /pincode/bulk` |
|---|---|---|
| Data travels in | The URL itself | The JSON request body |
| Declared as | A typed function parameter matching a `{placeholder}` | A parameter typed as a Pydantic model |
| Validated by | Whatever's manually written in the route (nothing else exists) | The model's own `field_validator`, automatically, before the route runs |
| Right verb for it | `GET` — appropriate for a single, simple lookup | `POST` — appropriate once the payload is structured and potentially large |

The practical rule of thumb this project leaves behind: small, simple, identifying values (an id, a code) belong in the path; anything shaped like a structured object — especially something that needs its own validation rules — belongs in the body, behind `POST`.
