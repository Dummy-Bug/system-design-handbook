# Geometry [1100]

Coordinate-plane reasoning — distances, areas, shapes, lattice points, line equations. Starts as basic distance/area at 1100 and **peaks at Band 1700 (31% of math)** before tapering. Stays a top-3 math topic from 1500 all the way to 1800.

Unlike most math topics that taper at high bands, geometry stays significant deep into 1800+ because it pairs naturally with sweep-line, computational geometry, and lattice-point counting — all of which compound on the basic primitives installed here.

## Empirical frequency

| Band | GEOM-tagged | % of math problems |
|------|-------------|--------------------|
| 1100-1399 | 29 | 10.1% |
| 1400-1499 | — | 9% |
| 1500-1599 | — | 15% |
| 1600-1699 | 12 | 18.5% (#1 math topic) |
| 1700-1799 | — | **31% (#1, dominant)** |
| 1800-1899 | 13 | 16.7% |
| 1900+ | tail | — |

**Total: ~70+ problems across 1100-1800.** This is the single most-frequent math topic in the 1500-1800 range. High-leverage install for the user's contest band.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Coordinate distance — Euclidean [1100]

**Cards (3):**
- a.1 — Euclidean distance formula `√((x₂-x₁)² + (y₂-y₁)²)`
- a.2 — Squared-distance reflex: compare `d² < r²` instead of `d < r` to avoid floating-point + sqrt cost
- a.3 — Overflow risk on `(x₂-x₁)²` when coordinates near 10⁹ — cast to long before squaring

---

## b. Manhattan distance [1100]

**Cards (2):**
- b.1 — Manhattan distance formula `|x₂-x₁| + |y₂-y₁|`
- b.2 — When grid problems force Manhattan (4-directional movement) vs Euclidean (continuous plane)

---

## c. Chebyshev distance [1300]

**Cards (1):**
- c.1 — Chebyshev distance formula `max(|x₂-x₁|, |y₂-y₁|)` — appears in 8-directional grid problems (king moves)

---

## d. Axis-aligned rectangle properties [1200]

**Cards (3):**
- d.1 — Area = width × height = `(x₂-x₁) × (y₂-y₁)`
- d.2 — Point-in-rectangle test: `x₁ ≤ x ≤ x₂ AND y₁ ≤ y ≤ y₂`
- d.3 — Rectangle overlap test: `max(x1a, x1b) < min(x2a, x2b)` on both axes

**LC anchor:** *Rectangle Overlap* (LC 836), *Maximum Area of a Triangle* (variants)

---

## e. Triangle area from 3 points [1300]

**Cards (2):**
- e.1 — Shoelace formula for triangle: `area = |x₁(y₂-y₃) + x₂(y₃-y₁) + x₃(y₁-y₂)| / 2`
- e.2 — Sign of the determinant tells orientation (clockwise vs counter-clockwise)

---

## f. Collinearity test [1400]

**Cards (1):**
- f.1 — Three points collinear iff triangle area = 0 (i.e., cross product of `(p₂-p₁)` and `(p₃-p₁)` is zero)

**LC anchor:** *Check If It Is a Straight Line* (LC 1232)

---

## g. Slope and line equations [1400]

**Cards (3):**
- g.1 — Slope = `(y₂-y₁) / (x₂-x₁)` — and the vertical-line trap (`x₂ = x₁`)
- g.2 — Avoid floating-point slope by storing as reduced fraction `(dy/gcd, dx/gcd)` with sign normalisation
- g.3 — Line through two points in `ax + by + c = 0` form

**LC anchor:** *Max Points on a Line* (LC 149)

---

## h. Lattice-point counting [1500]

**Cards (2):**
- h.1 — Lattice points on a segment from `(x₁, y₁)` to `(x₂, y₂)` = `gcd(|dx|, |dy|) + 1`
- h.2 — Lattice points inside / on a circle of radius r: iterate x, count valid y by `floor(√(r² - x²))`

**Depends on:** GCD/LCM → Number Theory `[1400]`

**LC anchor:** *Lattice Points Inside a Circle* (LC 2249)

---

## i. Polygon area (Shoelace) [1600]

**Cards (2):**
- i.1 — Shoelace formula for n-vertex polygon: `area = |Σ (xᵢ × yᵢ₊₁ - xᵢ₊₁ × yᵢ)| / 2`
- i.2 — Convex vs non-convex — Shoelace works for both as long as vertices are in order (cw or ccw)

---

## j. Manhattan ↔ Chebyshev transform [1700]

**Cards (1):**
- j.1 — Rotation transform: `(x, y) → ((x+y)/√2, (x-y)/√2)` converts Manhattan distance to Chebyshev (and vice versa). Used to reduce 4-directional distance problems to max-coordinate problems.

**LC anchor:** *Minimize Manhattan Distances* (LC 3102)

---

## k. Circle / disk geometry [1700]

**Cards (3):**
- k.1 — Point inside circle test: `(x - cx)² + (y - cy)² ≤ r²`
- k.2 — Circle-circle intersection test: distance between centres compared to `|r₁ - r₂|` and `r₁ + r₂`
- k.3 — Counting points within radius r from each centre — sort-based / grid bucketing for n centres

**LC anchor:** *Detonate the Maximum Bombs* (LC 2101)

---

## l. Sweep line / coordinate compression [1800]

**Depends on:** Sorting + interval algorithms (outside math syllabus)

**Cards (2):**
- l.1 — Recognising when 2D problem reduces to 1D sweep (events sorted by x, query on y)
- l.2 — Coordinate compression: map sparse coordinates to dense indices to enable Fenwick/segment-tree queries

---

## m. Convex hull intuition [1800]

**Cards (1):**
- m.1 — Convex hull = smallest convex polygon containing all points. Identification rather than implementation — most LC problems hint at hull via "extremes only matter."

---

## Card count

26 atomic cards across 13 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (3) + b (2) = **5 cards** |
| 1200-1299     | + d (3) = **8 cards** |
| 1300-1399     | + c (1) + e (2) = **11 cards** |
| 1400-1499     | + f (1) + g (3) = **15 cards** |
| 1500-1599     | + h (2) = **17 cards** |
| 1600-1699     | + i (2) = **19 cards** |
| 1700-1799     | + j (1) + k (3) = **23 cards** |
| 1800+         | + l (2) + m (1) = **26 cards (full)** |

## Notes for Socratic drill

- Subtopic `a.2` (squared-distance reflex) is one of the highest-value cards in this whole syllabus. Floating-point bugs from `sqrt` comparisons appear constantly at 1500+. The reflex "compare squares, never sqrts" closes that entire bug family.
- Subtopic `g.2` (slope as reduced fraction) is the *Max Points on a Line* trap — most candidates use `double` slope, hit precision loss, get WA. Reflex: always reduce to `(dy, dx)` form with GCD and sign normalisation.
- Subtopic `h.1` (lattice points on segment via GCD) is the unexpected number-theory link in geometry. Pair install with GCD subtopic when both bands open.
- Subtopic `j` (Manhattan ↔ Chebyshev) is the single most-rewarding geometric trick in the 1700+ band. Hard to spot without the install; trivial with it.
