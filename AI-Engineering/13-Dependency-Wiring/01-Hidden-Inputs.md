#dependency-injection #python #architecture #testing

**The first line of a function tells every caller what to hand it.** Most of the time that line is complete. This note is about the functions where it is not — where something the function needs is fetched from inside its body instead of asked for — and why that one habit decides whether a piece of code can ever be used outside the program it was written in.

# Hidden Inputs

> [!info] Two words used throughout. A **signature** is the `def` line of a function: its name, the parameters it takes with their types, and what it returns. A **collaborator** is anything a function uses to do its job without having created it itself — a dictionary of salaries, a database client, a service object that calls another system.

## The def line is a promise, and one of these breaks it

Two functions with the same job: look up one employee's salary.

`src/wiring_lab/note01/a_the_signature_is_a_promise.py`:

```python
SALARIES: dict[str, int] = {}


def salary_passed_in(employee_id: str, salaries: dict[str, int]) -> int:
    return salaries[employee_id]


def salary_reached_for(employee_id: str) -> int:
    return SALARIES[employee_id]


print("passed in   ->", salary_passed_in("1000", {"1000": 900_000}))
print("reached for ->", salary_reached_for("1000"))
```

Before running it, read only the two `def` lines. Each one is the function telling its caller what it needs:

| Function | What the def line asks for | What the body actually uses |
|---|---|---|
| `salary_passed_in` | an employee id and the salaries | an employee id and the salaries |
| `salary_reached_for` | an employee id | an employee id **and** the module-level `SALARIES` |

The first row matches itself. The second does not, and nothing on the `def` line hints at the difference. Now call each function exactly as its own `def` line asks:

```
$ uv run python src/wiring_lab/note01/a_the_signature_is_a_promise.py

passed in   -> 900000

Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/a_the_signature_is_a_promise.py", line 27, in <module>
    print("reached for ->", salary_reached_for("1000"))
                            ~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/a_the_signature_is_a_promise.py", line 23, in salary_reached_for
    return SALARIES[employee_id]
           ~~~~~~~~^^^^^^^^^^^^^
KeyError: '1000'
```

Each lab file opens with a comment header explaining what it demonstrates, and those headers are left out of the code shown here. That is why the line numbers in this note's output are larger than the code above them — here and in every output block that follows.

**The second call did everything its signature asked.** One argument, the right type, a real employee id. It failed anyway, because the function needs a second thing — a `SALARIES` dictionary that has been filled — and it gets that thing by reaching for it inside its body rather than by asking for it on its `def` line.

The only ways to discover that second requirement are to read the body, or to call the function and watch it fail. The signature, which exists precisely so that a caller does not have to read the body, says nothing.

> [!important] Nobody called it wrongly
> The caller of `salary_reached_for` followed the promise exactly. The defect is not in the call, it is in the promise: the function needs two things and admits to one.

## Inside the program it never fails, which is why nobody notices

In a real program the dictionary is never left empty. Some code fills it when the program starts, and only after that does anything call the function. The function below is the same one as before; the only addition is the code that fills `SALARIES`.

`src/wiring_lab/note01/b_inside_the_program.py`:

```python
SALARIES: dict[str, int] = {}


def load_salaries() -> None:
    SALARIES["1000"] = 900_000


def salary_reached_for(employee_id: str) -> int:
    return SALARIES[employee_id]


if __name__ == "__main__":
    load_salaries()
    print("1000 ->", salary_reached_for("1000"))
```

The last block is this program's startup. `if __name__ == "__main__":` means **run this only when this file is started as the program** — when another file imports it, the block is skipped. So starting it fills the dictionary first and then uses it:

```
$ uv run python src/wiring_lab/note01/b_inside_the_program.py

1000 -> 900000
```

It works on every run, on every machine, for every employee in the dictionary. That is the only view of this function anybody normally gets — the person who wrote it, the person who reviewed it, and production all see the program start up first.

Now call the same function from a file that is not the program starting up.

`src/wiring_lab/note01/c_from_outside_the_program.py`:

