#ai-engineering #evals #agents #block-1 #syllabus

# Block 1 · Agent Evals — Syllabus

**22 notes, 224 rungs.** Generic — the practice and its failure modes, not Xarvis's implementation, which is mapped at the bottom.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — the judge agrees with you 94% of the time, therefore it looks trustworthy, therefore you check which 6%, therefore they are all the failures, therefore the number was measuring the easy cases. Rungs are not topics and not section headings. Seven to fifteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about evaluation teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

**Why generic first.** If the syllabus is derived from the codebase, every concept the codebase happens not to exercise gets silently dropped — and those are exactly the ones an interviewer asks about. So: learn the full surface, **then** map. Concepts Xarvis cannot demonstrate become theory-only, deliberately, rather than by accident.

**Three halves, trained differently.** Notes 1 to 12 and 15 to 21 are mechanism — what a measurement does and how it lies — and respond to retrieval practice, so the rungs are the recall unit. Notes 13, 14 and 22 are **craft**: error analysis, golden-set design, and harness construction are learned by doing them badly once, and retrieval drills do not transfer. Those three are worked on real data, not recalled.

**Ends with three numbers Xarvis has never had:** tool-selection accuracy · param-extraction accuracy · access-control enforcement rate.

**Currency check (2026-09-06):** Frontier models now saturate the classic public benchmarks, so a leaderboard score decides nothing about your application — note 2 is more true in 2026 than when it was written. The important 2026 finding on judges is that their failure is **asymmetric**: true positive rate is usually fine and **true negative rate is low**, meaning a judge agrees enthusiastically that good output is good and quietly misses real failures. Minority-veto ensembles and chain-of-thought judging (the G-Eval line) are the current mitigations, and position, verbosity and self-preference remain the three named biases. LangChain's 2026 State of AI Agents reports 57% of organisations running agents in production with **quality as the number one barrier**, which is the market reason this block is first. Re-verify before relying on: RAGAS's current metric set and API surface, whether your provider's eval product scores trajectories natively, and **your LangSmith plan's trace retention** — the free Developer tier is 14 days with a 5,000-trace monthly cap, which decides whether you have a corpus or a rolling window.

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**Where a rung says break, it is run, not read.** Watching the same suite return 71% and then 78% at temperature zero produces a problem the fix attaches to. Reading that LLMs are nondeterministic produces a fact that decays.

**Recall is per note, from memory, file closed.** Recognising an answer does not count.

**Notes 13 and 14 need real traces and cannot be faked.** They are the two that produce the portable artifact, and they are the two that expire with repository access. If trace retention turns out to be short, they move to the front regardless of the numbering.

**Three rabbit holes are marked and binding** — statistical significance machinery in note 18, the classical precision/recall/F1 literature in note 8, and benchmark internals in note 21. All three are deep, satisfying, and pay back nothing here.

**Spacing:** re-test notes 1 to 7 after finishing note 12, and 8 to 16 after the harness is built. Same-day re-testing is close to wasted, because retrieval works when forgetting has started.

**The syllabus governs the numbering — never the source material.** A lecture, video or article covering concept 7 becomes `07-*.md`, even if it was the fourth video in its playlist. One video may feed several notes, or several videos one note. Gaps in the numbering are concepts not yet reached, not missing files.

---

# A · Foundations

## Note 1 · Why Evals, Not Vibes

9 rungs. No break — this is framing.

1. You change a prompt, try three inputs, they look better, you ship.
2. That is a measurement with a sample size of three, chosen by you, after the change.
3. It is also **correct** in one specific case: a system with one user, cheap failures, and a change you can fully inspect.
4. **Break it** — the fourth input, which you did not try, is now worse, and you will not find out until someone complains.
5. So the problem is not that spot-checking is unrigorous, it is that it does not **persist**: nothing from today's three inputs is available tomorrow.
6. An eval is a **fixed set of cases plus a grader plus a recorded number** — the persistence is the point, not the rigour.
7. Two kinds of number come out, and confusing them is the common error: **quality metrics** you want to go up, and **guardrail metrics** that must not go down while you chase quality.
8. Which means an eval suite is not one number but a scoreboard, and a change that raises the first while dropping the second is a regression that looks like progress.
9. The maturity path is therefore not vibes to evals but a ladder: vibes → spot checks → a golden set → a CI gate → online monitoring, and **each rung costs more and catches a class the one below cannot**.

