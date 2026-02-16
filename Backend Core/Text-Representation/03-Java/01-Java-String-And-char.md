
## Java char Is a Storage Unit, Not a Character

In Java:

```java
char c;
```

`char` is:

> An **unsigned 16-bit storage unit**.

That’s it.

It is **not**:

- A Unicode character
    
- A user-visible symbol
    
- A grapheme
    

Java `char` corresponds to **one UTF-16 code unit**.

---

## Why char Is 16 Bits

Historical reason:

- Early Unicode fit within 16 bits
    
- Java was designed during that period
    
- Java aligned `char` with UTF-16
    

Unicode later expanded beyond 16 bits,  
but Java kept `char` unchanged for:

- Backward compatibility
    
- Performance stability
    
- Memory predictability
    

This decision is **intentional**, not accidental.

---

## What Java String Really Is

In Java:
String s = "hello";

Conceptually:

> `String` = sequence of `char`

Which means:

> `String` = sequence of **UTF-16 code units**

Java never promised:

> `String` = sequence of Unicode characters

That promise exists only in developer intuition.

---

## Why Things Usually Feel Correct

For most characters:

- 1 Unicode character
    
- 1 UTF-16 code unit
    
- 1 Java `char`
    

Examples:

- `A`
    
- `你`
    
- `ह`
    
- `ك`
    

So intuition holds **most of the time**.

That’s why the problem hides for years.

---

## Where It Breaks: Emoji and Some Symbols

Example:
Example:

`"😂"`

Unicode:

`😂 → U+1F602`

UTF-16 representation:

`[high surrogate][low surrogate]`

Java sees:

`String = 2 char values`

So:

`"😂".length() == 2`

Java is correct.  
The confusion comes from mixing layers.

## Important Consequence

Because of UTF-16:

- One Unicode character may occupy **two char**
    
- A single `char` may represent **half a character**
    

This means:

- `charAt()` is **not character-safe**
    
- Indexing can land inside a surrogate pair
    
- Iterating by `char` can split characters
    

---

## charAt() Is Code-Unit Based

`char c = s.charAt(i);`

This returns:

> One UTF-16 code unit

Not:

- A Unicode character
    
- Not what a user sees as “one symbol”
    

This is correct behavior — just often misunderstood.
