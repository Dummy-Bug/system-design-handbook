# 32 — Sentence Similarity III

- **Link:** https://leetcode.com/problems/sentence-similarity-iii/
- **Band:** 1550–1600 · Phase 2 sealed queue deal #5 · Q2 · AR ~48%
- **Bucket (revealed post-solve):** Two Pointers (string)
- **Dealt:** 2026-06-01 20:48:53 IST
- **AC:** 2026-06-02 08:34:36 IST
- **Result:** ❌→✓ **SOFT FAIL** — multiple WA before AC, ~2h total across two days (≫ 30-min cap). Does NOT count toward ownership ([[lc-no-vanilla-reps]] / derivation clause: clause exempts *time*, not WA discipline).
- **WA-cause [over-modeled]:** built a HashMap<String,Deque<Integer>> index-matching engine for a front/back two-pointer problem; every WA was a bug *inside self-invented machinery* (`s2[i]` vs `s2[j]` typo; `q.offer(index)` vs `q.offer(id)`; size bookkeeping), not a flaw in the idea.

## The trap

The intended solution is **prefix + suffix two-pointer**, O(n). The shorter sentence is "similar" iff it is a
**prefix concatenated with a suffix** of the longer one (insert one contiguous block of words into the shorter
to get the longer). User instead:
- shorter/longer chosen by **character length** (not word count) — a latent bug source.
- indexed every word of the longer sentence into a `Deque<Integer>` per word, then for each word of the shorter
  tried every candidate index and ran a `compare` helper. Overcomplicated; eventually ACed but fragile.

## WA timeline
1. **WA #1** — test `"A"`, `"a A b A"`. Offset/flag logic (`prev`, `flag`) mismodeled the insert.
2. **WA #2** — `compare` used `s2[i]` instead of `s2[j]` (wrong pointer) → mismatch on `"d T d ED uXW L U J n klIe"` vs same minus `n`.
3. **WA #3** — `q.offer(index)` re-queued the peeked index instead of the polled `id`; corrupted the deque.
4. **AC** — fixed pointer + requeue; returns true on full consumption.

## Canonical form (target for revision — own THIS, not the hashmap)

```java
public boolean areSentencesSimilar(String s1, String s2) {
    String[] a = s1.split(" "), b = s2.split(" ");
    int n = a.length, m = b.length;
    int i = 0, j = 0;
    while (i < n && i < m && a[i].equals(b[i])) i++;               // match prefix words
    while (j < n - i && j < m - i && a[n-1-j].equals(b[m-1-j])) j++; // match suffix words
    return i + j >= Math.min(n, m);                                // shorter fully consumed?
}
```

- `i + j >= min(n, m)` (not `==`): prefix and suffix scans can overlap on the shorter sentence; `>=` absorbs that.
- The `j < n - i` / `j < m - i` guards stop the suffix scan from crossing the prefix already matched.
- No hashing, no helper, no longer/shorter swap needed — symmetric in both args.

### Same algorithm, deque framing (official) — note the ROLE of the deque

```java
public boolean areSentencesSimilar(String s1, String s2) {
    Deque<String> d1 = new ArrayDeque<>(Arrays.asList(s1.split(" ")));
    Deque<String> d2 = new ArrayDeque<>(Arrays.asList(s2.split(" ")));
    while (!d1.isEmpty() && !d2.isEmpty() && d1.peek().equals(d2.peek()))     { d1.poll();     d2.poll();     } // prefix
    while (!d1.isEmpty() && !d2.isEmpty() && d1.peekLast().equals(d2.peekLast())) { d1.pollLast(); d2.pollLast(); } // suffix
    return d1.isEmpty() || d2.isEmpty();   // shorter fully consumed
}
```

- This is **the same prefix+suffix two-pointer**: front-poll = prefix pointer, back-poll = suffix pointer,
  `isEmpty() || isEmpty()` = "shorter consumed." Destructive polling removes the overlap guard and the
  shorter/longer swap for free.
- **Key contrast — deque ROLE is the whole lesson.** WA-attempt 1 here used `Map<String,Deque<Integer>>`:
  the deque stored *index lists* to look up "where else does this word occur" = **arbitrary-position lookup
  = over-model.** This official deque is a *two-ended queue you pop matching ends off* = **two-pointer.**
  Same structure, opposite role. The alarm is never "deque/map bad" — it's *what is the structure doing:*
  front/back consumption (good) vs. find-any-matching-occurrence (over-model). See cross-problem note below.

## Recurring reflex flagged (cross-problem, 2026-06-02)
Over-modeling here is **not isolated** — same `Map<key, Deque/List<index>>` "store-the-positions-and-poll-them"
reflex appeared in **#27 (find-mirror-score)** and **#29 (doubled-array)** too. See
[[lc-index-bookkeeping-overmodel]] for the full 3-problem analysis + the counter-heuristic.

## Perturbation probes
- **Operator (`==` words → matching with insert):** load-bearing fact = the inserted text is **one contiguous
  block**. That's why prefix+suffix suffices. Perturb to "insert up to *two* blocks" ⇒ this collapses; you'd need
  DP / subsequence logic. The single-block guarantee IS the problem.
- **Structure (which is shorter):** correct discriminator is **word count**, not character length. User used char
  length — happened to pass but is the kind of mismodel that bites. Survives only because prefix/suffix logic is
  symmetric once split.
- **Meta (one sentence):** "the short sentence must be a prefix and a suffix of the long one, meeting in the
  middle." If that sentence is clear, the two-pointer falls out immediately — no machinery.

## Lesson
First instinct reached for **machinery (map+deque+helper)** instead of looking for the **collapse**
(front/back two pointers). The 50% AR didn't beat the solve — the self-invented model did. Train the reflex:
*before* coding, ask "what's the simplest frame that makes this trivial?" Connects to [[lc-perturbation-debrief]]
(find the load-bearing constraint = single contiguous insert) and [[lc-revise-to-cleanest-form]].

## REVISION TARGET (Day+14)
Re-solve directly as the **prefix+suffix two-pointer** (canonical form above), from a blank file, no hashmap.
Re-answer the 3 perturbation probes from memory. Must be a sub-cap clean solve to show the reflex installed.