```python
from wiring_lab.note01.b_inside_the_program import salary_reached_for

print("1000 ->", salary_reached_for("1000"))
```

```
$ uv run python src/wiring_lab/note01/c_from_outside_the_program.py

Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/c_from_outside_the_program.py", line 13, in <module>
    print("1000 ->", salary_reached_for("1000"))
                     ~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/b_inside_the_program.py", line 20, in salary_reached_for
    return SALARIES[employee_id]
           ~~~~~~~~^^^^^^^^^^^^^
KeyError: '1000'
```

The import brought the function across and skipped the startup block, so nothing filled the dictionary. Same function, same argument, opposite result:

| How the function was reached | Who filled `SALARIES` first | Result |
|---|---|---|
| the file started as the program | the startup block | `900000` |
| imported into another file | nobody | `KeyError: '1000'` |

**Inside the program, the broken promise costs nothing.** The program always does the hidden setup before the first call, so the function never fails there. With no failure there is no signal; with no signal the pattern looks correct in review and correct in production, and the next function gets written the same way.

> [!important] The failure is reserved for outside callers
> The only way to see the problem is to call the function from somewhere that does not run the program's startup first. A throwaway script is one such caller. A test is the one that matters, because a test is built to call one function without starting the whole program.

## From outside, the caller has to rebuild the startup

The smallest change that makes the outside call work leaves the function alone and changes the caller: do what the program's startup would have done, then call.

`src/wiring_lab/note01/d_rebuild_the_startup.py`:

```python
from wiring_lab.note01.b_inside_the_program import load_salaries, salary_reached_for

load_salaries()
print("1000 ->", salary_reached_for("1000"))
```

```
$ uv run python src/wiring_lab/note01/d_rebuild_the_startup.py

1000 -> 900000
```

It works. Now look at what the caller had to know to write the `load_salaries()` line, and where that knowledge came from:

| What the caller had to know | Where it is written down |
|---|---|
| that some setup has to happen at all | nowhere — the `KeyError` from the previous section was the only hint |
| that `load_salaries` is the function that does it | inside another file |
| that it must run before the call, not after | nowhere |

The `def` line still reads `salary_reached_for(employee_id: str)`. **The caller needed three pieces of knowledge and the promise supplied none of them.** In this file the setup happens to be one line, which makes it look cheap.

## A real function reaches for more than one thing

A salary lookup in a real system does not just return a number. It checks who is asking first. Here an employee may read their own salary and an admin may read anybody's, which means the function now needs three things: who is logged in, which ids belong to admins, and the salaries themselves.

`src/wiring_lab/note01/e_three_hidden_inputs.py`:

```python
CURRENT_USER: dict[str, str] = {}
ADMIN_IDS: set[str] = set()
SALARIES: dict[str, int] = {}


def log_in(employee_id: str) -> None:
    CURRENT_USER["employee_id"] = employee_id


def load_admins() -> None:
    ADMIN_IDS.add("2000")


def load_salaries() -> None:
    SALARIES["1000"] = 900_000
    SALARIES["1001"] = 1_200_000


def salary_reached_for(employee_id: str) -> int:
    caller = CURRENT_USER["employee_id"]
    if caller != employee_id and caller not in ADMIN_IDS:
        raise PermissionError(f"{caller} may not read the salary of {employee_id}")
    return SALARIES[employee_id]


if __name__ == "__main__":
    load_admins()
    load_salaries()
    log_in("1000")
    print("1000 reads 1000 ->", salary_reached_for("1000"))
```

```
$ uv run python src/wiring_lab/note01/e_three_hidden_inputs.py

1000 reads 1000 -> 900000
```

The startup block now makes three calls, and the `def` line still asks for one string. Inside the program that difference is invisible, exactly as before.

Now check one rule from outside the program: an admin may read another employee's salary.

`src/wiring_lab/note01/f_one_rule_from_outside.py`:

```python
from wiring_lab.note01.e_three_hidden_inputs import (
    load_admins,
    load_salaries,
    log_in,
    salary_reached_for,
)

load_admins()
load_salaries()
log_in("2000")

print("admin 2000 reads 1001 ->", salary_reached_for("1001"))
```

