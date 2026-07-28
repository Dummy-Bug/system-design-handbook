Retrieval came down to one unfinished word: "grab the query's **nearest** chunks." Nearest by what measure? A point in 512-dimensional space can be "close" to another in more than one sense, and the sense you pick changes what gets retrieved. There are three metrics you'll meet constantly: **Euclidean distance**, **cosine similarity**, and **dot product**.

---

## Euclidean distance — the straight-line ruler

The most intuitive measure. The **Euclidean distance** between two points is simply the length of the **straight line** joining them — a ruler laid between vector A and vector B. If you've done any machine learning you've already used it; it's the distance inside algorithms like **KNN** and inside clustering.

The formula is the Pythagorean theorem stretched to n dimensions — difference in each coordinate, squared, summed, square-rooted:

```
d = √( (x₁ − y₁)² + (x₂ − y₂)² + … + (xₙ − yₙ)² )
```

Work a concrete 2-D case. Let point **A = (2, 4)** and point **B = (3, 2)**:

```
d = √( (2 − 3)² + (4 − 2)² )
  = √( (−1)²   + (2)²   )
  = √( 1 + 4 )
  = √5
  ≈ 2.23
```

So A and B are `2.23` apart. And the reading is: **the lower the distance, the more similar the vectors.** Two chunks whose points are a short straight line apart mean nearly the same thing; a large distance means they're unrelated.

> [!info] Euclidean distance = straight-line distance between two points. Range is `0` (identical) upward, with no upper bound. **Smaller = more similar.** It's the everyday notion of "how far apart," extended from 2-D to however many dimensions your embeddings have.

### Where Euclidean distance breaks — the curse of dimensionality

It has a real weakness, and it's the reason RAG rarely leans on it: **it is sensitive to the number of dimensions.** To see why, look again at the formula — it sums a squared difference from *every* dimension:

```
d = √( (x₁−y₁)² + (x₂−y₂)² + … + (xₙ−yₙ)² )
```

For any given pair of chunks, only a **handful** of dimensions carry the real signal — the meaning that actually makes them similar or different. Every other dimension holds a tiny, near-random difference — **noise**. And Euclidean adds *all* of it under the root, signal and noise together. With few dimensions the signal ones dominate the sum. With hundreds of dimensions the sum is swamped by hundreds of accumulated tiny noise terms — and that accumulated noise is roughly **the same for every pair of points**, so all distances drift toward one middle value and near stops looking different from far.

Make it concrete. Take two chunks that are genuinely **similar** — they agree on the one meaningful dimension and differ only by a tiny ±0.1 jitter on all the others — and two that are genuinely **different** — a full `1.0` apart on the meaningful dimension, plus the same ±0.1 jitter everywhere else.

```
In 2 dimensions:
  similar    →  √(0.1² + 0.1²)  = √0.02 = 0.14
  different  →  √(1.0² + 1.0²)  = √2    = 1.41     → different is ×10 farther ✅ easy to separate

In 500 dimensions (now 499 noise dimensions, each ±0.1):
  noise alone contributes √(499 × 0.1²) = √4.99 = 2.23
  similar    →  2.23                       (meaningful dim agrees — only noise left)
  different  →  √(1.0² + 4.99) = √5.99 = 2.45   → different is only ×1.1 farther ❌
```

The `1.0` of real signal got **drowned by 2.23 of accumulated noise.** In 2-D the different pair stood out at ten times the distance; in 500-D it's a rounding error away from the similar pair — `2.23` vs `2.45`. Euclidean can no longer tell "same topic" from "different topic."

That was one hand-picked example. Simulate it honestly — scatter random points and measure the **contrast**, `(farthest − nearest) / nearest`, as dimensions grow — and the same collapse appears every time:

![[AI-Engineering/RAG/03-Embeddings/Images/06-Curse-Of-Dimensionality.png]]

Panel A is the example above; panel B is the general law. At 2 dimensions the farthest point is ~42× the nearest — enormous contrast. By **512 dimensions the contrast is 0.15** — the farthest chunk is only about 1.15× as far as the nearest. "Nearest neighbour" has almost stopped meaning anything.

