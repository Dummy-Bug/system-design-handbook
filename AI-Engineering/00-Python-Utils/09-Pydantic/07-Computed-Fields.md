Every field seen so far is something the **caller** supplies — a username, an age, a password. A computed field is the opposite: a value **derived from other fields on the same model**, that the caller never provides directly and that still shows up in the model's output as if it were an ordinary field.

```python
from pydantic import BaseModel, computed_field

class User(BaseModel):
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    follower_count: int = 0

    @computed_field
    @property
    def display_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @computed_field
    @property
    def is_influencer(self) -> bool:
        return self.follower_count >= 10000
```

Two decorators stack here, and each does a different job:
>`@property` is plain Python — it turns the method into something accessed as `user.display_name`, no parentheses, **computed fresh from the model's current field values every time it's read**. 
>`@computed_field` is the Pydantic-specific part on top — it tells Pydantic's serialization machinery **this property counts as a field too**, so it shows up in `model_dump()` and `model_dump_json()` output alongside every ordinary field, without the caller ever having supplied it.

> [!important] The method name becomes the field's name in output. 
> A property named `calculate_bmi` shows up in the dumped dict as `"calculate_bmi"`, not `"bmi"` — there's no separate renaming step. Name the method exactly what the output field should be called.

Given `User(first_name="Corey", last_name="Schafer", username="coreyms", follower_count=500)`:

```python
print(user.display_name)   # "Corey Schafer"
print(user.is_influencer)  # False
```

And `model_dump_json(indent=2)` includes both `display_name` and `is_influencer` in the output right alongside the real fields — despite neither ever having been part of the constructor call. That's the whole value of a computed field over just calling a regular method when needed: it participates in serialization automatically, so anything consuming the JSON — a frontend, another service, a log — gets the derived value for free without needing to know it was derived at all.