```
$ uv run python src/wiring_lab/note01/f_one_rule_from_outside.py

admin 2000 reads 1001 -> 1200000
```

The rule being checked is the last line. The three lines above it are the program's startup, rebuilt by hand.

None of them is optional. Delete any one of the three setup lines from that file and run it again:

| Line deleted | What the last line does instead |
|---|---|
| `log_in("2000")` | `KeyError: 'employee_id'` |
| `load_admins()` | `PermissionError: 2000 may not read the salary of 1001` |
| `load_salaries()` | `KeyError: '1001'` |

> [!warning] The errors do not say what was forgotten
> Each missing setup fails differently, and no message names the call that was skipped. `KeyError: 'employee_id'` is a dictionary complaining about a key; nothing in it says `log_in` was never called. The second row is worse, because a `PermissionError` looks like the rule working correctly, when in fact nobody told the function who the admins are.

**This is the cost that the broken promise was deferring.** One line to check, three hidden things to rebuild before it can run, and the only guide to those three is the body of the function and the errors it throws when one is missing. Every additional thing a function reaches for adds another line to that setup and another error that names the wrong thing.

## The tools read the promise, so they cannot see past it

The first file again, with the same kind of mistake made twice: the first call forgets to pass the salaries, the second forgets to fill them.

`src/wiring_lab/note01/g_what_the_checker_can_see.py`:

```python
SALARIES: dict[str, int] = {}


def salary_passed_in(employee_id: str, salaries: dict[str, int]) -> int:
    return salaries[employee_id]


def salary_reached_for(employee_id: str) -> int:
    return SALARIES[employee_id]


print("passed in   ->", salary_passed_in("1000"))
print("reached for ->", salary_reached_for("1000"))
```

Ask the type checker about it, without running anything:

```
$ uv run ty check src/wiring_lab/note01/g_what_the_checker_can_see.py

error[missing-argument]: No argument provided for required parameter `salaries` of function `salary_passed_in`
  --> src/wiring_lab/note01/g_what_the_checker_can_see.py:29:25
   |
29 | print("passed in   ->", salary_passed_in("1000"))
   |                         ^^^^^^^^^^^^^^^^^^^^^^^^
info: Parameter declared here
  --> src/wiring_lab/note01/g_what_the_checker_can_see.py:21:40
   |
21 | def salary_passed_in(employee_id: str, salaries: dict[str, int]) -> int:
   |                                        ^^^^^^^^^^^^^^^^^^^^^^^^

Found 1 diagnostic
```

One diagnostic for two mistakes. It names the forgotten parameter and points at the line that declares it, before the program has run at all.

The second mistake produces nothing, and the reason is the only thing a type checker has to work with — the `def` line and the call:

| Call | The def line asks for | The call provides | What the checker concludes |
|---|---|---|---|
| `salary_passed_in("1000")` | an id and the salaries | an id | a mismatch, reported with the missing name |
| `salary_reached_for("1000")` | an id | an id | a perfect match, nothing to report |

That is not a weakness of this checker. On the second line the promise and the call agree completely, and `SALARIES` appears in neither, so there is nothing for any checker to compare it against.

Running the file shows the same asymmetry from the other side. It stops at the first call and never reaches the second:

```
$ uv run python src/wiring_lab/note01/g_what_the_checker_can_see.py

Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/g_what_the_checker_can_see.py", line 29, in <module>
    print("passed in   ->", salary_passed_in("1000"))
                            ~~~~~~~~~~~~~~~~^^^^^^^^
TypeError: salary_passed_in() missing 1 required positional argument: 'salaries'
```

Even at run time the forgotten parameter fails at the call, naming `salaries`. The forgotten setup, as the earlier sections showed, fails inside the body with a `KeyError` naming a dictionary key.

The type checker is not alone in this. Everything that helps a person use a function works from the same `def` line:

| Who works from the def line | A forgotten collaborator that is **passed in** | A forgotten collaborator that is **reached for** |
|---|---|---|
| the type checker | caught before running, with the parameter named | not caught |
| the editor's parameter hints | the parameter is in the declaration they read from | absent from that declaration, so there is nothing to hint |
| a person reading the call | a visibly missing argument | nothing looks wrong |
| the running program | fails at the call, naming the parameter | fails inside the body, naming a dictionary key |

> [!important] The pattern has a name: service locator
> A function that locates what it needs from a shared place at the moment it runs, instead of being handed those things by its caller, is using the **service locator** pattern.
>
> It is widely called an anti-pattern, and the reason is the table above rather than taste: the thing the function depends on is invisible to every tool that reads the function's promise — and the type checker, the editor and the person reading the code all read the promise.

## Move the hidden things onto the def line

The fix is to stop reaching. Take the three shared places the salary lookup reached into, and make each one a parameter:

| Reached for inside the body | Asked for on the def line |
|---|---|
| `CURRENT_USER["employee_id"]` | `caller_id: str` |
| `ADMIN_IDS` | `admin_ids: set[str]` |
| `SALARIES` | `salaries: dict[str, int]` |

`src/wiring_lab/note01/h_everything_on_the_def_line.py`:

```python
def salary_passed_in(
    employee_id: str,
    caller_id: str,
    admin_ids: set[str],
    salaries: dict[str, int],
) -> int:
    if caller_id != employee_id and caller_id not in admin_ids:
        raise PermissionError(f"{caller_id} may not read the salary of {employee_id}")
    return salaries[employee_id]


print(
    "admin 2000 reads 1001 ->",
    salary_passed_in(
        employee_id="1001",
        caller_id="2000",
        admin_ids={"2000"},
        salaries={"1001": 1_200_000},
    ),
)

try:
    salary_passed_in(
        employee_id="1001",
        caller_id="2000",
        admin_ids=set(),
        salaries={"1001": 1_200_000},
    )
except PermissionError as exc:
    print("same caller, no admins ->", "refused:", exc)
```

```
$ uv run python src/wiring_lab/note01/h_everything_on_the_def_line.py

admin 2000 reads 1001 -> 1200000
same caller, no admins -> refused: 2000 may not read the salary of 1001
```

The rule inside the function did not change. What changed is where its three inputs come from: there are no module-level dictionaries left, and no `log_in`, `load_admins` or `load_salaries` to call first. Reading the `def` line now tells you everything the function needs, which is the complete promise the first section was missing.

The first call is the same rule that took a whole file to check from outside before. Side by side:

| Checking one rule from outside the program | Reached for, `f_one_rule_from_outside.py` | Passed in, this file |
|---|---|---|
| names imported | four | one |
| setup lines before the call | three, in the right order | none |
| where you learn what the function needs | its body, or the errors it throws | its def line |
| forgetting one of the three | an error naming a dictionary key, or a `PermissionError` that looks like the rule working | the type checker names the missing parameter before anything runs |

That last row is checkable. Delete the `admin_ids=` line from the first call and ask the type checker:

```
$ uv run ty check src/wiring_lab/note01/h_everything_on_the_def_line.py

error[missing-argument]: No argument provided for required parameter `admin_ids` of function `salary_passed_in`

Found 1 diagnostic
```

The mistake that looked like a correct refusal in the reached-for version is now a named error, reported before the program runs.

**The second call is the part that matters for testing.** It asks what happens when the same caller is not an admin. With the reached-for version the only way to arrange that was to skip `load_admins()`, and skipping it produced a refusal indistinguishable from the rule working. Here the arrangement is an ordinary argument, `admin_ids=set()`, written in the call where anyone reading it can see what was chosen.

> [!important] A parameter can be given a different value, and a hidden input cannot
> Once a collaborator is on the `def` line, every caller decides what to hand over — the real admin list, an empty one, three test salaries instead of a production table. Nothing is filled, faked or reset beforehand, because nothing is shared. That single property is what makes a function usable from outside the program it was written in.

## A name inside a string hides the name as well