> **Recall:** When is spot-checking the correct choice rather than the lazy one? · What does an eval have that a spot check does not? · What is the failure mode of a single headline number?

## Note 2 · Model Evals Versus Application Evals

10 rungs. **Break:** find the MMLU score of the model you use, then ask what it predicts about your own system's accuracy.

1. Two questions sound the same and are not: is this model good, and is my system good.
2. The first is answered by public benchmarks — MMLU, GSM8K, and their successors.
3. **Break it** — a model at the top of every leaderboard still fails your application, because your application is a prompt, a tool schema, a retrieval step and a parser wrapped around that model.
4. So a benchmark measures a component you did not build and cannot change, which makes it a **procurement** signal and nothing else.
5. Two mechanisms make it worse than merely irrelevant: **saturation**, where every frontier model scores within noise of every other, and **contamination**, where the test set has leaked into training data.
6. As of 2026 the classic benchmarks are saturated, so the leaderboard has stopped discriminating even for procurement.
7. An application eval measures the assembled system on **your** inputs, which no one else can build for you.
8. That is the part you cannot outsource, and it is also the part that is worth something on a resume, because everyone has read the leaderboard and almost nobody has built the other thing.
9. The practical consequence: model upgrades become a hypothesis, not an improvement — you swap the model and rerun your suite.
10. Which is only possible if the suite exists first, so the ordering is forced.

> **Recall:** What can a benchmark score legitimately be used for? · Name the two mechanisms that degrade a benchmark's usefulness and how they differ. · Why does a model upgrade require an eval suite rather than justify one?

## Note 3 · Eval-Driven Development

9 rungs. No break — this is placement.

1. Tests in ordinary software are written before or alongside code, and the loop is red, green, refactor.
2. The obvious move is to do the same thing with evals, and the analogy holds for the first two steps: write cases, watch them fail, change the system.
3. **Where it breaks** — you cannot make a probabilistic system green. There is no change that takes 87% to 100% and holds it there.
4. So the passing condition is not all-green but a **threshold**, and choosing that threshold is a product decision rather than an engineering one.
5. Which means the eval suite cannot be a blocking gate in the way a unit test is, or every deploy is blocked forever.
6. Instead it gates on **delta**: this change must not drop the score, rather than this score must be perfect.
7. That reframes the whole loop — evals are a **ratchet**, not a proof, and their job is to make regressions visible rather than to establish correctness.
8. It also explains why evals feel unsatisfying to people arriving from strong testing cultures, and why saying so out loud is a good interview answer.
9. The place evals sit in the loop is therefore beside the deploy, not before the merge, until the suite is cheap enough and stable enough to run per pull request.

> **Recall:** Exactly where does the TDD analogy break? · Why is the gate a delta rather than an absolute? · What is a ratchet, in this sense?

---

# B · The Taxonomy — How You Grade

## Note 4 · Grading Methods

12 rungs. **Break:** write a code assertion for did the assistant answer politely, and watch it be impossible.

1. Something has to turn a system output into a score, and there are exactly three things that can: code, a model, or a person.
2. **Code-graded** assertions are deterministic, free, instant, and repeatable — did it call the right tool, is the JSON valid, is the employee id the one requested.
3. **Break it** — try to code-grade whether an answer is helpful, or polite, or complete, and you will find yourself writing a keyword list that is wrong by the third example.
4. So code grading is bounded by whether the property is **checkable in principle**, not by effort.
5. **Model-graded** (LLM-as-judge) handles exactly the properties code cannot, because it can read.
6. Its cost is money and latency per case, and its risk is that the grader is the same kind of thing being graded, with the same blind spots.
7. **Human evaluation** is the only ground truth, and is therefore both the most reliable and the one you can afford least of.
8. Which produces the actual rule: humans define ground truth on a small set, the judge is aligned against that set, and code grades everything it can so the judge is never asked what an assertion could answer.
9. Getting that ordering backwards — reaching for a judge first — is the most common and most expensive mistake in the field.
10. A useful test for which to reach for: if two careful people would agree on the answer without discussion, it is code-gradeable or judge-gradeable; if they would argue, no grader will save you and the criterion is wrong.
11. Judge depth — biases, calibration, rubric design — is **Block 3**; here it is only placed in the taxonomy.
12. So the deliverable of this note is a rule for choosing, not a judge.

