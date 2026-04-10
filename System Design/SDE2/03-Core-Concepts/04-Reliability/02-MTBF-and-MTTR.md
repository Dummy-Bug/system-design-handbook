> [!question] Your system is reliable right now. But how does it behave across weeks and months?
> MTBF and MTTR are the two numbers that answer that question.

---

## MTBF — Mean Time Between Failures

**How long does your system run before something breaks?**

If your server crashes once every 30 days on average — your MTBF is 30 days.

```
MTBF = Total operational time / Number of failures

Example:
System ran for 300 hours, failed 3 times
MTBF = 300 / 3 = 100 hours between failures
```

Higher MTBF = more reliable. The system breaks less often.

---

## MTTR — Mean Time To Recovery

**When something breaks, how long until it's working again?**

This includes: detecting the failure + alerting the team + diagnosing + fixing + deploying the fix + verifying it's healthy.

```
MTTR = Total downtime / Number of failures

Example:
3 failures, each took 30 minutes to fix
MTTR = 90 minutes / 3 = 30 minutes per failure
```

Lower MTTR = more resilient. You recover faster.

---

## Why both matter together

MTBF tells you how often you fall down. MTTR tells you how fast you get back up.

A system with low MTBF but very low MTTR can still be highly available — it breaks often but recovers in seconds. Netflix's chaos engineering is built on exactly this: break things constantly in production, force MTTR to near-zero, don't rely on MTBF being high.

A system with high MTBF but terrible MTTR is dangerous — it rarely breaks, but when it does, it's down for hours.

---

## The availability connection

These two numbers directly calculate your availability:

```
Availability = MTBF / (MTBF + MTTR)

Example:
MTBF = 99 hours (fails once every 99 hours)
MTTR = 1 hour (takes 1 hour to recover)

Availability = 99 / (99 + 1) = 99/100 = 99%
```

Want 99.9%? Either make MTBF much larger (fail less often) or make MTTR much smaller (recover faster). Two completely different engineering strategies.

---

## How you improve each

**Improving MTBF** — prevent failures from happening:
- Better hardware
- Code reviews, testing, canary deployments
- Chaos engineering — find weaknesses before they hit production

**Improving MTTR** — recover faster when they do happen:
- Automated alerting — know instantly when something breaks
- Runbooks — engineers don't improvise during an incident, they follow a playbook
- Automated rollback — bad deploy? One command reverts it
- Good observability — logs, metrics, traces so you find the root cause fast

---

## The key insight

Most engineers only think about MTBF — "how do I prevent failures?" But at scale, failures are inevitable. The teams that maintain high availability focus just as hard on MTTR — "when it breaks, how fast can we recover?"

> [!tip] Designing for low MTTR is often more cost-effective than designing for high MTBF
> Prevention gets exponentially expensive. Fast recovery is an engineering discipline you can build cheaply — better alerting, runbooks, automated rollback cost far less than eliminating every possible failure.
