# Stack Atom 06 — notes

## Daily Temperatures (LC 739) — the announced rep

For each day, find how many days until a strictly warmer one. The naive solution is, for each `i`, walk forward until `a[j] > a[i]`: correct but O(n²), and with `n` up to `10^5` that's ~10^10 in the worst case (a descending array, where every day scans to the end) — too slow. The monotonic stack does it in O(n), and the reason *why* it's allowed to throw work away is the entire insight.

### The load-bearing insight — domination (why O(n))

Scanning right-to-left, when we reach day `i` we permanently discard ("pop") every element already seen with `temperatures[e] <= temperatures[i]`. Why is that safe forever?

Concretely, `[70, 75, 72]`: at index 1 (`75`) we pop the `72` at index 2. Who could still want that `72`? Only days to the *left* (index 0, `70`). Day 0 looks rightward for its first warmer day; its candidates are `75` (1 step) and `72` (2 steps). The `75` is **both warmer and closer** — and to even reach the `72` you'd have to look *past* `75`, which already stops the search. So the `72`, sitting *behind a taller, closer* element, is **invisible** to everyone further left. The instant `75` appears, that `72` is dead weight.

Both halves are required and that's the part that's easy to under-state:
- `75 ≥ 72` (the new element is at least as warm), **and**
- `75` is closer to anyone on the left (it stands between them and the `72`).

Together → the `72` is *dominated* and can be dropped permanently. Because every element is dropped at most once and pushed at most once, total work is O(n). The stack stays monotonic for free: the only elements that would violate the order are exactly the dominated ones we just removed.

### The right-to-left solution (the one derived)

```java
class Solution {
    class Tuple { int temp; int index; Tuple(int t, int i){ temp=t; index=i; } }

    public int[] dailyTemperatures(int[] temperatures) {
        Deque<Tuple> stack = new ArrayDeque<>();
        int n = temperatures.length;
        int[] ans = new int[n];
        for (int i = n - 1; i >= 0; i--) {
            while (!stack.isEmpty() && stack.peek().temp <= temperatures[i]) stack.pop();
            ans[i] = stack.isEmpty() ? 0 : stack.peek().index - i;
            stack.push(new Tuple(temperatures[i], i));
        }
        return ans;
    }
}
```

The `Tuple(temp, index)` is convenient but not necessary — you can push just the **index** and look temperatures up via `temperatures[stack.peek()]`, which is the more common form (the array is right there). `<=` (not `<`) because we need *strictly* warmer: an equal temperature is dominated and must be popped, otherwise it'd be wrongly reported as the answer.

Trace `[73,74,75,71,69,72,76,73]` (right-to-left): index 7 `73`→push; 6 `76`→pop 73, ans 0; 5 `72`→top 76, ans `6-5=1`; 4 `69`→top 72, ans 1; 3 `71`→pop 69, top 72, ans `5-3=2`; 2 `75`→pop 71, pop 72, top 76, ans `6-2=4`; 1 `74`→top 75, ans 1; 0 `73`→top 74, ans 1 → `[1,1,4,2,1,1,0,0]`. ✓

### The duality — what a pop *means* depends on scan direction

The same problem solves left-to-right, and seeing how cements the whole family. Going left-to-right you *don't* know an element's warmer day when you stand on it — so you don't answer it yet, you leave it **pending** on the stack, and resolve it later when a warmer day shows up.

`[70, 71, 72]` left-to-right, stack holds *indices of days still waiting*:
- day 0 (`70`): pending → `[0]`
- day 1 (`71`): `71 > 70` → **day 1 is day 0's answer**, `ans[0]=1`, pop 0; pending → `[1]`
- day 2 (`72`): `72 > 71` → `ans[1]=1`, pop 1; pending → `[2]`
- end: day 2 unresolved → `ans[2]=0`

So a pop here means **"I, the current element, am the answer for this popped element"** — the future resolves the past. Contrast the right-to-left version where a pop means **"discard a dominated element I'll never need"** and the *peek* reads my own answer.

| | stack holds | a pop means | answer read via |
|---|---|---|---|
| right-to-left (this rep) | future candidates (decreasing) | discard a dominated element | peek (my own answer) |
| left-to-right | past elements still waiting | resolve the popped element's answer | the pop itself |

This — *what the stack holds, in what order, and what a pop signifies* — is the monotonic-stack discriminator, and naming it correctly is 90% of any problem in the family.

### The DP-state analogy (worth keeping)

Defining a monotonic stack's invariant feels exactly like **defining DP state**: hard to come up with, but once named, the code is a cakewalk. In DP the fight is "what does `dp[i]` mean?"; here it's "what does the stack hold + what does a pop mean?". Both are loop invariants; in both, the hard 90% is *naming* the invariant and the easy 10% is typing the transition / push-pop. This is the derivation-budget thesis in action: once the invariant is a retrievable chunk, your whole budget goes to the one novel decision instead of re-deriving the machinery mid-problem.

## Perturbation findings — three knobs generate the whole family

Every monotonic-stack problem is the same invariant with one or more knobs turned. The suspicious specifics of Daily Temperatures and what each one is hiding:

1. **"warmer" = greater.** Flip the pop comparison (`<=` → `>=`) and you get **next smaller**. ("Next cooler day.")
2. **direction "next" (to the right).** Flip the scan direction and you get **previous** greater/smaller. (Right-to-left peek gives *next*; the mirror gives *previous*.)
3. **read distance `index - i`.** Read something else on the pop instead: the **value** of the neighbor (Next Greater Element 496/503), an index, or **accumulate** a quantity as you pop — this is where it gets rich (Largest Rectangle in Histogram 84 sums area as bars pop; Sum of Subarray Minimums 907 counts spans). The "what you read on a pop" knob is the one that turns simple lookups into the hard problems.

So the grid is `{next, previous} × {greater, smaller}`, and Daily Temperatures is the `(next, greater, read-distance)` cell. The disguised rep (Largest Rectangle, 84) turns knob 3 to *accumulate*, which is the real test of whether the invariant chunked.

> **Logging honesty:** the announced rep (739) was a **clean, self-derived, first-submission AC** — no hints on the solve, derived and coded cold, correct on first paste. That is a genuine ownership rep (1 of 2) for the monotonic blind-spot (rule 6B). The perturbation debrief afterward (domination's "closer" half made explicit, the left-to-right duality) was collaborative, but it is post-AC learning and does not taint the solve. One more clean self-derived AC (the disguised rep or a blind deal) completes ownership.
