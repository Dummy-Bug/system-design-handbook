# Adversarial test construction — solve, don't guess

> [!info] To construct a test case that breaks your solution, don't *guess* inputs and check — *solve* algebraically for inputs that satisfy the bug condition. This is how top coders find edge cases the problem author missed.

---

## Why this is a meta-skill

Most learners construct edge cases by **trial and error** — pick a random array, run through their solution, hope to find a break. This is slow and unreliable.

Top coders construct edge cases by **algebraic derivation**:

> "I want X to happen (the bug). What constraint does X impose on the input? Now solve for any input that satisfies that constraint."

This converts a *search problem* (try random inputs) into a *solve problem* (work backwards from the bug condition). The construction is deterministic, fast, and guaranteed to produce a failing case.

---

## The three-step recipe

### Step 1: Identify the bug condition

What internal state would cause the solution to produce wrong output? Express it as an equation or inequality.

Example (outlier problem):
> Bug: `set.contains(target)` returns true even though the only occurrence of `target` is the outlier candidate itself.
>
> Condition: `target == nums[i]` AND `count(target) == 1`.

### Step 2: Translate to input constraints

Substitute the algorithm's derivation into the bug condition. Solve for input properties.

Example continued:
> `target = (tSum - nums[i]) / 2`
>
> Setting `target = nums[i]`:
> `nums[i] = (tSum - nums[i]) / 2`
> `2 * nums[i] = tSum - nums[i]`
> `3 * nums[i] = tSum`
> `nums[i] = tSum / 3`
>
> So: one element must equal `tSum/3`, appearing exactly once.

### Step 3: Construct a minimal array satisfying the constraints

Build the smallest valid input from scratch.

Example continued:
> I want a valid configuration first: `specials = [1, 4]`, `sum_element = 5`, `outlier = X`.
> Array: `[1, 4, 5, X]`, tSum = `10 + X`.
>
> I want value `4` to be the fake. So `4 = tSum/3 = (10 + X)/3` → `X = 2`.
>
> Final test: `nums = [1, 4, 5, 2]`. Real outlier = 2, fake outlier (from bug) = 4. Bug triggers.

---

## More examples

### Example 1: integer overflow

**Solution:** `int sum = nums[0] + nums[1] + ...`
**Bug condition:** `sum > Integer.MAX_VALUE` (≈ 2.1 × 10⁹).

**Input constraint:** sum of nums > 2.1 × 10⁹.

**Construction:** with `n = 10^5` and `nums[i] = 10^4`, total = 10⁹. Need to push higher → use `nums[i] = 10^5` (if constraints allow). Or, with `n = 10^5` and average `nums[i] = 25000`, total = 2.5 × 10⁹. Adversarial test:

```java
int[] nums = new int[100000];
Arrays.fill(nums, 25000);
// sum = 2.5e9 > Integer.MAX_VALUE → overflow
```

### Example 2: negative modular result

**Solution:** `int shift = (a - b) % 26`.
**Bug condition:** result is negative.

**Input constraint:** `a < b`.

**Construction:** `a = 'a'`, `b = 'z'` → `(a - z) % 26 = -25 % 26 = -25` (negative).

Minimal test for Caesar pairs: words `"az"` and `"za"` should produce the same signature, but the buggy version produces `[0, 25]` and `[0, -25]`.

### Example 3: off-by-one boundary

**Solution:** binary search with `right = nums.length - 1`.
**Bug condition:** missed the last element.

**Input constraint:** the target is at `nums[length-1]`.

**Construction:** `nums = [1, 2, 3, 4, 5]`, `target = 5`. If your binary search uses `while (left < right)` instead of `while (left <= right)` without correct termination, you'll miss index 4.

### Example 4: empty result handling

**Solution:** returns `nums[0]` when no valid answer exists.
**Bug condition:** problem expects -1 or null on empty result.

**Input constraint:** an input with no valid answer.

**Construction:** if problem is "find sum pair that equals K", give `nums = [1, 2, 3]`, `K = 100`. No pair works. Buggy solution returns garbage instead of -1.

---

## How to practice this skill

1. **After every AC, do a 2-minute adversarial review.** Don't just submit and move on. Ask:
   - "Where in my code is the riskiest line?"
   - "What value of `nums[i]` would make that line behave badly?"
   - "Solve for that value algebraically."
2. **Before submit, construct one adversarial test of your own.** Mentally run your solution on it. If it produces the right answer, you've earned the submit click.
3. **When you DO get a WA**, write down the failing test in `patterns/edge-cases.md` along with the *algebraic condition* that caused it. Build the dictionary.

---

## What "algebraic" means here

You don't need formal mathematics. You need:

- The ability to **write down** what your code computes as an equation
- The ability to **manipulate** that equation to isolate input properties
- The ability to **construct** an input matching those properties

This is just bookkeeping with symbols. Anyone can do it; most people just don't.

---

## Source problems

- LC 3289 — outlier problem — derived `nums[i] = tSum/3` algebraically
- LC ??? — Caesar cipher — derived `a < b` for negative modular bug
- LC 1639 — House Robber V — derived overflow threshold

---

## Related patterns

- [[02-self-reference-in-lookup]] — common bug class to derive tests for
- [[05-constraint-reading-first]] — constraints define the input space you derive within
