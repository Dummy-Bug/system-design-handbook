# Stack Atom 05 — notes

## Decode String (LC 394) — the announced rep

The job is to expand `k[encoded]` where `encoded` itself can contain more `k[...]` to any depth. `"3[a2[c]]"` is `3` copies of `a` followed by `2` copies of `c` — i.e. `a` then `cc`, the whole thing tripled: `accaccacc`. The defining difficulty is the **arbitrary nesting** — the moment a bracket can sit inside another bracket, no fixed number of variables can hold the state, because you don't know in advance how deep it goes.

### The two dead ends (worth keeping, they're instructive)

**Right-to-left scan.** Tempting idea: read from the end, prepend characters, and when you hit `[` look left for the digit and repeat. It dies on **multi-digit counts** — `"100[a]"` — because the digit you peek at isn't the whole number, and reconstructing the full multi-digit count while walking backwards is awkward. Left-to-right accumulation (`num = num*10 + d`) is the natural direction for reading numbers, which is a quiet hint that the scan should go forward.

**Recursion sketch with no return position.** "If letter, `s + f(i+1)`; if digit, repeat" collapses because a recursive call over a nested bracket has to tell its caller *where the matching `]` was* so the parent can resume after it. Without returning that index, the parent re-reads the child's characters. Recursion *can* solve this (see the equivalence section), but only if each call returns both the decoded chunk **and** the resume index — which is exactly the bookkeeping the explicit stack makes disappear.

### Deriving it by breaking the simpler tool

Strip the nesting first. For `"3[a]2[bc]"` two variables are plenty: a current string `sb` and a current number `num`. Read `3` → `num=3`; `[` → remember to repeat; build `a`; `]` → `sb += a×3`; reset; and so on. One pass, no stack at all.

Now nest it: `"3[a2[c]]"`. Trace with just those two variables and watch the collision. You read `3`, hit `[`, start building `sb="a"`, read `2`, then hit the **inner** `[`. At that instant `sb="a"` and `num` is about to be needed for the child (`2`), but the child needs `sb` to start empty. The single `sb`/`num` can represent only one level. So at every `[` you must **save the parent's (count, partial-string) somewhere and start the child fresh**, then at the matching `]` **restore the parent and fold the finished child into it**. Saved-and-restored in last-opened-first-closed order is a stack. That's the whole atom: the stack holds **one partial result per open level**.

### What to push, and the fold formula

At a `[`, the two things you already know are the **count just read** and the **prefix already built at this level** — push them together as one unit (they were both true at this same instant; they are not independently stacked). Reset `sb` and `num`, build the child. At the matching `]`, pop that pair and fold:

```
sb = prefix + (sb × count)
```

The count multiplies **only the bracket's inside**; the prefix is concatenated in front and **not** repeated. The counterexample that nails this: `"ab3[c]"` decodes to `"abccc"` (prefix `ab`, then `c×3`). The wrong formula `(prefix + inside)×count` would give `(ab+c)×3 = "abcabcabc"` — it repeats the `ab` too. So prefix and count are different roles: the prefix is finished parent text that never gets touched again, the count belongs to this bracket and repeats only its contents.

```java
class Solution {

    class Tuple {
        int count;
        String s;
        Tuple(int freq, String string) { count = freq; s = string; }
    }

    public String decodeString(String s) {
        Deque<Tuple> stack = new ArrayDeque<>();
        int num = 0;
        StringBuilder sb = new StringBuilder();

        for (char ch : s.toCharArray()) {
            if (Character.isDigit(ch)) {
                num = num * 10 + ch - '0';                 // multi-digit
            } else if (ch == '[') {
                stack.push(new Tuple(num, sb.toString())); // save (count, prefix)
                sb = new StringBuilder();                  // child starts fresh
                num = 0;
            } else if (ch == ']') {
                Tuple top = stack.pop();
                StringBuilder inside = new StringBuilder(sb);
                for (int i = 1; i < top.count; i++) sb.append(inside);  // sb = inside×count
                sb.insert(0, top.s);                       // prefix + inside×count
            } else {
                sb.append(ch);                             // letter
            }
        }
        return sb.toString();
    }
}
```

Note on the repeat loop: `sb` already holds one copy of `inside`, so appending `inside` a further `count-1` times yields exactly `count` copies. `sb.insert(0, prefix)` then prepends the saved parent text.

### Step 2 — worked example `"2[ab3[c]]"`

Stack shown top→bottom.

| read | action | sb | stack |
|---|---|---|---|
| `2` | num=2 | `""` | |
| `[` | push (2,""); reset | `""` | (2,"") |
| `a b` | append | `"ab"` | (2,"") |
| `3` | num=3 | `"ab"` | (2,"") |
| `[` | push (3,"ab"); reset | `""` | (3,"ab") (2,"") |
| `c` | append | `"c"` | (3,"ab") (2,"") |
| `]` | pop (3,"ab"): `sb = "ab" + "c"×3` | `"abccc"` | (2,"") |
| `]` | pop (2,""): `sb = "" + "abccc"×2` | `"abcccabccc"` | |

