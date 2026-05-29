# Minimum Discards to Balance Inventory (cold re-solve) — Second Attempt (Cold Re-solve)

| Field | Value |
|-------|-------|
| Date | 2026-05-25 |
| Link | https://leetcode.com/problems/minimum-discards-to-balance-inventory/description/ |
| Rating | 1638 |
| Start | 12:23 |
| Note | re-solve of First-Attempt #4 (orig 60min) |

### Thinking log (verbatim)

**Step 1 — Constraints:** constraints allow up to n log n.

**Step 2 — Problem reading / disambiguation:** sample cases discard an item but feel incomplete — what if the same item appears again later with a count now below threshold? Re-read: the problem says discard an *item*, not discard an *occurrence* of an item. So once an item is discarded, all its later occurrences can be ignored — they don't contribute to the answer, it's already recorded on the first offense.

**Step 3 — Window-shrink question (self-generated edge case):** if an item is discarded, do we remove all its occurrences and shrink the window? Sample cases don't cover this. Test case: `w=5, m=2`, `[1,2,2,1,2,1]`. If discarding `2` (first offense) removes its occurrences, the window shrinks → the next `1` enters the window, its freq could exceed 2, and `1` also lands in the answer. Re-read to resolve:
- *"minimum number of arrivals to be discarded"* → we discard **arrivals**, not the whole item. So window size stays the same.
- the window represents the **last m days**, not a count of item-types kept. So if we discard on a day, nobody's count increases that day and we just shift the window right.
- this raised a worry: if we count discards for distinct arrivals, could the same item be discarded twice? Resolved by *"an item may only be discarded on its arrival day."* → once discarded (and recorded) earlier, that item can't be taken again, and the window-shrink confusion is gone — the window is the last m days regardless of what was kept.

**Step 3 (cont.) — traced answer:** for `[1,2,2,1,2,1]`, answer = 1 — from `2`'s freq exceeding the threshold; after that the window shifts right and the leftmost `1` falls out of the window.

**Step 4 — Approach (reduced form):** the whole problem reduces to a **fixed-size sliding window with counting**. Build the first window and check for discards; if an item is discarded, store it in a Set. For each next item, first check it's not already in the discarded-Set, then check its count and apply the if/else; once the window is full, keep shifting it, processing items, and eventually return the Set size. Also need a freq-count **map** alongside the Set.

**Step 4 — example/edge traces:**
- Both sample cases → working.
- `[1,1,1,1]`, m=1, w=2 → working.
- `[1]` → working.
- Max input `[10^5, …, 10^5]`: one element can hit 10^5 occurrences, m up to 10^5 — approach unchanged, already handled; no int overflow possible (counting only).

**Step 5 — First submission: WA.**

```java
public int minArrivalsToDiscard(int[] nums, int w, int m) {
    Map<Integer,Integer> map = new HashMap<>();
    Set<Integer> set = new HashSet<>();
    int n = nums.length, i = 0;
    for (int j = 0; j < n; j++) {
        int count = map.getOrDefault(nums[j], 0);
        if (count + 1 > m) {
            set.add(nums[j]);
        }
        map.put(nums[j], count + 1);
        if (j - i + 1 == w) {
            map.put(nums[i], map.get(nums[i]) - 1);
            i++;
        }
    }
    return set.size();
}
```

**Step 6 — WA diagnosis via failing case:** `[8,8,8,1,7,4,3,7,5,2]`, w=7, m=1 → my answer 2, expected 3. Re-read the statement: *"an item may only be discarded on its arrival day"* sounded like discard-the-item, but *"minimum number of arrivals to be discarded"* means discard-the-**arrival**. I'd coded the former; this case proves it's the latter. Same item can be discarded on multiple arrival days, so discards must be counted per-arrival-index, not per-item-value.

**Step 7 — Second submission: AC.** Two fixes from v1:
1. Track discards by **arrival index** (`set.add(j)`), not by item value (`set.add(nums[j])`).
2. A discarded arrival is **not kept**, so only increment the freq map in the `else` (kept) branch; and on window exit, only decrement if that index was kept (`if (!set.contains(i))`).

```java
public int minArrivalsToDiscard(int[] nums, int w, int m) {
    Map<Integer,Integer> map = new HashMap<>();
    Set<Integer> set = new HashSet<>();
    int n = nums.length, i = 0;
    for (int j = 0; j < n; j++) {
        int count = map.getOrDefault(nums[j], 0);
        if (count + 1 > m) {
            set.add(j);                       // count the arrival, not the item
        } else {
            map.put(nums[j], count + 1);      // only kept arrivals occupy a slot
        }
        if (j - i + 1 == w) {
            if (!set.contains(i)) {
                map.put(nums[i], map.get(nums[i]) - 1);
            }
            i++;
        }
    }
    return set.size();
}
```

### Outcome (Min Discards)

| Field | Value |
|-------|-------|
| Start → End | 12:23 → ~13:21 |
| Time | **58 min exact** (First-Attempt was 60 min — no speed gain on re-solve) |
| AC | Y after 1 WA |
| Verdict | **Soft fail** (WA-then-AC) |

**Root cause: problem-reading error (item vs arrival).** The entire WA was a misread of *what is being counted* — discard an *arrival/occurrence*, not a distinct *item*. This is a Step-1 ritual failure ("comprehend: what is input, output, the rule, in ONE sentence"). The one-sentence statement was wrong, so every downstream decision (`set.add(nums[j])`, unconditional count increment) inherited the error.

**WA-cause [read-error]:** misread the counted unit (item vs arrival) — wrong one-sentence rule, not an algorithm bug.

**Band tally:** 4/10 done. Clean first-submission AC: #3 only (#1, #2, #4 are WA-then-AC soft fails). Currently **1/4 clean** — below the ≥7/10 bar; the binding weakness so far is not algorithmic, it's **first submissions going out on a misread/untraced statement.**

---
