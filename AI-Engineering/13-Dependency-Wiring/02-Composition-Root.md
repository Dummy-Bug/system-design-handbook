#dependency-injection #python #architecture #composition-root

**When a function stops reaching for what it needs, the need does not disappear.** The objects still have to exist before anything can use them. This note is about where they get made — and why the answer that turns out to work is a single place, at the start of the program, that makes all of them.

# Composition Root

> [!info] Three words used throughout. To **construct** an object is to call its class to make one, as in `SalaryService(salaries=...)`. **Wiring** is handing the objects that were constructed to the code that uses them. A **collaborator**, as in [[01-Hidden-Inputs]], is anything a function uses without having made it itself.

## If nobody fetches it, somebody has to build it

A request in a real service passes through layers: something receives the request, calls a tool, and the tool uses a service. Here are all three, each asking for what it needs on its `def` line and none of them reaching for anything.

`src/wiring_lab/note02/a_someone_has_to_build_it.py`:

```python
class SalaryService:
    def __init__(self, salaries: dict[str, int]) -> None:
        self.salaries = salaries

    def salary_for(self, employee_id: str) -> int:
        return self.salaries[employee_id]


def salary_tool(employee_id: str, salary_service: SalaryService) -> int:
    return salary_service.salary_for(employee_id)


def handle_request(employee_id: str, salary_service: SalaryService) -> str:
    return f"{employee_id} earns {salary_tool(employee_id, salary_service)}"


salary_service = SalaryService(salaries={"1000": 900_000})
print(handle_request("1000", salary_service))
```

```
$ uv run python src/wiring_lab/note02/a_someone_has_to_build_it.py

1000 earns 900000
```

`SalaryService` receives its salaries when it is constructed, instead of having them written inside it. The two functions receive the service. Follow the service back through the file and ask each layer one question — did you build it, or were you handed it:

| Where | Built the service, or was handed it | What it does with it |
|---|---|---|
| `salary_tool` | handed it by `handle_request` | calls `salary_for` on it |
| `handle_request` | handed it by the last two lines of the file | passes it on to `salary_tool` |
| the last two lines of the file | **built it** | passes it to `handle_request` |

Only one line in the file constructs a `SalaryService`, and it is the line that runs before anything else.

In the reaching version from the previous note, the tool fetched its service out of a shared dictionary, so the question of where the service came from was answered inside the tool. Once the tool asks for it instead, the tool cannot answer that question any more — and neither can `handle_request`, which also only asks. The question climbs one layer at a time until it reaches the only code that is not called by anything: the start of the program.

> [!important] Asking for collaborators moves construction, it does not remove it
> Every object a function asks for still has to be made by someone before that function runs. Taking collaborators as parameters takes that job away from the code that uses them and pushes it up to the place where the program starts.

## Build it in several places, and a change becomes a search

In the previous file exactly one line had to know that a `SalaryService` is built from a salaries dictionary: the line that builds it. The two functions only pass the finished object along.

A real service rarely has a single starting point, though. There is the web server, and usually also a job that runs on a schedule and a script somebody runs by hand. Each needs a `SalaryService`, and the easy thing is for each to build its own.

`src/wiring_lab/note02/b_built_in_three_places.py`:

```python
class SalaryService:
    def __init__(self, salaries: dict[str, int]) -> None:
        self.salaries = salaries

    def salary_for(self, employee_id: str) -> int:
        return self.salaries[employee_id]


def serve_web_request(employee_id: str) -> None:
    salary_service = SalaryService(salaries={"1000": 900_000})
    print("web request    ->", salary_service.salary_for(employee_id))


def run_nightly_report(employee_id: str) -> None:
    salary_service = SalaryService(salaries={"1000": 900_000})
    print("nightly report ->", salary_service.salary_for(employee_id))


def run_admin_script(employee_id: str) -> None:
    salary_service = SalaryService(salaries={"1000": 900_000})
    print("admin script   ->", salary_service.salary_for(employee_id))


serve_web_request("1000")
run_nightly_report("1000")
run_admin_script("1000")
```

