#machine-learning #deep-learning #transformers #syllabus #just-in-time

---

# The plan changed: the model is now the *first* thing you build, not the last. What do you learn?

> Prerequisites: [[00-learning-path]] (the full catalogue, every resource rated /10) and
> [[01-fast-track-order]] (the just-in-time re-ordering). **This note supersedes the build order in
> both** for the current scope, and points back to them for everything it defers.

The earlier two notes were written for a build that starts with ~6–8 weeks of **zero ML** — raw
archive, tokenizer, identity resolution, case assembly — and reaches the transformer *last*, as the
cheap final 10%. The scope has since inverted: **build the model first, on synthetic sequences, to
prove the pipeline trains and predicts at all.** The data-platform work (the 90%) is deferred.

That inversion changes the syllabus more than it looks, so it's worth stating the finding plainly.

---

## The finding

When the transformer was the *last* thing, the deep-learning arc could live on a slow evening burn
([[01-fast-track-order]] Track B) because nothing was waiting on it. Now it **is** the critical path —
and the two blocks that used to dominate the schedule fall off it entirely.

| Old critical path (files 00/01) | Status now |
|---|---|
| Process mining — DFGs, conformance, pm4py, van der Aalst (~8h + the papers) | **deferred** — you're not building the mining product (Gen 1) in this spike |
| Trees / LightGBM / boosting / SHAP (~12h) | **deferred** — you're skipping the statistical model (Gen 2) and going straight to the transformer |
| Calibration + survival analysis (~4h) | **deferred** — Gen 2 polish |
| Production ML / MLflow (~5h) | **deferred** — nothing is being deployed |
| The deep-learning arc → transformer (was the *evenings* track) | **now the critical path** |
| + multi-attribute encoding (was **not** in either file) | **new, and required** — see block 5 |

> [!success] The re-cut in one sentence: **mining, trees, calibration, and production drop off the
> critical path; the transformer arc moves onto it; and one new thing gets added that the old plan
> never needed — encoding *multiple* event attributes into the model.**
>
> Net effect: ~**41–50h** (vs. 55–65h), but denser, because it's almost all deep learning now and
> almost none of it is optional.

Nothing above is *deleted* — it's deferred. When the platform and Gen 1/2 work resumes, [[00-learning-path]]
and [[01-fast-track-order]] are still exactly right for it. This note only covers the model-first spike.

---

## The build → what each artifact refuses to work without

The spike has four artifacts. Map each to its knowledge, and the order to learn in falls out.

| Build artifact | Knowledge required |
|---|---|
| **1 · The sequence-record contract** (the frozen input schema) | **none** — it's a Pydantic model; you already write these |
| **2 · The synthetic generator** (branch tables → sequences) | ~1–2h of probability |
| **3 · The decoder-only model** (the whole point) | the full deep-learning arc **+** multi-attribute encoding |
| **4 · The eval harness** (is the number real?) | splits, leakage, top-k, a pre-registered baseline |

Artifact 3 is ~70% of the hours. Everything else is small. So the syllabus is really *"how do I get
to a transformer I can modify and trust"* — with two short bookends (probability before, discipline
after).

---

## The critical path, in build order

Learn each block **immediately before** the artifact that needs it. Blocks marked **build it** are
not watch-only — for a working developer, typing the code is where the understanding actually lands.

> [!info] **Build tags.** Each resource that involves *typing code* is tagged for whether you should
> actually implement it — because the fastest route to a working *product* model runs through a few
> deliberate builds, not all of them:
> - **[MUST build]** — type it: it either *becomes* your product, or you can't debug the product without it.
> - **[OKAYISH build]** — building teaches it best, but you can meet the concept while building the real thing; compress if the clock is tight.
> - **[SKIPPABLE build — watch instead]** — throwaway; no code carries forward; watching gives you the whole payoff.
>
> Resources with **no tag are watch/read only** — there's nothing to implement, just consume them.

**Build-effort at a glance** (only the resources that have code to write):

