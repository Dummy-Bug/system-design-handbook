# The constructors of `String`

Six of them, and each answers *"I have this — how do I get a `String` from it?"*

| # | Constructor | Creates |
|---|---|---|
| 1 | `new String()` | an **empty** `String` object on the heap |
| 2 | `new String(String literal)` | an equivalent `String` object **on the heap** for the given literal |
| 3 | `new String(StringBuffer sb)` | an equivalent `String` for the given `StringBuffer` |
| 4 | `new String(StringBuilder sb)` | an equivalent `String` for the given `StringBuilder` |
| 5 | `new String(char[] ch)` | an equivalent `String` for the given char array |
| 6 | `new String(byte[] b)` | an equivalent `String` for the given byte array |

> [!info] **`String`, `StringBuffer` and `StringBuilder` are brothers.** Constructors 3 and 4 exist because conversion between them is a routine need — small differences between the three classes, and a way across each boundary.

## Constructor 5 — from a char array

A string **is** a sequence of characters, so a group of characters should convert directly.

```java
char[] ch = {'j', 'a', 'v', 'a'};
String s = new String(ch);
System.out.println(s);
```

Measured on JDK 25:

```
java
```

The four characters are grouped into one string.

## Constructor 6 — from a byte array

Same idea, but the bytes are read as character codes.

First, a check you should not need to think about: **what is the range of `byte` in Java?** **−128 to +127.**

```java
byte[] b = {97, 98, 99, 100};
String s = new String(b);
System.out.println(s);
```

Do **not** answer `97 98 99 100`. Those byte values are converted into their corresponding characters — 97 is the code for lowercase `a`, 98 is `b`, and so on. (Lowercase `a` is 97, uppercase `A` is 65.)

Measured on JDK 25:

```
abcd
```

---

# The methods

Around fourteen, and these are the ones used constantly.

## 1 · `public char charAt(int index)`

Returns the character located at the specified index. **Indexing is zero-based.**

```java
String s = "durga";
System.out.println(s.charAt(3));
```

```
d  u  r  g  a
0  1  2  3  4
```

Measured: `g`.

And out of range:

```java
System.out.println(s.charAt(30));
```

Index 30 does not exist — only 0 to 4 — so you get a runtime exception, `StringIndexOutOfBoundsException`. Measured on JDK 25:

```
java.lang.StringIndexOutOfBoundsException: Index 30 out of bounds for length 5
```

> [!warning] **The message text has changed since the recording.** In the Java 6/7 era this read `String index out of range: 30`. Modern JDKs give `Index 30 out of bounds for length 5`, which also tells you the length. The **exception type is unchanged**, so any question asking *which* exception is raised has the same answer. Verified on JDK 25.

## 2 · `public String concat(String str)`

Joins another string on the end and **returns a new object** — remember that the original is never modified.

```java
String s = "durga";
s = s.concat("software");
System.out.println(s);
```

Measured: `durgasoftware`.

**The `+` and `+=` operators do the same job.** All three of these are equivalent:

```java
s = s.concat("software");
s = s + "software";
s += "software";
```

All three measured on JDK 25 give `durgasoftware`. `concat` is a method; `+` and `+=` are overloaded operators meant for concatenation. Use whichever reads better.

## 3 · `public boolean equals(Object o)`

Content comparison, and **case is significant**. This is the overriding version of `Object`'s `equals()`.

```java
String s = "DURGA";
System.out.println(s.equals("durga"));
```

Measured: `false`. The letters match; the case does not.

## 4 · `public boolean equalsIgnoreCase(String s)`

Content comparison where **case is ignored**. Unlike `equals()`, this one is **not** an override of anything — it is a method specially designed for `String`.

```java
String s = "DURGA";
System.out.println(s.equalsIgnoreCase("durga"));
```

Measured: `true`.

> [!important] **The example that fixes which is which: username and password.**
> A **username or email** may be typed in any case — Gmail does not care whether you type it in uppercase or lowercase. Validate it with **`equalsIgnoreCase()`**.
> A **password** is always case-sensitive — which is exactly why a stray Caps Lock costs you a login attempt. Validate it with **`equals()`**.

So `String` has **two** equality methods: one where case counts, one where it does not.

## 5 · `public boolean isEmpty()`

Checks whether the string has **zero characters**.

```java
System.out.println("".isEmpty());        // true
System.out.println("durga".isEmpty());   // false
```

Both measured as shown.

## 6 · `public int length()`

