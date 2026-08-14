Interview questions on **exception handling specifically**, as asked by small startups and early-stage product teams for a backend role at 3–5 years.

> [!important] **What a startup is testing here.** Nobody is going to review your error handling, and there is no on-call rota to catch what you miss. Every question below is a proxy for one worry: *will this person swallow an exception and leave us with a silent failure we cannot debug at 2am.* Plain, confident answers win. Unlike GC, this is a topic where you are expected to have opinions from your own code — they will ask what you actually do, not just what the language does.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of question frequency. This is my judgement from how often each recurs across the interview-prep sources surveyed in August 2026, weighted toward 2025–2026 material. Treat the **bands** as reliable, the order inside a band as approximate.

**Coverage markers:** ✅ covered in the note listed · ⚠️ partial · ❌ gap in our notes.

---

# Band A — expect these in almost every screen

### 1. What is an exception?

- **Tests:** the baseline opener. Near-universal.
- **Notes:** ✅ `01` — an unwanted, unexpected event that disturbs the normal flow of the program.
- **Say the second half unprompted:** the *point* of handling it is graceful termination — the rest of the program still runs. That single sentence is what separates a definition from an understanding.

### 2. Difference between `Exception` and `Error`?

- **Tests:** whether you know where the line is and why it is drawn there.
- **Notes:** ✅ `02` — two dimensions: *who caused it* (your program vs. lack of system resources) and *can you recover* (yes vs. no).
- **What loses points:** saying *"errors cannot be caught."* They can — `catch (Error e)` compiles fine. The real distinction is **recoverability**: there is nothing useful to put in the block. `09` makes this point explicitly.

### 3. Checked versus unchecked exceptions?

- **Tests:** the most-asked exception question after the opener.
- **Notes:** ✅ `03` — checked are enforced by the **compiler**; unchecked are the JVM's business at runtime.
- **The framing that lands:** a checked exception is the compiler forcing the caller to *make a decision*. `03` demonstrates both with measured compiler output rather than assertion.
- **Chained follow-up:** *"Give an example of each"* — `FileNotFoundException` and `NullPointerException` will do.

### 4. `throw` versus `throws`?

- **Tests:** a trap question dressed as a warm-up. The names are one letter apart and the meanings are unrelated.
- **Notes:** ✅ `09` keyword table, plus `07` and `08` in full.
- **The one-line answer:** `throw` hands an exception object to the JVM **now**; `throws` **delegates** the responsibility to the caller. One is an action, the other is a declaration.

### 5. What is `finally` for, and will it always run?

- **Tests:** very common, and the follow-up is where people fall over.
- **Notes:** ✅ `05` — cleanup code, and it runs whether or not an exception was raised and whether or not the catch matched.
- **The exception they are fishing for:** **`System.exit(0)`**. `05` measures it — the JVM is shut down, so there is nothing left to run the block. Say this before they ask.
- **Second answer worth having:** if you never *entered* the `try`, `finally` does not run. Entering is the condition, not reaching.

### 6. Can you have multiple `catch` blocks? Does order matter?

- **Tests:** whether you have actually written one.
- **Notes:** ✅ `04` — child to parent, always. Parent first is a **compile error**, not a warning.
- **The exact message is worth quoting:** `exception XXX has already been caught`. Naming the error verbatim reads as first-hand experience, because it is.

### 7. What is a custom exception and when would you write one?

- **Tests:** whether you have modelled a domain, or only caught what the library threw.
- **Notes:** ✅ `09` — extend `RuntimeException`, and call `super(s)` so the message reaches the stack trace.
- **The reasoning that scores:** nothing in the JVM knows that being under eighteen is a problem in *your* application. Predefined exceptions cover language-level failures; domain failures are yours to name.

### 8. What is a `NullPointerException` and how do you deal with them?

- **Tests:** the single most common exception in real Java, so they want a practical answer.
- **Notes:** ⚠️ `10` covers what it is and when it is raised; **prevention is a gap.**
- **Recency:** ⬆ **say the modern half.** Since **Java 14** the message names the exact expression that was null — `Cannot invoke "String.length()" because "<local3>" is null`. On a 2016 JDK you got a bare class name and worked it out yourself. `06` shows a measured example of the new form.

---

