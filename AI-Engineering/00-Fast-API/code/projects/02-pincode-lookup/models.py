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
