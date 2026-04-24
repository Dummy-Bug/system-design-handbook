Almost every system you build needs to assign IDs to things — users, orders, messages, transactions. The simplest approach is a database auto-increment (1, 2, 3...). That works fine on a single database, but the moment you have multiple database servers (which every large system does), two servers can both assign ID `1001` to different records at the same time. Collision.

A Unique ID Generator is a dedicated service that generates IDs which are:

- **Globally unique** — no two IDs are ever the same, across any server, anywhere in the world
- **Sortable by time** — newer records get higher IDs, so you can sort by ID and get chronological order for free
- **Fast** — systems like Twitter, Instagram, and Uber need millions of IDs per second

The interesting design challenge is: how do you generate IDs that are unique *and* time-ordered *and* fast at massive scale — without a single bottleneck that every write in your entire system has to wait on?

---

> [!info] Real-world context
> Twitter's Snowflake, Instagram's ID generator, and Discord's ID scheme are all variations of the same core idea. Understanding this system means you understand how IDs work inside every major platform you've ever used.
