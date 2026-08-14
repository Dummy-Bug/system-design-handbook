# Control flow in try-catch-finally

The control-flow table from part 4, extended by one block — which takes it from four cases to five.

```java
try {
    statement1;
    statement2;
    statement3;
}
catch (X e) {
    statement4;
}
finally {
    statement5;
}
statement6;
```

| Case | Situation | Executed | Termination |
|---|---|---|---|
| **1** | no exception | 1, 2, 3, **5**, 6 | normal |
| **2** | exception at 2, catch **matches** | 1, 4, **5**, 6 | normal |
| **3** | exception at 2, catch does **not** match | 1, **5** | **abnormal** |
| **4** | exception at statement **4** (inside catch) | 1, **5** | **abnormal** |
| **5** | exception at statement **5** (inside finally) **or 6** | — | **always abnormal** |

**Statement 5 appears in every row where it can** — cases 1 to 4, whatever else happens. That is the entire content of this part, expressed as a table, and notice in cases 3 and 4 that `finally` runs and statement 6 does not, which is the sequence measured above. Case 5 is the exception to it in both senses: statement 5 cannot run *itself* if statement 5 is what failed, and there is no further `finally` behind it to catch the fall.

> [!info] **Case 4 is worth a second look.** An exception inside the `catch` block is unhandled — nothing is guarding the catch. The program dies. But `finally` still runs first, which is why cleanup belongs there and nowhere else.

---

# Nesting, and which combinations are legal

## Nested try-catch-finally

You can put a `try`-`catch`-`finally` inside another one, and the PDF traces **fourteen** control-flow cases through it — one for every place an exception can be raised, crossed with whether a handler matches.

```java
try {                          // ← outer try
    stmt-1;
    stmt-2;
    stmt-3;
    try {                      // ← inner try
        stmt-4;
        stmt-5;
        stmt-6;
    } catch (X e) {
        stmt-7;                // ← inner catch
    } finally {
        stmt-8;                // ← inner finally
    }
    stmt-9;
} catch (Y e) {
    stmt-10;                   // ← outer catch
} finally {
    stmt-11;                   // ← outer finally
}
stmt-12;
```

Twelve numbered statements, two `catch` blocks, two `finally` blocks. The exception types are `X` for the inner catch and `Y` for the outer one — deliberately unrelated, so "matched" always means exactly one of them.

## The fourteen cases

| Case | Raised at | Handler | Statements executed | Termination |
|---|---|---|---|---|
| **1** | nowhere | — | 1, 2, 3, 4, 5, 6, **8**, 9, **11**, 12 | normal |
| **2** | **stmt-2** | outer `catch` matches | 1, 10, **11**, 12 | normal |
| **3** | **stmt-2** | nothing matches | 1, **11** | **abnormal** |
| **4** | **stmt-5** | **inner** `catch` matches | 1, 2, 3, 4, 7, **8**, 9, **11**, 12 | normal |
| **5** | **stmt-5** | inner misses, **outer** matches | 1, 2, 3, 4, **8**, 10, **11**, 12 | normal |
| **6** | **stmt-5** | neither matches | 1, 2, 3, 4, **8**, **11** | **abnormal** |
| **7** | **stmt-7** (inner catch) | outer `catch` matches | 1, 2, 3, 4, 5, 6, **8**, 10, **11**, 12 | normal |
| **8** | **stmt-7** (inner catch) | nothing matches | 1, 2, 3, 4, 5, 6, **8**, **11** | **abnormal** |
| **9** | **stmt-8** (inner finally) | outer `catch` matches | 1, 2, 3, 4, 5, 6, 7, 10, **11**, 12 | normal |
| **10** | **stmt-8** (inner finally) | nothing matches | 1, 2, 3, 4, 5, 6, 7, **11** | **abnormal** |
| **11** | **stmt-9** | outer `catch` matches | 1, 2, 3, 4, 5, 6, 7, **8**, 10, **11**, 12 | normal |
| **12** | **stmt-9** | nothing matches | 1, 2, 3, 4, 5, 6, 7, **8**, **11** | **abnormal** |
| **13** | **stmt-10** (outer catch) | — | **11** runs, then it dies | **always abnormal** |
| **14** | **stmt-11** or **stmt-12** | — | — | **always abnormal** |

Read it in five groups rather than fourteen rows.

**Cases 1–3 — the exception is in the outer `try`, before the inner one is ever reached.** The inner block is skipped entirely, so 4 through 8 never appear. Case 2 shows the outer catch working; case 3 shows nothing matching, and even then **statement 11 still runs** before the program dies.

**Cases 4–6 — the exception is inside the inner `try`, and these are the three that teach nesting.** They differ only in who catches it:

- **Case 4**, inner catch matches → statement 7 runs, and the program carries on to statement 9 as if nothing happened. The outer catch is never consulted.
- **Case 5**, inner catch misses → statement 7 does **not** run, but statement 8 does, and control leaves the inner block for the outer catch. Statement 9 is skipped, because it is inside the outer `try` after the point of failure.
- **Case 6**, nobody matches → 8 and 11 both run on the way out, then abnormal termination.

**Cases 7–8 — the exception is inside the inner `catch`.** Nothing guards a `catch` block, so the inner construct is finished with; the exception goes straight to the outer catch. Statement 8 still runs, because the inner `finally` is owed.

**Cases 9–12 — the exception is in the inner `finally` or at statement 9.** By this point the inner construct is complete either way, so these behave exactly like cases 2–3: the outer catch matches or it does not.

