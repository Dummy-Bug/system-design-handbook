#machine-learning #syllabus #just-in-time #process-mining #transformers

---

# You have three months and a system to ship. What do you actually need to know *first*?

> Prerequisite: [[00-learning-path]] — the full catalogue, every resource rated out of 10.
> That note answers *"what is worth learning?"*. This one answers *"what is worth learning **this
> week**, and what can wait until the build demands it?"*
>
> **Scope note:** this ordering assumes the *platform-first* build (zero ML for the first ~6–8 weeks,
> transformer last). If you're building the **model first on synthetic data**, [[02-model-first-syllabus]]
> supersedes the order below — the transformer arc becomes the critical path and the mining/trees
> blocks defer.

A syllabus read front-to-back makes you feel permanently behind, because it is ordered by *subject*
and you are constrained by *time*. Re-order it by what the next thing you build refuses to work
without, and something surprising falls out.

---

## The finding

Take the build in the order it has to be built, and ask each phase what it actually requires:

| Build phase | ML knowledge required |
|---|---|
| Raw event archive + ingestion API | **none** |
| Vocabulary v0 + tokenizer rules | **none** |
| Deterministic identity resolution | **none** |
| Case assembler + boundary rules | **none** |
| Synthetic trace generator | ~1h of probability |
| First discovered process graph | process mining — **not ML** |
| Baseline predictor | process mining + one counting idea |
| Statistical model | splits, trees, calibration, censoring |
| Sequence transformer | the whole deep-learning stack |

> [!success] **The first six to eight weeks of building need zero machine learning.** The
> fast-track isn't a shorter syllabus. It's the discovery that most of the syllabus isn't a
> prerequisite for anything you're doing yet.

So the material splits into two tracks that never block each other.

---

## Track A — Just-in-time (~24h, gated by the build)

Learn each block **immediately before** the phase that needs it. Never earlier: knowledge acquired
three months before use is knowledge re-acquired.

---

### A1 · Now, before you write a line

**Concepts you're buying**
- Launch without ML before launching with it
- Your first model should be simple, and should be a *baseline*
- The metric you optimise vs. the metric you care about
- Why building infrastructure before you have data is the classic failure

