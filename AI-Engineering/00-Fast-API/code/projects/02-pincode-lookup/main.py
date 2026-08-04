from fastapi import FastAPI

from data import PINCODE_DB
from models import LocationResponse, BulkRequest, BulkResponse
from exceptions import (
    PinCodeNotFoundError,
    pincode_not_found_handler,
    InvalidPinCodeError,
    invalid_pincode_handler,
)

app = FastAPI(
    title="Pincode Lookup API",
    description="Autofill city and state from Indian pincode during checkout.",
)

app.add_exception_handler(PinCodeNotFoundError, pincode_not_found_handler)
app.add_exception_handler(InvalidPinCodeError, invalid_pincode_handler)


@app.get("/")
def root():
    return {"message": "Pincode Lookup API"}


@app.get("/pincode/{code}", response_model=LocationResponse)
def lookup_pincode(code: str):
    if len(code) != 6 or not code.isdigit():
        raise InvalidPinCodeError(code, "Pin code must be exactly 6 digits")

    if code not in PINCODE_DB:
        raise PinCodeNotFoundError(code)

    return PINCODE_DB[code]


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
