# Plan — November 2026 to March

2026-11-11 · updated 2026-11-15 after [[13-Trajectory-2026]] · follows [[11-Amazon-SDE2-Loop]]

> [!abstract] What this file is
> Where I actually stand on 2026-11-11, who the prep is for, and how the weekday hours split. It replaces the September course plan in [[07-Course-Strategy-And-Lab-2]] and the timeline in [[08-Action-Plan-To-December]]: the deadline is March, when the company either breaks even or shuts, and the targets are an Amazon SDE-2 referral plus AI-engineer roles at startups.

---

## Where I stand on 2026-11-11

| Area | Now | Evidence |
|---|---|---|
| **AI engineering** | Building compliance-agent since about 5 October: an agentic interface over Compliflow that files and pays Professional Tax on state portals, with HR consent before every filing | 5,083 source lines, **5,592 test lines, 153 tests, 375 assertions**, mypy strict, ruff with security rules, a PRD, **95 ADRs**, 28 tickets, 15 bug write-ups |
| **Xarvis** | Sole author, verified in September | 99.7% of 25,789 lines ([[05-Repo-Audit-xarvis]]) |
| **Testing** | The worst September finding is reversed | Xarvis had 0 assertions in ten months; compliance-agent's tests outweigh its source |
| **DSA** | Idle since **2026-06-26**, about 4.5 months | ~108 problem notes from May and June, ~1530 contest rating in May, 3 contests logged |
| **DSA, the real wall** | ~300 classics known from watched solutions and solved several times; unseen problems fail | Self-report, and the June diagnosis in `LC/reflexes/00-install-roadmap.md`: derivation speed |
| **DSA, open families** | Tree-DP 0 of 2, monotonic stack 1 of 2, graph and DP reflex tracks never started | `LC/topic-install-ledger.md` |
| **LLD** | 30 notes with Java code: BookMyShow, Parking Lot, Splitwise, thread-safe LRU, rate limiter, mostly October | `Low Level Design/` |
| **Hand-written code** | Rusty, since coding agents write nearly all of it at work | Self-report |
| **HLD** | LeetDezine case studies, pattern reactivation in progress | `System Design/` |
| **AI course** | At module 16, RAG; about 3 hours of recorded lectures a week | `camp/16-RAG/` |

Dropped from the September plan: Kafka with the outbox, Testcontainers and the VPS deploy. No loop I am targeting asks for them.

---

## The deadline

```mermaid
flowchart LR
    A["11 Nov<br/>plan starts"] --> B["25 Nov<br/><b>first review</b><br/>logged hours vs target"]
    B --> C["Amazon referral<br/>when unseen mediums<br/>reach OA level"]
    B --> D["February<br/><b>startup applications</b><br/>earlier if the outlook changes"]
    C --> E["OA invite<br/>triggers the<br/>classics window"]
    D --> F["March<br/><b>break-even or shutdown</b>"]
    E --> F
    style B fill:#1f6feb,color:#fff
    style D fill:#238636,color:#fff
    style F fill:#4d1414,color:#fff
    style E fill:#bb8009,color:#fff
```

- **March decides the company.** It either breaks even or shuts, and a shutdown is not certain.
- **Startup applications start in February.** If the outlook changes first, with a sale falling through, salaries slipping or people leaving, they start that week instead.
- **One assumption is untested:** that another startup job is easy to find if the company shuts. 2026 has no interviews to support it, and a search takes weeks.
- **Amazon has no fixed date.** The shortlist is uncertain, so the referral goes in once unseen mediums are at online-assessment level, not on a calendar date.
- **A failed Amazon loop costs about six months of cooldown**, which would overlap the shutdown. Amazon is never the only line.

---

## Who the prep is for