**Learn from** → [Zinkevich, *Rules of Machine Learning*](https://developers.google.com/machine-learning/guides/rules-of-ml) (Google, free) — **Rules 1–23 only**

**Time** 1h · one sitting

> [!important] Read this before the conversation where you agree what to ship, not after. Rule 1
> (*"don't be afraid to launch a product without machine learning"*) is the argument for shipping
> the discovery product before the prediction product, written by someone with more authority
> than you or me.

---

### A2 · Before the case assembler (~week 4–5)

**Concepts you're buying**
- **Event log** — the raw table everything is derived from
- **Case** and case ID — the unit one journey is described by
- **Activity** — the thing that happened
- **Trace** — one case's ordered activity sequence, i.e. the "sentence"
- **Variant** — a distinct path through the process, ranked by frequency
- **Directly-follows graph (DFG)** — which activity follows which, how often, how fast
- **Process discovery** — alpha, heuristics and inductive miners
- **Conformance checking** — fitness and precision against an expected model
- **Bottleneck / stall analysis** — cases idle beyond an expected duration
- **XES** — the interchange format the tooling expects

**Learn from** → van der Aalst, *Process Mining: Data Science in Action* (2nd ed.), **ch. 2 + ch. 6** (add ch. 8 when you build conformance views)
**Or** → [Coursera — *Process Mining: Data Science in Action*](https://www.coursera.org/learn/process-mining), weeks 1–2, free to audit, taught by the same author

**Time** 6h

> [!tip] This is the highest-differentiation block in either track. Most ML engineers have never
> heard of this field. Six hours puts you ahead of nearly anyone you could hire.

**Gate** — you can explain what a DFG shows, and why a nonsense DFG proves the bug is *upstream* of
the mining rather than in it.

---

### A3 · Before the discovery gate (~week 6)

**Concepts you're buying**
- Importing an event log and casting the case/activity/timestamp columns
- Discovering a DFG and a Petri net from a log
- Variant extraction and frequency ranking
- Running a conformance check and reading fitness

**Learn from** → [pm4py documentation](https://processintelligence.solutions/) — *Getting Started*, *Process Discovery*, *Conformance Checking*. Code along with a real export, not the sample data.

**Time** 2h

**Gate** — a discovered graph from your own data that you can look at and say "yes, that is roughly
how this works" — or "no, and here's which upstream component is wrong."

---

### A4 · Before writing the trace generator

**Concepts you're buying**
- Probability distribution, sampling, and seeding for reproducibility
- **Why durations are lognormal, not normal** — waiting times are multiplicative and right-skewed; a normal distribution will hand you negative durations
- **Percentiles** — p50 and p90, and why you report a range rather than a mean
- Sampling a branch from a categorical probability vector

**Learn from** → [Seeing Theory](https://seeing-theory.brown.edu/) ch. 1–3 (Brown University, free, visual and interactive) · then [`numpy.random.Generator`](https://numpy.org/doc/stable/reference/random/generator.html) docs for the sampling API you'll actually call

**Time** 1h

---

### A5 · Before the baseline predictor

**Concepts you're buying**
- **n-gram / bigram model** — a frequency table *is* a model
- A probability distribution over the next symbol
- **Backoff** — when the 3-gram is unseen, fall back to the 2-gram
- Why a neural version converges to the same answer on small data

**Learn from** → [Karpathy, *Building makemore* part 1](https://karpathy.ai/zero-to-hero.html) — **watch only, 2h.** Building it belongs to Track B; here you only need the idea.

**Time** 2h

> [!info] The counting table you see in the first twenty minutes is your baseline — the null
> hypothesis every later model has to beat before it earns its complexity.

---

### A6 · Before the first statistical model (~week 10+, if the timeline allows)

**Concepts you're buying**
- Train / validation / test, and why touching test more than rarely invalidates it
- **Overfitting**, seen as the gap between two curves
- **Early stopping**
- **Leakage** — the feature that smuggles the answer into the input
- **Case-level splitting** — a whole trace lives in exactly one split
- **Temporal splitting** — the future is the test set
- **Held-out-group splitting** — the only measure of transfer to a source you didn't train on
- Cross-validation, and why random row splits are fatal for sequence data

**Learn from** → Géron, *Hands-On ML* (3rd ed.) **ch. 2 only** · [scikit-learn User Guide §3.1](https://scikit-learn.org/stable/modules/cross_validation.html)

**Time** 5h

**Gate** — deliberately introduce a leak into your own pipeline (join a feature computed from the
whole trace rather than its prefix), watch the accuracy jump, then remove it. Seeing the fake
number appear by your own hand is the entire lesson.

---

### A7 · With A6 — the model itself

**Concepts you're buying**
- Decision tree, splitting criterion, depth and pruning
- **Bagging vs. boosting** — averaging independent models vs. each model correcting the last
- Gradient boosting as sequential residual-fitting
- Learning rate / shrinkage; `min_data_in_leaf` as regularisation
- Native categorical handling (why you don't one-hot for trees)
- Feature importance, and why it isn't an explanation

**Learn from** → [StatQuest](https://www.youtube.com/c/joshstarmer) — *Decision Trees*, *Gradient Boost 1–4*, *XGBoost 1–4* · [LightGBM docs](https://lightgbm.readthedocs.io/) — *Features* + *Parameters Tuning*

**Time** 4h

---

### A8 · Only if the model ships

**Concepts you're buying**
- **Calibration** — when it says 70%, does it happen 70% of the time?
- Reliability diagram, expected calibration error
- **Temperature scaling** and isotonic regression as post-hoc fixes
- **Quantile regression** — predicting a range rather than a point
- **Censoring** — cases still running are information, not missing data
- Kaplan–Meier, Cox proportional hazards, concordance index

**Learn from** → [scikit-learn §1.16 — Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html) · [lifelines docs](https://lifelines.readthedocs.io/) — Introduction + Cox model

**Time** 4h

---

## Track B — Foundations (~37h, evenings, ungated)

This is the *"I know what is happening behind the scenes"* track. It is deliberately **not** on the
build's critical path, so it can never block you — and it is the more durable half, because nobody
will ever ask you about boosting hyperparameters and plenty of people will ask how attention works.

Strict order. Each one earns the next.

---

### B1 · The picture (2h, watch)

**Concepts** — neuron, layer, weights and biases, activation function, cost function, gradient descent, what a gradient geometrically *is*

**Learn from** → [3Blue1Brown — *Neural Networks* ch. 1–4](https://www.3blue1brown.com/topics/neural-networks)

---

### B2 · The mechanism (10h, **build it**)

**Concepts** — computational graph, forward pass, the chain rule, automatic differentiation, what `.backward()` actually does, an MLP as function composition, the training loop, why you `zero_grad`

**Learn from** → [Karpathy — *building micrograd*](https://karpathy.ai/zero-to-hero.html) (2h25m)

> [!important] ~100 lines of pure Python. No numpy, no PyTorch. You implement autograd yourself.
> This is the single highest understanding-per-hour item in either track — afterwards
> backpropagation isn't something you believe in, it's code you wrote.

---

### B3 · Language modelling (6h, build it properly)

**Concepts** — one-hot encoding, softmax, negative log-likelihood and cross-entropy, smoothing, sampling from a distribution, PyTorch tensors and broadcasting

**Learn from** → [Karpathy — *Building makemore* part 1](https://karpathy.ai/zero-to-hero.html) (1h57m)

*You watched this in A5. Now build it.*

---

### B4 · Embeddings (4h)

**Concepts** — an **embedding** as a learned coordinate that puts similar things near each other, embedding lookup as a matrix multiply, context windows, minibatches, finding a learning rate, hyperparameters vs. parameters

**Learn from** → [Karpathy — *Building makemore* part 2: MLP](https://karpathy.ai/zero-to-hero.html) (1h15m)

> [!info] Every "similar entities behave similarly, so a new one inherits its lookalikes' priors"
> claim you will ever make is this idea. Don't skim it.

---

### B5 · Attention (3h, watch and read)

**Concepts** — self-attention, query/key/value, attention scores, multi-head attention, positional encoding, the residual stream

**Learn from** → [3Blue1Brown ch. 5–7](https://www.3blue1brown.com/topics/neural-networks) (*But what is a GPT?*, *Attention in transformers*) · [Jay Alammar — *The Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/)

---

### B6 · The transformer (12h, **build it**)

**Concepts** — decoder-only architecture, causal masking, layer norm, residual connections, the feed-forward block, autoregressive generation, AdamW, cosine schedule with warmup, dropout, weight tying

**Learn from** → [Karpathy — *Let's build GPT: from scratch, in code, spelled out*](https://karpathy.ai/zero-to-hero.html) (1h56m)

Build it, then rebuild it without pausing the video.

---

### B7 · Optional — when training misbehaves (4h)

**Concepts** — activation and gradient statistics, dead neurons, vanishing/exploding gradients, initialisation scale, batch norm

**Learn from** → [Karpathy — *Building makemore* part 3: Activations & Gradients, BatchNorm](https://karpathy.ai/zero-to-hero.html) (1h55m)

Skip until a training run misbehaves. Then it stops being optional.

---

## If you only get five hours this month

In this exact order, and nothing else:

| | | |
|---|---|---|
| 1 | [Zinkevich, *Rules of ML*](https://developers.google.com/machine-learning/guides/rules-of-ml) | 1h — changes what you build **today** |
| 2 | van der Aalst ch. 2 | 2h — changes what you build **next** |
| 3 | [3Blue1Brown ch. 1–4](https://www.3blue1brown.com/topics/neural-networks) | 2h — the cheapest possible removal of the black box |

Everything else waits for its gate. That is not falling behind; that is the schedule.

---

## Mental Model To Remember

> [!info] Order learning by **what the next thing you build refuses to work without**, not by what
> chapter comes next. Knowledge acquired three months before use is knowledge acquired twice. The
> only exception is the foundations track — learn that on a slow burn precisely *because* nothing
> is waiting on it, which is what stops it from being cut every time the schedule slips.
