# 06 — Reward Top K Students

- **Link:** https://leetcode.com/problems/reward-top-k-students/
- **Band:** 1600–1699 · sealed queue · blind deal #6 · Q2 (AR 47.1%)
- **Bucket:** answer key files it **Heap (+Hashing)**; **OUR code = bounded size-`k` min-heap** (evict-smallest) → credit **Heap**.
- **Dealt:** 2026-06-11
- **AC:** 2026-06-11 08:26 _(20m **SUB-CAP**; self-derived)_
- **Result:** ✅ **clean first-submission AC, self-derived.** → **Heap 1/2** (carried 0/2 debt opened). Clean-rate now **5/6 (83%)**; clean streak = 4 (#03, #04, #05, #06).
- **Honest note on difficulty:** vanilla / soft rep — flagged at deal time. Filed in the queue's *"Standard application (clean reps)"* tier, not the trickiness tier. The problem's only tax is **spec-parsing + tie-break bookkeeping** (comprehension, like #04), not the algorithm. Heap is **not load-bearing** here — a plain sort + take-`k` is the same complexity. Counts as a legit Heap rep anyway (the bounded-heap idiom *was* exercised), but it's a soft one.

---

## The problem
`positive_feedback` / `negative_feedback` are word lists. Each `report[i]` (space-separated words) belongs to `student_id[i]`. Per report: +3 per positive word, −1 per negative word. Rank students by **points desc, then id asc**; return the top `k` ids.

## Approach — score via two word-sets, keep top-`k` in a bounded min-heap (self-derived)
1. Dump `positive_feedback` / `negative_feedback` into two `HashSet<String>` for O(1) membership.
2. For each report: split on space, sum +3 / −1 per word.
3. Push `{score, id}` into a **size-bounded min-heap**; whenever `size > k`, poll the head (the current worst), so the heap always holds exactly the top `k`.
4. Drain + reverse → highest rank first.

## Solution (clean first-AC)
```java
class Solution {
    public List<Integer> topStudents(String[] positive_feedback,
                                     String[] negative_feedback,
                                     String[] report,
                                     int[] student_id,
                                     int k) {
        Set<String> positive = new HashSet<>();
        Set<String> negative = new HashSet<>();
        for (String s : positive_feedback) positive.add(s);
        for (String s : negative_feedback) negative.add(s);

        // min-heap on (score asc, then id desc) → head = current worst → evict it
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> {
            if (a[0] != b[0]) return a[0] - b[0];
            return b[1] - a[1];
        });

        for (int i = 0; i < report.length; i++) {
            int score = 0;
            for (String word : report[i].split(" ")) {
                if (positive.contains(word)) score += 3;
                else if (negative.contains(word)) score -= 1;
            }
            pq.offer(new int[]{score, student_id[i]});
            if (pq.size() > k) pq.poll();
        }

        List<Integer> ans = new ArrayList<>();
        while (!pq.isEmpty()) ans.add(pq.poll()[1]);
        Collections.reverse(ans);
        return ans;
    }
}
```

## The tie-break logic (the one careful part)
Min-heap, so the **head is the worst element** and is what gets evicted / polled first.
- **Different scores:** `a[0]-b[0]` → ascending → lowest score at head → evicted first. ✓ (keep high scores)
- **Equal scores:** `b[1]-a[1]` → the **larger id** sits at the head → evicted first. ✓ Lower id ranks higher, so evicting the larger id is exactly right.
- **Final order:** draining pops worst→best; for tied scores the larger id pops first, lands earlier in `ans`, then `reverse` pushes it later → within a tie, **smaller id ends up first**. Matches "id asc". ✓

## WINS
1. **Bounded size-`k` heap** — never holds more than `k`, so it's O(n log k) not O(n log n). The "I only need the top k, so cap the heap" reflex fired. ✅
2. **Two-set scoring** — O(1) membership instead of scanning the feedback arrays per word. Clean.
3. **Tie-break got the direction right first try** — the min-heap-evicts-head + reverse-at-end reasoning is the easy place to flip a sign; didn't. ✅ (this *is* the careless-bug surface this band is about, and it stayed clean.)

## Complexity
Let `n` = #reports, `L` = total words across reports. Sets: O(P+N). Scoring: O(L). Heap: O(n log k). Drain: O(k log k). **Total O(P + N + L + n log k).**

## Lesson
- **Bounded heap when you only need top-`k`** — cap at `k`, evict the worst (the min, for a "largest-k" query). O(n log k) beats sort's O(n log n) and beats an unbounded heap.
- **Min-heap head = the element you're willing to throw away.** Set the comparator so the *worst-by-your-ranking* floats to the head; for a "smaller-is-better tie-break" that means ordering the tie key **descending** in the min-heap.
- Same "is the structure load-bearing?" axis as #03/#04 — here it isn't (sort works); shipped the heap as the intended-bucket rep, eyes open.

## PENDING
- Perturbation debrief — Socratic in chat first, then logged ([[lc-perturbation-before-write]]). No probes pre-written.
- Revision Day+14: re-derive the bounded-min-heap top-`k` idiom cold; re-state the tie-break direction (why id desc inside a min-heap) from scratch.
