# Pattern-Reflex Deck

Atomic **trigger → move** cards for problem-solving framings — the same idea as `math-reflex/`, one level up the stack. Math-reflex installs *recall* ("n=20 pairs → 190"). This installs *recognition* ("this situation → that move") so a framing that cost minutes the first time costs seconds forever.

## Where cards come from

Cards are NOT mined from a corpus — the framing move lives in the *solution*, not the problem statement, so it can't be tagged from data. **Every card is born from a real solve.** After each AC, ask one question:

> "What single move would have made this instant instead of slow?"

That move becomes a card. The deck grows one problem at a time. No card is invented from intuition — it has to have cost real time on a real problem first.

## How a card graduates (same bar as math-reflex)

1. Answered in **<5 seconds**, cold — name the move, no warm-up.
2. Quizzed in **mixed order** with other cards.
3. Holds across **3 consecutive days**.

Drill the deck in the **3-minute maintenance slot** of the daily math-reflex session — mixed in with the math facts. Status markers: `◐` installing · `●` graduated.

## How a card is quizzed

Application-level, not definition-level. The prompt is a **1-line mini-scenario**; the correct answer is *naming the move* in under 5 seconds — never a full solution.

- Bad quiz: "What is candidate enumeration?" (tests memorization)
- Good quiz: "A boundary element was counted in both halves and belongs to exactly one — you want the min difference. Move?" → *"try it on each side, take min"* in <5s.

---

## Card 01 — Ambiguous assignment → enumerate the small set, take best  `◐`

**Trigger (the felt signal):**
You catch yourself reasoning "should this go *here* or *there*?" — an element, boundary, or value could plausibly be assigned more than one way, and you're trying to *deduce* which assignment is best.

**Move:**
Stop deducing. The set of valid assignments is small (2, 3, a handful). Compute the result for each, take `min` / `max`. Don't reason about which wins — *let the candidates compete*.

**Why the hesitation is the tell:**
The 5-minute cost is never the mechanics — it's failing to *recognize* you're in this situation. The moment you feel "which way is better?" is the trigger firing. Recognize it → the work collapses to "enumerate + min".

**Anchors:**
- *Split Array With Minimum Difference* (2026-05-25) — shared element counted in both halves belongs to exactly one side → `min(|lSum − shared − rSum|, |lSum − (rSum − shared)|)`. **Cost the 5 minutes that created this card.**
- *Nearest palindrome* family — the candidate is one of {P−1, P, P+1}, take the closest. Same move, 3 candidates instead of 2.

**Family:** pre-submit checklist item 9 ("single-candidate trap on nearest X — generate a small candidate set and take min, never assume one candidate covers all").

**Quiz prompt:** "An item legally fits more than one group and you want the best total. What's the move — in one breath?"
**Reflex answer:** "Enumerate the small set of assignments, take min/max. Don't reason about which."

---

## Card 02 — Can't picture the edge case? Force its condition and build the instance around it  `◐`

**Trigger (the felt signal):**
You suspect an edge case might exist, you try to *imagine* an input that hits it, you fail — and you start drifting toward "I can't construct it, so it can't happen, so I'll skip guarding against it." That slide from "can't picture it" to "doesn't exist" is the trigger. (The map-vs-set fix downstream is *not* the hard part — you already know that. The hard part is not wrongly declaring the case impossible.)

**Move:**
Don't imagine the counterexample — **derive it.** Write the condition that triggers the edge as an equation, solve for the values that satisfy it, then pad the rest of the instance with whatever keeps it legal.
- If the system is **satisfiable** → the counterexample exists; you just built it. Guard against it.
- If the system is **contradictory** → the case is genuinely unreachable; skipping the guard is now *proven* safe, not assumed safe.

**The 41-minute anchor — *Identify the Largest Outlier* (2026-05-25):**
Stuck because "I can't build an array where sum-element and outlier collide → maybe it never happens → use a Set." Construction-by-forcing instead of imagination:
1. Collision condition is `target == z` ⇔ `tSum = 3z`. Pick the trap value: `z = 7` ⇒ `tSum` forced to `21`.
2. Pad legally: plant a *real* outlier `o = 3` ⇒ sum element `s = (21−3)/2 = 9` ⇒ specials must sum to 9 and hold the single `7` → `[7, 2]`.
3. Instance: `[7, 2, 9, 3]`. `z=7` matches `x=7` against its own single self (fake); real answer `3`. **The system was satisfiable → the edge is real → freq map required.**
Note the secondary unlock: `z` in `tSum=3z` is the **loop candidate**, not "the outlier" — that conflation was half the 41 minutes.

**Why it transfers (not niche to outliers):**
`tSum=3z` is throwaway. The *method* — "translate the edge into a solvable condition, then either build it or prove it contradictory" — is how you settle *any* "can this even happen?" doubt: unreachable-state guards, overflow-only-if inputs, can-two-things-coincide questions. It replaces gut-feel "nah, won't happen" (the thing that ships WAs) with a satisfiability check.

**Family:** feeds pre-submit item 4 (set vs freq map under index-distinctness) — but this card is upstream of it: the card is *deciding the guard is needed at all*, the checklist item is the fix.

**Quiz prompt:** "You think an edge case might exist but can't imagine an input that hits it. What do you do before deciding it's safe to ignore?"
**Reflex answer:** "Write the trigger as an equation, solve it, pad to a legal instance. Satisfiable → it's real, guard it. Contradictory → proven safe."

---

## Deck status

| Card | Move | Born from | Status |
|------|------|-----------|--------|
| 01 | Ambiguous assignment → enumerate, take best | Split Array Min Diff (2026-05-25) | ◐ installing |
| 02 | Can't picture an edge case → force its condition, build/refute the instance | Largest Outlier (2026-05-25) | ◐ installing |

*(Next card slots fill as problems are solved — one move per problem, only when it cost real time.)*