```
$ uv run python src/wiring_lab/note02/b_built_in_three_places.py

web request    -> 900000
nightly report -> 900000
admin script   -> 900000
```

It works, and the three construction lines are identical. Each of them knows how a `SalaryService` is built.

Now the service changes: it has to report a currency, so its constructor needs one more thing. The developer making the change updates the constructor and the one starting point they were working in, the web request, and does not know about the other two.

`src/wiring_lab/note02/c_the_constructor_changes.py`:

```python
class SalaryService:
    def __init__(self, salaries: dict[str, int], currency: str) -> None:
        self.salaries = salaries
        self.currency = currency

    def salary_for(self, employee_id: str) -> str:
        return f"{self.salaries[employee_id]} {self.currency}"


def serve_web_request(employee_id: str) -> None:
    salary_service = SalaryService(salaries={"1000": 900_000}, currency="INR")
    print("web request    ->", salary_service.salary_for(employee_id))


def run_nightly_report(employee_id: str) -> None:
    salary_service = SalaryService(salaries={"1000": 900_000})
    print("nightly report ->", salary_service.salary_for(employee_id))


def run_admin_script(employee_id: str) -> None:
    salary_service = SalaryService(salaries={"1000": 900_000})
    print("admin script   ->", salary_service.salary_for(employee_id))


serve_web_request("1000")
run_nightly_report("1000")
run_admin_script("1000")
```

```
$ uv run ty check src/wiring_lab/note02/c_the_constructor_changes.py

error[missing-argument]: No argument provided for required parameter `currency` of `SalaryService.__init__`
  --> src/wiring_lab/note02/c_the_constructor_changes.py:32:22
   |
32 |     salary_service = SalaryService(salaries={"1000": 900_000})
   |                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
info: Parameter declared here
  --> src/wiring_lab/note02/c_the_constructor_changes.py:18:50
   |
18 |     def __init__(self, salaries: dict[str, int], currency: str) -> None:
   |                                                  ^^^^^^^^^^^^^

error[missing-argument]: No argument provided for required parameter `currency` of `SalaryService.__init__`
  --> src/wiring_lab/note02/c_the_constructor_changes.py:37:22
   |
37 |     salary_service = SalaryService(salaries={"1000": 900_000})
   |                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
info: Parameter declared here
  --> src/wiring_lab/note02/c_the_constructor_changes.py:18:50
   |
18 |     def __init__(self, salaries: dict[str, int], currency: str) -> None:
   |                                                  ^^^^^^^^^^^^^

Found 2 diagnostics
```

```
$ uv run python src/wiring_lab/note02/c_the_constructor_changes.py

web request    -> 900000 INR
Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note02/c_the_constructor_changes.py", line 42, in <module>
    run_nightly_report("1000")
    ~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note02/c_the_constructor_changes.py", line 32, in run_nightly_report
    salary_service = SalaryService(salaries={"1000": 900_000})
TypeError: SalaryService.__init__() missing 1 required positional argument: 'currency'
```

As in [[01-Hidden-Inputs]], each lab file's comment header is left out of the code shown here, which is why the line numbers in the output are larger than the code above them.

The web request — the one the developer checked — works. The nightly report crashes, and in production it would crash at night, when it runs.

| One change to how `SalaryService` is built | Count |
|---|---|
| places that build a `SalaryService` | 3 |
| updated by the developer | 1 |
| missed | 2 |
| found by the type checker before running | 2 |
| crash if it is run anyway | the first missed one reached |

The type checker found both missed lines here, because each is a named constructor call — the same reason a renamed parameter was caught in [[01-Hidden-Inputs]]. It found them; it did not make them unnecessary. **A change that belongs to one object still turned into three edits in three places**, and in a real codebase those places live in different files, owned by different people, some of them never opened by the person making the change.