> **Recall:** What bounds code grading, and what bounds judge grading? · State the ordering rule and why reversing it is expensive. · What does it mean when two careful graders disagree?
>
> **Stop:** No judge prompt engineering, no bias taxonomy, no calibration. Block 3.

## Note 5 · Reference-Based Versus Reference-Free

8 rungs. **Break:** take a correct answer, reword it entirely, and score both against the reference with exact match.

1. The easiest grader compares output to a known correct answer.
2. That requires a gold answer to exist, which it does for classification, extraction, and tool selection.
3. **Break it** — for a generated paragraph there are thousands of correct answers, and exact match scores a perfect rewording as zero.
4. The classical repair is fuzzy overlap: BLEU and ROUGE count shared n-grams.
5. **Break that too** — they reward sharing words with the reference, which correlates with correctness only weakly and can be gamed by copying the question.
6. So for generated text the gold answer is not merely hard to write, it is the **wrong shape**: correctness is a property of the output alone, judged against criteria, not against another string.
7. That is reference-free evaluation — grading against a rubric or a property rather than an answer key.
8. Which means the choice is decided by the output space, not by convenience: a closed output space gets a reference, an open one gets criteria.

> **Recall:** What property of the output decides between the two? · Why does n-gram overlap fail where exact match already failed? · Give one thing in an agent that legitimately has a gold answer.

## Note 6 · Offline Versus Online

15 rungs. **Break:** take your golden set, and try to write a case for an input you have never seen.

1. Offline evaluation runs a fixed set of cases before shipping.
2. It has three jobs and they are distinct: **gating** a release, **comparing** two versions on a level field, and **catching regressions** in what already worked.
3. The level field is the part people miss — the same cases, the same grader, so the only variable is the change.
4. **Break it** — a golden set can only contain inputs somebody thought of, and production is a firehose of inputs nobody thought of.
5. Three things escape offline entirely: **unanticipated inputs**, **emergent failures** visible only at scale, and **drift** that quietly makes yesterday's golden set describe a system that no longer exists.
6. So online evaluation is not a nicer version of offline, it is the only thing that can see those three.
7. Online has one crippling constraint: **there is no answer key**, because the input arrived a second ago and nobody has labelled it.
8. Which forces a change of question, from correctness to **normality** — not is this answer right, but is this answer like the ones that were right.
9. Concretely that means comparing against a baseline distribution: response length, tool-call counts, latency, refusal rate, retry rate.
10. And harvesting **implicit feedback**, which is the user telling you without being asked: thumbs, retries, rephrasings, escalations, abandonment.
11. Abandonment is the strongest and the least logged — a user who closes the tab mid-answer has rated it.
12. The online pipeline has a fixed shape: logging → captured versus computed signals → stratified sampling → evaluator → dashboard → alerting.
13. **Stratified** matters because uniform sampling of production traffic returns the boring majority and misses the failures you are looking for.
14. And the loop closes: every online failure found becomes an offline case, so the golden set grows from production rather than from imagination.
15. Which is the real relationship — offline is a cache of what online already taught you.

> **Recall:** Name the three things offline cannot see, and why each escapes. · What replaces correctness when there is no answer key? · Why stratified rather than uniform sampling? · What is the direction of the loop between online and offline?

Broadened 2026-07-30 — originally one line about pre-ship versus production. The online pipeline is substantial enough to carry the concept. Logging, dashboarding and alerting get their depth in Block 2 (Observability); here they appear only as the eval pipeline's plumbing.

---

# C · What You Measure In An Agent

## Note 7 · The Failure Taxonomy And Risk Categories

14 rungs. **Break:** make every component test pass, then run one real end-to-end request.

