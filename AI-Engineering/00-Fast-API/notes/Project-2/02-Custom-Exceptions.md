The general exception-class-plus-handler pattern, applied to the two failure modes this project's flow already planned: a well-formed pin code that isn't in the data, and a pin code that's malformed to begin with.

```python
class PinCodeNotFoundError(Exception):
    def __init__(self, pin_code: str):
        self.pin_code = pin_code


class InvalidPinCodeError(Exception):
    def __init__(self, pin_code: str, reason: str = "Invalid pin code format"):
        self.pin_code = pin_code
        self.reason = reason
```

Both carry exactly what their handler will need to build a useful message — the pin code itself in both cases, and a `reason` on the invalid one, defaulted so it doesn't have to be specified every time it's raised.

```python
from fastapi import Request
from fastapi.responses import JSONResponse


async def pincode_not_found_handler(request: Request, exc: PinCodeNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "pincode_not_found",
            "message": f"No location found for pin code {exc.pin_code}",
            "pin_code": exc.pin_code,
        },
    )


async def invalid_pincode_handler(request: Request, exc: InvalidPinCodeError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_pincode",
            "message": f"Pin code {exc.pin_code} is invalid: {exc.reason}",
            "pin_code": exc.pin_code,
        },
    )
```

The status codes match the flow planned in the client-briefing note exactly: `404` when the pin code was well-formed but not found in the data, `400` when it never should have reached a lookup at all. Both handlers return the same three keys — `error`, `message`, `pin_code` — a small deliberate consistency: whichever of the two failure modes a caller hits, the response has a predictable, identically-shaped body to parse.

Both classes and both handlers live in one file, `exceptions.py` — the convention this whole pattern follows, keeping "what went wrong" and "how it becomes a response" next to each other rather than scattered across the app.

Neither handler is wired up yet. A `PinCodeNotFoundError` raised right now would still crash as an unhandled exception — the handler functions exist, but nothing has told FastAPI to route that exception type to them. That registration happens in `main.py`, next.
