#python #type-hints #typing #annotations #python-utils


So far annotations have only appeared on functions. They also go on classes and on modules, and moving to a class exposes something the function case hides completely.

## An annotation binds nothing

```python
1  class Employee:
2      name: str
3      age: int = 30
4      company = 'Repute'
```

Three lines, three different shapes. `name` has an annotation and no value. `age` has both. `company` has a value and no annotation.

Ask the class for each of them:

```python
6  print(Employee.age)
7  print(Employee.company)
8  print(Employee.name)
```

```
$ python3 employee.py
30
Repute
AttributeError: type object 'Employee' has no attribute 'name'
```

> [!info] Not `None`, not an empty slot — **`name` does not exist on the class at all.**

The reason is one you can read straight off the source. `= 30` is an assignment; `: str` is not. An assignment creates something. An annotation is a claim *about* a name, and writing a claim about a name has never been the same as binding it.

## Two independent registers

If `name` isn't on the class, the `str` still went somewhere:

```python
print(Employee.__annotations__)
# {'name': <class 'str'>, 'age': <class 'int'>}

print({k: v for k, v in vars(Employee).items() if not k.startswith('__')})
# {'age': 30, 'company': 'Repute'}
```

Two dictionaries, and they overlap only where a line happened to do both jobs:

| field | in `__annotations__`? | has a value? |
|---|---|---|
| `name` | yes | **no** |
| `age` | yes | yes |
| `company` | **no** | yes |

> [!info] Neither is a subset of the other. Anything that wants a complete picture of a class's fields has to read **both** — the annotations alone miss `company`, the namespace alone misses `name`

This is the same `__annotations__` from concept 1, in a second location. It also exists on modules:

```python
# at the top of a file
API_KEY: str
```

Same behaviour — the module's `__annotations__` records it, and no variable is created.

> [!important] **`__annotations__` is a separate register sitting alongside the thing it describes**, not a property of the attributes themselves. That's why it can describe a field the class doesn't have. Far from being a defect, this is what makes a class body usable as a *declaration of shape* — you write down what the fields are and what they hold, without having to give any of them a value.

## When the type doesn't exist yet

A node points at another node of the same kind. Say that directly:

```python
1  class Node:
2      value: int
3      parent: Node
```

```
$ python3 node.py
    parent: Node
            ^^^^
NameError: name 'Node' is not defined
```

The class body runs top to bottom *before* Python finishes building the class. **On line 3, `Node` is still under construction — the name isn't bound yet**, so the lookup fails and the class is never created.

The fix is quotes:

```python
1  class Node:
2      value: int
3      parent: "Node"
```

```python
print(Node.__annotations__)
# {'value': <class 'int'>, 'parent': 'Node'}
```

It works for exactly the reason concept 1 established: Python evaluates whatever follows the colon and files the result without checking it's a type. Evaluating a string literal just yields the string — **nothing is looked up, so nothing can fail.**

But notice what's now in the dictionary. `value` holds the real `int` class; `parent` holds four characters of text:

```python
raw = Node.__annotations__
print(isinstance(raw['value'], type))    # True
print(isinstance(raw['parent'], type))   # False
```

## Resolving the strings

A string that spells a type is not a type. To get something usable, the name has to be looked up — and by then it exists, because the class body finished long ago. `typing.get_type_hints()` does that lookup:

```python
1  from typing import get_type_hints
2
3  print(Node.__annotations__)
4  # {'value': <class 'int'>, 'parent': 'Node'}
5
6  print(get_type_hints(Node))
7  # {'value': <class 'int'>, 'parent': <class '__main__.Node'>}
8
9  print(get_type_hints(Node)['parent'] is Node)   # True
```

Two ways of asking the same class, two different answers:

- **`__annotations__`** — what was literally written. Cheap, never fails, may hand you a string.
- **`get_type_hints()`** — the real objects, with strings looked up. Can fail, because it's the only one doing a lookup.

```python
1  class Broken:
2      thing: "NeverDefined"
```

```python
print(Broken.__annotations__)   # {'thing': 'NeverDefined'}  ← no complaint
get_type_hints(Broken)          # NameError: name 'NeverDefined' is not defined
```

Same split seen throughout this folder: **storing is safe, resolving is where reality gets checked.**

## What resolving does and doesn't check

It's tempting to read `get_type_hints()` as a validation step. It isn't, and three cases pin down exactly what it does.

Give the name a value that is itself a string:

```python
1  NeverDefined = "abc"
2
3  class A:
4      thing: "NeverDefined"
```

```
$ python3 resolve.py
NameError: name 'abc' is not defined
```

The complaint has moved. `NeverDefined` resolved perfectly well — it yielded `"abc"`, and **a string in a type position means "a name to look up"**, so resolution went round again looking for `abc`. Resolution is recursive: it chases strings until it lands on something that isn't one.

Give the name a class and it stops after one hop:

```python
1  NeverDefined = int
2
3  class B:
4      thing: "NeverDefined"
```

```
$ python3 resolve.py
{'thing': <class 'int'>}
```

And give it something that is neither a string nor a type:

```python
1  NeverDefined = 42
2
3  class C:
4      thing: "NeverDefined"
```

```
$ python3 resolve.py
{'thing': 42}
```

**No error.** It resolved to the number `42` and handed it back without comment. `42` is not a class, not a type, and meaningless as an annotation — and nothing in the pipeline cared.

> [!warning] `get_type_hints()` answers one question: **"can I find what these names refer to?"** It chases strings until it hits a non-string, then stops.
>  Whether the result makes any sense as a type is a question nobody here is asking. The only tool that would object reads the source text and never runs any of this.

## What this concept claims

**Annotations live in a separate `__annotations__` dictionary attached to the thing they describe** — a function, a class, or a module — and that dictionary is independent of whatever values actually exist.

Four consequences worth carrying forward:

1. An annotation alone binds nothing. A class body can declare a field the class does not have.
2. Annotations and values are independent registers; a complete picture needs both.
3. What's stored is whatever you wrote, evaluated once — sometimes a class, sometimes a bare string when quotes were needed to get past a name that didn't exist yet.
4. `get_type_hints()` turns those strings into objects and is therefore the step that can raise — while still checking nothing about whether the result is a sensible type.