1. A failing system fails somewhere specific, and where decides what you can do about it.
2. There are three levels: **component**, **workflow**, **entire application**.
3. **Break it** — every component passes and the application still fails, because the components were correct and their composition was not.
4. So green at one level implies nothing about the level above, and a suite that tests only components is measuring the easy half.
5. Cutting the other way, there are three risk categories: **application quality**, **safety**, and **operational**.
6. Quality failures annoy, safety failures harm, operational failures cost — and they need different thresholds, different owners, and different alerting.
7. Levels times categories is a grid, and **the grid is what tells you how many evals a system needs** and where each one goes.
8. Within that grid, agents fail in named ways worth memorising because they recur.
9. **Tool-call hallucination** — invoking a tool that does not exist.
10. **Wrong tool selected** — a real tool, the wrong one for the request.
11. **Right tool, wrong parameters** — the subtlest and the most damaging in a data system, because it returns a confident answer about the wrong record.
12. **Infinite loops** and **premature termination** are the two ends of the same control failure, and a recursion cap converts the first into the second.
13. **Giving up too early** is distinct from premature termination: the agent finishes cleanly while declining a task it could have done.
14. **Context pollution** and **goal drift** are the long-conversation failures — earlier turns poisoning later ones, and the objective quietly changing between step 3 and step 30.

> **Recall:** Why does component-level green tell you nothing about the application? · What does the levels-by-categories grid decide? · Distinguish premature termination from giving up too early. · Which agent failure is most dangerous in a system holding real records, and why?
>
> **Stop:** No classical precision/recall/F1 derivations. Rabbit hole, marked, binding.

Broadened 2026-07-30 — originally scoped as the agent failure taxonomy, which was too narrow. This is the concept that determines how many evals a system needs and where each one goes, so it has to cover non-agent systems too.

## Note 8 · Trajectory Versus Outcome

12 rungs. **Break:** find a case where the final answer is correct and the tool sequence is wrong, and decide whether it passed.

1. An agent produces two things: a **path** (which tools, in what order, with what arguments) and an **answer**.
2. The obvious thing to grade is the answer, because that is what the user sees.
3. **Break it** — an agent that reaches the right answer by calling an unauthorised tool, or by guessing, has passed your eval and is a live bug.
4. So a right answer via a wrong path is not a pass, it is a **latent failure** that will surface on the next input where guessing does not happen to work.
5. Grading the path is therefore not optional in an agent, and it is also the only grading that localises the fault.
6. Two numbers fall straight out and are the most quotable metrics in this whole block: **tool-selection accuracy** and **parameter-extraction accuracy**.
7. They are code-gradeable, deterministic, and free — which is why note 4's ordering rule sends you here before it sends you to a judge.
8. Matching a trajectory has three strictnesses, and choosing wrong makes the number meaningless.
9. **Exact match** — same tools, same order. Correct when order is semantically required.
10. **Subset / in-order-with-extras** — the required calls happened in order, additional ones are tolerated. Correct when the agent may legitimately explore.
11. **Order-insensitive** — the right set of calls in any order. Correct when the calls are independent.
12. The failure mode is defaulting to exact match, which turns every harmless extra lookup into a red test and trains you to ignore the suite.

> **Recall:** Why is a right answer by a wrong path a failure? · Name the two metrics this note produces and why they are cheap. · What breaks when you default to exact-match trajectory scoring?

## Note 9 · Evaluating The Tool Layer Itself

9 rungs. **Break:** take a failing tool-selection case, change only the tool's description string, and rerun.

1. When an agent picks the wrong tool, the instinct is that the model is not smart enough.
2. **Break it** — change nothing but the tool's description, and the same model now picks correctly.
3. So the tool description is part of the prompt, and a wrong selection is frequently a **documentation** bug wearing a model bug's clothes.
4. Which makes tool names, descriptions, parameter names and schemas **eval targets** rather than fixed inputs.
5. The same applies to error messages: what a tool returns on failure is read by the model and steers the next step.
6. A tool that fails with a bare stack trace teaches the agent nothing; one that fails with what it needed teaches recovery.
7. So you A/B tool schemas the way you A/B prompts, against the tool-selection accuracy from note 8.
8. This is also the cheapest lever in the entire block — a description edit costs nothing and can move the number several points.
9. And it is the lever nobody tries first, which is why it is worth being the person who does.

> **Recall:** What is the usual real cause of wrong-tool selection? · Why is a tool's error message an eval target? · Which metric does this note act on?

## Note 10 · Should-Refuse And Negative Cases

8 rungs. **Break:** count how many of your eval cases have a correct answer of no.