The number of characters in the string.

```java
String s = "durga";
System.out.println(s.length());          // 5
```

### The trap — `length()` versus `length`

```java
String s = "jobs4times";
System.out.println(s.length);            // compile-time error
```

Measured on JDK 25:

```
C.java:4: error: cannot find symbol
        System.out.println(s.length);
                            ^
  symbol:   variable length
  location: variable s of type String
```

> [!important] **`length` is a variable and belongs to arrays. `length()` is a method and belongs to `String`.** Swap them either way and you get a compile-time error:
>
> ```java
> int[] x = {10, 20, 30, 40};
> System.out.println(x.length);     // ✅ 4      — variable, arrays
> System.out.println(x.length());   // ❌ error  — arrays have no such method
> System.out.println(s.length());   // ✅ 5      — method, String
> System.out.println(s.length);     // ❌ error  — String has no such variable
> ```
>
> Certification exams ask this directly, in both directions.

## 7 · `public String replace(char old, char new)`

Replaces **every** occurrence of the old character with the new one.

```java
String s = "ababab";
System.out.println(s.replace('a', 'b'));
```

Measured: `bbbbbb`. Every `a` became a `b`.

## 8 · `public String substring(int begin)`

Returns the substring from the begin index **to the end of the string**.

```java
String s = "abcdefg";
System.out.println(s.substring(3));
```

Index 3 is `d`, so from `d` onwards. Measured: `defg`.

> [!info] **The tagline he uses to remember `abcdefg`** comes from a Telugu film titled *Balu* — *"a boy can do everything for a girl"* — which was popular enough that people immediately produced reversed versions of it. Whether the original or the reversal is the truer statement he leaves open.

## 9 · `public String substring(int begin, int end)`

Returns the substring from the begin index to **`end − 1`**.

> **`end − 1` is the important word.** The end index is exclusive.

```java
String s = "abcdefg";
System.out.println(s.substring(3, 6));
```

3 to 6 means 3 to **5**, so `def`. Measured: `def`.

And on `ashoksoft`, measured: `substring(5)` → `soft`, `substring(3, 7)` → `okso`.

> [!warning] **The method name is `substring`, all lowercase.** Writing `subString` with a capital `S` — which looks right, since Java uses camelCase for compound names — is a compile-time error: `cannot find symbol`. It is treated as a **single word**.

## 10 · `public int indexOf(char ch)`

Returns the index of the character. Two rules attached:

- If the character is **not present**, it returns **`−1`**.
- If the character occurs **multiple times**, it returns the **first** occurrence.

```java
String s = "durga";
System.out.println(s.indexOf('g'));      // 3
System.out.println(s.indexOf('z'));      // -1

String t = "babab";
System.out.println(t.indexOf('a'));      // 1  — first 'a', not the later one
```

All three measured as shown.

## 11 · `public int lastIndexOf(char ch)`

The mirror image — the index of the **last** occurrence, and again `−1` if absent.

```java
String t = "babab";
System.out.println(t.lastIndexOf('a'));  // 3
```

Measured: `3`.

> [!info] **There is no `secondIndexOf`.** Asked for the second, third or fourth occurrence, the answer is that the API covers the common cases only — first and last. Anything else you write yourself.

## 12 · `public String toLowerCase()` · 13 · `public String toUpperCase()`

Convert every character in the string to lower or upper case respectively, returning a new string.

---

# 14 · `trim()`, and the case study that motivates it

This one gets a section of its own, because the reason for it is a genuine bug rather than a definition.

## The application

A greeting program. It reads a city name and responds in that city's style.

```java
import java.util.*;

class Test {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("enter your city name : ");
        String name = sc.nextLine();

        if (name.equals("hyderabad")) {
            System.out.println("hello hyderabadi, adab");
        }
        else if (name.equals("chennai")) {
            System.out.println("hello madrasi, vanakkam");
        }
        else if (name.equals("bangalore")) {
            System.out.println("hello kannadiga, namaskara");
        }
        else {
            System.out.println("please enter a valid city name");
        }
    }
}
```

The product is only available in three cities, so covering only three is the requirement, not an oversight. Typed in lowercase, it works perfectly.

**And yet there are two bugs in it** — logical mistakes, not coding mistakes. If they were coding mistakes the program would not run at all. Show this to any real-time expert, or push it to live, and both will surface.

## Bug one — the end user is not a software engineer