> [!important] Scattered construction makes every change a search
> When several places build the same object, each of them holds a copy of how it is built. Changing that knowledge means finding every copy — a search across the codebase — rather than editing the one place the knowledge should have lived.

## One function builds it, and the starting points only receive it

The fix is to take construction out of the three starting points and give it one home: a single function whose only job is building the service. Each starting point then asks for the service on its `def` line, the way [[01-Hidden-Inputs]] ended.

`src/wiring_lab/note02/d_one_function_builds_it.py`:

```python
class SalaryService:
    def __init__(self, salaries: dict[str, int], currency: str) -> None:
        self.salaries = salaries
        self.currency = currency

    def salary_for(self, employee_id: str) -> str:
        return f"{self.salaries[employee_id]} {self.currency}"


def build_salary_service() -> SalaryService:
    print("building the salary service")
    return SalaryService(salaries={"1000": 900_000}, currency="INR")


def serve_web_request(employee_id: str, salary_service: SalaryService) -> None:
    print("web request    ->", salary_service.salary_for(employee_id))


def run_nightly_report(employee_id: str, salary_service: SalaryService) -> None:
    print("nightly report ->", salary_service.salary_for(employee_id))


def run_admin_script(employee_id: str, salary_service: SalaryService) -> None:
    print("admin script   ->", salary_service.salary_for(employee_id))


salary_service = build_salary_service()
serve_web_request("1000", salary_service)
run_nightly_report("1000", salary_service)
run_admin_script("1000", salary_service)
```

```
$ uv run python src/wiring_lab/note02/d_one_function_builds_it.py

building the salary service
web request    -> 900000 INR
nightly report -> 900000 INR
admin script   -> 900000 INR
```

The `print` inside `build_salary_service` is there to count: the service is built once and used three times. The line inside that function is now the only line in the file that knows a `SalaryService` needs salaries and a currency.

This file already contains the `currency` change that broke the previous one. Compare what the same change cost:

| Adding `currency` to the constructor | Scattered, `c_the_constructor_changes.py` | One function, this file |
|---|---|---|
| lines that construct a `SalaryService` | 3 | 1 |
| lines to edit | 3 | 1 |
| lines that can be missed | 2 were | none — there is only one |
| running it | web request worked, nightly report crashed | all three work |

> [!important] The pattern is called a composition root
> A **composition root** is the one place that builds the objects a program needs and decides which object goes to which piece of code. It runs once, when the program starts. Everything else asks for what it needs and never constructs a collaborator itself.

One detail the example compresses. In a real system the web server, the scheduled job and the hand-run script are **three separate programs**, and separate programs cannot share one object in memory. What they share is the function: each program calls `build_salary_service()` as the first thing it does. The knowledge of how the service is built still lives in exactly one place, which is the property that made the change a single edit. The lab puts all three starting points in one file only to keep the example small enough to read.

## The composition root is the only place that reads configuration

The build function above has two values written straight into it, and they are not the same kind of thing:

| Value | What kind of thing | Where it comes from in a real service |
|---|---|---|
| `"INR"` | a configuration value | the settings class, read from the environment when the program starts |
| `{"1000": 900_000}` | data | a database or an HR system's API — itself a collaborator that gets built, like `SalaryService` |

The examples keep the salaries as sample data and move only the currency, so one thing changes at a time.

There are two ways to get the currency from the settings into the service. The easy one is for the service to read the setting itself.

`src/wiring_lab/note02/e_settings_read_inside.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    currency: str = "INR"


settings = Settings()


class SalaryService:
    def __init__(self, salaries: dict[str, int]) -> None:
        self.salaries = salaries

    def salary_for(self, employee_id: str) -> str:
        return f"{self.salaries[employee_id]} {settings.currency}"


def build_salary_service() -> SalaryService:
    return SalaryService(salaries={"1000": 900_000})


salary_service = build_salary_service()
print("1000 ->", salary_service.salary_for("1000"))
```