| Resource | Build it? | Why |
|---|---|---|
| micrograd (block 3) | **SKIPPABLE — watch** | throwaway; PyTorch does autograd; pure debugging insurance, no code carries forward |
| makemore pt 1 — toy (4a) | **OKAYISH** | cheapest way to meet softmax / NLL / PyTorch tensors; you rewrite the baseline on real data anyway |
| makemore pt 2 — embeddings (4b) | **OKAYISH** | watch fully; build only if embeddings feel shaky (the *concept* is a must, the *toy* isn't) |
| Karpathy *Let's build GPT* (5a) | **MUST** | it's **stage 1 of your product** on easy data, not a toy — get it green, then mutate it |
| Multi-attribute encoding (5b) | **MUST** | the extension you add *into* the 5a model — it **is** the product architecture |
| Synthetic generator (artifact 2) | **MUST** | your own build; there's no video for it |
| Eval harness + the leak exercise (block 6) | **MUST** | your own build; the hand-done leak is the entire lesson |

> The pattern: you build **two small throwaways** (micrograd + a tiny makemore) and then **one real
> codebase** that starts as *Let's build GPT* on toy data and grows into the product. The only fully
> throwaway *build* is micrograd — everything tagged MUST either carries forward as code or **is** the
> thing you ship.

### Three ways in — pick the channel that clicks

> [!important] **Every concept is offered in all three modalities where they exist — 🎥 video · 📝
> article/blog/book · 💻 code/repo — and you learn it from whichever lands. You do *not* owe the other
> two.** Covering the *same* idea three ways is the point: some ideas click for you on video, some when
> read, some only when you run the code. Two standing rules:
> 1. **A must-have concept stays required even if it's read-only with no video** — necessity decides
>    inclusion, not format. Those are marked **★ read-required**: you read them regardless.
> 2. **For a developer, a paper's repo usually beats its prose**, and **anything still opaque, paste it
>    to me** — I'll rewrite it plain or walk it line by line. You never sit alone with a page you can't parse.

| Block / concept                                           | 🎥 Video                                                                                                                                                                                                                                    | 📝 Article / blog / book                                                                                                                                                                     | 💻 Code / hands-on                                                                                                   |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **1 · Mindset** (baselines; don't fool yourself)          | StatQuest *ML Fundamentals* / *Bias & Variance* (partial)                                                                                                                                                                                   | **★ [Zinkevich *Rules of ML*](https://developers.google.com/machine-learning/guides/rules-of-ml)** — must-have, no real video equivalent; plain English, no math                             | — (pairs with the block-6 leak exercise)                                                                             |
| **2 · Probability** (categorical, lognormal, percentiles) | StatQuest *Probability* / *Normal Distribution*; Khan Academy                                                                                                                                                                               | [Seeing Theory](https://seeing-theory.brown.edu/) (interactive)                                                                                                                              | [`numpy.random`](https://numpy.org/doc/stable/reference/random/generator.html) → write the generator                 |
| **3 · Mechanism** (backprop, autograd)                    | [3Blue1Brown ch. 1–4](https://www.3blue1brown.com/topics/neural-networks); [Karpathy *micrograd*](https://karpathy.ai/zero-to-hero.html); StatQuest *Gradient Descent*                                                                      | [Nielsen — *Neural Networks & Deep Learning*](http://neuralnetworksanddeeplearning.com/) (free book)                                                                                         | [micrograd repo](https://github.com/karpathy/micrograd)                                                              |
| **4 · Next-token + embeddings**                           | [Karpathy *makemore* 1 & 2](https://karpathy.ai/zero-to-hero.html); StatQuest *Word2Vec*                                                                                                                                                    | [Alammar — *Illustrated Word2vec*](https://jalammar.github.io/illustrated-word2vec/); [Raschka *Build a LLM*](https://www.manning.com/books/build-a-large-language-model-from-scratch) ch. 2 | [makemore repo](https://github.com/karpathy/makemore); [Raschka repo](https://github.com/rasbt/LLMs-from-scratch)    |
| **5a · Transformer**                                      | [3B1B ch. 5–7](https://www.3blue1brown.com/topics/neural-networks); [Karpathy *Let's build GPT*](https://karpathy.ai/zero-to-hero.html); StatQuest [*Attention*](https://www.youtube.com/watch?v=PSs6nxngL6k) + *Decoder-Only Transformers* | [Alammar — *Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/); [*The Annotated Transformer*](http://nlp.seas.harvard.edu/annotated-transformer/) (prose+code)   | [nanoGPT repo](https://github.com/karpathy/nanoGPT); The Annotated Transformer                                       |
| **5b · Multi-attribute encoding**                         | — *(none exists — honest gap; ask me instead)*                                                                                                                                                                                              | [Multi-attribute Transformers](https://link.springer.com/chapter/10.1007/978-3-031-18840-4_14); [ProcessTransformer paper](https://arxiv.org/abs/2104.00721) *(read for depth)*              | **★ [ProcessTransformer repo](https://github.com/Zaharah/processtransformer)** — the paper as runnable code          |
| **6 · Discipline + metrics**                              | StatQuest *Cross Validation*, *Bias & Variance*, *ROC/AUC* ([channel](https://www.youtube.com/@statquest)); CampusX / Krish Naik (Hinglish)                                                                                                 | Géron *Hands-On ML* ch. 2; [Thakur — *Approaching Almost Any ML Problem*](https://github.com/abhishekkrthakur/approachingalmost)                                                             | [sklearn §3.1](https://scikit-learn.org/stable/modules/cross_validation.html) → call it; the leak exercise you write |
| **6 · Grounding papers**                                  | — *(none)*                                                                                                                                                                                                                                  | [*David vs Goliath*](https://arxiv.org/pdf/2606.15868); Tax et al. *(optional — I'll give the one-line takeaway)*                                                                            | their repos, if you want to run them                                                                                 |

> [!info] **Two different axes — don't confuse them.** The **build tags** above (MUST / OKAYISH /
> SKIPPABLE) answer *"do I type this code as a deliverable?"*. This table answers *"which representation
> do I learn the concept from?"* — e.g. backprop is a SKIPPABLE *build* (micrograd) but you still
> *learn* it, ideally from the 🎥 video. **Learn every concept; build only what's tagged MUST.**

> [!tip] If even **Karpathy feels too fast**, the patient video path is **Vizuara** (Raj Dandekar) and
> **CampusX / Krish Naik** (Hinglish) — the slower alternatives rated in [[00-learning-path]]. Same
> ideas, more minutes each. Nothing says you must learn from the fastest source.

---

### 1 · The mindset — before you agree what to ship (1h)

**Concepts** — launch the simplest thing first; your first model is a *baseline*; the metric you
optimise vs. the one you care about; **why a good number can still be a lie** (the entire risk of a
synthetic spike is a beautiful-but-meaningless score).

**Learn from** → [Zinkevich, *Rules of ML*](https://developers.google.com/machine-learning/guides/rules-of-ml)
— Rules 1–23. (Rated 9/10 in [[00-learning-path]] Stage 3.)

> [!important] Read this *before* you promise anyone what the spike proves. It's the discipline that
> stops "the model predicts!" from becoming a claim it can't support.

---

### 2 · Probability — before the synthetic generator (1–2h)

**Concepts** — sampling from a **categorical** distribution (choosing a branch by its probability
vector); **seeding** for reproducibility; **why durations are lognormal, not normal** (waiting times
are multiplicative and right-skewed — a normal draws negative times); **percentiles** (p50/p90,
report a range not a mean).

**Learn from** → [Seeing Theory](https://seeing-theory.brown.edu/) ch. 1–3 (Brown, free, interactive)
· then [`numpy.random.Generator`](https://numpy.org/doc/stable/reference/random/generator.html) for the
API you'll call. *(Both watch/read; the generator you write from them is **[MUST build]** — it's artifact 2.)*

**Gate** — your generator emits reproducible sequences into the sequence-record schema, with realistic
right-skewed time gaps.

---

### 3 · The mechanism — nothing is magic (2h watch + 8h build, or 2.5h watch-only)

**Concepts** — neuron/layer/weights; cost function; gradient descent and what a gradient *is*;
computational graph; the chain rule; automatic differentiation; what `.backward()` does; the training
loop; `zero_grad`.

**Learn from** →
[3Blue1Brown *Neural Networks* ch. 1–4](https://www.3blue1brown.com/topics/neural-networks) (2h, watch)
· then [Karpathy — *building micrograd*](https://karpathy.ai/zero-to-hero.html) (2h25m video, ~8h to
build) — **[SKIPPABLE build — watch instead if crunched]**. Both rated 9–10/10 in [[00-learning-path]] Stage 1.

> [!tip] **This is the one place to compress if the clock is truly against you.** micrograd is the
> highest understanding-per-hour item in the whole path — but it's also the most skippable *for
> shipping*, because PyTorch does autograd for you. Build it if you can; the day a training run
> misbehaves it pays for itself. If you genuinely can't spare the day, **watch it, don't build it**,
> and come back. Every *other* build-it block below is load-bearing and should not be compressed.

---

### 4 · Next-token + embeddings — the heart of it (10h, **build both**)

This is two Karpathy videos, and for *this* project they are the most important hours you will spend —
because the model is nothing but next-token prediction over learned embeddings, and the cross-company
"companies like you" mechanism is **literally an embedding**.

**4a · Next-token, counted then learned** → [Karpathy — *makemore* part 1](https://karpathy.ai/zero-to-hero.html)
(1h57m, build — 6h) — **[OKAYISH build]** (build the toy once for the PyTorch/softmax plumbing + baseline idea)
**Concepts** — a frequency/**bigram table *is* a model**; softmax; negative log-likelihood /
cross-entropy; sampling; PyTorch tensors + broadcasting.
> The counting table you build in the first 20 minutes **is your baseline** — the null hypothesis the
> transformer has to beat before it has earned anything (block 6). Double duty: you need it for
> artifact 4 anyway.

**4b · Embeddings** → [Karpathy — *makemore* part 2 (MLP)](https://karpathy.ai/zero-to-hero.html)
(1h15m, build — 4h) — **[OKAYISH build]** (watch fully; build only if embeddings still feel fuzzy)
**Concepts** — an **embedding** = a learned coordinate that puts similar things near each other;
embedding lookup as a matrix multiply; context windows; minibatches; finding a learning rate.
> [!info] **Do not skim this one.** Two things in your model are embeddings: the activity tokens, *and*
> the per-company vector that makes a new company borrow from its lookalikes. The whole cross-tenant
> thesis is this block. (Rated 9/10, [[00-learning-path]] Stage 5.)

---

### 5 · The transformer — and the one extension the old plan never mentioned (16h build + 3h read)

**5a · Vanilla decoder-only** (watch/read the picture, then build):
- [3Blue1Brown ch. 5–7](https://www.3blue1brown.com/topics/neural-networks) + [Jay Alammar — *Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/) — attention, visually (3h)
- [Karpathy — *Let's build GPT, spelled out*](https://karpathy.ai/zero-to-hero.html) (1h56m, build — 10–12h) — **[MUST build]**. **This is the architecture you ship** — stage 1 of your product on easy data. Build it, get it green on Shakespeare, then mutate it (swap the data loader, add 5b). Rebuild it once without pausing.
  **Concepts** — self-attention (Q/K/V), multi-head, positional encoding, causal masking, residual
  stream, layer norm, the FFN block, AdamW, cosine-warmup schedule, dropout, weight tying.

> [!info] At ~1M parameters on a laptop, `nanoGPT` isn't a toy of something bigger — it **is** the
> reference implementation for this project. (See the [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) repo.)

**5b · Multi-attribute encoding + a conditioning prefix — the new required block.** **[MUST build — you add this *into* the 5a model; it's the product, not a separate toy.]**
Vanilla nanoGPT eats a *single* stream of tokens. Your sequence-record has **several channels per
event** (`token`, `time_gap`, `actor`, `source`, `position`) **plus a context vector** (`org`,
`emp_type`, `dept`, `designation`, `industry`, `size`) that conditions the whole sequence. Feeding all
of that into one transformer is a real design step nanoGPT doesn't show you — and it's a *solved,
published* problem, so read rather than reinvent:

**Concepts** — **sum (or concatenate) one embedding per attribute** at each position; **static vs.
dynamic attributes** (context is static across the sequence, the event channels are dynamic);
bucketise the continuous `time_gap` into a categorical and embed it (or project it); feed the context
either as a **prefix "system prompt"** or as a bias added to every position; the **org embedding** is
just this same lookup applied to company id.

**Learn from** →
- [Multi-attribute Transformers for Sequence Prediction in BPM](https://link.springer.com/chapter/10.1007/978-3-031-18840-4_14) (Springer) — **the most on-target paper for this exact step**; it compares ways to encode activity + resource + time into one transformer. **9/10 for this project.**
- [ProcessTransformer](https://arxiv.org/abs/2104.00721) — mine it for input-encoding choices and benchmark numbers (already 9/10 in [[00-learning-path]]).

**Gate** — a decoder-only model that trains on your synthetic sequence-records, consuming all event
channels **and** the context vector, and emits a probability distribution over next activity.

---

### 6 · The eval harness — is the number real? (5h + 2 papers)

Skipping this is not an option: the *entire* value of a synthetic spike is a *trustworthy* verdict, and
a synthetic score is the easiest number in the world to fake yourself into. The harness and the
deliberate-leak exercise are **[MUST build]** — they're your artifact 4, not a video to watch.

**Concepts** — train/validation/test; overfitting as the gap between two curves; early stopping;
**leakage** (a feature that smuggles the answer in — e.g. anything computed from the whole trace rather
than its prefix); **the three splits that matter here**:
- **case-level** — a whole sequence lives in exactly one split (never day-2 in train, day-3 in test);
- **temporal** — the future is the test set;
- **held-out-group** — a whole *company* held out; the only honest measure of "works on one we didn't train on."

Plus the two spike-specific checks from `gen3-synthetic-validation-plan.md`:
- **held-out combination** — train on some factor combos, test an unseen one → does the model *blend*?
- **embedding convergence** — two similar-but-differently-named synthetic companies → do their org
  embeddings move together? (That's the cross-tenant claim, made falsifiable.)

**Metric** — **top-k accuracy** on the held-out split, with a **pre-registered** pass/fail threshold
written down *before* you run.

**Learn from** → Géron *Hands-On ML* ch. 2 · [scikit-learn §3.1](https://scikit-learn.org/stable/modules/cross_validation.html)
(both rated in [[00-learning-path]] Stage 3) · and read two papers that are your exact problem:
- [*David vs. Goliath in Next Activity Prediction*](https://arxiv.org/pdf/2606.15868) — a trivial argmax baseline vs. LSTM/transformer/LLM. **Read first** — it's block 1's "always run the baseline," proven empirically in your domain. (10/10)
- Tax et al. — *Predictive Business Process Monitoring with LSTM* (CAiSE 2017) — the canonical short paper everything cites. (9/10)

**Gate** — you deliberately introduce a leak (join a whole-trace feature), watch top-k jump, then
remove it. Seeing the fake number appear by your own hand is the lesson the whole spike depends on.

---

## What's now cut — and where it went

For clarity, everything from files 00/01 that is **not** on this path, and why it's safe to skip *for
the spike*:

| Deferred | Comes back when |
|---|---|
| Process mining (pm4py, van der Aalst, DFG, conformance, XES) | you build the discovery/mining product (Gen 1) on real traces |
| Trees / LightGBM / boosting / SHAP | you build the statistical model (Gen 2) for cold-start + explanations |
| Calibration + survival/censoring | Gen 2 ships and needs honest probabilities + duration ranges |
| Production ML / MLflow / monitoring | anything is actually deployed and retrained on a schedule |
| Tokenizer-from-bytes, RAG, fine-tuning, agents | not this project — see the "skip deliberately" table in [[00-learning-path]] |


---

## Latest-resource notes (checked July 2026)

Three updates since files 00/01 were written — two are traps, one is the block-5b addition above.

- **Karpathy's [nanochat](https://github.com/karpathy/nanochat) (Oct 2025)** — a full-stack ChatGPT
  clone in ~8k lines (tokenizer → pretrain → SFT → RL → chat UI) for ~$100 of GPU.
  [[00-learning-path]]'s verdict on the *tokenizer* and *deep-dive* videos applies here too:
  **outstanding, mostly the wrong problem for this spike.** Its *pretraining* half overlaps nanoGPT;
  the SFT/RL/chat-UI half is a different job you're not doing. **nanoGPT remains the right reference.**
  Watch nanochat for your career, not for this build.
- **Raschka — [*Build a Reasoning Model (From Scratch)*](https://www.manning.com/books/build-a-reasoning-model-from-scratch) (2025–26)** —
  a sequel to his excellent *Build a LLM (From Scratch)*. **Also out of scope** (reasoning/RL, not
  next-activity prediction). The *original* book (+ Vizuara's free video walkthrough) is still the best
  book-form alternative to Karpathy for blocks 4–5, exactly as rated in [[00-learning-path]].
- **The process-monitoring field is hot right now** (2025–26: graph/hypergraph nets, switch-transformers,
  RAG-with-LLMs for next-activity). **Do not chase these for a first spike** — they're accuracy-squeezing
  variants that assume you already have the plain decoder working. The Multi-attribute Transformers
  paper (block 5b) is the one worth reading *now*; the rest are for later.

---

## If you only get five hours this month

In this exact order, and nothing else:

| | | |
|---|---|---|
| 1 | [Zinkevich, *Rules of ML*](https://developers.google.com/machine-learning/guides/rules-of-ml) 1–23 | 1h — the discipline that keeps the spike honest |
| 2 | [3Blue1Brown ch. 1–4](https://www.3blue1brown.com/topics/neural-networks) | 2h — removes the black box |
| 3 | [Karpathy — *makemore* part 1](https://karpathy.ai/zero-to-hero.html) (watch) | 2h — next-token + your baseline, in one sitting |

Everything else waits for its artifact. That's the schedule, not falling behind.

---

## Mental Model To Remember

> [!info] When the model was the *last* 10%, you could learn deep learning slowly. Now it's the *whole*
> deliverable, so the transformer arc **is** the critical path — but the honest-evaluation block (6) is
> still what decides whether the spike means anything, exactly as it was when the model was small.
> Order changed; the rule didn't: **mechanism so nothing is magic, then discipline so you can catch
> yourself lying, then the one model you're actually shipping.**

---

> [!warning] You still don't need all of it before you start. Write the schema and generator after
> block 2; build the model across blocks 3–5; learn block 6 right before you trust a number. Knowledge
> acquired three months before use is acquired twice.

## Sources

- [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) · [karpathy/nanochat](https://github.com/karpathy/nanochat) · [Karpathy — Zero to Hero](https://karpathy.ai/zero-to-hero.html)
- [3Blue1Brown — Neural Networks](https://www.3blue1brown.com/topics/neural-networks) · [Jay Alammar — Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Multi-attribute Transformers for Sequence Prediction in BPM](https://link.springer.com/chapter/10.1007/978-3-031-18840-4_14) · [ProcessTransformer](https://arxiv.org/abs/2104.00721) · [David vs. Goliath in Next Activity Prediction](https://arxiv.org/pdf/2606.15868)
- [Raschka — Build a Reasoning Model (From Scratch)](https://www.manning.com/books/build-a-reasoning-model-from-scratch) · [Raschka — Build a LLM (From Scratch)](https://www.manning.com/books/build-a-large-language-model-from-scratch)
- [Zinkevich — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml) · [scikit-learn §3.1 Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) · [Seeing Theory](https://seeing-theory.brown.edu/)
- **Beginner video channels:** [StatQuest — channel](https://www.youtube.com/@statquest) · [StatQuest — Attention, Clearly Explained](https://www.youtube.com/watch?v=PSs6nxngL6k) · [ProcessTransformer — GitHub (read the code, not the paper)](https://github.com/Zaharah/processtransformer)
- **Multi-modal (all three channels):** [Nielsen — Neural Networks & Deep Learning](http://neuralnetworksanddeeplearning.com/) · [The Annotated Transformer](http://nlp.seas.harvard.edu/annotated-transformer/) · [Alammar — Illustrated Word2vec](https://jalammar.github.io/illustrated-word2vec/) · repos: [micrograd](https://github.com/karpathy/micrograd) · [makemore](https://github.com/karpathy/makemore) · [Raschka LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch)
