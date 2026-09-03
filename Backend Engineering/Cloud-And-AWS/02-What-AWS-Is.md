**Cloud providers were named in passing in [[01-Why-Cloud]]. This note is about the one that leads the market**, what it actually contains, and what it costs to open an account and start using it.

# A division of Amazon

Amazon is best known as an e-commerce company, but it runs several businesses — streaming through Prime Video, among others, and cloud services through AWS.

**AWS stands for Amazon Web Services.** It is the division of Amazon that handles everything to do with its cloud offerings.

**AWS is not one thing.** It is a large collection of separate services, and a phrase like `deployed on AWS` could mean any of them. A few examples of what is on offer:

- Rent a plain machine and install whatever operating system you want on it
- Set up a database and host it there
- Run load balancers
- Run messaging queues
- Send email

That list is a small sample. The full catalogue is the subject of [[04-Services-And-Access]].

# The alternatives

AWS is not the only option.

| Provider | Run by |
| --- | --- |
| AWS — Amazon Web Services | Amazon |
| GCP — Google Cloud Platform | Google |
| Azure | Microsoft |

Any of the three will do the job. **AWS is the most widely used and is the market leader**, and a great many large, heavily scaled applications run on it — Hotstar among them.

The useful thing is to know one of them well. The concepts carry across: the vocabulary in [[03-Regions-And-Zones]] is not AWS-specific, and neither is most of what follows.

# Opening an account

Two things are needed: an internet connection and a credit card.

**The credit card is for identity, not for charges.** Amazon does charge for its services in general, but it also knows the platform matters for learning, so a new account can be used within limits without being billed. The card is verified with a nominal charge — one or two rupees — and that is the extent of it.

# What is free, and for how long

> [!important] **This changed recently, and older material describes the previous scheme.** What follows is the current arrangement.

**A new account gets credits rather than a twelve-month window.** You receive 100 US dollars in credits immediately and can earn up to 100 more, so up to 200 dollars over six months. The account closes on its own six months after you open it, or when the credits run out, whichever happens first.

**Alongside the credits there are two plans.** On the Free Plan you are not charged unless you choose to upgrade, and you can use a selected subset of services. On the Paid Plan you pay as you go and everything is available.

**Separately from both, more than thirty services are always free within monthly usage limits**, and those limits apply on the Free Plan and the Paid Plan alike.

> [!info]- **The scheme this replaced**
> Older material describes a twelve-month free tier: a new account could use certain services free for twelve months, with published per-service allowances — 750 hours a month of EC2, 5 GB of S3 storage, 750 hours of RDS, and so on. Stay inside the allowances and nothing was billed. That is no longer how a new account works, though the always-free monthly limits above are its descendant.

The practical advice has not changed with the scheme: watch what you switch on. Used carefully for learning, an account can run a long time without a bill; used carelessly, it will not.