The examples so far reached for plain data. Real programs usually go one step further: at startup they register their service objects in one shared dictionary, **by name**, and functions look those objects up by that name when they need them.

`src/wiring_lab/note01/i_a_name_in_a_string.py`:

```python
class SalaryService:
    def salary_for(self, employee_id: str) -> int:
        return {"1000": 900_000}[employee_id]


SERVICES: dict[str, SalaryService] = {}


def start_program() -> None:
    SERVICES["salary_details"] = SalaryService()


def salary_tool(employee_id: str) -> int:
    service = SERVICES["salary_detail"]
    return service.salary_for(employee_id)


start_program()
print("program started, registered:", list(SERVICES))
print("1000 ->", salary_tool("1000"))
```

During a tidy-up somebody renamed the registration to `"salary_details"`, and the lookup in `salary_tool` still asks for `"salary_detail"`. One letter, in two places, both inside quotes.

```
$ uv run ty check src/wiring_lab/note01/i_a_name_in_a_string.py

All checks passed!
```

```
$ uv run python src/wiring_lab/note01/i_a_name_in_a_string.py

program started, registered: ['salary_details']
Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/i_a_name_in_a_string.py", line 36, in <module>
    print("1000 ->", salary_tool("1000"))
                     ~~~~~~~~~~~^^^^^^^^
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/i_a_name_in_a_string.py", line 30, in salary_tool
    service = SERVICES["salary_detail"]
              ~~~~~~~~^^^^^^^^^^^^^^^^^
KeyError: 'salary_detail'
```

Look at the order of events. **The program started successfully** — startup ran and printed a healthy list of what it registered. The failure waited for the lookup line to run, and in a real service that line runs the first time a user asks that question, which may be hours after a deploy whose startup log said everything was fine.

Now make the same one-word rename to a parameter instead. The `def` line says `salary_table`, and a call still passes `salaries=`.

`src/wiring_lab/note01/j_a_name_in_a_parameter.py`:

```python
def salary_passed_in(employee_id: str, salary_table: dict[str, int]) -> int:
    return salary_table[employee_id]


print("1000 ->", salary_passed_in(employee_id="1000", salaries={"1000": 900_000}))
```

```
$ uv run ty check src/wiring_lab/note01/j_a_name_in_a_parameter.py

error[missing-argument]: No argument provided for required parameter `salary_table` of function `salary_passed_in`
  --> src/wiring_lab/note01/j_a_name_in_a_parameter.py:21:18
   |
21 | print("1000 ->", salary_passed_in(employee_id="1000", salaries={"1000": 900_000}))
   |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
info: Parameter declared here
  --> src/wiring_lab/note01/j_a_name_in_a_parameter.py:17:40
   |
17 | def salary_passed_in(employee_id: str, salary_table: dict[str, int]) -> int:
   |                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

error[unknown-argument]: Argument `salaries` does not match any known parameter of function `salary_passed_in`
  --> src/wiring_lab/note01/j_a_name_in_a_parameter.py:21:55
   |
21 | print("1000 ->", salary_passed_in(employee_id="1000", salaries={"1000": 900_000}))
   |                                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^
info: Function signature here
  --> src/wiring_lab/note01/j_a_name_in_a_parameter.py:17:5
   |
17 | def salary_passed_in(employee_id: str, salary_table: dict[str, int]) -> int:
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Found 2 diagnostics
```

```
$ uv run python src/wiring_lab/note01/j_a_name_in_a_parameter.py

Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/j_a_name_in_a_parameter.py", line 21, in <module>
    print("1000 ->", salary_passed_in(employee_id="1000", salaries={"1000": 900_000}))
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: salary_passed_in() got an unexpected keyword argument 'salaries'
```

Before anything runs, the checker names both the stale argument and the new parameter it is missing.

| The same one-word rename | Name inside a string, `SERVICES["salary_detail"]` | Name as a parameter, `salary_table=` |
|---|---|---|
| can the type checker see the mismatch | no — two strings are only two strings | yes, both names reported |
| is it something an editor can rename everywhere | no — it is text inside a string | yes — it is a parameter name |
| when the mistake surfaces | when that line first runs, after a successful start | before running, and at the call if run anyway |
| what the error names | a dictionary key | the old argument and the new parameter |