**Cases 13–14 — the exception is in the outer `catch` or the outer `finally`.** There is nothing left above to handle it. Case 13 still owes statement 11, so that runs first. Case 14 has nothing owed at all, so it just dies.

> [!important] **Three rules generate all fourteen, and these are what to carry rather than the table.**
> **1.** An exception looks for a handler **innermost first**. Raised at statement 5, the inner `catch` gets first refusal; if it does not match, the outer `catch` is tried.
> **2.** **Every `finally` whose `try` was entered will run** — so a failure at statement 5 still runs statement 8 *and* statement 11, in that order, on the way out.
> **3.** If nothing matches anywhere, it is abnormal termination — but only *after* every entered `finally` has run.
>
> Everything in the table is those three rules applied to a different starting point. If you can state them, you can derive any row on the spot, which is what an interviewer is actually testing.

> [!warning] **Four rows of the PDF's table list a statement that cannot have run, and measuring the cases is how you see it.**
>
> **Cases 7 and 8** list statements **5 and 6** as executed. They cannot be — the premise is that statement 7 ran, and statement 7 is the *inner catch*, which only runs when something in the inner `try` failed. Measured, cases 7 and 8 give `1 2 3 4 8 10 11 12` and `1 2 3 4 8 11`.
>
> **Cases 9 to 12** list statement **7** as executed. It cannot be — the premise is that statements 4, 5 and 6 all completed, so the inner `catch` was never entered. Measured, case 11 gives `1 2 3 4 5 6 8 10 11 12`, with no 7.
>
> The listings are **schematic**: he is writing down every statement that appears textually above the failure point, not a path that a real run can take. **The other ten cases are exactly right**, and the three rules above are unaffected — so learn the rules, and treat those four rows as a slip in the source rather than something to memorise.

And the two notes worth carrying:

> **1.** If we do not **enter** the `try` block, the `finally` block won't be executed. Once we have entered the `try` block, we cannot come out without executing `finally`.

> **2.** The most **specific** exceptions can be handled by the inner `try`-`catch`, and **generalised** exceptions by the outer one.

That second note is the design reason to nest at all: the inner block deals with the precise failure it knows about, the outer one is the net for everything else.

## Only the most recent exception is reported

A striking consequence, and the PDF gives a program for it:

```java
try {
    System.out.println(10/0);          // ArithmeticException
} catch (ArithmeticException e) {
    System.out.println(10/0);          // ArithmeticException again
} finally {
    String s = null;
    System.out.println(s.length());    // NullPointerException
}
```

Measured on JDK 25:

```
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.length()" because "<local3>" is null
	at Recent.main(Recent.java:9)

exit code: 1
```

Three exceptions were raised. **One is reported** — the `NullPointerException` from `finally`, the most recent. The two `ArithmeticException`s are gone without trace.

> The **default exception handler can handle only one exception at a time**, and that is the **most recently raised** exception.

> [!warning] **This is exception masking, and it is a real source of lost bugs.** The original failure — the `ArithmeticException` in the `try` — is what you actually wanted to know about, and it has been silently replaced by a failure in the cleanup code. It is the same shape as the `return`-inside-`finally` problem above: **the `finally` block overwrites what came before it.**
>
> Modern Java's answer is `try`-with-resources, where an exception from closing a resource is **suppressed and attached** to the primary exception rather than replacing it — so both survive. That is part 10.

> [!info] **Notice the NPE message itself: `Cannot invoke "String.length()" because "<local3>" is null`.** That precision is **helpful NullPointerExceptions**, added in Java 14. In 2016 this line would have read only `java.lang.NullPointerException` with no explanation, and working out *which* thing was null was a manual exercise. It is on by default now, and it is one of the most useful debugging changes in modern Java.

## Which combinations compile

> 1. Whenever we write a `try` block, we must write either `catch` or `finally`. **`try` without `catch` or `finally` is invalid.**
> 2. `catch` without `try` is invalid.
> 3. `finally` without `try` is invalid.
> 4. In `try`-`catch`-`finally`, **the order is important.**
> 5. Nesting of `try`-`catch`-`finally` is possible.
> 6. **Curly braces are mandatory** for all three.

Measured on JDK 25 — each row is the whole body of `main`:

| Written | Result |
|---|---|
| `try {}` | ❌ `'try' without 'catch', 'finally' or resource declarations` |
| `catch (Exception e) {}` | ❌ `'catch' without 'try'` |
| `finally {}` | ❌ `'finally' without 'try'` |
| `try {} finally {} catch (Exception e) {}` | ❌ `'catch' without 'try'` — **order matters** |
| `try {} catch (Exception e) {} finally {}` | ✅ compiles |
| `try {} finally {}` | ✅ compiles — `catch` is optional |
| `try {} catch (Exception e) {} catch (Exception e2) {}` | ❌ `exception Exception has already been caught` |
| `try {} catch (Exception e) { try {} catch (Exception e1) {} }` | ✅ compiles — nesting is fine |

> [!important] **Row four is the one that surprises people.** `try {} finally {} catch (…) {}` fails with *`'catch' without 'try'`* — which reads oddly, since there is clearly a `try` above it. The reason is that `finally` **closes** the construct: once it appears, the `try` statement is complete, and the `catch` that follows belongs to nothing. Order is not stylistic.
>
> Note also that the `try`-alone message names **`resource declarations`** as a third way to satisfy a `try`. That is try-with-resources, and it is why `try (…) { }` with no `catch` and no `finally` is legal — part 10.

---