Result `"abcccabccc"`. The pairing is the subtle part: count `3` is welded to prefix `"ab"` because both were true at the inner `[`; popping `3` with the bottom prefix `""` would be the classic mismatch.

### Step 3 — edge cases

1. Multi-digit count `"100[a]"` → 100 `a`s — handled by `num*10 + d`, the reason the scan goes left-to-right.
2. No brackets `"abc"` → `"abc"` — falls straight through the letter branch, stack never used.
3. Prefix before a bracket `"ab3[c]"` → `"abccc"` — the prefix-not-repeated case; `sb.insert(0, prefix)` keeps `ab` out front.
4. Adjacent brackets `"2[a]3[b]"` → `"aabbb"` — each `]` fully resets, so the second group starts clean.
5. Deep nesting `"2[2[2[a]]]"` → 8 `a`s — stack depth grows with nesting; nothing special needed.

## Why a stack here, when everyone's instinct is recursion — the equivalence

This is the real lesson of the atom, so it's worth stating plainly: **recursion and the explicit stack are the same machine.** If your instinct on a nested problem was "recurse," that instinct was *correct* — recursion runs on the call stack, and the call stack is a stack. The iterative solution above is just that call stack written out by hand. The mapping is exact:

- the recursive **call** on an inner `[...]` = **push** at `[` (save the caller's locals — here the `(count, prefix)` — and enter a fresh frame),
- the recursive **return** from that call = **pop** at `]` (restore the caller's locals and fold the returned value in),
- the function's **local variables** = the `(num, sb)` you carry, one live set per frame, the rest parked on the stack.

So "think of a stack" and "think of recursion" are not two competing ideas — they are one idea, and the only choice is whether to let the language manage the stack (recursion) or manage it yourself (explicit stack). The cue that fires *both* is identical: **a structure that nests to arbitrary, unknown depth with matched delimiters.** Whenever you must remember "where was I in the parent when I descended into the child," and resume parents last-opened-first, that LIFO memory is a stack — appearing either as recursion's call stack or as an explicit one.

Why pick the explicit stack here rather than recursion? For a single left-to-right parse it's usually cleaner, because recursion would have to thread the *resume index* back to the caller (the exact thing that sank the recursion sketch above). The explicit stack processes the whole string in one forward pass and the resume position is implicit in "keep scanning." Both are O(n); choose by which bookkeeping is lighter.

**And why not backtracking?** Backtracking is for problems with *choices* — try an option, undo, try another, search a space of possibilities. Decode String has **no choices**: there is exactly one decoding, fully determined by the input. With nothing to try-and-undo, backtracking's machinery is dead weight. The discriminator: backtracking ⇔ a search over alternatives; fold-up ⇔ a single deterministic walk over a nested structure. Seeing "nested + deterministic, one answer" should point at fold-up (stack/recursion), and seeing "branching decisions, many candidates" at backtracking.

## Basic Calculator I (LC 224) — the disguised rep (fold-up with a different fold operator)

The problem: evaluate an expression of non-negative integers, `+`, `-`, `(`, `)`, and spaces. **No `*` or `/`.** `"(1+(4+5+2)-3)+(6+8)"` → `23`. The trap is to import the precedence machine from atom #4 — but **224 has no precedence at all.** Only `+` and `-` appear, and they're the same level evaluated left-to-right, so a level's value is just a running total. What makes it non-trivial is *only* the parentheses → nesting → fold-up. So 224 is the cleanest possible fold-up: the fold operator is "add the child's value into the parent with the saved sign."

### The version derived first — a stack of terms (simulation-faithful)

The instinct that worked: treat the whole expression as a flat list of signed terms, and let a `(` open a sub-list. Push every finished term `(num, sign)`; push a **marker at `(` carrying the sign that sat in front of the parenthesis**; at `)` pop-and-sum back to the marker, multiply that inner sum by the marker's group sign, and push it back as a single term; sum the whole stack at the end.

```java
class Triplet {
    int num; int sign; boolean marker;   // marker entry stores the group sign in `sign`
    Triplet(int num, int sign, boolean marker){ this.num=num; this.sign=sign; this.marker=marker; }
}
public int calculate(String s) {
    Deque<Triplet> stack = new ArrayDeque<>();
    int num = 0, sign = 1;
    for (int i = 0; i < s.length(); i++) {
        char c = s.charAt(i);
        if (Character.isDigit(c)) {
            num = num * 10 + (c - '0');
        } else if (c == '+' || c == '-') {
            stack.push(new Triplet(num, sign, false));      // finish a term
            num = 0; sign = (c == '+') ? 1 : -1;
        } else if (c == '(') {
            stack.push(new Triplet(0, sign, true));          // marker carries group sign
            num = 0; sign = 1;
        } else if (c == ')') {
            stack.push(new Triplet(num, sign, false));
            num = 0;
            int inner = 0;
            while (!stack.peek().marker) { Triplet t = stack.pop(); inner += t.sign * t.num; }
            int groupSign = stack.pop().sign;                // pop marker
            stack.push(new Triplet(inner, groupSign, false));// fold child into parent
            sign = 1;
        }
    }
    stack.push(new Triplet(num, sign, false));
    int ans = 0;
    while (!stack.isEmpty()) { Triplet t = stack.pop(); ans += t.sign * t.num; }
    return ans;
}
```

Two bugs got fixed on the way to this (both worth keeping, they recur): (1) the **digit-flush** — an earlier version finished a term on *every* non-space char, which split `"2147483647"` into ten single-digit terms (and corrupted `op` into a digit char). A term is finished **only** at `+ − ) end`, never at a digit. (2) **double-handling** — `(`/`)` are also non-digit/non-space, so a stray flush block fired on them too; the `if/else-if` chain must own each char exactly once.

### The canonical reduction — two variables `(result, sign)`

The term-stack is the fold-up *wearing extra clothes*: it stores every term and re-sums, when a level only ever needs its **running total** and the **sign in front of it**. Fold each number in immediately and the stack shrinks to holding only suspended outer levels — O(n) space → **O(depth)**.

```java
public int calculate(String s) {
    Deque<Integer> stack = new ArrayDeque<>();
    int result = 0, sign = 1, num = 0;
    for (int i = 0; i < s.length(); i++) {
        char c = s.charAt(i);
        if (Character.isDigit(c)) {
            num = num * 10 + (c - '0');
        } else if (c == '+' || c == '-') {
            result += sign * num; num = 0;
            sign = (c == '+') ? 1 : -1;
        } else if (c == '(') {
            stack.push(result); stack.push(sign);     // save the suspended parent level
            result = 0; sign = 1;
        } else if (c == ')') {
            result += sign * num; num = 0;
            result = stack.pop() * result + stack.pop();  // sign on top, then parent result
        }
    }
    return result + sign * num;
}
```

The one load-bearing line is `result = stack.pop() * result + stack.pop()`. At `(` we pushed `result` then `sign`, so `sign` is on top: the first `pop()` is the sign, the second is the parent result, evaluated left-to-right → `sign×inner + parent` = the fold `parent + savedSign×child`. Swapping the pops breaks it.

The term-stack maps onto this line by line: "push a term" → `result += sign*num`; the `(` marker → `push(result); push(sign)`; the `)` collapse-loop+re-push → the single fold line (nothing to re-collapse, the parent sits right on top); sum-the-stack → `return result + sign*num` (only the trailing number is left).

### The recursion identity, made literal

This is the harvest of the whole atom. In the two-variable form: **`(` = a recursive call** (save the caller's locals `result, sign`, descend into a fresh level), **`)` = the return** (restore the caller's locals, fold the returned value in). The locals are exactly `(result, sign)`. The stack now holds nothing but suspended call frames — one per open paren. The hand-rolled term-stack was doing the call stack's job, just smeared across many entries.

## Perturbation findings — the fold *operator* is the only thing that varies

The suspicious specific across this whole atom is the fold operation, and it is the single line that changes while the skeleton (carry per-level state, save on open, fold child on close) stays fixed:

- Decode String (394): child is a string, fold = **repeat `×count` and prepend the prefix**.
- Basic Calculator I (224): child is an int, fold = **add with the saved sign**.
- Score of Parentheses (856): fold = **double / sum siblings** (`()`→1, `(A)`→2A, `AB`→A+B).
- Number of Atoms (726): child is a count-map, fold = **multiply child counts by the group multiplier and merge into the parent map** — the hardest costume.

And the *other* load-bearing specific in 224 is what it omits: `*` and `/`. Their absence is exactly why a level is a flat running sum with no precedence. Add them back and you cross from pure fold-up into **fold-up ⊕ atom #4 precedence** = Basic Calculator III (772): the per-level evaluation is no longer a running sum but a sum-of-terms (227's `*//` handling), wrapped in the same save-on-`(`/fold-on-`)` scaffolding. So 772 = atom #5 skeleton with atom #4 as the per-level fold.

> **Logging honesty:** both reps are **guided**. Decode String's approach was hint-assisted (right-to-left and recursion-sketch dead ends corrected; the fold formula surfaced via the `"ab3[c]"` counterexample), code self-written. Basic Calculator I's term-stack architecture was **self-derived**, but the precedence-is-absent realization, the sign-fold (`2-(3+1)` counterexample), and the digit-flush bug were all assisted, and the canonical two-variable reduction was shown, not derived. So this is acquisition, not a cold ownership rep — the cold certificate for atom #5 is owed on a Phase-2 blind deal (a fold-up problem derived end-to-end with no hints).