| Target | What the loop asks | How likely |
|---|---|---|
| **Amazon SDE-2**, by referral | OA of one DSA problem plus an AI-assisted repo task; two DSA rounds of one medium and one hard with full code; LLD as class design; HLD; Leadership Principles in every round ([[11-Amazon-SDE2-Loop]]) | Shortlist uncertain |
| **AI-engineer roles at startups**, the March fallback | Shorter live coding with AI off, graded on decomposition, complexity and debugging; AI system design such as RAG pipelines; a deep dive on a system I shipped ([AITechConnect](https://aitechconnect.in/tips/ai-engineer-interview-2026-live-coding-ai-assisted-rounds), [Taggd](https://taggd.in/blogs/how-to-hire-ai-engineers/), [Kalvium](https://kalvium.com/blog/ai-engineer-india-skill-stack/)) | Where my profile carries weight |
| **Indian product startups** with a machine-coding round | 60 to 90 minutes of code that must run, then review (`Low Level Design/00-Round-Formats.md`) | Some of the fallback list |

The startup sources are vendor and career-guide blogs, not first-hand reports, so the shape is indicative.

---

## The tracks

```mermaid
flowchart TD
    subgraph ON["Always on — mornings"]
        O1["1 to 2 hours of unseen zerotrac problems<br/>no AI, written by hand<br/>the Sunday contest in the same slot"]
    end
    subgraph WORK["Work hours"]
        M1["compliance-agent: the deploy first,<br/>then evals and tracing, then RAG"]
    end
    subgraph EVE["Evenings"]
        L1["1 hour of LLD<br/>machine coding by hand"]
    end
    subgraph ONCE["Write once"]
        W1["8 to 10 STAR stories<br/>from Xarvis and compliance-agent"]
    end
    subgraph TRIG["On trigger — Amazon OA invite"]
        T1["Classics revision<br/>cold, trigger, twist"]
        T2["Remaining Amazon LLD prompts"]
    end
    ON --> AMZ["Amazon OA<br/>+ startup coding rounds"]
    WORK --> ST["Startups<br/>+ the shipped-system deep dive"]
    EVE --> MC["Machine-coding rounds<br/>+ Amazon LLD"]
    ONCE --> BOTH["Amazon LPs<br/>+ startup deep dives"]
    TRIG --> LOOP["Amazon loop only"]
    style ON fill:#1f3a5f,color:#fff
    style WORK fill:#0d3d20,color:#fff
    style EVE fill:#3d1f5f,color:#fff
    style ONCE fill:#4d3a0a,color:#fff
    style TRIG fill:#4d1414,color:#fff
```

| Track | What | Serves | When |
|---|---|---|---|
| **Always on** | Unseen zerotrac problems in my band, no AI, written by hand, plus the Sunday contest | Amazon OA and startup coding rounds | Every morning, 1 to 2 hours |
| **Work hours** | The compliance-agent deploy to the dev environment with Docker, Kubernetes and Helm, then evals and tracing, then RAG. Each AI piece counts as done when compliance-agent shows a result: a pass rate on its 17 hand-judged scenarios, a trace for every run. The course lectures continue alongside | Startups, the shipped-system deep dive, and closing the operations gap | The deploy from 2026-11-16; DevOps tapers once it is integrated |
| **Evenings** | LLD machine coding: build the problem by hand, no AI, until it runs | Startup machine-coding rounds and Amazon LLD | 1 hour every evening |
| **Write once** | 8 to 10 STAR stories with numbers | Amazon Leadership Principles and startup project deep dives | About one a week, never re-revised for nothing |
| **On trigger** | Classics revision and the remaining Amazon LLD prompts: Amazon Locker, file search and filter, pub-sub, meeting scheduler | Amazon loop only | Only after an OA invite arrives |

> [!important] Why the classics wait for a trigger
> Classics cannot train unseen solving, because I already know where each one starts. Re-revising them without an interview call is the exact pattern from the past: revise everything, get no call, revise again. They are revised once, inside the window between an OA invite and the loop.

---

## The weekday

| | Hours outside work | Split |
|---|---|---|
| **Target day** | 2 to 3 | DSA 1 to 2 in the morning, LLD 1 in the evening; AI and DevOps run inside work hours |
| **Minimum day** | 1 | One unseen zerotrac problem, nothing else |

- **DSA, 1 to 2 hours every morning:** one or two unseen zerotrac problems in band. The Sunday contest sits in the same slot, because the rating is computed only from contests, and 2026 had 7 of them.
- **AI and DevOps, inside work hours:** the compliance-agent deploy first, then evals and tracing, then RAG. Doing the deploy myself is the learning, rather than handing it to a senior engineer.
- **LLD, 1 hour every evening:** machine coding — build the problem by hand, no AI, until it runs. This prepares the startup machine-coding round and rebuilds hand-written code at the same time.
- **Minimum day:** the streak is what failed last time — two months of daily DSA in May and June, then 4.5 months of nothing. On a bad day, one problem counts as a done day.

Outside work this is 2 to 3 hours a day, inside the roughly 18 hours a week I measured once staffed. The first week, 11 to 15 November, logged 20.5 hours, half of it DevOps and none of it LLD, which is why DevOps moved into work hours and LLD got the evening.

---

## DSA method

- **Band:** set by current contest rating, 50 to 100 below it (`LC/TT.md`). After 4.5 months idle, 1500 to 1550 may fit the first week or two better than 1550 to 1600.
- **No AI anywhere while solving,** and code typed in a plain editor. Both Amazon and the startups grade hand-written code.
- **Readiness to use the referral:** an unseen Amazon-tagged medium solved in 20 minutes or less, with clean code, explained out loud.

## The Amazon window, once an OA invite arrives

- **Classics revision:** cold attempt from the statement only, name the trigger line out loud, then change one constraint and solve the variant without looking. Amazon's 2025 and 2026 questions are mostly classics with a twist: LC 316 asking for the largest result, Subarray Sum Equals K with follow-ups, a stack with O(1) middle operations.
- **The list is prepared now, solved later:** about 60 Amazon classics, written down so the window starts on day one.
- **Remaining LLD prompts** as whiteboard class design, since Amazon's round is design discussion rather than running code.

---

## LLD course under consideration

[Strike — Low-Level Design and Machine Coding, Java](https://strikes.in/course/lld-java): Strike lists about two months and 45+ hours for ₹3,999, with two years of access. The full syllabus has 48 lessons in 8 modules, recorded Monday to Friday with one live doubt class on Friday evenings, and the batch started on 9 November. No independent reviews were found; the testimonials are on Strike's own site.

| Module | Problems |
|---|---|
| 1 to 3: foundations and the design patterns | Parking Lot, a contest platform, **Amazon Locker**, a support-ticket system, an elevator, document search |
| 4: concurrency | An LRU cache with expiry, a rate limiter, a task scheduler with worker pools, an auction, a load balancer |
| 5: database schema and transactions | Isolation levels, locking, idempotency, airline booking, a multi-tenant SaaS schema, BookMyShow without double bookings |
| 6: fintech and reservations | A wallet on a double-entry ledger, subscription billing, refunds, **meeting-room booking**, carpooling, hotel booking |
| 7: infrastructure | A **pub-sub event bus**, a notification engine with retries, a key-value store, a URL shortener, a social-media schema, a web crawler |
| 8: capstone and mocks | A ChatGPT-style app with streaming, cancellation and token usage; a library, a Kanban board and a feature-flag system as mocks |

It covers three of the four Amazon LLD prompts still open, Amazon Locker, pub-sub and the meeting scheduler, and modules 5 to 7 are new ground rather than revision. About 33 of the 48 lessons are design problems. Attempting each by hand before watching takes about 1.3 hours, which comes to about 5 hours a week, the whole evening slot, so the theory lessons in modules 1 to 3 get skimmed. Two months ends around mid-January, before the February applications.

> [!important] The rule if I take it
> Attempt every machine-coding problem by hand, with no AI, before watching the instructor's solution. Watching first is how 300 classics turned into answers I can recall but cannot derive.

---

## Review on 2026-11-25

Two weeks of the study log against the new split: DSA every morning, LLD every evening, the Sunday contest. The early warning for the old pattern is the first missed Sunday contest. A track that keeps landing near zero gets cut or moved rather than carried as guilt.

## Open items

- [ ] Check the current contest rating and set the starting band
- [ ] Ask the friend: which OA format their org sends now, the usual gap from OA to loop, whether the Bar Raiser is a separate round, and which teams have L5 headcount near AI or LLM work
- [ ] Write down the ~60 Amazon classics list, without solving it
- [ ] Decide on the Strike course
- [ ] Settle the weekend: hours, STAR stories, RAG design practice out loud
- [ ] Decide whether to test the startup-market assumption before February: one referral chat or one recruiter call
- [ ] Review on 2026-11-25