Who types the city name? **The end user.** And they may type `Hyderabad`, `HYDERABAD`, or `HyDeRaBaD`. Your program compares against lowercase only.

Measured: entering `Hyderabad` with a capital H gives `please enter a valid city name`. Same for `Chennai` and `Bangalore`.

> [!important] **You cannot blame the end user.** They are not a software engineer and do not know that case matters. Handling it is the programmer's job.

**Two fixes, and the second is better.**

*Fix one* — replace `equals()` with `equalsIgnoreCase()`. Correct, but it must be done in **three** places.

*Fix two* — normalise the input once, on the way in:

```java
String name = sc.nextLine().toLowerCase();
```

**One line instead of three.** Whatever case is typed, it becomes lowercase before any comparison, and the rest of the program is untouched.

## Bug two — the leading and trailing spaces

Even with case fixed, one problem remains, and it is the more dangerous of the two.

Some users type a space or two before the city name. Or after it. Your program then compares `"  hyderabad"` against `"hyderabad"`, finds no match, and rejects a perfectly valid city.

Measured: with one leading space, `please enter a valid city name`. With three trailing spaces, the same. Any number of spaces at either end breaks it.

Again — **not the user's fault.** They do not know that a space is significant.

**The fix is `trim()`:**

> `public String trim()` — removes blank spaces present at the **beginning** of the string and at the **end** of the string.

```java
String name = sc.nextLine().toLowerCase().trim();
```

Measured after the fix: `   HYDeRabad   ` with leading and trailing spaces and mixed case is accepted and answers `hello hyderabadi, adab`. Same for the other two cities.

## The catch, and it is examined heavily

> [!important] **`trim()` removes blank spaces at the beginning and at the end — but *not* in the middle.**

```java
String s = "durga soft";
System.out.println(s.length());
System.out.println(s.trim().length());
```

Count the characters: `d-u-r-g-a` is five, the space is six, `s-o-f-t` takes it to **ten**. There are no spaces at either end, so `trim()` has nothing to remove — and the space in the middle is not its business.

Measured on JDK 25:

```
10
10
```

**Both are ten.** This exact shape appears in certification questions, and the expected wrong answer is 9.

> [!warning] **`trim()` has a modern replacement, and the difference is not cosmetic.** `trim()` dates from Java 1.0 and removes any character **≤ U+0020** — which includes control characters that are not spaces at all. **`strip()`, added in Java 11**, removes whatever `Character.isWhitespace()` considers whitespace, which is the Unicode-aware answer.
>
> Measured on JDK 25, wrapping `ab` in each character:
>
> | Character | `isWhitespace` | `trim()` removes | `strip()` removes |
> |---|---|---|---|
> | `U+0020` space | true | ✅ | ✅ |
> | `U+001F` unit separator | true | ✅ | ✅ |
> | `U+2003` em space | true | ❌ | ✅ |
> | `U+3000` ideographic space | true | ❌ | ✅ |
> | `U+00A0` no-break space | **false** | ❌ | ❌ |
>
> So `trim()` silently leaves the wide Unicode spaces that a user pasting from a document will actually produce. **Prefer `strip()` in new code.** Note the last row: the non-breaking space is not whitespace by definition, so *neither* method removes it — a real source of confusion when cleaning pasted input. Everything Durga Sir teaches about `trim()` remains exactly true; `strip()` is an addition, not a correction.
>
> Java 11 also added **`isBlank()`** — true for a string that is empty *or* only whitespace — which is usually what the city-name check actually wanted.

---

# What this part established

| | |
|---|---|
| Constructors of `String` | **six** — empty, literal, `StringBuffer`, `StringBuilder`, `char[]`, `byte[]` |
| `new String(byte[])` converts | byte values to their **character codes** — `{97,98,99,100}` → `abcd` |
| `charAt(i)` out of range | **`StringIndexOutOfBoundsException`** at runtime |
| Concatenation | `concat()`, `+` and `+=` all do the same thing |
| `equals()` | content comparison, **case matters** — use for passwords |
| `equalsIgnoreCase()` | content comparison, **case ignored** — use for usernames |
| `length` versus `length()` | **variable for arrays**, **method for `String`** — swapping either way is a compile error |
| `substring(b, e)` returns | from `b` to **`e − 1`** — the end is exclusive |
| `indexOf` / `lastIndexOf` | first / last occurrence, **`−1`** if the character is absent |
| `trim()` removes | blank spaces at the **beginning and end only** — **never the middle** |
