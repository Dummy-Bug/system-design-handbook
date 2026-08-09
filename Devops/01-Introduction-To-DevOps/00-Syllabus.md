#devops #syllabus #introduction

The opening module of the course. It contains **no tools and no commands** — it is entirely about why the DevOps role exists, what the philosophy actually claims, and how you measure whether a company is living up to it.

That ordering is deliberate. Linux, Git, Docker, Kubernetes, Jenkins and Prometheus all come later; the point of this module is that you should be able to say *why* each of those tools is being reached for before you touch any of them.

> [!info] **Where this sits.** Everything here is vocabulary and framing an engineer is expected to already hold. It is also the part most likely to be asked in an interview as a straight question — *"what is DevOps"*, *"what are DORA metrics"* — where a vague answer reads as inexperience.

---

## A · Why the role exists

**1. How applications got complicated**
The path from a static website maintained by one person to a multi-service, multi-server, data-intensive application. Client/server request-response, the frontend/backend split, and monolith → microservices. → `01`

**2. Developers, operations, and the silo model**
The two roles that emerged, what each actually owns, and why *"it works on my machine"* is a structural problem rather than a careless one. The incentive contradiction — one side paid to change the system, the other paid to keep it from changing — and the **silo working model** it produces. Then the trap: **solving silos by adding a DevOps team**, and the enabling-versus-gatekeeping test that tells the two apart. → `02`

## B · What DevOps claims

**3. What DevOps actually is**
DevOps as a *philosophy* and as a *role*. The four fundamental ideas: shared ownership, automation, small and regular deployments, fast feedback. Plus **infrastructure as code** — automating the machines, not just the pipeline. The two goals everything reduces to — **fast delivery** and **reliable delivery**. → `03`

**4. The CALMS framework**
Culture, Automation, Lean, Measurement, Sharing — the five-part checklist for judging whether a company genuinely practises DevOps or just employs someone with the title. → `04`

## C · How it gets measured

**5. DORA metrics**
Four questions, four numbers: deployment frequency, lead time for change, change failure rate, mean time to recovery. How each is calculated, and why the four split cleanly into two about speed and two about reliability. The note then covers **DORA's current five-metric model**, what it replaced and why, and how the metrics get misused. → `05`

**6. Recovery: hot fix, revert, and disable**
What "recovery" means in practice once something has failed in production, and how to choose between patching it, pulling it out, and switching it off. Then the larger idea feature flags unlock — **deploying is not releasing**, and why that is what makes frequent deployment safe. → `06`

## D · The neighbouring disciplines

**7. DevOps, SRE and platform engineering**
Three job titles with overlapping descriptions and three different starting problems: organisational silos, reliability as an engineering discipline, and developer cognitive load. How they relate rather than compete. → `07`

---

> [!tip] **Currency check (updated 2026-08-09).** CALMS dates from 2010 and is stable. DORA is not, and it is the one thing on this list to re-verify before citing:
>
> - **The four key metrics have been steady since the 2018 *Accelerate* research**, and remain what most people mean by "DORA metrics". The lecture teaches these.
> - **The current published model has five**, split Throughput / Instability. MTTR was replaced by **Failed Deployment Recovery Time** (because "MTTR" ambiguously means Repair, Recover, Restore *or* Resolve), and **Deployment Rework Rate** was added. Note `05` covers both models and says plainly which came from the class.
> - **The performance bands** — what counts as "elite" deployment frequency — shift between annual State of DevOps reports. Never quote a threshold without naming the year's report it came from.
