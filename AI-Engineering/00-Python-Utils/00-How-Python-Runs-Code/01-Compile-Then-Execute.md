#python #execution-model #bytecode #pycache #python-utils


Typing `python main.py` looks like one action. It is two, and almost every confusing failure in Python comes from not separating them.

## Four words for two things

**Run**, **compile**, **interpret** and **execute** get used interchangeably, and they are not the same thing.

| Word | What it names |
|---|---|
| **Compile** | Turning your text into **bytecode** — a list of low-level instructions. A real, separate step, and it always happens. |
| **Execute** | Carrying out those instructions, one at a time. |
| **Interpret** | The same activity as **execute**. The word names **how**: a program reads the instructions and acts on them, rather than the processor running native machine code directly. |
| **Run** | The colloquial umbrella — **compile it, then execute it**. What **you** do. |

So there are **two phases, not four**. **Interpret** is another word for **execute**, and **run** covers both.

That also settles a question people argue about. Is Python compiled or interpreted? **Both.** It compiles your source to bytecode, then interprets that bytecode. **Compiled language** usually implies compiled all the way down to machine code — that's the distinction actually being drawn, not whether compilation happens at all. It always happens.

## What each phase can catch

The two phases ask different questions, and only one of them requires your program to be running.

**Compilation asks: is this well-formed Python?** Nothing more. Here is a file that fails that bar:

```python
print("STEP 1: the module started running")

def f(x: ) -> int:
    return x
```

```
$ python3 bad_syntax.py
  File "bad_syntax.py", line 3
    def f(x: ) -> int:
             ^
SyntaxError: invalid syntax
```

**`STEP 1` did not print.** There is a `print` on line 1 and it produced nothing at all. The file was **run** — you typed the command, Python started, opened the file, read it — but nothing was ever **executed**, because Python cannot turn line 3 into an instruction and therefore produces no instructions for the file at all. One malformed line anywhere and not a single line runs.

**Execution asks: does this name actually exist?** That question can only be answered once execution reaches the line that asks it:

```python
print("STEP 1: the module started running")

def f(x: does_not_exist) -> int:
    return x
```

```
$ python3 bad_name.py
STEP 1: the module started running
Traceback (most recent call last):
  File "bad_name.py", line 3, in <module>
    def f(x: does_not_exist) -> int:
NameError: name 'does_not_exist' is not defined
```

This time `STEP 1` **did** print. Compilation was perfectly happy — `does_not_exist` is a well-formed name, and the compiler never asks whether a name refers to anything. Execution began, line 1 ran, and the failure waited until line 3.

| | valid Python? | anything executes? | where it fails |
|---|---|---|---|
| `x: )` | **no** | **none of it** | before line 1 |
| `x: does_not_exist` | yes | yes, until line 3 | at line 3 |

> [!important] This is why a `SyntaxError` and a `NameError` feel so different to live with. A syntax error is **total and immediate** — the program does nothing at all, no matter where in the file the mistake sits. A `NameError` is **local and late** — everything before it ran normally, and the failure waits until execution arrives at the offending line. A bad name on a rarely-taken branch can sit there for months without anyone noticing.

## Seeing the compile step leave evidence

The compile phase isn't something you have to take on faith. It writes a file.

```python
# helper.py
print("   helper.py executing")

def greet(name: str) -> str:
    return f"hi {name}"
```

```python
# main.py
print("main.py executing")
import helper
print(helper.greet("laxya"))
```

Before running, the folder holds exactly what you wrote:

```
$ ls
helper.py
main.py
```

Run `python main.py`:

```
$ python3 main.py
main.py executing
   helper.py executing
hi laxya
```

and something new has appeared:

```
$ ls
__pycache__     helper.py     main.py

__pycache__ contains:
helper.cpython-313.pyc
```

That `.pyc` is the compiled bytecode for `helper.py`, saved to disk so the next run can skip compiling it again. Three things about it are worth knowing:

- **The name records the interpreter** — `cpython-313`. Bytecode is not portable across Python versions, so each version keeps its own copy rather than fighting over one file.
- **It knows when it's stale.** The file carries a small header noting the source's timestamp and size. Edit `helper.py` and the next import notices the mismatch, recompiles, and rewrites the `.pyc`. You never need to clear it by hand.
- **It changes nothing about behaviour.** Caching is purely a start-up optimisation. Delete `__pycache__` and your program runs identically, just fractionally slower to begin.

And the detail that catches people out:

> [!important] **There is no `main.cpython-313.pyc`.** The file you **run** is compiled fresh every time and never cached — only files you **import** get a `.pyc`. The reasoning: a script is typically run once per process, so caching it would save nothing, while an imported module may be loaded by many programs, many times over.

## Why this matters beyond trivia

Two consequences that come up constantly.

**Reading code and running code are unrelated activities.** A program can extract everything it needs from your source without executing a line of it — which is how your editor offers completions inside a function you are still halfway through typing, on a file that could not possibly run. It isn't waiting for anything; it re-reads the text and answers from that.

**Compilation is not a safety net.** It confirms your file is well-formed Python and stops. It does not check that names exist, that a function is called with the right number of arguments, or that types line up. Anything beyond grammar is either caught later, when execution reaches it, or by a separate tool you choose to run.