**Reaching for a collaborator hides the collaborator. Reaching for it by string hides its name as well**, so a typo or a half-finished rename passes every check, survives startup, and waits for its first real use.

## The same fix already worked on configuration

This exact problem has a well-known version one layer down, in configuration, which is the subject of [[AI-Engineering/12-Configuration/01-Declared-Not-Fetched|Declared, Not Fetched]] — including what `BaseSettings` and `validation_alias` do in the second file below. A setting read from the environment by a name inside a string behaves like the service lookup above.

`src/wiring_lab/note01/k_a_setting_named_in_a_string.py`:

```python
import os

print("program started")
print("jwt ->", os.environ["JWT_SECRETS"])
```

```
$ JWT_SECRET=abc123 uv run python src/wiring_lab/note01/k_a_setting_named_in_a_string.py

program started
Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/k_a_setting_named_in_a_string.py", line 15, in <module>
    print("jwt ->", os.environ["JWT_SECRETS"])
                    ~~~~~~~~~~^^^^^^^^^^^^^^^
  File "<frozen os>", line 716, in __getitem__
KeyError: 'JWT_SECRETS'
```

The variable really is set. The code asks for it with one letter too many, the type checker passes it, the program starts, and the read fails when it runs.

The fix for configuration is to declare each setting once, on a settings class, and use it everywhere else as an attribute.

`src/wiring_lab/note01/l_a_setting_declared_once.py`:

```python
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str = Field(validation_alias="JWT_SECRET")


settings = Settings()

print("program started")
print("jwt ->", settings.jwt_secrets)
```

The last line carries the same kind of typo. The type checker catches it without running anything:

```
$ uv run ty check src/wiring_lab/note01/l_a_setting_declared_once.py

error[unresolved-attribute]: Object of type `Settings` has no attribute `jwt_secrets`
  --> src/wiring_lab/note01/l_a_setting_declared_once.py:32:17
   |
32 | print("jwt ->", settings.jwt_secrets)
   |                 ^^^^^^^^^^^^^^^^^^^^

Found 1 diagnostic
```

And a missing variable stops the program before it does anything at all — `program started` is never printed:

```
$ uv run python src/wiring_lab/note01/l_a_setting_declared_once.py

Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note01/l_a_setting_declared_once.py", line 29, in <module>
    settings = Settings()
  File "/Users/home/Desktop/projects/wiring-lab/.venv/lib/python3.13/site-packages/pydantic_settings/main.py", line 262, in __init__
    super().__init__(**__pydantic_self__.__class__._settings_build_values(sources, init_kwargs))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/home/Desktop/projects/wiring-lab/.venv/lib/python3.13/site-packages/pydantic/main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
JWT_SECRET
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
```

Side by side, the configuration version and the collaborator version are one argument:

| | Configuration | Collaborators |
|---|---|---|
| reached for by a string at the point of use | `os.environ["JWT_SECRET"]` | `SERVICES["salary_detail"]` |
| a typo in that string | passes the checker, fails when the line runs | passes the checker, fails when the line runs |
| the fix | declare `jwt_secret` once, use `settings.jwt_secret` | ask for it on the `def` line |
| a typo after the fix | the checker names the attribute before running | the checker names the parameter before running |
| missing entirely | the program refuses to start | the call fails, naming what is missing |

> [!important] A string cannot always be removed, but it can be confined
> Environment variables are named by strings, and so is almost everything outside a program. The settings class does not make `"JWT_SECRET"` disappear — it writes it exactly once, inside one declaration that is checked all at once when the program starts. Every other line uses `settings.jwt_secret`, a real attribute the type checker, the editor and a reader can all see.
>
> A hidden collaborator is the same problem in a different place, and the same move fixes it: stop fetching the thing by name wherever it is used, and state once, where it can be checked, what the code needs.
