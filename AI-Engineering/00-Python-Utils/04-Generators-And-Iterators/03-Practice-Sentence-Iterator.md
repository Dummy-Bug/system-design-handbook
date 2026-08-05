#python #generators #iterators #practice #python-utils


A practice problem for the protocol from the previous note, and a good one — it's small enough to hold in your head and it walks straight into the trap that note ended on.

## The problem

Build a `Sentence` object that takes a string of words. Looping over it should yield the words one at a time. Ignore punctuation; split on whitespace alone.

```python
my_sentence = Sentence('This is a test')

for word in my_sentence:
    print(word)
```

```
This
is
a
test
```

Write it twice: once as a class, once as a generator function.

> [!tip] **Stop here and write both before reading on.** The class version needs three methods and one piece of state, and the whole point of the exercise is having tried to place them yourself. Reading a solution produces the feeling of understanding without the ability to reproduce it.

## The class, done directly

The protocol says: `__iter__` must return an iterator, and an iterator needs `__next__` plus a position it remembers. Defining `__next__` on the class itself lets `__iter__` just return `self`:

```python
class Sentence:
    def __init__(self, sentence):
        self.words = sentence.split()
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.words):
            raise StopIteration
        index = self.index
        self.index += 1
        return self.words[index]
```

```python
my_sentence = Sentence('This is a test')
for word in my_sentence:
    print(word, end=' ')
# This is a test
```

The `__next__` body is the part worth reading slowly. It saves the current index into a local, advances the stored one, then returns the word at the **saved** index — so the value handed back is the one for this call while the state is already pointing at the next. Swap those two lines and the first word is skipped.

Because the object is its own iterator, `next()` works on it directly:

```python
s = Sentence('This is a test')
print(next(s), next(s))   # This is
```

That's a correct implementation of the spec as written. It's also, as a design, wrong — and this problem is a much better illustration of why than the range example was.

## Where it breaks

```python
print([w for w in my_sentence])   # []
```

The second loop is empty. `self.index` is already past the end and nothing resets it.

Nested loops are worse, since both levels share the one position:

```python
s = Sentence('a b c')
print([(x, y) for x in s for y in s])
# [('a', 'b'), ('a', 'c')]
```

Two pairs. The same comprehension over a plain list of those words gives nine.

> [!important] **A sentence is a collection, not a stream.** The previous note's rule applies exactly here: return `self` from `__iter__` when the object represents a one-time flow of data — a socket, a cursor, a file being consumed. A sentence is a fixed thing you might reasonably want to read twice, count the words in, or loop over inside another loop. Making it its own iterator means the object *is used up* by the first `for` loop, which is not a property any reader would expect from something called `Sentence`.

## The class, done properly

The words are already in a list, and a list knows how to produce fresh iterators. So delegate — the entire class collapses to this:

```python
class Sentence:
    def __init__(self, sentence):
        self.words = sentence.split()

    def __iter__(self):
        return iter(self.words)
```

```python
s = Sentence('This is a test')
print([w for w in s])   # ['This', 'is', 'a', 'test']
print([w for w in s])   # ['This', 'is', 'a', 'test']

s2 = Sentence('a b')
print([(x, y) for x in s2 for y in s2])
# [('a', 'a'), ('a', 'b'), ('b', 'a'), ('b', 'b')]
```

Both loops work, nesting works, and the index bookkeeping is gone entirely — `iter(self.words)` hands back a brand-new `list_iterator` on every call, each with its own position.

One consequence is worth being explicit about, because it looks like a regression and isn't:

```python
next(s)
# TypeError: 'Sentence' object is not an iterator
```

That's correct now. `Sentence` is **iterable but not an iterator**, exactly like a list — and exactly like a list, you get an iterator from it when you want one:

```python
print(next(iter(s)))   # This
```

> [!info] If the words aren't already sitting in a list — say they're being read lazily from somewhere — `__iter__` can be written as a generator instead. It returns a fresh generator per call, so re-iterability is preserved:
> ```python
> class Sentence:
>     def __init__(self, sentence):
>         self.words = sentence.split()
>
>     def __iter__(self):
>         for word in self.words:
>             yield word
> ```
> Same behaviour: looping twice works, because each `for` loop calls `__iter__` again and gets its own generator.

## The generator function

The second half of the problem, and it's four lines:

```python
def sentence(text):
    for word in text.split():
        yield word
```

```python
for word in sentence('This is a test'):
    print(word, end=' ')
# This is a test
```

`__iter__`, `__next__`, the position, and the `StopIteration` are all supplied for you. Compare that against the ten-line class and the reason generators get reached for first is not subtle.

The one thing to stay aware of: a generator *is* its own iterator, so it has the single-use property the broken class had.

```python
g = sentence('This is a test')
print([w for w in g])   # ['This', 'is', 'a', 'test']
print([w for w in g])   # []
```

The difference is that this is honest about what it is. `sentence(...)` names a *process*, and calling it again is free:

```python
print(list(sentence('This is a test')))
```

Whereas `Sentence(...)` names a *thing*, and a thing that empties itself when read is a surprise.

## One detail in `split()`

`text.split()` with no argument is not the same as `text.split(' ')`, and the difference shows up the moment input isn't perfectly formatted:

```python
text = 'This  is   a test'

print(text.split())
# ['This', 'is', 'a', 'test']

print(text.split(' '))
# ['This', '', 'is', '', '', 'a', 'test']
```

```python
padded = '  hello world  '

print(padded.split())
# ['hello', 'world']

print(padded.split(' '))
# ['', '', 'hello', 'world', '', '']
```

The no-argument form splits on *runs* of any whitespace — spaces, tabs, newlines — and discards leading and trailing ones. Passing `' '` explicitly splits on each single space, producing empty strings between consecutive spaces. For splitting text into words, the no-argument form is almost always the one you want.

## The four versions

| | Re-loopable | Nested loops | Lines |
|---|---|---|---|
| class returning `self` | no | broken | 10 |
| class returning `iter(self.words)` | yes | yes | 5 |
| class with a generator `__iter__` | yes | yes | 6 |
| generator function | no — but cheap to recreate | n/a | 3 |

The takeaway isn't that one of these wins. It's that **`__iter__` returning `self` is a commitment**, and this problem is a clean case of making it by accident: the direct application of the protocol produces working code, passes the stated test, and quietly breaks the second time anyone loops over it.
