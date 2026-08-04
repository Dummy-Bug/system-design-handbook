from fastapi import Request
from fastapi.responses import JSONResponse


class PinCodeNotFoundError(Exception):
    def __init__(self, pin_code: str):
        self.pin_code = pin_code


class InvalidPinCodeError(Exception):
    def __init__(self, pin_code: str, reason: str = "Invalid pin code format"):
        self.pin_code = pin_code
        self.reason = reason


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
