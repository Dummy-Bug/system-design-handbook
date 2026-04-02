# Error Budget

> [!question] Your SLO allows 0.1% failure. What do you do with that 0.1%?
> That's your error budget — the amount of failure your system is allowed to have before breaching the SLO.

---

## What it is

Your SLO says — *"system must be available 99.9% of the time over 30 days"*.

That 0.1% you're allowed to fail is your error budget.

```
30 days = 43,200 minutes
0.1% of 43,200 = 43.2 minutes of allowed downtime per month
```

That **43.2 minutes** is your error budget. Spend it wisely.

---

## Why it exists

Two teams are always in tension:

**Engineering** — wants to move fast. Deploy new features, ship code, make changes. But every deployment risks downtime. Every change risks an incident. Each incident burns error budget.

**Reliability** — wants stability. Fewer changes, less risk, more uptime.

Without an error budget, this is a constant argument — *"can we deploy or not?"* It's subjective, political, and frustrating.

The error budget makes it **objective**. Both teams look at the same number. The number decides.

> [!tip] The error budget is the negotiation tool between speed and stability
> It replaces opinion with math.

---

## How it changes decisions

| Error budget remaining | What it means | Decision |
|---|---|---|
| 80%+ remaining | System is healthy, plenty of room | Deploy freely, move fast |
| 50% remaining | Moderate caution | Deploy but monitor closely |
| 20% remaining | Getting tight | Only critical deployments |
| 0% remaining | SLO breached or about to be | Freeze all deployments, focus only on stability |

---

## A real conversation with error budgets

**Without error budget:**
*"Can we deploy the new feature today?"*
*"I don't know, seems risky..."*
*"But we really need to ship it"*
*"Fine whatever"* — nobody is happy, decision is based on nothing

**With error budget:**
*"Can we deploy the new feature today?"*
*"We have 73% of our error budget remaining with 2 weeks left in the month — yes, deploy."*

Or:

*"Can we deploy the new feature today?"*
*"We've burned 85% of our budget in the first week — no deployments until next month. We need to focus on stability."*

Same question. One is a guess. One is a decision backed by data.

---

## Error budget resets

Error budgets reset at the start of every measurement window — typically every 30 days.

A good month with no incidents = full budget available next month → team can move fast.
A bad month with multiple incidents = budget burned early → team slows down next month.

> [!info] This creates a natural feedback loop
> Teams that cause incidents lose their ability to deploy quickly the following month. It incentivises reliability without anyone having to enforce it manually.

---

## The formula

```
Error Budget = 100% - SLO target

For availability SLO of 99.9%:
Error Budget = 0.1% of time = 43.2 minutes per month

For availability SLO of 99.99%:
Error Budget = 0.01% of time = 4.32 minutes per month
```

> [!warning] The stricter your SLO, the smaller your error budget
> 99.99% availability sounds great for customers — but it leaves your engineering team only 4 minutes of downtime per month to work with. Every deployment becomes extremely risky. Choose your SLO carefully.
