Retrieval came down to one unfinished word: "grab the query's **nearest** chunks." Nearest by what measure? A point in 512-dimensional space can be "close" to another in more than one sense, and the sense you pick changes what gets retrieved. There are three metrics you'll meet constantly: **Euclidean distance**, **cosine similarity**, and **dot product**. This note walks all three, and — importantly — why cosine similarity is the one RAG usually reaches for.

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

### Where Euclidean distance breaks

It has a real weakness, and it's the reason RAG rarely leans on it: **it is sensitive to the number of dimensions.** As dimensionality climbs, points spread out — everything drifts far from everything else — and the straight-line distances lose their discriminating power. A distance between two points in 2-D is trustworthy; the "same" distance across 256 or 512 or 1536 dimensions is much noisier.

> [!danger] The more dimensions, the less Euclidean distance can be trusted. Embedding models routinely output hundreds or thousands of dimensions, and at that scale Euclidean distances become unreliable — the accuracy degrades. Rule of thumb: Euclidean is fine for **low-dimensional** vectors, poor for the **high-dimensional** vectors embeddings actually produce. That's the opening cosine similarity walks through.

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

Here is the crucial bit. Cosine cares **only about direction, not magnitude** (length). Suppose the similarity between A and B is `0.7`. Now take a vector C that points in the exact same direction as B but is much longer or shorter — a different magnitude. The cosine similarity between A and C is *still* `0.7`, because the angle hasn't changed. The length of the vector is simply invisible to the metric.

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

Unlike cosine, the dot product is **unbounded** — the result can be any value, and it *is* affected by magnitude: make a vector longer and its dot products grow. On its own that makes it harder to interpret than a tidy −1-to-1 score.

But there's an elegant relationship that ties it back to cosine. The full definition of cosine similarity is the dot product divided by the two magnitudes:

```
cosine similarity(A, B) =        A · B
                           ─────────────────
                              ‖A‖ · ‖B‖
```

Now **normalize** the vectors — scale each to unit length so `‖A‖ = ‖B‖ = 1`. The denominator becomes `1 × 1 = 1`, and the whole thing collapses:

```
with normalized vectors:   cosine similarity(A, B) = A · B
```

So on normalized embeddings, **dot product and cosine similarity give the same answer** — but the dot product skips the magnitude division, so it's **cheaper to compute and gives faster retrieval.** That's why many vector databases normalize embeddings once up front and then use plain dot product internally: you get cosine's meaning at dot product's speed.

> [!important] If the embeddings are normalized to unit length, **dot product ≡ cosine similarity**, because the `‖A‖·‖B‖` denominator is just 1. Dot product then buys you the same similarity ranking with less computation — the standard trick behind fast vector search.

---

## The three side by side

| Metric | Measures | Range | Magnitude-sensitive? | Similarity reading | Best for |
|---|---|---|---|---|---|
| **Euclidean distance** | straight-line distance | `0 → ∞` | yes | lower = more similar | low-dimensional vectors |
| **Cosine similarity** | angle between vectors | `−1 → +1` (bounded) | **no** | higher = more similar | high-dimensional embeddings (RAG default) |
| **Dot product** | element-wise product, summed | unbounded | yes | higher = more similar | fast search on **normalized** vectors (≡ cosine) |

The throughline: **Euclidean** is intuitive but crumbles in high dimensions; **cosine** fixes that by scoring angle on a bounded scale and ignoring magnitude, which is why it's the go-to; and **dot product** is what you actually run for speed once vectors are normalized, where it becomes cosine similarity by another name.
