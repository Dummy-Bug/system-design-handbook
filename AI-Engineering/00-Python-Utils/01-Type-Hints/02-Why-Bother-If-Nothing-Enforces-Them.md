#python #type-hints #typing #python-utils


The previous note ended somewhere uncomfortable. Annotations are filed and never read; Python runs a function annotated `-> str` that returns an `int` without a murmur. A reasonable person draws the obvious conclusion: they're decoration.

So the question has to be answered properly rather than waved away. **Why write something the language ignores?**

## The comment challenge

The easy answer is "documentation" — and it collapses immediately, because a comment does that too:

```python
# a and b are ints, returns an int
def add(a, b):
    return a + b
```

```python
def add(a: int, b: int) -> int:
    return a + b
```

Both state the same thing in the same file. Neither is enforced — Python ignores the comment, and the previous note proved it ignores the annotation just as thoroughly. Both can be wrong and stay wrong forever. The comment is arguably friendlier, since it can say things like *"b must be positive"* that no annotation can express.

If "it documents the code" were the whole answer, the top version would win. So that isn't the answer.

## What one has that the other doesn't

Ask Python for the claim back.

```python
# a and b are ints, returns an int
def add_a(a, b):
    return a + b

def add_b(a: int, b: int) -> int:
    return a + b
```

```python
print(add_a.__annotations__)   # {}
print(add_b.__annotations__)   # {'a': <class 'int'>, 'b': <class 'int'>,
                               #  'return': <class 'int'>}
```

The commented version stores **nothing**. And there's nowhere else to look:

```python
print(hasattr(add_a, '__comment__'))                       # False
print([x for x in dir(add_a) if 'comm' in x.lower()])      # []
```

The claim was typed into the file, Python read past it, and it is now unrecoverable by any program. It exists as marks on a screen for human eyes and nowhere else.

The annotated version stored something you can pick up and act on:

```python
t = add_b.__annotations__['a']

print(t)                        # <class 'int'>
print(t('38'), type(t('38')))   # 38 <class 'int'>
```

That isn't a description of `int`. It's `int` — the real class, which can be called, compared, passed around, put in a registry.

Stored **where**, and **when**? On the function object, as an attribute named `__annotations__`, built the moment the `def` line executes:

```python
def add(a: int, b: int) -> int:
    return a + b

print(add.__annotations__)      # add() has NOT been called yet
# {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```

Not when the function is *called* — when the `def` itself runs. Once, and every later call reuses the same dictionary rather than rebuilding it. The full derivation is in `01-What-A-Type-Hint-Is`; all that matters here is that the claim ends up somewhere a program can reach, which is exactly what the comment failed to do.

> [!important] **A comment is prose. An annotation is grammar.**
> A tool can find `a: int` reliably because its position and shape are part of the language: after the parameter name, after a colon, always. To get the same fact out of `# a and b are ints`, a program would have to read English and guess.
>
> One is a note in the margin. The other is an interface.

That's the answer to "why bother". You are not writing for Python. **You are writing for the readers that do look** — and making the claim machine-findable is what makes them possible.

## When can those readers act?

Different readers get their turn at different moments, and it's worth separating them, because the first one operates before your program exists in any form.

### The one thing needed here

Typing `python main.py` is **two** steps, not one. Python first reads the whole file and turns it into instructions, and only then starts carrying them out. Preparing, then doing.

That first step asks one question — *is this well-formed Python?* — and nothing more. It never checks that a name exists, and never looks at what your annotations mean.

Which is all this note needs, plus the consequence that follows from it: because the whole file is prepared before anything happens, **a file can be run without a single line of it ever executing.**

> `00-How-Python-Runs-Code/01-Compile-Then-Execute` has the full treatment — the vocabulary (*compile*, *execute*, *interpret*, *run*), what each phase catches, and where the compiled bytecode goes.

### Watching it happen

Take a file that starts executing and then fails, because the annotation names something undefined:

```python
print("STEP 1: the module started running")

def f(x: does_not_exist) -> int:
    return x

print("STEP 2: past the def")
```

```
STEP 1: the module started running
NameError: name 'does_not_exist' is not defined
```

Note that STEP 1 *did* print. Python was content with the file as written, started running it, and only fell over on reaching the `def` and having to go find a thing called `does_not_exist`.

Contrast a file that is not valid Python at all:

```python
print("STEP 1: the module started running")

def f(x: ) -> int:
    return x
```

```
  File "bad_syntax.py", line 3
    def f(x: ) -> int:
             ^
SyntaxError: invalid syntax
```

