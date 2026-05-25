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

## Deck status

| Card | Move | Born from | Status |
|------|------|-----------|--------|
| 01 | Ambiguous assignment → enumerate, take best | Split Array Min Diff (2026-05-25) | ◐ installing |

*(Next card slots fill as problems are solved — one move per problem, only when it cost real time.)*
