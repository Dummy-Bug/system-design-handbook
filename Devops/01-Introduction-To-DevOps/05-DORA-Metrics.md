CALMS ends with **Measurement**, and leaves the question open: measure *what*, exactly?

**DORA metrics** are the answer. Four numbers that let you look at a company and say something factual about whether it practises DevOps, rather than something impressionistic.

> [!danger] DORA stands for  **DevOps Research and Assessment** — the name of the research group whose long-running study of engineering organisations produced these metrics. Worth having right, because this is the kind of thing an interviewer asks directly.

---

## What DORA is actually judging

Something important, and easy to miss:

> [!important] **DORA does not measure how skilled the engineers are.** A company can hire outstanding developers, an outstanding operations team and an outstanding DevOps engineer, and still score badly. If the numbers are bad, that company is drifting toward the silo model no matter who it employs.
>
> **The shape of the organisation dominates the talent inside it.** DORA measures the shape.

---

## Four questions

The whole framework is four questions you could ask any engineering organisation:

| # | Question | Metric |
|---|---|---|
| 1 | How frequently do you deploy? | **Deployment frequency** |
| 2 | How quickly does a change reach production? | **Lead time for change** |
| 3 | How frequently do failures occur in deployment? | **Change failure rate** |
| 4 | How quickly do you recover from those failures? | **Mean time to recovery** |

If a company can answer all four with real numbers, you can form a genuine view of how much DevOps philosophy it applies.

And notice how they split:

```mermaid
flowchart TB
    subgraph SP["Speed — how fast can you deliver?"]
        Q1["1 · Deployment frequency"]
        Q2["2 · Lead time for change"]
    end
    subgraph RE["Reliability — does it hold up?"]
        Q3["3 · Change failure rate"]
        Q4["4 · Mean time to recovery"]
    end
```

Which is exactly **fast delivery and reliable delivery** from note `03`, made countable. The four metrics are not saying anything new — they are the two goals with numbers attached.

---

## 1 · Deployment frequency

How often does this company put code into production?

The answer might be several times a day, once a week, once a month, or every fourteen days on a fixed sprint cycle — different teams follow different models.

**More frequent is better.** Shipping one or two small things every day is a healthy sign: it means small changes, arriving continuously.

**What counts as a deployment?** The company defines it. A small patch counts. A bug fix counts. A major feature counts. The rough test is whether something meaningful shipped — a new feature, or a fix to an existing one.

**Calculating it** is simple averaging. A company shipped 40 deployments over the last 20 days:

$$\frac{40 \text{ deployments}}{20 \text{ days}} = 2 \text{ deployments per day}$$

> [!warning] **High frequency alone does not mean a good company.** A team could deploy fifty things a day and have every one of them be a changed paragraph or a fixed spelling mistake. That is a large number describing nothing.
>
> This is why there are four metrics and not one. Deployment frequency gives you a rough shape, and the other three stop you from being fooled by it.

## 2 · Lead time for change

How long does it take a change to travel from *finished code* to *live in production*?

The clock starts where the developer's job ends — the code is written and **committed** — and stops when it is serving users.

```mermaid
flowchart LR
    C["Commit<br/><i>developer's work ends</i>"] --> B["Build"]
    B --> T["Testing<br/>unit + integration"]
    T --> E["Staging / QA<br/>environments"]
    E --> W["Waiting to batch<br/>with other features"]
    W --> P["Production<br/><i>live</i>"]
    C -.->|"⟵ lead time for change ⟶"| P
```

Everything in that middle stretch is time the developer is not in control of: the build, the test suites, running in one environment after another, and often simply waiting so that several features can go out together.

**Shorter is better.** If a feature took two days to write, you would like it live within a day or two of that — not four days later, and certainly not thirty.

> [!info] **Why so many environments?** Code usually runs in several places before production, and the count varies by company. Common ones are a **QA environment** for testing and a **staging environment** for a final check.
>
> Staging is often called **pre-prod**, and the name explains the idea: it looks exactly like production — same setup, same shape — but it is internal. Real users have not reached it. It is the last place a problem can be caught cheaply.

## 3 · Change failure rate

Of everything you deployed, how much of it broke?

$$\text{change failure rate} = \frac{\text{failed deployments}}{\text{total deployments}} \times 100$$

Deploy 50 things in a month and have 5 of them fail, and your change failure rate is 10%.

**Failed** means what you would expect: a feature that does not work, or a bug fix that did not fix the bug.

A small number of failures is normal and not worth panicking about — 5 out of 50 is survivable. What you are watching for is failure becoming the common case rather than the exception.

## 4 · Mean time to recovery

You now know how often things break. The remaining question is how long you stay broken.

Take a month with three failures, and time how long each took to resolve:

| Incident | Time to recover |
|---|---|
| Feature 1 | 20 minutes |
| Feature 2 | 40 minutes |
| Feature 3 | 90 minutes |
| **Total** | **150 minutes** |

$$\frac{150 \text{ minutes}}{3 \text{ incidents}} = 50 \text{ minutes}$$

So the mean time to recovery is **50 minutes**: on average, when something breaks in production, this company has it working again within roughly an hour.

> [!info] The standard term is **Mean Time to Recovery (MTTR)**, sometimes written as "time to restore service." 

What "recovering" actually consists of turns out to be a genuine question with three different answers — which is the next note.

---

> [!tip] **Interview framing.** This is theory, and DevOps interviews ask theory directly. You are not expected to have the four names memorised as vocabulary — you are expected to know **what each one measures and why anyone cares**. The strongest version of the answer connects them back: two of these measure speed, two measure reliability, and those are the only two things DevOps claims to deliver.