**STEP 1 did not print.** There's a `print` on line 1 and it produced nothing at all — because the preparation step failed before anything got its turn.

So the annotation `x: does_not_exist` survived preparation and died during execution, while `x: )` never made it past preparation. Two different questions, asked at two different moments — and the first one needs nothing to have run.

## How an editor helps before any of that

This is the part that looks impossible at first. Your editor suggests completions while you're halfway through typing a line — nothing has been run, nothing could be run.

It works because **the editor doesn't run your code. It reads it**, the same way you do — parsing the text in the buffer and building a picture of what's declared where.

Here is a program doing exactly that to the file that *crashes when run*:

```
found: parameter 'x' annotated does_not_exist
found: returns int

...and that file still cannot run:
NameError: name 'does_not_exist' is not defined
```

The annotations came out cleanly from a file that cannot execute, because reading and running are unrelated activities. That's why help arrives on a half-written function: the editor re-reads the text on every keystroke and answers from that.

> [!info] Real editors go further and use an error-tolerant parser, so even genuinely broken syntax still yields partial information. That's why completions keep working mid-keystroke, when the line isn't remotely valid Python yet.

## The three readers

Python is the only participant that ignores annotations. Three others don't:

1. **Your editor**, reading the text as you type — completions, jump-to-definition, safe renames. Needs nothing to have run.
2. **A checker**, reading the text before you run — a separate program whose entire job is comparing your claims against your code.
3. **Libraries that read the stored dictionary while running** — the `__annotations__` from the previous note, picked up by something that has chosen to care.

The third is the one that changes what you can build, and it rests entirely on the fact from concept 1 that surprises people: annotations are **kept, not discarded**. A library can ask a function what it expects and act on the answer.

### What that looks like

A FastAPI route, complete:

```python
@app.get('/items/{item_id}')
def read_item(item_id: int):
    return {'value': item_id, 'python_type': type(item_id).__name__}
```

Two requests:

```
GET /items/5
    200 {'value': 5, 'python_type': 'int'}

GET /items/abc
    422 {'detail': [{'type': 'int_parsing', 'loc': ['path', 'item_id'],
                     'msg': 'Input should be a valid integer, unable to
                             parse string as an integer', 'input': 'abc'}]}
```

Stop on the first one, because it should be impossible. **HTTP has no integers.** A URL is text — `/items/5` arrives as characters, and `item_id` could only ever be the string `"5"` unless somebody converted it. The function received `5`, an `int`, and there is no `int()` call anywhere in that code.

The second request didn't crash either. It came back as a structured error naming which parameter failed, what was expected, and what actually arrived — and no validation was written.

Now delete three characters, changing nothing else:

```python
def read_item(item_id):          # ": int" removed
```

```
GET /items/5   -> 200 {'value': '5',   'python_type': 'str'}
GET /items/abc -> 200 {'value': 'abc', 'python_type': 'str'}
```

Both strings. No conversion, no validation, and `abc` now sails through as a perfectly acceptable item id. **The annotation was the only thing that made either behaviour happen.**

### When it read it

Not on each request. When the `@app.get(...)` decorator ran — which is an ordinary function call, executed as the module was imported:

```
2. about to execute the decorated def...
3. the def has run. NO request has been made yet.
   FastAPI already knows: param 'item_id' -> type <class 'int'>
   and it already built a schema:
   [{'name': 'item_id', 'in': 'path', 'required': True,
     'schema': {'type': 'integer', 'title': 'Item Id'}}]
```

`'type': 'integer'`, before a single request existed. The decorator reached into `read_item.__annotations__`, found `int`, and built a converter and a schema from it — once. Every later request just uses what was built.

Which is the timing from earlier in this note, applied: one function object, one annotations dictionary, built when the `def` runs, reused by every call. A million requests, one read.

> [!tip] Worth noticing how little of this is magic. `read_item.__annotations__` gives you `{'item_id': <class 'int'>}`; seeing `int` there and calling `int("5")` is a few lines of ordinary Python. The framework's real contribution is the plumbing around it — matching the URL, catching the failure, turning it into a 422 response — not the annotation reading, which is the part you could write yourself.

## What this concept claims

**Annotations are worth writing because they are machine-readable, not because they are enforced.**

The enforcement question and the value question are separate, and conflating them is what makes "Python doesn't check them, so why bother?" feel like a checkmate. It isn't one. Python not checking them is precisely what leaves them available as a common format that three other kinds of tool can build on.

The trap in the other direction is equally real: because annotations enable checking, it's easy to slide into believing they *are* checking. They are not. Something has to read them, and whether anything is reading them in your project is a question about your setup — not something the syntax grants you.