1. An eval set is naturally built from things the system should do.
2. **Break it** — a system that answers everything scores perfectly on that set and is a security incident.
3. So the agent correctly **declining** is a passing case, not the absence of a case.
4. Four distinct categories, and they fail differently: **refusal** (should not), **access denial** (may not), **out of scope** (cannot), **unanswerable** (nobody could).
5. Access denial is the one with teeth in a system holding real records, and it produces a third quotable number: **access-control enforcement rate**.
6. That number is code-gradeable and needs no judge — the expected outcome is a specific denial, and anything else is a failure.
7. It is also the only eval that measures a security property, which makes it worth more per case than anything else in the suite.
8. And its cases are the easiest to generate honestly, because every guard in the system implies one.

> **Recall:** Why does an all-positive eval set flatter a broken system? · Name the four negative categories and what distinguishes them. · Which one produces a security number, and why is it cheap to grade?

## Note 11 · Multi-Turn And Conversational Evaluation

10 rungs. **Break:** take a passing single-turn case and prepend two unrelated turns.

1. Everything so far graded one request and one response.
2. **Break it** — prepend two turns of unrelated conversation and the same case can fail, because the model is now reading a history it was not tested with.
3. So the unit of evaluation for a chat system is the **conversation**, not the turn, and single-turn suites systematically overestimate.
4. Which raises an immediate problem: a conversation requires a second party, and the second party is a user you do not have.
5. **Simulated users** are the standard answer — a model playing the user against a persona and a goal.
6. Its cost is that you are now evaluating two models and can no longer attribute a failure cleanly.
7. Three conversational behaviours are worth their own cases, because none appear in single-turn testing.
8. **Mind-changing** — the user contradicts an earlier constraint, and the agent must follow the new one rather than average them.
9. **Clarification** — whether the agent asks when the request is genuinely ambiguous, which is a passing behaviour that looks like failure to complete.
10. **Recovery** — whether the agent gets back on track after a wrong turn, which is the behaviour that most separates a usable agent from a demo.

> **Recall:** Why do single-turn suites overestimate? · What does a simulated user cost you? · Name the three conversational behaviours and why each is invisible single-turn.

## Note 12 · Long-Horizon And Multi-Agent Evaluation

9 rungs. **Break:** score a 30-step task pass/fail and watch every run score zero.

1. Some tasks run 20 to 50 steps before producing anything.
2. Grading those pass/fail is the obvious move.
3. **Break it** — almost every run fails somewhere, every score is zero, and the number cannot distinguish a run that failed at step 2 from one that failed at step 29.
4. So long-horizon tasks need **partial credit**, which requires deciding in advance what counts as progress.
5. **Checkpoint scoring** is the practical form: named intermediate states, each independently verifiable, scored as how far it got.
6. That also converts a useless binary into a diagnostic, because the distribution of failure checkpoints tells you where to work.
7. When work crosses a handoff between agents, a new problem appears: **attribution**.
8. A failure at step 29 may have been caused by a bad handoff at step 6, and the agent that visibly failed is not the one that broke.
9. Which is why long-horizon evaluation depends on tracing in a way that single-turn evaluation does not — you cannot attribute what you did not record, and this is the concrete reason Block 2 exists.

> **Recall:** Why does binary scoring fail on long tasks specifically? · What does a checkpoint distribution tell you that a score cannot? · Why is attribution a tracing problem rather than an eval problem?

---

# D · The Dataset

## Note 13 · Error Analysis First

15 rungs. **Break:** write down the five failure modes you expect, then read twenty real traces and count how many you predicted. This is craft — it is done, not recalled.

1. The natural order is to decide what good looks like, then measure it.
2. **Break it** — write your five expected failure modes, read twenty real traces, and typically two of the five occur while the largest real bucket was not on your list.
3. So criteria written before looking measure your imagination, and the gap between imagined and actual failures is the single most reliable finding in this field.
4. Which inverts the order: **look at traces first, write criteria second**.
5. The method has a name borrowed from qualitative research, and borrowing it correctly matters.
6. **Open coding** — read one trace, write a short free-text note of what went wrong, in your own words, without a category list.
7. No category list is the discipline: the moment you have one you start filing rather than seeing.
8. Do that for 20 to 100 traces and you have a pile of notes, not a taxonomy.
9. **Axial coding** — group the notes into recurring buckets, name each bucket, and count how many traces fall in it.
10. The counts are the point. A taxonomy without counts cannot tell you what to fix.
11. Then the ordering is forced: **write evals for the biggest buckets**, because an eval for a rare failure costs the same as one for a common failure and is worth less.
12. This is also the step that produces the portable artifact — a named, counted failure taxonomy survives losing access to the system it came from.
13. The common objection is having no traces yet, and it has a real answer: generate plausible inputs, run them, and analyse those, accepting that the distribution is yours rather than your users'.
14. And a second, sharper answer — if the system is live, you have traces, you simply have not looked, and the reason is almost always that nobody set up the retention to keep them.
15. Which makes checking retention part of this note rather than an infrastructure detail: a 14-day window means the corpus is a rolling sample, and analysis cannot be deferred to a convenient month.

