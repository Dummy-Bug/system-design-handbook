### #27 — Find Mirror Score of a String
**Link:** https://leetcode.com/problems/find-mirror-score-of-a-string/
**Date attempted:** 2026-05-30
**Rating:** 1550–1600 band (Phase 2 — sealed queue, deal-list #2)
**AC at:** 2026-05-30 __:__ IST _(self-debugged)_
**Time:** 44 min total — WA on first submission, AC on second (over cap)
**Status:** ❌→✓ **WA-then-AC = SOFT FAIL** (derivation clause exempts time, not implementation discipline; rep does NOT count toward ownership)
**Pattern (debrief):** Stack (with-string) · Hashing — Q2, AR 35.8%

---

**Attempt 1 (WA):**
- Failing test: `"zadavyayobbgqsexaabk"` → got `13`, expected `18`.

**Solution code (attempt 1, WA):**

```java
class Solution {

    Map<Integer,Deque<Integer>> map = new HashMap<>();

    public long calculateScore(String s) {

        int n = s.length();
        long count = 0L;

        for (int i = 0; i < n; i++){

            char ch = s.charAt(i);

            int original = ch - 'a';
            int mirrored = 'z' - 'a' - original;

            if (map.containsKey(mirrored)){

                Deque<Integer> stack = map.get(mirrored);
                int j = stack.pop();
                count = count + i - j;

                if (stack.isEmpty()){
                    map.remove(mirrored);
                }else{
                    map.put(mirrored,stack);
                }
            }else {
                Deque<Integer> stack = new ArrayDeque();
                stack.push(i);
                map.put(original,stack);
            }

        }
        return count;
    }
}
```

**WA-cause [logic-overwrite]:** the `else` branch (no live mirror) always did
`stack = new ArrayDeque(); map.put(original, stack)` — so when a second occurrence
of a letter arrived **before** its mirror consumed the first, the new stack
**clobbered** the existing one, dropping the earlier index. Unmatched same-letter
indices must accumulate, not replace. (Failing case: repeated letters whose mirrors
come later — only the most recent index survived, undercounting → 13 vs 18.)

**Fix:** in the `else`, reuse the existing stack if `map.containsKey(original)`,
else create a fresh one, then push and put back.

**Attempt 2 (AC) — fixed code:**

```java
class Solution {

    Map<Integer,Deque<Integer>> map = new HashMap<>();

    public long calculateScore(String s) {

        int n = s.length();
        long count = 0L;

        for (int i = 0; i < n; i++){

            char ch = s.charAt(i);

            int original = ch - 'a';
            int mirrored = 'z' - 'a' - original;

            if (map.containsKey(mirrored)){

                Deque<Integer> stack = map.get(mirrored);
                int j = stack.pop();
                count = count + i - j;

                if (stack.isEmpty()){
                    map.remove(mirrored);
                }else{
                    map.put(mirrored,stack);
                }
            }else {
                Deque<Integer> stack;
                if (map.containsKey(original)){
                    stack = map.get(original);
                }
                else {
                    stack = new ArrayDeque();
                }
                stack.push(i);
                map.put(original,stack);
            }

        }
        return count;
    }
}
```

**Note:** since the map already holds a live `Deque` reference, the `map.put(...,
stack)` calls after pop/push are redundant (mutating in place suffices) — harmless.

**Lesson:** when keying a stack/list of pending indices by a value, the "create
new" branch must be `computeIfAbsent`-style (reuse if present), never an
unconditional fresh container. Classic last-writer-wins clobber.

---

**Shorter / canonical version (array of 26 stacks — no Map):**

The letters form a fixed 26-element universe, so use `Deque<Integer>[26]` indexed
`0..25` instead of a `HashMap`. This kills every `containsKey`/`get`/`put`/`remove`
AND makes the clobber bug *structurally impossible* (`st[c].push(i)` mutates the
slot in place — no fresh-vs-reuse decision to get wrong).

```java
class Solution {
    public long calculateScore(String s) {
        Deque<Integer>[] st = new ArrayDeque[26];
        for (int i = 0; i < 26; i++) st[i] = new ArrayDeque<>();

        long count = 0;
        for (int i = 0; i < s.length(); i++) {
            int c = s.charAt(i) - 'a';
            int m = 25 - c;                       // mirror of c
            if (!st[m].isEmpty()) count += i - st[m].pop();
            else st[c].push(i);
        }
        return count;
    }
}
```

What collapsed vs the AC version:
- `Map<Integer,Deque>` → `Deque[26]` (fixed tiny key universe → array, not map).
- The fresh-vs-reuse `else` branch vanishes → the WA bug can't recur.
- `'z'-'a'-original` → `25 - c`; dropped the `isEmpty → map.remove` cleanup
  (empty deque in a slot is free).
- Loop body is 5 lines; only tax is the 26-slot pre-init (generic array can't
  auto-fill).

> **⏳ REVISION TARGET:** on revise, the goal is to **re-derive THIS array-of-26-stacks
> form from scratch**, not the Map version. Reproducing the bugged/verbose original
> does NOT count as a clean revision rep. (Applies retroactively to past problems too —
> revise toward the cleanest known form, see [[lc-revise-to-cleanest-form]].)