> [!danger] The more dimensions, the less Euclidean distance can be trusted — this is the **curse of dimensionality**. Because the metric sums a squared difference from every dimension, hundreds of noise dimensions pile up and push all distances toward the same value (distance *concentration*), so near and far become indistinguishable. Embedding models routinely output hundreds or thousands of dimensions, exactly where this bites. Rule of thumb: Euclidean is fine for **low-dimensional** vectors, poor for the **high-dimensional** vectors embeddings actually produce.

**Why cosine escapes it:** cosine measures the **angle/direction**, not the summed length. Those hundreds of tiny noise jitters largely cancel out in direction and get normalized away with magnitude — so the direction still points at the signal even when the raw length is buried in noise. That robustness is the opening cosine similarity walks through next.

---

## Cosine similarity — measure the angle, ignore the length

Cosine similarity throws away the ruler and measures the **angle** between the two vectors instead of the distance between their tips. This is the metric that shows up in most **default** RAG settings, and the picture explains why:

![[AI-Engineering/RAG/03-Embeddings/Images/05-Cosine-Angle-Similarity.png]]

Draw vector A. A second vector pointing in nearly the same direction sits at a **small angle** to it — very similar. Swing that second vector round until it's **90°** to A, and they now share no direction at all — unrelated. Push on to **180°**, pointing exactly opposite, and they're as dissimilar as it gets. Cosine similarity turns that angle into a single bounded score:

```
angle   0°  →  score  +1   →  most similar   (same direction)
angle  90°  →  score   0   →  not similar    (orthogonal)
angle 180°  →  score  −1   →  opposite       (complementary)
```

> [!info] Cosine similarity measures the angle between two vectors and reports a score in the bounded range **[−1, +1]**. `+1` = same direction (most similar), `0` = perpendicular (unrelated), `−1` = opposite. **Higher = more similar** — the reverse direction of Euclidean, where lower was better. The smaller the angle, the higher the score.

### The property that makes it win: magnitude doesn't matter

Here is the crucial bit. Cosine cares **only about direction, not magnitude** (length). Suppose the similarity between A and B is `0.7`. Now take a vector C that points in the exact same direction as B but is much longer or shorter — a different magnitude. The cosine similarity between A and C is *still* `0.7`, because the angle hasn't changed. **The length of the vector is simply invisible to the metric.**

That is exactly the immunity Euclidean distance lacked. Because cosine ignores magnitude, it also shrugs off the dimensionality blow-up that made Euclidean unreliable — it keeps working cleanly for the high-dimensional vectors embedding models produce. Bounded, direction-based, magnitude-proof: that combination is why cosine similarity is the default similarity metric in RAG.

> [!tip] Interview framing: "Cosine similarity scores the *angle* between two embedding vectors on a bounded −1-to-1 scale, so it's immune to vector magnitude and to the high-dimensionality that wrecks Euclidean distance. Two chunks about the same topic point the same way regardless of length, so they score near +1. That robustness is why it's the RAG default."

---

## Dot product — fast, unbounded, and cosine's close cousin

The third metric is the **dot product**: multiply the two vectors element-wise and sum the results.

```
A · B = a₁·b₁ + a₂·b₂ + … + aₙ·bₙ

e.g.  A = [2, 3, 5]   B = [2, 6, 2]
      A · B = (2·2) + (3·6) + (5·2) = 4 + 18 + 10 = 32
```

Unlike cosine, the dot product is **unbounded** — the result can be any value, and it *is* affected by magnitude: make a vector longer and its dot products grow. On its own that makes it harder to interpret than a tidy −1-to-1 score. But there's an elegant relationship that ties it back to cosine — and to see it, we need two small building blocks first: **magnitude** and **normalization**.

### Building block 1 — magnitude `‖A‖` is just the arrow's length

A vector is an arrow from the origin to a point, and its **magnitude** `‖A‖` is simply **how long that arrow is.** You compute it with Pythagoras — square each number, add, square-root:

```
A = [3, 4]
‖A‖ = √(3² + 4²) = √(9 + 16) = √25 = 5      → the arrow to [3, 4] is 5 units long
```

