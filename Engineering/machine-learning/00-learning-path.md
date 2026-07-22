#machine-learning #deep-learning #transformers #process-mining #syllabus

---

# How do you learn only the ML you need to build one specific system?

> Prerequisite: none. This is a root note.
> Target: a **next-activity prediction system over process event logs** — read a partial sequence
> of events from a workflow, predict what happens next and when. The published field is called
> *predictive process monitoring*. Everything below is rated against that target and nothing else.
>
> **Building on a deadline? Start with [[01-fast-track-order]] instead** — it re-orders this
> catalogue by what the next build phase refuses to work without, and lists the concepts each
> resource actually buys you. Come back here when you want the ratings and the alternatives.
>
> **Building the model *first*, on synthetic data (scope changed)? See [[02-model-first-syllabus]]** —
> it supersedes the build order here for that spike: the transformer arc moves onto the critical path,
> mining/trees/calibration/production come off it, and one new block (multi-attribute encoding) is
> added. This catalogue's ratings still hold; only the order and scope change.

You have no ML background and a system to build. The obvious move is a course. The obvious move is wrong, and it's worth knowing why before spending three months on it.

---

## The Problem With Taking A Course

A general ML course spends its first third on things this system never touches — convolutional
networks, clustering, dimensionality reduction, reinforcement learning — and its last third on theory you will never hand-derive. Meanwhile the skill that actually decides whether the system works gets one lecture.

That skill is this:

> [!danger] **In machine learning, the default state is that your numbers are lying to you.**
> A leaked feature, a random row-split, a baseline you never ran — each produces a beautiful
> validation score and a model that is worthless in production. Nothing errors. Nothing crashes.
> You just ship something that doesn't work and find out months later.

So the path below is inverted from a course. It front-loads the *mechanism* (so nothing is magic),then immediately goes to *discipline* (so you can audit your own results), and treats the
transformer — the exciting part — as the fourth thing you learn, not the first.

**~55–65 hours of real work.** Watching is not working; you build every one of these. At 6 hrs/week
that is roughly ten weeks.

---

## How To Read The Ratings

Every score is **out of 10, for this path only.** A resource can be world-class in general andscore 5 here because it teaches the wrong thing well. Where that happens, it's said explicitly.

| | |
|---|---|
| **9–10** | Do it. Skipping it leaves a hole you will feel later. |
| **7–8** | Genuinely good; pick it if the primary doesn't suit your learning style. |
| **5–6** | Fine resource, wrong target. Listed so you don't waste weeks discovering that. |

---

## Stage 1 — What a neural network actually *is* (~10h)

**Goal:** "training" stops being a black box and becomes three concrete things — a graph of operations, a wrongness number, and the chain rule.

### Primary