```
$ uv run python src/wiring_lab/note02/e_settings_read_inside.py

1000 -> 900000 INR
```

```
$ CURRENCY=USD uv run python src/wiring_lab/note02/e_settings_read_inside.py

1000 -> 900000 USD
```

It works, and the environment variable changes it. But `salary_for` reaches for the module-level `settings` object — the hidden input from [[01-Hidden-Inputs]] again, this time holding configuration. Nothing on `SalaryService`'s constructor mentions a currency, so a `SalaryService` cannot be built with one. The only way to get a different currency is to change the environment of the whole running program, for every service at once.

The other way is for the build function to read the settings and hand the service a plain value.

`src/wiring_lab/note02/f_settings_read_in_the_root.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    currency: str = "INR"


class SalaryService:
    def __init__(self, salaries: dict[str, int], currency: str) -> None:
        self.salaries = salaries
        self.currency = currency

    def salary_for(self, employee_id: str) -> str:
        return f"{self.salaries[employee_id]} {self.currency}"


def build_salary_service(settings: Settings) -> SalaryService:
    return SalaryService(salaries={"1000": 900_000}, currency=settings.currency)


settings = Settings()
salary_service = build_salary_service(settings)
print("from settings  ->", salary_service.salary_for("1000"))

usd_service = SalaryService(salaries={"1000": 10_800}, currency="USD")
print("built directly ->", usd_service.salary_for("1000"))
```

```
$ uv run python src/wiring_lab/note02/f_settings_read_in_the_root.py

from settings  -> 900000 INR
built directly -> 10800 USD
```

```
$ CURRENCY=USD uv run python src/wiring_lab/note02/f_settings_read_in_the_root.py

from settings  -> 900000 USD
built directly -> 10800 USD
```

The environment variable still reaches the service, passed through by the build function. The last two lines are new: a second service with a different currency, built in the same program, with no environment variable involved. That is exactly what a test does.

Where the word `settings` appears in each file:

| | `e`, the service reads settings | `f`, the build function reads settings |
|---|---|---|
| inside `SalaryService` | yes, in `salary_for` | **never** — the constructor takes `currency: str` |
| in the build function | no | yes, passed in and read |
| at the start of the program | yes | yes |
| can a caller build one with a different currency | no — only by changing the environment | yes, with an ordinary argument |

> [!important] Configuration stops at the composition root
> The composition root is the one place that reads configuration and turns it into plain values for the objects it builds. `SalaryService` in `f` receives a string and cannot tell whether that string came from an environment variable, a test, or a default written in the class. Code that should not care where a value came from is never given the chance to find out.

## The composition root decides the environment, once

A real service behaves a little differently in each place it runs. On a laptop the salaries come from a small dictionary in memory; in production they come from the real HR system. The two classes below stand in for those — neither calls anything real, they only label where the answer would have come from, so the output shows which one ran. Both have the same method, so either can be used the same way.

The easy arrangement checks the environment inside every function that needs a salary.

`src/wiring_lab/note02/g_environment_checked_everywhere.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["local", "prod"] = "local"


settings = Settings()


class InMemorySalaries:
    def salary_for(self, employee_id: str) -> str:
        salaries = {"1000": 900_000}
        return f"{salaries[employee_id]} (from memory)"


class HrSystemSalaries:
    def salary_for(self, employee_id: str) -> str:
        salaries = {"1000": 900_000}
        return f"{salaries[employee_id]} (from the HR system)"


def salary_tool(employee_id: str) -> str:
    if settings.env == "local":
        source = InMemorySalaries()
    else:
        source = HrSystemSalaries()
    return source.salary_for(employee_id)


def nightly_report(employee_id: str) -> str:
    if settings.env == "local":
        source = InMemorySalaries()
    else:
        source = HrSystemSalaries()
    return source.salary_for(employee_id)


print(f"ENV={settings.env}")
print("tool   ->", salary_tool("1000"))
print("report ->", nightly_report("1000"))
```