> **Recall:** State the inversion and the evidence for it. · Why is having no category list the discipline in open coding? · What makes the counts, rather than the buckets, the output? · What is the honest answer when there are no traces?

## Note 14 · Building The Golden Set

12 rungs. **Break:** build a 500-case synthetic set and a 30-case real set, and compare what each catches. Craft — done, not recalled.

1. An eval needs cases, and more cases sounds better.
2. **Break it** — 500 generated easy cases catch less than 30 hard real ones, because the generated ones cluster around the behaviour that already works.
3. So the currency is **difficulty and realism**, not volume, and 20 to 50 genuinely hard real cases is a working set.
4. Cases come from four places, in descending order of value: production failures, error analysis buckets, known bugs, and imagination.
5. Which means note 13 is not a prerequisite by convention — it is where the cases physically come from.
6. A single case record has a fixed shape: input, any required setup or state, expected outcome or criteria, the grading method, and **why this case exists**.
7. The last field is the one everyone omits and the one that saves the set, because in three months a failing case whose purpose is unrecorded gets deleted rather than fixed.
8. Coverage is designed across **capabilities**, not across inputs — one case per thing the system claims to do, before ten cases for the thing it does most.
9. That is also how you notice a capability nobody ever tested, which is usually where the worst bug is.
10. Negative cases from note 10 belong in the same set, not a separate one, so that a change cannot improve helpfulness while quietly disabling a guard.
11. The set is a living artifact: cases get added from production and retired when the behaviour is permanently fixed.
12. And it is versioned, which is note 16.

> **Recall:** Why do 30 real cases beat 500 synthetic ones? · What are the five fields of a case record, and which one is always omitted? · Why is coverage designed across capabilities rather than inputs?

## Note 15 · Synthetic Eval Data

8 rungs. **Break:** generate 50 cases with a model, then check how many are variations of the same three.

1. Writing cases by hand is slow, so generating them with a model is the obvious accelerant.
2. It genuinely works for volume, for permutations of a known shape, and for filling a coverage gap you have already identified.
3. **Break it** — generate 50 cases and read them, and they collapse into a handful of templates with the nouns changed.
4. The reason is structural: **the generator's blind spots become your blind spots**, and it is blind in the same places your system is, because it is the same kind of thing.
5. Which produces the rule — synthetic data is safe for **coverage** and dangerous for **discovery**.
6. So it can broaden a bucket that error analysis already found, and it cannot find the bucket.
7. A practical mitigation is seeding: generate from real inputs as templates rather than from a description of the task.
8. And an honest one: label a synthetic case as synthetic in the record, so a suite's realism can be audited later.

> **Recall:** What is synthetic data safe for and dangerous for? · State the structural reason in one sentence. · Why does seeding from real inputs help?

## Note 16 · Splits, Versioning, And Overfitting

10 rungs. **Break:** tune prompts against one set for a week, then run the held-out set.

1. You run the suite, see 71%, change the prompt, see 78%, and repeat.
2. **Break it** — after a week of that, the number is 91% and the system is not better, because you have been fitting the prompt to the specific cases.
3. That is overfitting, and it happens faster with evals than with machine learning because the set is small and you look at every failure individually.
4. So the set splits: a **dev set** you iterate against and a **held-out set** you run rarely.
5. Rarely is the operative word — a held-out set consulted weekly becomes a dev set within a month.
6. Versioning follows, because the number only means something relative to the set that produced it.
7. A version records the cases, the grading criteria, **and the grader configuration** — including judge model and prompt, because changing the judge changes the number with no change to the system.
8. Comparing scores across versions without saying so is the most common way an eval report becomes a lie.
9. Sets also **rot**: the product changes, and cases silently start testing behaviour nobody wants any more.
10. You notice by tracking the pass rate of the oldest cases — a set where everything old passes and everything new fails has stopped measuring the system and started measuring its history.

