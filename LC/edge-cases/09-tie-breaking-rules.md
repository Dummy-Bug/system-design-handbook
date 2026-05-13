# Tie-breaking rules

> [!info] When multiple valid answers exist, the problem usually specifies a tie-breaking rule (smallest, largest, lexicographically first, earliest occurrence). Read it carefully. Missing the rule often produces "almost right" answers that fail on hidden tests.

---

## When to suspect it

Trigger words in the problem statement:

- "**smallest**" / "**largest**"
- "**lexicographically smallest**" / "**lexicographically largest**"
- "**first**" / "**last**"
- "**any one of them**"
- "**return any valid answer**"
- "**if multiple ... exist**"
- "**earliest**" / "**latest**"
- "with the **minimum** length / index / value"

Each of these flags a tie-breaking rule. Note it. Encode it explicitly in your code.

---

## Common tie-breaking traps

### 1. "Smallest" — initial value matters

```java
// Problem: find smallest valid X
// BUGGY — initial value of 0 may be a valid answer that wins incorrectly
int smallest = 0;

// FIX
int smallest = Integer.MAX_VALUE;
// ... update only when valid
return (smallest == Integer.MAX_VALUE) ? -1 : smallest;
```

### 2. "Largest" — same trap, opposite

```java
int largest = Integer.MIN_VALUE;  // not 0
```

### 3. Lexicographic vs numeric

```java
// "lexicographically smallest" means string comparison
// "smallest" usually means numeric

// "10" < "9" lexicographically (string compare)
// 9 < 10 numerically

// BUG — using wrong compare
Arrays.sort(arr);  // numeric sort
// vs
Arrays.sort(arr, (a, b) -> a.compareTo(b));  // lexicographic
```

### 4. Earliest occurrence vs any occurrence

```java
// Problem: find the leftmost index where condition holds
// BUGGY — keeps overwriting
int found = -1;
for (int i = 0; i < n; i++) {
    if (condition(i)) found = i;  // last one wins, but we want first
}

// FIX
for (int i = 0; i < n; i++) {
    if (condition(i)) { found = i; break; }  // first one wins
}
```

### 5. "If multiple answers, return any" — DON'T be lazy

Even when the problem allows any valid answer, **make sure your answer is actually valid**. Edge case bugs often hide here because the test suite has *one* expected answer and your slightly different valid answer fails. Always verify your output against constraints, even if "any" is allowed.

### 6. Tie-breaking on multiple keys

```java
// Problem: sort by score descending, then by name ascending
// BUGGY — only one key
Arrays.sort(students, (a, b) -> b.score - a.score);

// FIX — chained compare
Arrays.sort(students, (a, b) -> {
    if (a.score != b.score) return b.score - a.score;  // score desc
    return a.name.compareTo(b.name);  // name asc
});
```

### 7. Tie-breaking changes the algorithm

```java
// Problem: find any path from A to B (BFS finds shortest)
// VS: find lexicographically smallest path

// First needs BFS
// Second needs Dijkstra with custom priority OR full DP

// The tie-breaking RULE drives the algorithm choice
```

---

## Template for spotting in future problems

When reading the problem:

1. Find the phrase that describes the **output**.
2. Scan for tie-breaking adjectives: "smallest", "largest", "first", "lex...".
3. If present, **write it down at the top of your scratch** as a constraint.
4. If multiple criteria, **note the priority order** (primary, secondary, tertiary).
5. Verify your algorithm respects the tie-breaking — not just produces "a" valid answer.

---

## Algorithm impact

Tie-breaking often determines algorithm choice:

| Tie-breaking | Algorithm hint |
|--------------|----------------|
| "Any valid" | BFS, DFS, greedy — first found is fine |
| "Smallest value" | Sort + first, or min-heap |
| "Largest value" | Sort + last, or max-heap |
| "Lexicographically smallest" | Comparator, often greedy left-to-right |
| "Earliest in input order" | Linear scan, break on first |
| "Latest in input order" | Linear scan, overwrite without break |
| "Smallest length" | BFS (level order), or shortest-path |
| "Largest length" | DFS exhaustive, or longest-path DP |

---

## Concrete failing test patterns

| Problem | Tie-breaking trap |
|---------|-------------------|
| Find shortest substring containing X | Multiple substrings same length — which one? |
| Find smallest number after K operations | Lex vs numeric matters when digits differ |
| Find any valid path | Hidden test may check specific path, even if "any" stated |
| Sort by frequency | What if two elements have same frequency? |
| K most frequent | Same — ties need secondary sort key |

---

## Source problems

- LC 451 — Sort Characters by Frequency (freq ties)
- LC 692 — Top K Frequent Words (lex tie-breaking)
- LC 767 — Reorganize String (lex among valid arrangements)
- LC 316 — Remove Duplicate Letters (lex smallest result)
- LC 402 — Remove K Digits (lex smallest result)

---

## Related patterns

- [[08-empty-and-single-element]] — what to return when no answer exists
- [[10-category-checklists]] — see comparator-heavy categories
