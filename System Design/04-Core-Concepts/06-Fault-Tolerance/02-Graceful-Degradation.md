> [!info] Graceful Degradation = when a component fails, return something useful rather than total failure.

The alternative — failing completely when any part breaks — is almost always worse for the user.

---

## The Fallback Spectrum

Every fault tolerant system has a **degradation ladder** — a sequence of fallbacks from best to worst:

**Netflix example:**

```
┌─────────────────────────────────────────────────────┐
│ Level 1 — Everything working                        │
│ Show personalised recommendations for this user     │
├─────────────────────────────────────────────────────┤
│ Level 2 — Personalisation service down              │
│ Show generic popular titles (Top 10 in your region) │
├─────────────────────────────────────────────────────┤
│ Level 3 — Recommendation service fully down         │
│ Show cached recommendations from 1 hour ago         │
├─────────────────────────────────────────────────────┤
│ Level 4 — Cache also unavailable                    │
│ Show static homepage with featured titles           │
├─────────────────────────────────────────────────────┤
│ Level 5 — Complete failure                          │
│ Show error page with status update                  │
└─────────────────────────────────────────────────────┘
```

The user gets something useful at every level except the last.

---

## The Reliability Tradeoff

> [!warning] Graceful degradation deliberately trades reliability for availability.

```
Full reliability + full availability → impossible when a component fails

Pick one:
  Stay reliable  → return nothing until correct data is available  (less available)
  Stay available → return generic or cached data                   (less reliable)
```

Graceful degradation **consciously chooses availability** over perfect reliability in that moment.

---

## When It's Acceptable — and When It's Not

> [!important] Not every system can degrade gracefully. The decision depends on what "wrong data" costs.

| System | Graceful Degradation | Reason |
|---|---|---|
| Netflix recommendations | ✅ Yes | Generic titles are fine — user can still watch |
| Instagram Stories | ✅ Yes | Missing Stories bar is annoying, not damaging |
| Zomato menu prices | ❌ No | Showing ₹0 is dangerous — user places order at wrong price |
| Bank balance | ❌ No | Showing wrong balance is unacceptable |
| Payment processing | ❌ No | Must fail hard rather than charge wrong amount |

**The rule:** If wrong data causes financial loss, legal liability, or safety issues — **fail hard, don't degrade**.

---

## How to Design It

When designing a system, explicitly ask for each component:

> *"If this component fails, what's the best thing we can show instead?"*

```
Component fails          → Fallback
─────────────────────────────────────────────
Personalisation service  → Generic popular content
Search service           → Cached results from last hour
Payment gateway          → Show error, do NOT degrade (money involved)
Image CDN                → Show placeholder image
Live score service       → Show last known score with "updating..." label
```

> [!tip] Interview framing
> *"I'd design graceful degradation for non-critical paths — recommendations, search suggestions, social features. For anything involving money or user data correctness I'd fail hard rather than return potentially wrong data."*
