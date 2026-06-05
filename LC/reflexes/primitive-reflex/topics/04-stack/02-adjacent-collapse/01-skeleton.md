# Stack Atom 02 — Adjacent-collapse / resolve-against-top

*2026-06-05 07:11*

## The problem (Remove All Adjacent Duplicates, LC 1047)

Given a lowercase string, repeatedly remove any two **adjacent equal** letters. A removal can make new neighbors equal, so you keep going until no adjacent pair remains. Return the final string. `"abbaca"` → `"ca"`.

## ① Trigger

Each incoming element interacts with the **most recent survivor**: they may annihilate, merge, or cancel. After a removal the two elements that were separated become newly adjacent and may interact again — the interaction **cascades**.

## ② Motivation — the ladder (simpler tool first, then break it)

1. **Two-pointer + removed-set** — mark removed indices, on a match step back to the previous survivor. To find "previous survivor" you scan backward over removed slots → O(n²) worst case (`"aaaa…"`).
2. The scan-back is the waste: you only ever touch the **last** survivor, and after a pop the new last is the one *before* it. That is exactly LIFO → a **stack**.
3. Survivors can repeat (`"aba"` keeps two `a`s), so a *set* of survivors is wrong — order and multiplicity matter → stack, holding the survivors themselves.

So the stack is the minimal structure that gives O(1) "most-recent survivor" + O(1) "drop it and expose the one before".

## ③ The move

- read element → compare with `peek` (the last survivor)
- interacts (here: equal) → pop (annihilate)
- doesn't interact → push
- end → the stack **is** the answer, in order

For `char` survivors, a `StringBuilder` is the cleanest stack — `charAt(len-1)` = peek, `deleteCharAt(len-1)` = pop, `append` = push, and `toString()` is already in order (no reverse).

```java
StringBuilder sb = new StringBuilder();
for (char ch : s.toCharArray()) {
    int n = sb.length();
    if (n == 0 || sb.charAt(n - 1) != ch) sb.append(ch);   // no interaction → push
    else sb.deleteCharAt(n - 1);                            // equal → annihilate
}
return sb.toString();
```

## ④ Costumes

- Equal pair annihilation — Remove All Adjacent Duplicates (1047).
- k-run annihilation — Remove All Adjacent Duplicates II (1209): payload becomes `(char, count)`, pop the entry when `count == k`.
- Sign/magnitude collision — Asteroid Collision (735): pop-rule is collide-and-destroy, not equality.
- Path normalization — Simplify Path (71): `..` pops the last dir, `.`/`""` no-op, else push.

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| matching (#1) | matching pairs/validates and returns a boolean; collapse keeps the survivors as the answer, and an element can survive |
| plain dedup (set / two-pointer) | works only when removals don't cascade; the moment a removal creates a new interaction you need the stack |

## ⑥ Reflex check

Prompt: *each element fights the last survivor, removals chain — move?*
Answer: *push survivors on a stack; on interaction pop the top; cascade is automatic because the new top is the prior survivor. Payload carries exactly what the pop-decision needs (presence / count / sign+magnitude).*
