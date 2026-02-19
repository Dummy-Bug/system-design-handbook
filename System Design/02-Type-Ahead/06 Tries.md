
## Starting Point: Why Trie Looks Attractive

Trie gives:

- Fast prefix lookup.
- O(length of prefix) traversal.
- Natural fit for autocomplete.

So the naive instinct is:

> “Let’s put all queries into a Trie.”

Correct direction. Wrong execution.

---

## Problem 1 — We Don’t Want All Results

Autocomplete does NOT need:

- Every matching word.
    

It needs:

> Only **Top K results by frequency**.

So basic Trie output is already misaligned with product requirement.

---

## Problem 2 — Storing Trie in Database

Trie is:

- Pointer heavy.
- Graph-like.
- Memory optimized.

Traditional databases:

- Are row-oriented.
- Not pointer optimized.
- Terrible for tree traversal.

Result:

You cannot practically persist Trie structure in MySQL or DynamoDB and query it efficiently.

So:

> Trie must live in memory.

---

## Problem 3 — Sharding a Trie Is Hard

If traffic grows:

- You will shard your system.

But how do you shard a Trie?

Options:

- Split by first letter.
- Split by prefix ranges.

Problems:

- Hot prefixes concentrate load.
- Uneven distribution.
- Complex routing logic.

This becomes operationally painful.

---

## Conclusion So Far

We decide:

### Decision 1

> Use an **in-memory data structure**.

Not DB-backed.

---

## Next Naive Approach

Store Trie in memory.

For each terminal node:

- Store frequency count.

On request:

1. Traverse prefix.
2. DFS subtree.
3. Collect all words.
4. Sort by frequency.
5. Return top K.

---

## Why This Is Terrible

Step 2 and 3 are expensive.

For hot prefixes:

`"p"`

Subtree size = millions.

DFS cost:

- O(number of words under prefix).
- Repeated on every request.

At 1M QPS this collapses instantly.

This is the main performance killer.

---

## Optimization Insight

Observation:

For a given prefix:

> Top K suggestions do not change on every request.

They change only when:

- New searches arrive.
- Popularity updates.

So computing top K on every read is wasteful.

---

## Correct Optimization

### Store Top K Results At Each Prefix Node

Instead of:

- Computing dynamically with DFS.

We:

> Precompute and cache Top K at every prefix node.

So Trie node becomes:

`Node {   children   topKResults }`

Now request flow:

1. Traverse prefix.
2. Return stored topK.
3. Done.

Time complexity:

`O(prefix length)`

No DFS. No sorting. Constant response time.

This is the key breakthrough.

---

## How Do We Update Top K?

When a new search query comes:

Example:

`"paris city cost of living"`

Steps:

1. Increment global count for this query.
2. Walk through prefixes:

`p pa par pari paris ...`

3. At each prefix node:
    - Update Top K heap or sorted set.
    - Adjust ranking if needed.

This is incremental propagation.

Yes, it is extra write cost.

But writes are much lower than reads.

---

## Storage Tradeoff

We are duplicating data:

Same query appears in:

- Many prefix nodes.

Cost:

- Higher memory usage.

Benefit:

- Massive read performance gain.

This is a classic **space-for-time tradeoff**.

For typeahead, it is worth it.

---

## Important Observation

You actually do NOT need a traditional Trie.

You can represent the same idea using:

---

## Two HashMaps Approach

### HashMap 1 — Prefix → Top K Results

Example:

`"p"   → [paris, pizza, phone] "pa"  → [paris, party, park] "par" → [paris, party]`

Key:

Prefix string.

Value:

Top K result list.

---

### HashMap 2 — Query → Frequency

Example:

`"paris city cost of living" → 12045`

This is global popularity counter.

---

## Why This Works

Trie traversal:

`p → a → r`

HashMap lookup:

`"par" → results`

Both give:

O(prefix length) time.

But HashMap version:

- Simpler.
- Easier to shard.
- Easier to persist snapshot.
- Easier to rebuild.

Production systems often use this flattened approach.

---

## Write Load Estimation

Given:

`1B searches/day`

Only search submissions update counts.

Assume:

`50% unique-ish queries`

Each query updates ~10 prefixes.
	Each submitted query updates multiple prefixes.
	
	Example:
	
	Query:
	
	`"paris travel guide"`
	
	Prefixes:
	
	`p pa par pari paris paris  paris t ...`

Total prefix updates:
`1B × 10 = 10B prefix updates/day` 
Here 1B is taken for unqiue as well as old search submission queries as both would update the prefixes

Convert to QPS:

`10B / 100,000 ≈ 100,000 writes/sec`

This is high.