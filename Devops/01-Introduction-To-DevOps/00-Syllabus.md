#devops #syllabus #introduction

The opening module of the course. It contains **no tools and no commands** — it is entirely about why the DevOps role exists, what the philosophy actually claims, and how you measure whether a company is living up to it.

That ordering is deliberate. Linux, Git, Docker, Kubernetes, Jenkins and Prometheus all come later; the point of this module is that you should be able to say *why* each of those tools is being reached for before you touch any of them.

> [!info] **Where this sits.** Everything here is vocabulary and framing an engineer is expected to already hold. It is also the part most likely to be asked in an interview as a straight question — *"what is DevOps"*, *"what are DORA metrics"* — where a vague answer reads as inexperience.

---

## A · Why the role exists

**1. How applications got complicated**
The path from a static website maintained by one person to a multi-service, multi-server, data-intensive application. Client/server request-response, the frontend/backend split, and monolith → microservices. → `01`

**2. Developers, operations, and the silo model**
The two roles that emerged, what each actually owns, and why *"it works on my machine"* is a structural problem rather than a careless one. The incentive contradiction — one side paid to change the system, the other paid to keep it from changing — and the **silo working model** it produces. → `02`

## B · What DevOps claims

**3. What DevOps actually is**
DevOps as a *philosophy* and as a *role*. The four fundamental ideas: shared ownership, automation, small and regular deployments, fast feedback. The two goals everything reduces to — **fast delivery** and **reliable delivery**. → `03`

**4. The CALMS framework**
Culture, Automation, Lean, Measurement, Sharing — the five-part checklist for judging whether a company genuinely practises DevOps or just employs someone with the title. → `04`

## C · How it gets measured

**5. DORA metrics**
Four questions, four numbers: deployment frequency, lead time for change, change failure rate, mean time to recovery. How each is calculated, and why the four split cleanly into two about speed and two about reliability. → `05`

**6. Recovery: hot fix, revert, and disable**
What "recovery" means in practice once something has failed in production, and how to choose between patching it, pulling it out, and switching it off. → `06`

---

> [!tip] **Currency check (2026-08-05).** The concepts here are stable — CALMS dates from 2010, DORA's four key metrics have been steady since the 2018 *Accelerate* research. Two things worth re-verifying if you cite them: DORA's published performance bands (what counts as "elite" deployment frequency) shift between annual State of DevOps reports, and a fifth metric — **reliability**, later reframed around operational performance — was added after the original four. The lecture covers the original four only.