> **Recall:** Why does overfitting happen faster here than in ML? · What three things does a set version have to record? · How do you detect a rotting eval set?

---

# E · Making The Number Trustworthy

## Note 17 · Nondeterminism And Determinism Controls

10 rungs. **Break:** set temperature to 0 and run the same suite three times.

1. The obvious fix for a varying score is to set temperature to zero.
2. **Break it** — run the identical suite three times at temperature zero and the number still moves.
3. Temperature zero makes sampling greedy, which is not the same as making the computation deterministic.
4. Three mechanisms remain. **Floating-point non-associativity** under different batch sizes changes the arithmetic, and the provider batches your request with strangers.
5. **Provider-side variance** — the model behind a version string is updated, rerouted, or served from differently configured hardware.
6. **Ties** — when two tokens have near-identical probability, any of the above flips the choice, and one flipped token can change a whole trajectory.
7. A seed helps where the provider exposes one and does nothing where it does not, so it is a partial control rather than a solution.
8. Therefore the honest position is that a single run is a **sample**, and a score without a spread is an anecdote with a decimal point.
9. Which forces reporting a range or a run count alongside every number.
10. And it forces note 18, because if one run is a sample then the question is what to do with several.

> **Recall:** Why does temperature zero not give determinism? · Name the three remaining mechanisms. · What is wrong with a single reported score?

## Note 18 · pass@k And pass^k

11 rungs. **Break:** run one case five times, count passes, and compute both metrics on the same five results.

1. Note 17 leaves you running each case several times.
2. **pass@k** asks whether **at least one** of k attempts succeeded.
3. The naive estimator — run k times, check if any passed — is **biased**, because it depends on which k you happened to run.
4. The unbiased form estimates from n total samples with c successes, and is computed as a product of ratios rather than by expanding factorials, which overflow.
5. pass@k rises with k by construction, so a high pass@k can describe a system that fails most of the time.
6. Which is exactly right for code generation with a test suite, where you can try again and keep the one that works.
7. **Break it** — for an agent that sends an email or updates a record, the first attempt already happened, and there is no keeping the good one.
8. So **pass^k** asks whether **all** k attempts succeeded, which is the reliability question.
9. pass^k falls with k, fast, and a system at 90% per attempt is at 59% over five.
10. The pair is the point: pass@k flatters agents and pass^k is what production cares about, and quoting only the first is how demos are built.
11. Which one you report is therefore a claim about whether your system's actions are retryable.

> **Recall:** Why is the naive pass@k estimator biased? · What property of the task decides between the two metrics? · What is 90% per attempt over five attempts, and why does that number matter?
>
> **Stop:** No significance testing, confidence intervals, or power analysis. Rabbit hole, marked, binding — Block 3.

## Note 19 · Regression Versus Progression

7 rungs. **Break:** fix a bug, add its case, and watch it pass forever while telling you nothing.

1. Two questions look like one: did I break what worked, and did I fix what was broken.
2. **Regression** cases are things that already pass, and their job is to keep passing.
3. **Progression** cases are things that currently fail, and their job is to start passing.
4. **Break it** — put both in one suite and the aggregate number moves for two unrelated reasons, so it answers neither question.
5. They also want different thresholds: a regression suite is near-zero-tolerance, a progression suite is expected to be mostly red.
6. And different lifecycles — a progression case that passes reliably graduates into the regression set.
7. Which means the split is not organisational tidiness, it is what lets a single number mean something.

> **Recall:** Why does mixing them destroy the number? · What are the two thresholds and why do they differ? · What happens to a progression case that passes?

## Note 20 · The Cost Of Evaluating

8 rungs. **Break:** price your full suite per run, then multiply by your pull requests per week.

1. Every eval run is inference, and inference is money and wall-clock time.
2. A judge-graded suite costs a model call per case, on top of the system call per case.
3. **Break it** — a 300-case judged suite on every pull request is a real monthly bill and a twenty-minute wait, and the team will start skipping it.
4. A suite that gets skipped has a score of zero regardless of what it measures.
5. So suites are **tiered**: a fast smoke set per pull request, the full suite nightly, the expensive judged set weekly or on release.
6. Tiering is chosen by what each tier can catch — the smoke set carries the code-graded guardrails, because they are free and they are the ones that must never break.
7. Sampling is the other lever, and stratified sampling from note 6 applies here too: run all of the rare categories and a sample of the common one.
8. Which makes cost a design input to the suite rather than a consequence of it.

