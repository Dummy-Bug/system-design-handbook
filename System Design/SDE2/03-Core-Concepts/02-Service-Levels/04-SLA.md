# SLA — Service Level Agreement

> [!question] Your team has an internal target. But what do you promise your customers?
> That promise is your SLA.

---

## What it is

An SLA is an **external contract between you and your customers**.

It says — here's what we guarantee, and here's what happens if we break that guarantee.

- **SLO** — internal, your team's target, no consequences if breached other than fixing the problem
- **SLA** — external, customer-facing, breach it and you owe money, credits, or face legal action

---

## A Real Example — AWS S3 SLA

*"We guarantee 99.9% availability. If we drop below that, you get a service credit of 10% of your monthly bill. If we drop below 99%, you get 30% back."*

That's an SLA. A written promise with real financial consequences.

---

## SLOs are always stricter than SLAs

This is intentional. The gap between them is your **safety buffer**.

| | Target | Who sees it | Consequence if breached |
|---|---|---|---|
| **SLO** | 99.9% availability | Internal team only | Team gets alerted, engineers fix it |
| **SLA** | 99.5% availability | Customers, contracts | Refunds, credits, legal action |

If your SLA promises 99.5% availability — your internal SLO is 99.9%.

Your team gets alerted at 99.9% and fixes the problem **before it ever reaches 99.5%** — before you owe anyone a refund.

> [!tip] The safety buffer in plain English
> SLO is the alarm. SLA is the cliff edge. You fix the problem when the alarm goes off — not when you fall off the cliff.

---

## SLAs are not just for big companies

Any time you make a reliability promise to a customer, you have an SLA — even informally:

| Scenario | Implicit SLA |
|---|---|
| Startup telling customers *"99.9% uptime"* on their pricing page | That's an SLA |
| AWS, GCP, Azure publishing availability guarantees | That's an SLA |
| Your company's API docs saying *"responses under 500ms"* | That's an SLA |
| An enterprise contract with explicit uptime and penalty clauses | That's an SLA |

---

## Real world SLAs

| Company | Service | SLA |
|---|---|---|
| AWS S3 | Object storage | 99.9% availability, credits if breached |
| Google Cloud SQL | Managed database | 99.95% availability |
| Twilio | SMS API | 99.95% uptime |
| Stripe | Payments API | 99.99% uptime |
