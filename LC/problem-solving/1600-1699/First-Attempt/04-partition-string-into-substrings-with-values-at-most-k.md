# 04 — Partition String Into Substrings With Values at Most K

- **Link:** https://leetcode.com/problems/partition-string-into-substrings-with-values-at-most-k/
- **Band:** 1600–1699 · sealed queue · blind deal #4 · Q3 (AR 47.7%)
- **Bucket:** answer key files it **DP » String**; **OUR code = Greedy** (longest-valid-prefix), the optimal & cleaner route → credit **Greedy (owned ●)**.
- **Dealt:** 2026-06-10
- **AC:** 2026-06-10 _(25m **SUB-CAP**; algorithm self-derived)_
- **Result:** ✅ **clean first-submission AC.** Clean-rate now **3/4 (75%)** — back above the 70% bar; clean streak = 2 (#03, #04).
- **Bucket credit:** **Greedy ride-along (already owned)** → no new ownership; **DP-String stays 0/2** (not used). _(Honest asterisk: the **comprehension** was Claude-assisted — see below — so not a fully-cold rep; but the bucket is owned anyway, so no ownership stakes. Execution/clean-rate axis is legitimately clean.)_

---

## The problem
Cut `s` into contiguous chunks, each chunk's numeric value ≤ `k`; return **min #chunks**, or `-1` if impossible. Impossible ⟺ any single digit > k.

## The real difficulty was COMPREHENSION, not the algorithm
~10 min lost misreading the spec — chased a "same number can't repeat across substrings" red herring; the unexplained `-1` example (`"238182", k=5`) wasn't understood. Claude clarified **the spec only** (contiguous partition; chunk value ≤ k; minimize; `-1` if a single digit > k) — *not* the approach. Once the read was right, the algorithm was a 5-line afterthought. **This problem is the live proof: for this one, understanding the problem WAS the thing** (AR 47.7% is a comprehension tax, not an algorithm tax).

## Approach — Greedy (self-derived)
Longest-valid-prefix: extend the current chunk by one digit while value stays ≤ k; when the next digit would exceed k, cut and start a new chunk. Provably optimal (exchange argument: a longer prefix chunk only leaves a shorter, easier remainder → never forces more cuts).

## Solution (clean first-AC)
```java
public int minimumPartition(String s, int k) {
    long curr = 0;
    int parts = 1;
    for (char ch : s.toCharArray()) {
        int digit = ch - '0';
        if (digit > k) return -1;          // -1 edge handled up front
        long next = curr * 10 + digit;
        if (next <= k) curr = next;
        else { parts++; curr = digit; }
    }
    return parts;
}
```

## WINS worth reinforcing (the learning stuck *within the session*)
1. **Minimal structure — anti-over-model.** One `long curr` + one `int parts`. No stack, no array. This is the **exact opposite of #03 push-dominoes** (same session), where the instinct was a stack of tuples. Here the "do I need a structure, or just a running variable?" reflex fired correctly. ✅ [[lc-index-bookkeeping-overmodel]] counter-move applied.
2. **`long curr` + `digit > k` first.** Used `long` to hold the rolling value (no overflow) and checked the single-digit-> k edge up front (the `-1`). Carry-over from #02's overflow/edge lesson — applied without being told. ✅

## Greedy-vs-DP judgment (banked)
Greedy is safe here because **"grab as much as you can now" never hurts later** (max prefix → easier remainder). DP (`dp[i] = min over valid last chunk of dp[j]+1`) would also work but is heavier — overkill. The discriminator to keep: *"does grabbing the most now ever cost me later?"* No → greedy; unsure → DP as the safe fallback. (Opposite trap to #03: there = over-model; the mirror trap = greedy-ing where greedy is wrong.)

## Lesson
For comprehension-tax problems, the **pre-code "reproduce every example (chase the weird one)" ritual** is the whole game — if your reading can't produce the `-1`, your reading is wrong. Algorithm here was trivial once the spec was correct.

## PENDING
- Perturbation debrief — Socratic in chat first, then logged ([[lc-perturbation-before-write]]). No probes pre-written.
- Revision Day+14: re-derive greedy cold; re-state why greedy is optimal here + the greedy-vs-DP discriminator.