```
$ ENV=local uv run python src/wiring_lab/note02/g_environment_checked_everywhere.py

ENV=local
tool   -> 900000 (from memory)
report -> 900000 (from memory)
```

```
$ ENV=prod uv run python src/wiring_lab/note02/g_environment_checked_everywhere.py

ENV=prod
tool   -> 900000 (from the HR system)
report -> 900000 (from the HR system)
```

It works. But the question of which environment the program is in is asked once in `salary_tool` and again in `nightly_report`, and every function added later that needs a salary has to ask it again.

The other arrangement asks once, in the build function, and hands out the answer. `SalarySource` is a name for either of the two classes, so the functions that accept one do not each have to spell out both.

`src/wiring_lab/note02/h_environment_decided_in_the_root.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["local", "prod"] = "local"


class InMemorySalaries:
    def salary_for(self, employee_id: str) -> str:
        salaries = {"1000": 900_000}
        return f"{salaries[employee_id]} (from memory)"


class HrSystemSalaries:
    def salary_for(self, employee_id: str) -> str:
        salaries = {"1000": 900_000}
        return f"{salaries[employee_id]} (from the HR system)"


SalarySource = InMemorySalaries | HrSystemSalaries


def build_salary_source(settings: Settings) -> SalarySource:
    if settings.env == "local":
        return InMemorySalaries()
    return HrSystemSalaries()


def salary_tool(employee_id: str, source: SalarySource) -> str:
    return source.salary_for(employee_id)


def nightly_report(employee_id: str, source: SalarySource) -> str:
    return source.salary_for(employee_id)


settings = Settings()
source = build_salary_source(settings)
print(f"ENV={settings.env}")
print("tool   ->", salary_tool("1000", source))
print("report ->", nightly_report("1000", source))
```

```
$ ENV=local uv run python src/wiring_lab/note02/h_environment_decided_in_the_root.py

ENV=local
tool   -> 900000 (from memory)
report -> 900000 (from memory)
```

```
$ ENV=prod uv run python src/wiring_lab/note02/h_environment_decided_in_the_root.py

ENV=prod
tool   -> 900000 (from the HR system)
report -> 900000 (from the HR system)
```

The output is identical under both environments. What differs is where the question is asked:

| | `g`, checked in every function | `h`, decided in the build function |
|---|---|---|
| lines that check `settings.env` | 2, one inside each function | 1 |
| do `salary_tool` and `nightly_report` know environments exist | yes | **no** — each only calls `source.salary_for` |
| adding a `staging` environment | edit every check | edit one function |
| using the in-memory version regardless of `ENV` | not possible without changing the environment | pass an `InMemorySalaries()` as the argument, verified with `ENV=prod` |

> [!important] An environment difference is a wiring decision
> Which implementation runs in which environment is one more decision about what gets built and handed to whom, so it belongs in the composition root as a branch, next to the construction it affects. The code that uses the service is handed the right one and never has to ask where it is running.

## Hand back names, not strings

A composition root in a real program builds more than one service, so the build function has to hand back several at once. Two services are enough to show the choice, each with one method.

The easy shape is a dictionary keyed by name. One construct comes with it: `Any`. A dictionary's values all share one declared type, these two services are different types, and so the value type is declared as `Any` — which tells the type checker to stop checking anything about that value.

`src/wiring_lab/note02/i_root_returns_a_dict.py`:

```python
from typing import Any


class SalaryService:
    def salary_for(self, employee_id: str) -> int:
        return {"1000": 900_000}[employee_id]


class LeaveService:
    def leave_balance_for(self, employee_id: str) -> int:
        return {"1000": 12}[employee_id]


def build_services() -> dict[str, Any]:
    return {
        "salary": SalaryService(),
        "leave": LeaveService(),
    }


services = build_services()
print("salary ->", services["salary"].salary_for("1000"))
print("leave  ->", services["leaves"].leave_balance_for("1000"))
```