> **Recall:** What is the score of a suite that gets skipped? · How is the smoke tier chosen? · Why does the cheap grader belong in the most frequent tier?

---

# F · The Landscape

## Note 21 · Agent Benchmarks

7 rungs. No break — orientation.

1. Public agent benchmarks exist and get cited constantly: τ-bench, SWE-bench, WebArena, GAIA, AgentBench.
2. Each measures something specific — τ-bench tool use in customer-service dialogue with rule-following, SWE-bench resolving real GitHub issues, WebArena browser tasks on self-hosted sites, GAIA multi-step reasoning with tool use, AgentBench a spread of environments.
3. Knowing which is which is worth the twenty minutes, because they come up in interviews and misattributing them is a visible tell.
4. **They still cannot decide anything about your system**, for the same reason as note 2: they measure a component you did not build on a distribution that is not yours.
5. Their real use is **method**: reading how τ-bench scores rule-following, or how SWE-bench verifies a fix, teaches harness design.
6. So read one benchmark's evaluation code, not its leaderboard.
7. And treat a candidate who quotes benchmark numbers about their own product as having answered a different question.

> **Recall:** Name three benchmarks and what each measures. · What is their actual use to you? · Why does quoting one about your own system misfire?
>
> **Stop:** No benchmark internals, task lists, or leaderboard history. Rabbit hole, marked, binding.

---

# G · Implementation

## Note 22 · Building A Harness

11 rungs. **Break:** build the loop for one case with no framework, then decide what a framework would have given you. Craft — done, not recalled.

1. Everything above is a specification for one loop.
2. The loop is: **case → run → capture → grade → record**, and every eval framework is that loop with opinions.
3. **Case** is loaded from a versioned file, not written in the test body, so the set can be edited by someone who does not read code.
4. **Run** invokes the system the way production does — through the same entry point, or the harness measures a path no user takes.
5. **Capture** is where trajectory comes from, and it is the step that fails first, because most systems do not expose the tool calls to the caller.
6. Which is the concrete reason tracing is a dependency: you cannot grade a trajectory you cannot see.
7. **Grade** dispatches by method — code assertion, judge, or human queue — per the rule in note 4.
8. **Record** writes the result with the set version, the system version, the grader configuration, and the timestamp, because a score without those is not comparable to anything.
9. Building this once by hand, for one case, is what makes framework choice a decision rather than a default.
10. Then bind it to whatever is in front of you, and the binding is small — the framework supplies runners, storage and a UI, not the thinking.
11. The harness is also the artifact that does not survive losing repository access, which is why it ranks below the taxonomy and the golden set when time is short.

> **Recall:** State the five stages. · Which stage fails first in an untraced system, and why? · What four things does a recorded result need to be comparable?

---

## Deferred, deliberately

| Topic | Goes to |
|---|---|
| LLM-as-judge depth, judge biases, calibration, rubric design | Block 3 |
| Judge alignment metrics — TPR, TNR, Cohen's kappa | Block 3 |
| Inter-annotator agreement, handling human disagreement | Block 3 |
| Statistical significance, sizing an eval set for a real delta | Block 3 |
| Tracing, spans, cost and latency attribution | Block 2 |
| RAG-specific evals — the triad, RAGAS, recall@k / MRR / nDCG | Blocks 7-8 |

Block 1 is first precisely because it needs **no LLM judge and no new infrastructure**. Notes 4, 12 and 22 each point at a dependency, and each is deliberately left pointing rather than followed.

---

## Xarvis mapping

**To be filled after the concepts are learned — not before.** Each of the 22 lands in one of:

- **Applicable** → implement it in Xarvis, produce a number
- **Theory-only** → Xarvis cannot exercise it; learn it, be able to discuss it, do not fake having built it
- **Parked** → belongs to the retrieval product (blocks 7-9)

Rough expectation going in: several of 11, 12, 15 and 21 land in theory-only, and that is the correct outcome rather than a gap. Notes 8, 10 and 13 are the ones expected to produce real numbers, and note 13 is the one that expires with repository access.