That's all `‖A‖` means: the length of the vector.

### Building block 2 — normalization makes the length exactly 1

**Normalizing** a vector means **shrinking or growing it so its length becomes exactly 1, without changing the direction it points.** You do it by dividing every number in the vector by its own magnitude:

```
A = [3, 4],   ‖A‖ = 5
normalized A  =  [3/5, 4/5]  =  [0.6, 0.8]

check the new length:  √(0.6² + 0.8²) = √(0.36 + 0.64) = √1 = 1  ✅
```

Same direction as before, now length 1. A length-1 vector is called a **unit vector**. The one-line intuition: *keep the arrow's direction, throw away its length.*

### The relationship — cosine is a dot product with the lengths divided out

The full definition of cosine similarity is the dot product divided by both magnitudes:

```
cosine similarity(A, B) =        A · B
                           ─────────────────
                              ‖A‖ · ‖B‖
```

That division is the whole point: dividing out `‖A‖` and `‖B‖` **removes the lengths**, leaving only direction — which is exactly why cosine "ignores magnitude." Now watch what happens if the vectors are **already normalized** (both lengths 1): the denominator becomes `1 × 1 = 1`, and dividing by 1 does nothing:

```
with normalized vectors:   cosine(A, B) =  A · B  =  A · B
                                          ───────
                                            1
```

So **once the vectors are unit-length, cosine similarity is literally just the dot product** — no division, no square roots. Proof with real numbers:

```
A = [3, 4]   B = [4, 3]

Cosine the full way:
  A · B = (3·4) + (4·3) = 24
  ‖A‖ = 5,  ‖B‖ = 5
  cosine = 24 / (5 · 5) = 24 / 25 = 0.96

Normalize first, then just take the dot product:
  Â = [0.6, 0.8]      B̂ = [0.8, 0.6]
  Â · B̂ = (0.6·0.8) + (0.8·0.6) = 0.48 + 0.48 = 0.96      ← identical answer ✅
```

### Why that makes dot product *faster*

Both routes give `0.96`, so why prefer the dot product? It comes down to **when** you pay for the expensive operations — the square roots and the division. Computing **cosine** for one comparison forces the machine, *every single time*, to: take the dot product, **plus** compute `‖A‖` (square, sum, **square root**), **plus** compute `‖B‖` (square, sum, **another square root**), **plus** one **division**. The dot product route on pre-normalized vectors does only the first step.

Now scale it to a real query against **10 million chunks**:

```
Cosine each time:   10,000,000 × ( dot product + 2 square roots + 1 division )
Dot product only:   10,000,000 × ( dot product )        ← if vectors are already unit-length
```

If you **normalize every chunk once, up front** — when you store it — then all those square roots and divisions are already baked in, and every one of the 10 million query-time comparisons collapses to a plain dot product (multiply and add). You've deleted **10 million square roots and 10 million divisions** from the hot path.

> [!important] Normalize once at storage → then dot product **is** cosine similarity, without redoing the length maths on every comparison. Because `‖A‖ · ‖B‖ = 1` for unit vectors, the two metrics give the *same* ranking (`0.96` either way), but the dot product skips the square roots and division on every one of millions of comparisons. That's why vector databases normalize embeddings up front and use plain dot product internally — cosine's meaning at dot product's speed.

---

## The three side by side

| Metric | Measures | Range | Magnitude-sensitive? | Similarity reading | Best for |
|---|---|---|---|---|---|
| **Euclidean distance** | straight-line distance | `0 → ∞` | yes | lower = more similar | low-dimensional vectors |
| **Cosine similarity** | angle between vectors | `−1 → +1` (bounded) | **no** | higher = more similar | high-dimensional embeddings (RAG default) |
| **Dot product** | element-wise product, summed | unbounded | yes | higher = more similar | fast search on **normalized** vectors (≡ cosine) |

The throughline: **Euclidean** is intuitive but crumbles in high dimensions; **cosine** fixes that by scoring angle on a bounded scale and ignoring magnitude, which is why it's the go-to; and **dot product** is what you actually run for speed once vectors are normalized, where it becomes cosine similarity by another name.