The last line asks for `"leaves"`; the build function registered `"leave"`.

```
$ uv run ty check src/wiring_lab/note02/i_root_returns_a_dict.py

All checks passed!
```

```
$ uv run python src/wiring_lab/note02/i_root_returns_a_dict.py

salary -> 900000
Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note02/i_root_returns_a_dict.py", line 40, in <module>
    print("leave  ->", services["leaves"].leave_balance_for("1000"))
                       ~~~~~~~~^^^^^^^^^^
KeyError: 'leaves'
```

This is the name-inside-a-string problem from [[01-Hidden-Inputs]], now sitting in the composition root itself.

The other shape is a class with one named attribute per service. One construct comes with this too: `@dataclass`, which writes the class's constructor from the fields listed in it, so `Services(salary=..., leave=...)` works without an `__init__` written by hand.

`src/wiring_lab/note02/j_root_returns_named_attributes.py`:

```python
from dataclasses import dataclass


class SalaryService:
    def salary_for(self, employee_id: str) -> int:
        return {"1000": 900_000}[employee_id]


class LeaveService:
    def leave_balance_for(self, employee_id: str) -> int:
        return {"1000": 12}[employee_id]


@dataclass
class Services:
    salary: SalaryService
    leave: LeaveService


def build_services() -> Services:
    return Services(salary=SalaryService(), leave=LeaveService())


services = build_services()
print("salary ->", services.salary.salary_for("1000"))
print("leave  ->", services.leaves.leave_balance_for("1000"))
```

The same typo, as an attribute:

```
$ uv run ty check src/wiring_lab/note02/j_root_returns_named_attributes.py

error[unresolved-attribute]: Object of type `Services` has no attribute `leaves`
  --> src/wiring_lab/note02/j_root_returns_named_attributes.py:44:20
   |
44 | print("leave  ->", services.leaves.leave_balance_for("1000"))
   |                    ^^^^^^^^^^^^^^^

Found 1 diagnostic
```

```
$ uv run python src/wiring_lab/note02/j_root_returns_named_attributes.py

salary -> 900000
Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note02/j_root_returns_named_attributes.py", line 44, in <module>
    print("leave  ->", services.leaves.leave_balance_for("1000"))
                       ^^^^^^^^^^^^^^^
AttributeError: 'Services' object has no attribute 'leaves'. Did you mean: 'leave'?
```

Caught before running, and even when run anyway, the error suggests the name that was meant.

A second kind of typo separates the two shapes further. In each file, correct the service name and misspell the method instead — `leave_balanse_for` — then ask the type checker again. The dictionary version:

```
$ uv run ty check src/wiring_lab/note02/i_root_returns_a_dict.py

All checks passed!
```

And the named-attribute version:

```
$ uv run ty check src/wiring_lab/note02/j_root_returns_named_attributes.py

error[unresolved-attribute]: Object of type `LeaveService` has no attribute `leave_balanse_for`

Found 1 diagnostic
```

| The typo | Dictionary, `services["leave"]` | Named attributes, `services.leave` |
|---|---|---|
| wrong service name | not reported | `Services` has no attribute `leaves` |
| wrong method name on the service | **not reported either** | `LeaveService` has no attribute `leave_balanse_for` |
| when run anyway | `KeyError: 'leaves'` | `AttributeError`, with the right name suggested |

The second row is the one that matters. A dictionary does not only hide the name of a service; because its values have to be `Any`, it also hides what each service is, so every method called on one goes unchecked as well. The dataclass keeps both the name and the type.

> [!important] The composition root should return something with names
> Asking for collaborators instead of fetching them was worth doing because names can be checked and strings cannot. A composition root that builds every object correctly and then hands them back in a string-keyed dictionary gives that property back at the last step. Returning a class with one named, typed attribute per service keeps it all the way to the code that uses them.
