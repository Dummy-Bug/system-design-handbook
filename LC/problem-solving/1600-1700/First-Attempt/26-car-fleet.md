# 26 — Car Fleet

- **Link:** https://leetcode.com/problems/car-fleet/ (LC 853)
- **Dealt:** 2026-06-24 (replenishment deal #27)
- **Result:** ❌ **Socratic walk-through (editorial-level help) → NO REP**
- **Bucket (target):** **Monotonic-Stack ★** → stays **1/2**
- **AR / slot:** ~55.9% / Q2

## Clean-status note — two independent reasons no rep
1. **Editorial-level help.** Stuck >30m on a vague "merge-intervals-ish" idea, then the entire approach
   (arrival-time reframe + front-to-back running-max) was derived **with me leading Socratically** → not self-derived.
2. **Mechanic mismatch — this was a mono-stack MIS-PICK.** Car Fleet's honest solution is a **running-max scan**
   (one variable), NOT a load-bearing stack — any stack here collapses to its top element. Same disease as
   **#19 max-width-ramp** (sort-dodge) and the over-model habit [[lc-index-bookkeeping-overmodel]]. Even a clean
   solo AC would **not** have credited Mono-Stack. → **Mono-Stack stays 1/2**; the real 2nd rep is owed on a problem
   where the stack is actually load-bearing (carried #9 max-chunks, or Asteroid-Collision / Car-Fleet-II cross-band).

## The solution (running-max, O(n log n) sort + O(n) sweep, O(1) extra)
Each car reduces to ONE scalar — its **unobstructed arrival time** `t = (target − pos) / speed`. A car **behind**
joins the fleet ahead iff `t_behind ≤ t_ahead` (equality = arrives together = same fleet, per the problem).
Sort by **position descending**; sweep front→back holding `lead = max arrival time seen so far`:
- `t > lead` → slower than everything ahead, can never catch → **new fleet**, `lead = t`.
- `t ≤ lead` → catches the fleet ahead, clamps to its speed → **merges**, `lead` unchanged.

`lead` is just the running max ⇒ the "stack" is a decoy ⇒ one variable suffices.

## Why position (not arrival time) drives the sort — the load-bearing assumption
**Position determines the catch graph; arrival time only resolves *whether* a catch happens, never *who can
catch whom*.** Catching is purely spatial: a car can only be blocked by cars **ahead** of it. Sorting by position
descending guarantees that by the time you reach a car, every car that could block it is already folded into
`lead` — zero look-back. Sort by arrival time instead and that guarantee dies (counterexample in Perturbation 2).

## Step 2 / Step 3
- **Worked example (the merge case):** target 10 · Car A pos 0 spd 10 → `t=1.0` · Car B pos 5 spd 1 → `t=5.0`.
  Position-desc order: B(5) → fleet#1, lead 5; A(1) → `1 ≤ 5` merges. **1 fleet** ✓ (A is behind+fast, catches B).
- **Edges:** single car → 1; empty → 0; two cars with **equal** arrival time → one fleet (use `>` not `≥`);
  positions guaranteed **unique** (Map<pos,speed> only safe because of this); behind-car slower than all ahead
  → its own fleet.

## ⚠ WA-landmine — float precision (the real lesson of this solve)
Submitted `float` and it AC'd, but that's **test-data luck, not safety**:
- Arrival times reach ~`10⁶` (speed 1). `float` ≈ **7 significant digits** (relative precision) → at magnitude
  `10⁶` essentially **nothing left for the fraction** (gap between adjacent floats ≈ 0.1). Two distinct true times
  can collapse to the same float → flips a merge/split decision.
- Smallest possible gap between two **distinct** arrival times: `|a/s₁ − b/s₂| = |a·s₂ − b·s₁| / (s₁·s₂) ≥
  1/(s₁·s₂) ≈ 10⁻¹²` (numerator is a nonzero integer ⇒ ≥ 1). That gap is **astronomically below** float's
  resolution ⇒ a forcing input exists *in principle*; LC just ships none.
- **`double`** (~15–16 sig figs) shrinks the risk hugely; **integer cross-multiplication** removes it entirely:
  `t_i > t_lead  ⟺  (target−pos_i)·speed_lead > (target−pos_lead)·speed_i`, products up to ~`10¹²` ⇒ use **long**.
  Store `lead` as a `(num, den) = (target−pos, speed)` pair. **This is the cleanest canonical form** ([[lc-revise-to-cleanest-form]]).

## Perturbation debrief ([[lc-perturbation-debrief]])
1. **"Cars can't pass" → deleted.** Position drops out entirely; problem collapses to trivial counting. ⇒ **all**
   of Car Fleet's difficulty lives in the no-pass blocking rule, and that rule is *also* what forces sorting by
   position. (Under can-pass, "fleet" stops being physically forced — it becomes a definitional choice:
   define fleet = same arrival time → answer = #distinct times; else → answer = n.)
   ⚠ In the **real** problem (no-pass), two cars arriving at the same instant **ARE** one fleet — don't carry the
   can-pass ambiguity back.
2. **Sort by arrival time instead of position.** Breaks: arrival-time order put a fast **rear** car "first" and
   treated it as a fleet leader, double-counting. Counterexample = the Step-2 case (gives 2, truth is 1).
   Confirms position is the only valid sort key.

## Credit
Mono-Stack **stays 1/2** (Socratic help + mechanic mismatch). Flagged as a mono-stack **mis-pick** alongside #19.
Not counted in band clean-rate (guided solve). Retire from queue; do **not** re-deal.
