# Atom 03 — Two pointers over two sequences

Tier 1 (Pointers) · motion `→ →` ×2 (two read heads, no write head)
*Derived Socratically 2026-06-03 (Is Subsequence).*

## ① Trigger

Two separate inputs, and you walk one pointer down each, advancing based on a comparison between them. Tell vs #2: there are **two sequences**, not one array being rewritten — so there's no write head.

## ② The atom (derived — asymmetric costume)

Is Subsequence: is `s` a subsequence of `t`? Pointer `i` on `s` (needle), `j` on `t` (haystack).

- `s[i] == t[j]` → advance **both**.
- `s[i] != t[j]` → advance **only `j`**.
- Answer: `s` is a subsequence iff `i == len(s)` at the end.

Invariant: `i` = how much of `s` has been matched, in order. `j` (haystack) advances every step; `i` (needle) advances only on a match.

```java
int i = 0, j = 0;
while (i < s.length() && j < t.length()) {
    if (s.charAt(i) == t.charAt(j)) i++;   // needle moves on match
    j++;                                   // haystack always moves
}
return i == s.length();
```

## ③ Costumes (two different advance rules)

- Asymmetric (derived): one needle, one haystack — needle on match, haystack always. *Is Subsequence.*
- Symmetric + write (derived): compare, emit the smaller, advance that pointer; when one side runs out, drain the other's tail. *Merge Sorted Array, Intersection of Two Arrays II.*
  - In-place twist (LC 88): merging `b` into `a`'s trailing empty slots, fill **from the back** (place the larger at the end) so you never clobber an unplaced `a` element. Same core, reversed direction.

The family is fixed (two pointers, two sequences); only the advance rule changes.

## ④ Confusion matrix

| Confused with | Discriminator |
|---|---|
| #2 same-direction | two arrays, two read heads, no write *vs* one array, read+write building a prefix |
| #1 opposite-end | both sweep forward on separate inputs *vs* converge from two ends of one array |

## ⑤ Practice queue (both facets derived; reps to install later)

- [x] Is Subsequence (392) — asymmetric, derived 2026-06-03
- [x] Merge Sorted Array (88) — symmetric advance + in-place-from-back, derived 2026-06-03
- [ ] Intersection of Two Arrays II (350) — symmetric, sorted, dedup output (rep)
- [ ] Backspace String Compare (844) — recognition twist: two pointers scanning from the **end**

## ⑥ Reflex check

Prompt: *match/merge across two inputs — move?*
Answer: *one pointer per input; advance the haystack always and the needle on match (asymmetric), or advance the smaller element (symmetric). No write head — that's #2.*
