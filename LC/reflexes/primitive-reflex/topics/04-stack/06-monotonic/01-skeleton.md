# Stack Atom 06 — Monotonic stack ★

*2026-06-06 17:55*

## The problem (Daily Temperatures, LC 739)

Given daily `temperatures`, return `answer` where `answer[i]` = number of days to wait after day `i` for a **warmer** day (0 if none). `[73,74,75,71,69,72,76,73]` → `[1,1,4,2,1,1,0,0]`. `n ≤ 10^5`.

## ① Trigger

For each element you need the **nearest element to one side that is greater (or smaller)** — "next warmer day," "next greater element," "previous smaller," "how far until something bigger." The brute force is, for each `i`, scan outward until you find it: O(n²). The signal for a monotonic stack is exactly this *"nearest larger/smaller on one side, for every element"* shape at n large enough that O(n²) dies.

## ② Motivation — why a monotonic stack (break the simpler tool)

Brute force re-scans the same elements over and over. The waste: when you're standing on a tall element, every shorter element *behind* it (already passed) is **invisible** to anything further along — they hit the tall one first. So shorter-element-behind-a-taller-closer-one is dead weight that never needs to be re-examined. A stack that **drops dominated elements the moment a dominating one appears** examines each element O(1) amortized — each is pushed once and popped once → **O(n)**. The stack stays *monotonic* precisely because every element that would break the order is exactly the dominated one you discard.

## ③ The move

Define the invariant first (this is the whole atom — like defining DP state): **what the stack holds, in what order, and what a pop means.** Two equivalent framings for "next greater":

- **Right-to-left** (this rep): stack holds *future candidates* in decreasing-from-bottom order. At `i`, pop everything `<= a[i]` (dominated), then the top (if any) is your next-greater → read its index/value; push `i`. *Pop = discard a dominated element I'll never need; peek = read my own answer.*
- **Left-to-right**: stack holds *indices still waiting for their answer*. At `i`, while `a[i] >` top's value, pop `j` and set `ans[j]` using `i` (current is `j`'s next-greater); push `i`. *Pop = resolve someone else's answer; the future resolves the past.*

```java
for (int i = n - 1; i >= 0; i--) {                 // right-to-left, next-greater
    while (!st.isEmpty() && a[st.peek()] <= a[i]) st.pop();   // drop dominated
    ans[i] = st.isEmpty() ? 0 : st.peek() - i;     // peek = next warmer
    st.push(i);
}
```

`<=` (not `<`) because we want *strictly* warmer → equal temps are dominated and popped.

## ④ Costumes — the 2×2 grid (one knob each)

| Knob | Daily Temps cell | turn it |
|---|---|---|
| greater ↔ smaller | next **greater** | flip the pop comparison (`<=`→`>=`): next **smaller** |
| next ↔ previous | **next** | flip scan direction: **previous** greater/smaller |
| what you read on a pop | **distance** `idx-i` | the **value** (Next Greater Element 496/503), an index, or *accumulate* (Largest Rectangle 84, Sum of Subarray Minimums 907) |

`{next, previous} × {greater, smaller}` = the whole family; Daily Temps = (next, greater, distance).

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| adjacent-collapse (#2) | both "pop while top vs incoming," but #2's pop **merges/annihilates** the popped element (it interacts with the incoming and changes it); here the popped element just gets its **answer resolved or is discarded as dominated** — nothing merges, the array values are untouched |
| matching (#1) | #1's stack holds delimiters and a pop checks *pairing/validity*; here it holds values/indices in **sorted order** and a pop encodes an **order relationship** (nearest greater/smaller) |
| fold-up (#5) | #5 pushes once per nesting level and pops once per `)` (structure-driven, depth = nesting); here push/pop are driven by the **value ordering**, not by bracket structure |

## ⑥ Reflex check

Prompt: *for every element, nearest greater/smaller to one side — move?*
Answer: *monotonic stack. First name the invariant (what it holds + what a pop means). Right-to-left + pop-dominated-then-peek = next-greater for me; left-to-right + pop-resolves-the-popped = next-greater is current. `{next,prev}×{greater,smaller}` via scan direction + comparison; read distance/value/accumulate on the pop. O(n): each element pushed and popped once.*
