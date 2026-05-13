# Boundary — first/last element

> [!info] The first and last elements of any sequence (array, string, list) often behave differently than middle elements. Code that handles `nums[i-1]` or `nums[i+1]` always needs explicit boundary handling.

---

## When to suspect it

Trigger conditions:

- Any access to `nums[i-1]`, `nums[i+1]`, `nums[i-k]`, `nums[i+k]`
- Sliding window / two pointers
- Prefix/suffix arrays
- DP with transition referencing previous/next index
- String parsing with separator-detection logic
- Linked list traversal with `current.next` or `prev`

---

## Common boundary bugs

### 1. Off-by-one on loop range

```java
// BUGGY — accesses nums[n] when i = n-1
for (int i = 0; i <= n - 1; i++) {
    sum += nums[i] + nums[i + 1];
}

// FIX — stop one short, or guard the access
for (int i = 0; i < n - 1; i++) {
    sum += nums[i] + nums[i + 1];
}
```

### 2. First-element special case

```java
// Problem: count elements where nums[i] > nums[i-1]
// BUGGY — first element has no predecessor
for (int i = 0; i < n; i++) {
    if (nums[i] > nums[i - 1]) count++;  // ArrayIndexOutOfBounds at i=0
}

// FIX — skip first, or initialize previous
for (int i = 1; i < n; i++) {  // start from 1
    if (nums[i] > nums[i - 1]) count++;
}
```

### 3. Last-element flush

```java
// Problem: group consecutive same characters
// BUGGY — last group never flushed
List<String> groups = new ArrayList<>();
StringBuilder current = new StringBuilder();
for (int i = 0; i < n; i++) {
    if (i > 0 && s.charAt(i) != s.charAt(i - 1)) {
        groups.add(current.toString());
        current = new StringBuilder();
    }
    current.append(s.charAt(i));
}
// MISSED — final group still in `current`, never added

// FIX — explicit flush after loop
groups.add(current.toString());
```

### 4. Sentinel pattern (avoids special-casing)

```java
// Avoid first/last edge cases by padding with sentinels
int[] padded = new int[n + 2];
padded[0] = Integer.MIN_VALUE;
padded[n + 1] = Integer.MIN_VALUE;
for (int i = 0; i < n; i++) padded[i + 1] = nums[i];
// Now the boundary logic works uniformly for all indices
```

### 5. Linked list head/tail handling

```java
// BUGGY — assumes head exists
ListNode current = head;
while (current.next != null) { ... }  // NPE if head is null

// FIX — null-check head
if (head == null) return null;
ListNode current = head;
```

### 6. String separator at start/end

```java
// Problem: split "a,b,c" by comma
// BUGGY for ",a,b,c," — empty strings at start and end
String[] parts = s.split(",");

// CHECK what the expected behavior is — often you want to skip empties
List<String> nonEmpty = Arrays.stream(parts).filter(p -> !p.isEmpty()).toList();
```

---

## Universal boundary checklist

Before submitting any sequence-based solution:

| Question | If yes → check |
|----------|----------------|
| Access `nums[i-1]` or `nums[i+1]`? | Bounds on `i` are correct |
| Does first element behave specially? | Loop starts from `1` (or first iteration is initialized) |
| Does last element get flushed? | Explicit post-loop flush exists |
| Linked list / tree traversal? | Null check at head/root |
| Window slides? | Window boundaries are inclusive/exclusive consistently |
| Slicing / substring? | Indices include the endpoint correctly |

---

## Concrete failing test patterns

| Bug class | Smallest failing test |
|-----------|----------------------|
| First-element comparison | `nums = [1]` (n=1, no i-1 exists) |
| Last-element flush | input where the answer is in the last unflushed state |
| Off-by-one loop end | input where the last element is the target |
| Window boundary | `nums = [1, 2]` with `k = 1` or `k = 2` |
| Separator at edges | `,a,b,` or `a,,b` |
| Empty sequence | `[]`, `""`, `null` |

---

## Template for spotting in future problems

When you write any index-based logic, ask:

1. **Does `i = 0` work?** Does the code reference anything before index 0?
2. **Does `i = n-1` work?** Does the code reference anything after the array?
3. **Does the loop terminate correctly?** Last iteration's state is the final answer?
4. **Is there a "pending" state after the loop?** If yes, flush it.

For string parsing specifically:
- What if the separator is at the start?
- What if the separator is at the end?
- What about consecutive separators?
- What about an empty string?
- What about a single character?

---

## Source problems

- LC 1556 — Thousand Separator (string-parsing boundaries)
- LC 1109 — Corporate Flight Bookings (range update, off-by-one)
- LC 53 — Maximum Subarray (boundary flush)
- LC 152 — Maximum Product Subarray (first/last sign tracking)

---

## Related patterns

- [[08-empty-and-single-element]] — extreme boundary cases
- [[10-category-checklists]] — see "Sliding window" and "Binary search" rows
