## The Rule of Thumb

> Reach for a graph database when **relationships are the primary thing you're querying**, not the data itself. The moment you find yourself doing 3+ hop joins in SQL, that's your signal.

---

## 1. Social Networks — LinkedIn, Twitter, Instagram

The classic graph problem. Every user is a node. Every follow/friendship is an edge.

```
(Alice) ──[FRIENDS_WITH]──▶ (Bob) ──[FRIENDS_WITH]──▶ (David)
(Alice) ──[FRIENDS_WITH]──▶ (Charlie) ──[FRIENDS_WITH]──▶ (Eve)
```

LinkedIn's "2nd degree connections" is a 2-hop traversal. "People you may know" combines 2-hop and 3-hop traversals with ranking.

"What is the shortest professional path between you and Sundar Pichai?" — BFS on the graph, returns the chain of connections. Impossible to do in real time with SQL at LinkedIn's scale (900 million users, billions of connections).

---

## 2. Fraud Detection — PayPal, Uber, Banks

A fraudster creates a new account with a different name and email. Looks clean on the surface. But they can't easily change their phone number or device.

```
(Account: "John Smith") ──[USES_PHONE]──▶ (Phone: +1-555-1234)
(Account: "Alice Jones") ──[USES_PHONE]──▶ (Phone: +1-555-1234)
(Account: "Alice Jones") ──[USES_DEVICE]──▶ (Device: iPhone-XYZ-789)
(Account: "Bob Brown")   ──[USES_DEVICE]──▶ (Device: iPhone-XYZ-789)
(Account: "Bob Brown")   ──[BANNED_FOR]──▶  (Fraud: credit card scam)
```

3-hop traversal: "John Smith" → shared phone → "Alice Jones" → shared device → "Bob Brown" → BANNED.

The graph database finds this pattern in milliseconds — fast enough to block the transaction before it completes. SQL would require 3 joins across massive tables, too slow for real-time fraud blocking.

> [!important] The relationship pattern IS the fraud signal
> It's not that any single piece of data is suspicious. It's the web of shared identifiers connecting a new account to a known bad actor. Only a graph database can efficiently surface this pattern at scale.

---

## 3. Recommendations — Amazon, Netflix, Spotify

Netflix and Amazon use ML for recommendations. But the data those ML models work on is often structured as a graph.

```
(Alice) ──[BOUGHT]──▶ (iPhone 15)
(Bob)   ──[BOUGHT]──▶ (iPhone 15)
(Bob)   ──[BOUGHT]──▶ (AirPods Pro)
```

Simple graph traversal — no ML required for the basic version:

```
Alice bought iPhone 15
→ Who else bought iPhone 15? Bob
→ What else did Bob buy? AirPods Pro
→ Recommend AirPods Pro to Alice
```

Just following edges. ML adds sophistication (weights, rankings, collaborative filtering across millions of users) but the underlying data structure is still a graph. The graph traversal finds the candidates; ML ranks them.

---

## 4. Knowledge Graphs — Google Search

Google wants to answer "Where was Barack Obama born?" directly — not show 10 blue links and make you click.

They store the world's facts as a graph:

```
(Barack Obama) ──[BORN_IN]──▶ (Honolulu)
(Honolulu)     ──[LOCATED_IN]──▶ (Hawaii)
(Hawaii)       ──[IS_A]──▶ (US State)
(Barack Obama) ──[WAS]──▶ (US President)
(Barack Obama) ──[MARRIED_TO]──▶ (Michelle Obama)
```

Each fact is an edge. When you search "Obama birthplace", Google traverses this graph and directly returns "Honolulu, Hawaii". The entire knowledge panel on the right side of Google Search results is powered by this graph.

**Scale note:** Google doesn't use Neo4j for this. Billions of entities (every person, city, company, scientific concept on earth) requires a custom-built distributed graph infrastructure across thousands of machines. The concept is identical — nodes, edges, traversal — but the implementation is Google-scale engineering, not an off-the-shelf tool.

> [!tip] Interview framing
> "For fraud detection or social graphs at normal scale, I'd use Neo4j. For Google's Knowledge Graph scale — billions of entities — you'd need a custom distributed graph store. Neo4j supports clustering but Google's use case is beyond what any off-the-shelf tool handles today."

---

## When NOT to Use a Graph Database

Graph DBs are bad at bulk data scans — queries that touch many nodes based on their properties rather than their relationships:

```
-- Bad fit for graph DB:
"Give me all users older than 30"
"Give me all products under $50"
"Count total orders in the last month"
```

These queries don't traverse relationships — they scan and filter node data. SQL with indexes is far more efficient for this. Graph DBs optimize for traversal at the cost of bulk scan performance.

The signal: if your query starts at one specific node and follows edges — graph DB. If your query scans a collection of nodes by attribute — SQL.
