RRF assigns every document a fresh score, and it computes that score from **one input only: the position the document occupied in each retrieval run.**

![[AI-Engineering/07-RAG/07-Reranking-And-Query-Transforms/Images/17-RRF-Score-Formula.png]]

$$\text{RRF score}(d) = \sum_{r} \frac{1}{\text{rank}_r(d) + k_c}$$

Sum over every retrieval run `r`. `rank` is the document's position in that run's list, counting from 1. `k_c` is a constant, conventionally **60**.

> [!important] **The original similarity score is discarded entirely.** Not down-weighted — discarded. A document that scraped in at rank 1 with a cosine similarity of 0.51 contributes exactly the same as one that hit rank 1 with 0.99. RRF only ever asks *"where did it come?"*, never *"by how much?"*. That is a deliberate design choice, and the reason is that scores from different retrieval runs (or different retrievers entirely) are not comparable to one another, whereas ranks always are.

---

## A worked example

Three rephrasings of the user's question produce three retrieval runs:

![[AI-Engineering/07-RAG/07-Reranking-And-Query-Transforms/Images/14-Three-Retrieval-Runs.png]]

| Run | Rank 1 | Rank 2 | Rank 3 |
|---|---|---|---|
| ① | Doc 2 | Doc 5 | Doc 1 |
| ② | Doc 3 | Doc 2 | Doc 1 |
| ③ | Doc 2 | Doc 4 | Doc 3 |

Note that the orderings genuinely disagree — that is the normal case, because each run answered a differently-worded question.

Now apply the formula. A document that does not appear in a run contributes **0** for that run.

![[AI-Engineering/07-RAG/07-Reranking-And-Query-Transforms/Images/15-RRF-Formula-And-Scores.png]]

**Doc 1** — rank 3 in ①, rank 3 in ②, absent from ③:

$$\frac{1}{3+60} + \frac{1}{3+60} + 0 = 0.015873 + 0.015873 = \mathbf{0.031746}$$

**Doc 2** — rank 1 in ①, rank 2 in ②, rank 1 in ③:

$$\frac{1}{1+60} + \frac{1}{2+60} + \frac{1}{1+60} = 0.016393 + 0.016129 + 0.016393 = \mathbf{0.048915}$$

**Doc 3** — rank 1 in ②, rank 3 in ③:

$$\frac{1}{1+60} + \frac{1}{3+60} = 0.016393 + 0.015873 = \mathbf{0.032266}$$

**Doc 4** and **Doc 5** appear once each, both at rank 2: $\frac{1}{62} = \mathbf{0.016129}$ apiece.

### The re-ranked result

| Document | RRF score | Appearances |
|---|---|---|
| **Doc 2** | 0.048915 | **3 of 3** |
| Doc 3 | 0.032266 | 2 of 3 |
| Doc 1 | 0.031746 | 2 of 3 |
| Doc 4 | 0.016129 | 1 of 3 |
| Doc 5 | 0.016129 | 1 of 3 |

**Doc 2 wins decisively** — not because it was ever spectacularly similar, but because it turned up in *every* run. Doc 4 and Doc 5 sit at the bottom despite both having ranked 2nd, because they each showed up only once.

---

## What the formula is actually rewarding

The property being rewarded is **consistency**.

A document that appears across multiple retrieval runs is a document that matched *several different phrasings* of the same question. That means it covers most — or all — of the information the user was circling around, rather than happening to match one particular wording.

Conversely, a document that ranks first in one run and is absent from the others is a **one-off**. It matched a single phrasing, possibly a quirk of that phrasing, and RRF treats it as the outlier it probably is.

> [!info] **Why summation gets you this for free.** Each additional appearance adds roughly `1/61`-ish to the total. Each *improvement in rank within* a run adds almost nothing — the difference between rank 1 and rank 3 is `0.016393 − 0.015873 = 0.00052`, about **thirty times smaller** than the gain from appearing one more time. So the sum is dominated by *how many times* a document appears, not *where* it appears.

### Rank still matters — just barely

Compare Doc 3 and Doc 1. Both appeared in exactly two runs, so appearance-count is tied. The tiebreak goes to rank:

- Doc 3 came **1st and 3rd** → 0.032266
- Doc 1 came **3rd and 3rd** → 0.031746

Doc 3 edges ahead by 0.00052. Its one first-place finish outweighs Doc 1's second third-place finish — but only just. That is the design working as intended: **consistency decides the big gaps, rank decides the ties.**

---

## Why the constant is there

![[AI-Engineering/07-RAG/07-Reranking-And-Query-Transforms/Images/16-Why-The-Constant-60.png]]

The obvious formula would be plain `1/rank`. The constant is what turns it from a rank-dominated score into a consistency-dominated one. Look at what `+60` does to the values:

| rank | `1/(rank+60)` | plain `1/rank` |
|---|---|---|
| 1 | 0.0164 | 1.000 |
| 2 | 0.0161 | 0.500 |
| 3 | 0.0159 | 0.333 |
| 4 | 0.0156 | 0.250 |
| 5 | 0.0154 | 0.200 |

With the constant, ranks 1 through 5 span **0.0164 to 0.0154** — a range of 0.001, essentially flat. Without it, rank 1 is **five times** rank 5.

So the constant is a **damping factor**, and it is a dial:

- **Increase `k_c`** → denominator grows → the gaps between ranks shrink further → rank matters even less, consistency matters even more. Push it high enough and the score becomes little more than a count of appearances.
- **Decrease `k_c`** → gaps widen sharply. At `k_c = 1`: rank 1 scores `1/2 = 0.5`, rank 2 scores `1/3 = 0.33`, rank 3 scores `1/4 = 0.25`. Now a single first-place finish can beat three mediocre showings, and you are back to **favouring rank**.

**60 is the conventional value**, and it sits deliberately far along the consistency end of that dial.

> [!note] **What RRF guarantees:** a document agreed on by many retrieval runs outranks one that any single run loved. **What it does not guarantee:** that the agreed-upon document is the best answer. If every rephrasing shares the same blind spot — because they all came from one LLM rewriting one query — they can agree on the wrong thing, and RRF will confidently promote it. Consensus is being used as a proxy for relevance, and it is only ever a proxy.

---

> [!tip] Interview framing
> "RRF scores each document as the sum over retrieval runs of `1/(rank + k)`, with `k` conventionally 60, and it uses *only* rank — the underlying similarity scores are thrown away, because scores from different retrievers aren't comparable while ranks always are. The effect of the constant is what matters: `1/61` through `1/65` are all within about a thousandth of each other, so moving up a rank barely changes the score, while appearing in one more retrieval run adds a whole extra `~0.016`. So the sum is dominated by consistency — how many phrasings retrieved this document — and rank only breaks ties. In the lecture's example a document appearing in all three runs scored 0.0489 versus about 0.032 for documents in two runs, and two documents that each ranked 2nd but appeared only once came last. The constant is the dial: raise it and you approach pure vote-counting, drop it to 1 and rank-1 finishes start dominating again. The caveat is that consensus is a proxy for relevance — if the rephrasings share a blind spot, RRF promotes their shared mistake."