| Resource | Rating | Why |
|---|---|---|
| [3Blue1Brown — Neural Networks, ch. 1–4](https://www.3blue1brown.com/topics/neural-networks) | **9/10** | ~1.5h. The best visual answer to "what *is* a gradient". No code, pure intuition. Watch before touching a keyboard. |
| [Karpathy — *The spelled-out intro to neural networks and backpropagation: building micrograd*](https://karpathy.ai/zero-to-hero.html) | **10/10** | 2h25m video, ~8h if you build it. **You must build it.** |

`micrograd` is ~100 lines of pure Python — no numpy, no PyTorch. You implement autograd yourself.
For a working developer this is the highest-leverage ML resource that exists: afterwards,
backpropagation isn't a concept you believe in, it's code you wrote.

### Alternatives

| Resource | Rating | When you'd pick it |
|---|---|---|
| [Vizuara — *Build LLMs from Scratch*, Dr. Raj Dandekar](https://www.youtube.com/watch?v=Xpr8D6LeAtw) | **8/10** | 44 lectures, 1500+ minutes, free, by an MIT PhD; follows Raschka's book. Slower and more patient than Karpathy, Indian-English delivery. Pick it if Karpathy's pace loses you. |
| [CampusX — *100 Days of ML*, Nitish Singh](https://learnwith.campusx.in/) | **7/10** | Hinglish, extremely thorough, has written notes. Downgraded only because 100 videos is the opposite of optimizing — it's a course, and a good one. |
| [fast.ai — *Practical Deep Learning for Coders*](https://course.fast.ai/) | **6/10** | Excellent, famous, top-down — you fine-tune a working model in lesson 1. Wrong for you: you want the mechanism, and it defers exactly that. |
| [Andrew Ng — ML Specialization (Coursera)](https://www.coursera.org/specializations/machine-learning-introduction) | **7/10** | The canonical foundation. Broad and slow relative to your target; take it if you want the whole field rather than this system. |

> [!success] **Done when** you can explain what `.backward()` does without using the word "gradients".

---

## Stage 2 — Next-token prediction, counted *then* learned (~10h)

**Goal:** understand that predicting the next item in a sequence is a counting problem before it is a neural problem — and see exactly where the neural version starts to win.

### Primary

| Resource | Rating | Why |
|---|---|---|
| [Karpathy — *Building makemore*, part 1](https://karpathy.ai/zero-to-hero.html) | **10/10** | 1h57m. Builds a bigram model **as a counting table**, then rebuilds the identical model as a neural network and shows they converge. |

That counting table is the exact shape of the baseline every serious project needs — *"predict whatever most frequently followed"* — the null hypothesis that every fancier model must beat. You will build it on toy data here and on real sequences later.

### Alternatives

| Resource | Rating | When you'd pick it |
|---|---|---|
| [Sebastian Raschka — *Build a Large Language Model (From Scratch)*](https://www.manning.com/books/build-a-large-language-model-from-scratch) ch. 2 | **9/10** | Manning, 2025. The book version of this whole arc, and the best written treatment available. Paid. |
| Vizuara's lectures on the above | **8/10** | Free video walkthrough of Raschka's book, chapter by chapter. |

> [!success] **Done when** you can say why the neural version isn't better than the count table here,
> and describe the conditions under which it would start to be.

---

## Stage 3 — Discipline (~10h) ← *the stage that decides everything*

**Goal:** be able to look at any reported number — yours or someone else's — and say whether it is trustworthy.

This is roughly 60% of applied ML competence and roughly 5% of most curricula. Do it here, right after you've watched something train, so that "overfitting" is a chart you have personally seen rather than a word.

### Primary

| Resource | Rating | Why |
|---|---|---|
| [Zinkevich — *Rules of Machine Learning*](https://developers.google.com/machine-learning/guides/rules-of-ml) (Google) | **9/10** | Free, ~1h, rules 1–23. Opinionated and correct: *"don't be afraid to launch without ML"*, *"your first model should be simple"*. |
| Géron — *Hands-On ML* (3rd ed.), **ch. 2 only** | **9/10** | The end-to-end project: splits, leakage, pipeline hygiene. Skip the rest of the book for now. |
| [Abhishek Thakur — *Approaching (Almost) Any ML Problem*](https://github.com/abhishekkrthakur/approachingalmost) | **8/10** | Free PDF. 4× Kaggle Grandmaster. The cross-validation and metrics chapters are precisely on target; it teaches *how to work*, not what algorithms are. |
| [scikit-learn User Guide §3.1](https://scikit-learn.org/stable/modules/cross_validation.html) | **8/10** | Cross-validation, done properly. |

**Do this stage on your own data.** Build the frequency baseline. Then *deliberately introduce a
leak* — join a feature computed from the whole sequence rather than from its prefix — and watch
accuracy jump. Seeing the fake number appear with your own hands is the entire lesson.

### Alternatives

| Resource | Rating | When you'd pick it |
|---|---|---|
| [Kaggle Learn — Intro + Intermediate ML](https://www.kaggle.com/learn) | **7/10** | Fastest hands-on route. Shallow on *why*, which is the part you need. |
| [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course) | **6/10** | Solid and free; aimed at breadth, and heavier on TensorFlow than is useful here. |

> [!danger] There is no substitute for this stage. Everything downstream — every claim you make to a
> stakeholder — inherits its trustworthiness from here. If you skip one stage, skip Stage 5, not this.

---

## Stage 4 — Trees, and everything a first real model needs (~12h)

**Goal:** build the model that will probably carry the product for a year. Gradient-boosted trees
are the reigning champion for tabular data, work with hundreds of examples rather than millions,
and explain their own predictions.

### Primary

| Resource | Rating | Why |
|---|---|---|
| [StatQuest — Decision Trees, Gradient Boost 1–4, XGBoost 1–4](https://www.youtube.com/c/joshstarmer) | **10/10** | Josh Starmer works the arithmetic by hand, visually, one step at a time. The best beginner explanation of tree ensembles anywhere, and it isn't close. |
| [LightGBM docs — *Features* + *Parameters Tuning*](https://lightgbm.readthedocs.io/) | **8/10** | 30 minutes that prevent weeks of cargo-culting hyperparameters. |
| [Molnar — *Interpretable ML*, SHAP chapter](https://christophm.github.io/interpretable-ml-book/shap.html) | **8/10** | Free. "Why did you predict this?" is a product feature, not a debugging tool. |
| [scikit-learn §1.16 — Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html) | **8/10** | When the model says 70%, does it happen 70% of the time? If you promise honest probabilities, this is where you keep the promise. |
| [lifelines docs — intro + Cox model](https://lifelines.readthedocs.io/) | **8/10** | Survival analysis and **censoring**. Cases still running aren't failures — throwing them away biases every duration estimate optimistically. |
| Guo et al. — *On Calibration of Modern Neural Networks* (ICML 2017), §1–3 | **7/10** | Where temperature scaling comes from. Read three sections, skip the proofs. |

### Alternatives

| Resource | Rating | When you'd pick it |
|---|---|---|
| CampusX — ensemble/boosting videos | **7/10** | Same material in Hindi/Hinglish, more slowly. |
| [Krish Naik — ML playlists](https://www.youtube.com/@krishnaik06) | **6/10** | Enormous catalogue and genuinely popular; variable depth and loose sequencing. Better as a lookup for one topic than as a path. |
| XGBoost or CatBoost docs instead of LightGBM | **7/10** | All three are excellent. LightGBM wins here on speed, native categorical handling, and quantile objectives. |

> [!success] **Done when** you can explain why a boosted tree beats a single deep tree, and can read
> a SHAP plot out loud to a non-technical person.

---

## Stage 5 — Transformers, properly (~15h)

**Goal:** build a small decoder-only transformer and understand every line. Now that you've done
Stage 2, "next-token prediction" already means something concrete.

### Primary

| Resource | Rating | Why |
|---|---|---|
| [3Blue1Brown — ch. 5–7 (*But what is a GPT?*, *Attention in transformers*)](https://www.3blue1brown.com/topics/neural-networks) | **9/10** | The attention mechanism, visually, before you meet it in code. |
| [Jay Alammar — *The Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/) | **8/10** | The canonical picture-based explanation. Read alongside the videos. |
| [Karpathy — *Building makemore* part 2 (MLP)](https://karpathy.ai/zero-to-hero.html) | **9/10** | Where **embeddings** appear — a learned coordinate that puts similar things near each other. Every "similar entities behave similarly" claim you will ever make lives here. |
| [Karpathy — *Let's build GPT: from scratch, in code, spelled out*](https://karpathy.ai/zero-to-hero.html) | **10/10** | 1h56m video, 10h+ to build. Build it, then rebuild it without pausing the video. This *is* the architecture you'll ship. |

> [!info] Your model will be ~1M parameters and train on one GPU in hours. `nanoGPT` is not a toy
> version of something bigger you'll need later — at this scale it **is** the reference implementation. Everything through this stage runs on a laptop CPU.

### Alternatives

| Resource | Rating | When you'd pick it |
|---|---|---|
| [Umar Jamil — *Coding a Transformer from scratch in PyTorch*](https://www.youtube.com/watch?v=ISNdQcPhsts) | **9/10** | Full encoder–decoder with training, inference and attention visualisation. More complete than Karpathy on the training loop; excellent as a second pass. |
| [Raschka — *Build a LLM (From Scratch)*](https://www.manning.com/books/build-a-large-language-model-from-scratch) | **9/10** | The book to own if you prefer reading to video. Covers pretraining through fine-tuning. |
| [Vizuara — 44-lecture series on Raschka's book](https://www.youtube.com/watch?v=Xpr8D6LeAtw) | **8/10** | Free, exhaustive, patient. The most complete Indian-educator resource in this space. |
| Karpathy — *Let's build the GPT Tokenizer* | **5/10** | Superb video, wrong problem. Byte-pair encoding solves a text problem; a domain vocabulary is authored by hand, not learned from bytes. **9/10** if your goal is general LLM understanding. |
| Karpathy — *Deep Dive into LLMs like ChatGPT* (~3.5h) | **5/10** | Same verdict: outstanding, and about pretraining/SFT/RLHF, which you are not doing. Watch it for your day job, not for this. |

---

## Stage 6 — Production ML (~5h)

| Resource | Rating | Why |
|---|---|---|
| Chip Huyen — *Designing ML Systems*, **ch. 8** | **8/10** | Distribution shift and monitoring. Real processes are non-stationary — reorgs, tool migrations — so retraining is design, not maintenance. |
| [MLflow — Tracking + Model Registry quickstarts](https://mlflow.org/docs/latest/index.html) | **7/10** | Enough to operate an experiment tracker and promote models. Don't read more than the quickstarts. |

**Alternative:** Huyen ch. 6 (offline evaluation) — **7/10**, worth it after ch. 8, not before.

---

## Side Track — Process mining (~8h, and it isn't ML at all)

This runs in parallel and **gates the first thing you build**, because discovering a process from an
event log requires zero machine learning. Start it whenever.

| Resource | Rating | Why |
|---|---|---|
| [Coursera — *Process Mining: Data Science in Action*](https://www.coursera.org/learn/process-mining) (van der Aalst, TU/e) | **9/10** | Taught by the man who founded the field. Free to audit. |
| van der Aalst — *Process Mining: Data Science in Action* (2nd ed.), ch. 2 & 6 (ch. 8 for conformance) | **9/10** | The textbook. Two chapters carry most of what you need. |
| [pm4py documentation — Discovery + Conformance](https://processintelligence.solutions/) | **8/10** | The library you'll actually use. Code along with real exports. |
| [Celonis × RWTH — *Process Mining: From Theory to Execution*](https://www.celonis.com/academy/) | **7/10** | ~10h, industry-flavoured, also van der Aalst. Good second pass, vendor-shaped. |

> [!tip] Almost no ML engineer has heard of predictive process monitoring. Four items here puts you
> ahead of most people you could hire.

### The papers — this is your exact research field

| Paper | Rating | Why |
|---|---|---|
| **"David vs. Goliath in Next Activity Prediction: Argmax vs. LSTM, Transformer, and LLM"** ([arXiv 2606.15868](https://arxiv.org/pdf/2606.15868)) | **10/10** | Read this *first*. A trivial argmax baseline benchmarked against LSTMs, transformers and LLMs on next-activity prediction. Stage 3's "always run the baseline" lesson, delivered empirically, in your own domain. |
| **"Enhancing Predictive Process Monitoring on Small-Scale Event Logs Using LLMs"** ([Springer](https://link.springer.com/chapter/10.1007/978-3-032-02929-4_16)) | **9/10** | Reports accurate predictions from **as few as 10 training traces**. Directly relevant to any cold-start situation — and it suggests using an LLM *as* the predictor at cold start rather than training a model on invented data. |
| **"Leveraging Data Augmentation and Siamese Learning for PPM"** ([arXiv 2507.18293](https://arxiv.org/abs/2507.18293)) | **9/10** | Generates synthetic trace variants using **statistically grounded, control-flow-aware transformations** rather than free generation. If you ever need synthetic sequences, this is the defensible way to make them. |
| Tax et al. — *Predictive Business Process Monitoring with LSTM Neural Networks* (CAiSE 2017) | **9/10** | Short, canonical, the paper everything else cites. Read fully. |
| Bukhsh et al. — *ProcessTransformer* ([arXiv 2021](https://arxiv.org/abs/2104.00721)) | **9/10** | The transformer version of the above. Mine it for input-encoding choices and benchmark numbers. |
| Teinemaa et al. — *Outcome-Oriented PPM: Review and Benchmark* (TKDD 2019) | **8/10** | §2–3 for the landscape and the evaluation traps; skim the rest. |

---

## What To Skip, Deliberately

A course teaches all of this. None of it touches the target.

| Skipped | Why |
|---|---|
| CNNs / computer vision | Nothing here is an image. |
| RNNs / LSTMs *as implementation* | Read the Tax paper; never build one. The architecture you want is a transformer. |
| Reinforcement learning, GANs, diffusion | Different problems entirely. |
| Deriving gradients by hand | Stage 1's micrograd is the only maths you need. |
| Fine-tuning LLMs, RAG, prompt engineering | A different job. Real skills, wrong project. |
| Kubeflow, Spark, feature stores, vector DBs | Infrastructure for a scale you do not have. |
| Attention maths beyond what Karpathy codes | The code *is* the understanding. |

---

## Where To Keep Watching After

Signal, not noise: **@karpathy** and **@rasbt** (Sebastian Raschka) on X are the two accounts whose teaching output is consistently worth the interruption. Beyond that, the honest answer is that
predictive process monitoring barely exists on social media — its real activity is in the **BPM** and **ICPM** conference proceedings, published annually. Set a calendar reminder to skim the
proceedings rather than expecting a feed to surface them.

---

## Mental Model To Remember

> [!info] Learn the **mechanism** so nothing is magic, then the **discipline** so you can catch
> yourself lying, then the **simple model** that will carry production, and only then the
> transformer. Reversing that order produces someone who can train a network and cannot tell
> whether it works — which is worse than knowing nothing, because it comes with confidence.

---

> [!warning] Learning order is not build order. The first thing you build needs no ML at all — the
> side track covers it. Don't wait to finish the path before starting; run them in parallel and each
> one makes the other concrete.
