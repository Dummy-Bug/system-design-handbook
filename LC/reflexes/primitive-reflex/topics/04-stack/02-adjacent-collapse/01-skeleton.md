# Stack Atom 02 — Adjacent-collapse / resolve-against-top

Stack family · *Derived Socratically 2026-06-03 (Remove All Adjacent Duplicates).*

## ① Motivation (easy case → break it)

Remove adjacent equal pairs.

- **Non-cascade** (remove once, don't re-check newly-formed pairs): `"abbaca"` → drop `bb` → `"aaca"` and stop. No stack needed — one-pass lookahead pairing:
  ```java
  StringBuilder sb = new StringBuilder();
  int i = 0;
  while (i < s.length()) {
      if (i + 1 < s.length() && s.charAt(i) == s.charAt(i + 1)) i += 2; // drop pair
      else { sb.append(s.charAt(i)); i++; }                            // keep
  }
  ```
- **Cascade** (LC 1047 — newly-formed pairs also go): `"abbaca"` → `"ca"`. The `i+1` lookahead can't see survivors collapsing behind it → forced up to a stack.

## ② Trigger — the discriminator is the word "cascade"

"Remove once / no re-check" → plain scan. **"Keep collapsing until stable" / "newly adjacent pairs also go" / "repeatedly"** → stack (resolve-against-top). The tell: survivors can interact with *future* incoming elements.

## ③ The atom

Process left→right, keep survivors on a stack. Each incoming element **interacts with the top**: cancel/collapse → pop; otherwise → push. The top is always the most-recent survivor, so cascades resolve for free (after a pop, the new top is the correct neighbor).

```java
StringBuilder sb = new StringBuilder();          // SB used as the stack
for (char c : s.toCharArray()) {
    int n = sb.length();
    if (n > 0 && sb.charAt(n - 1) == c) sb.deleteCharAt(n - 1); // pop: cancels
    else sb.append(c);                                          // push: survives
}
return sb.toString();
```

Trace `"abbaca"`: `a→"a"`, `b→"ab"`, `b→"a"`, `a→""`, `c→"c"`, `a→"ca"`. ✓

## ④ Costumes (the interaction isn't always "equal cancels")

- Equal pair cancels — Remove All Adjacent Duplicates (1047/1209).
- Collision, asymmetric survivor — Asteroid Collision (735): who pops depends on size/direction.
- `..` pops a directory, names push — Simplify Path (71).
- Case-mismatch (`aA`) cancels — Make String Great (1544).

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| #1 matching | pop just *checks a pair*; here pop *resolves an interaction* and the survivors **are** the answer |
| plain scan (non-cascade) | no cascade → `i+1` lookahead, no stack; cascade → stack |

## ⑥ Reflex check

Prompt: *collapse adjacent things, and collapsing can cascade — move?*
Answer: *stack of survivors; each incoming resolves against the top (pop if it cancels, else push); cascades handled for free.*