# Band B — common once the role touches real code

### 9. Can you write `try` on its own?

- **Notes:** ✅ `06` — no. `try` needs `catch` or `finally`, and the measured error is `'try' without 'catch', 'finally' or resource declarations`.
- **The bonus half:** the message names **`resource declarations`** as a third way to satisfy it — that is try-with-resources, which is why `try (…) { }` alone is legal.

### 10. What happens if there is a `return` in both `try` and `finally`?

- **Tests:** a classic puzzle, asked because the answer is surprising.
- **Notes:** ✅ `05`, measured — **`finally` wins**. Its return value replaces the one from `try`.
- **Add the judgement:** and that is exactly why you should not `return` from a `finally` block. It silently discards results, and it will swallow an in-flight exception the same way.

### 11. What is try-with-resources?

- **Notes:** ✅ `11` — resources declared in the parentheses are closed automatically, so you stop writing `finally { conn.close(); }` by hand.
- **The requirement to name:** the resource must implement **`AutoCloseable`**.
- **Recency:** ⬆ since **Java 9** you can list an already-declared effectively-final variable, instead of being forced to declare it inside the parentheses.

### 12. Draw the exception hierarchy.

- **Tests:** whether the pieces are connected in your head or memorised as a list.
- **Notes:** ✅ `02` and `04`, with a diagram in `04`.
- **The two facts to get right:** `Throwable` is the root and it is a **class**, not an interface. And **`RuntimeException` is a child of `Exception`** — which is why "unchecked" is a region *inside* the exception tree, not a sibling of it.

### 13. If nobody catches an exception, what happens?

- **Notes:** ✅ `02` — the seven-step walk, ending at the **default exception handler**, which prints name, description and stack trace and terminates abnormally.
- **The detail that lands:** it terminates each method on the way up and pops its frame, so nothing after the failing line runs in *any* of them. `02` proves it with exit code 1.

### 14. How do you read a stack trace?

- **Notes:** ✅ `02` — deepest frame first. Top line is *where it broke*; read down for *how you got there*.
- **Why they ask:** at a startup you are the one debugging production, and this is the cheapest possible test of whether you have done it.

---

# Band C — occasional depth probes

### 15. Can you catch an `Error`?

- **Notes:** ✅ `09` — syntactically yes, and `03`'s table confirms it compiles over any `try` because `Error` is unchecked.
- **The right answer is two-part:** yes, and you shouldn't. Being *able* to catch it does not give you anything to do in the block.

### 16. `final` versus `finally` versus `finalize`?

- **Tests:** pure vocabulary, asked because the names collide.
- **Notes:** ✅ `05`, side by side — a modifier, a block, and a method.
- **Recency:** ⬆ `finalize()` has been **deprecated since Java 9 and marked for removal since Java 18**. Mentioning that is free marks.

### 17. Should a custom exception be checked or unchecked?

- **Notes:** ✅ `09` — unchecked is the recommendation, because a checked exception forces a `throws` clause on every method above it, all the way up.
- **The nuance that reads as senior:** checked is right when the caller genuinely *can* recover and you want to force them to decide. Most of the time they cannot, which is why the industry default landed on unchecked.

### 18. What is the difference between `throw new Exception()` and `throw e`?

- **Notes:** ⚠️ `11` covers rethrowing.
- **The point:** rethrowing the caught object preserves the original stack trace. Constructing a fresh one throws that information away — which is how the real cause of a production bug disappears.

---

# Gaps this file exposes

| # | Missing from the notes | Why it matters here |
|---|---|---|
| 1 | **What to do about NPEs** — `Optional`, `Objects.requireNonNull`, null-checking discipline | Q8, and NPE is the exception they have actually been bitten by |
| 2 | **Logging practice** — what to log, log-and-rethrow as an anti-pattern | not asked directly at this tier, but it is behind Q18 and the whole "silent failure" worry |
| 3 | **Spring's `@ControllerAdvice`** — one sentence on centralised handling | any startup running Spring Boot will ask, and every one of them is |

Three gaps, and only the first is likely to be asked head-on. **Fifteen of eighteen questions are answered outright by material already on disk**, which makes this the strongest of the three chapters at startup level — largely because Durga Sir teaches exactly the fundamentals this tier asks about.
