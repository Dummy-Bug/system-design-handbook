 **HNSW — Hierarchical Navigable Small World** is more accurate than clustering, it's what most production vector databases actually run (ChromaDB, for one, uses it under the hood), and it is comfortably the most intricate idea in the whole retrieval pipeline. We'll build it slowly, from an everyday intuition all the way to the layer-by-layer search — because rushing it is how it stays confusing.

Like clustering, HNSW does its structural work **once, at initialisation** — the moment you first add embeddings to the vector store. The query-time search then rides on top of that pre-built structure. Keep that split in mind throughout: there's a *build* phase and a *search* phase.

---

## The intuition: six degrees of separation

HNSW is built on a famous social-network idea called **six degrees of separation**. The claim is startling: pick any random person on earth, and they are connected to any *other* person — no matter how famous or distant — through only about **five or six intermediate people**.

![[AI-Engineering/RAG/04-Vector-Stores/Images/07-Six-Degrees-Chain.png]]

Walk a concrete chain. Start with me — call me person **A**. I'm connected to a **B**, maybe a relative or family friend. That relative is connected to a **C**, perhaps their school friend. That friend is connected to a **D**, say a college professor. That professor knows an **E**, a professor in the US they once did research with. And that US professor once taught an **F** — who happens to be Donald Trump. Six hops, and a random person reaches a world-famous one. The principle says this holds for essentially *any* two people: five-to-six mutual connections bridge them.

### Why the hops stay so small — the exponential math

This sounds too good to be true until you count the connections. Suppose I personally know **100** people — that's my immediate circle. Now each of those 100 people knows *their own* ~200 people. And each of *those* knows another ~200-300.

![[AI-Engineering/RAG/04-Vector-Stores/Images/08-Neighbourhood-Math-And-Graph.png]]

The reach multiplies at every hop: 100, then 100×200 = 20,000, then that ×200 = 4,000,000, and so on. The growth is exponential, so after just five or six hops the number you can reach has swollen to cover the **entire population of the earth**. That's the engine behind the six-degrees claim — not that everyone is directly close, but that a handful of multiplicative hops explodes your reach to everyone.

And here's the shape that matters for us: this whole web of people-and-connections is naturally a **graph**. Represent each **person as a node** and each **connection as an edge**, and you've drawn the social network as a graph — A linked to B by an edge, B to C, and so on. That graph structure is exactly what HNSW borrows.

---

## Carrying the idea into embedding space

Now swap people for embeddings. Your document embeddings live in a **high-dimensional space** (a hyperspace) whose dimensionality equals the embedding model's output size — 1536 for `text-embedding-3-small`, and so on, exactly as the earlier notes established. Scatter your document vectors into that space.

![[AI-Engineering/RAG/04-Vector-Stores/Images/09-Local-Neighbourhood-Hyperspace.png]]

Pick any one embedding at random. The embeddings sitting **closest to it** — smallest distance away — are its **local neighbourhood**. And because in embedding space small distance means similar meaning, that local neighbourhood is precisely the set of embeddings whose **semantic meaning** resembles the one you picked. They're near it *because* they mean something similar.

This is the bridge: just like a person sits inside a local neighbourhood of ~100 direct connections, each embedding sits inside a local neighbourhood of its most semantically-similar embeddings. So we can wire embeddings into a graph — each embedding a **node**, each "these two are close in meaning" link an **edge** — and then navigate that graph the same way six-degrees navigates a social network. That is the heart of HNSW.

---

## Decoding the name — Hierarchical, Navigable, Small World

The algorithm's name is a compressed description of how it works. Unpack it from the back.

**Small World.** A "small world" is the six-degrees property itself: any node reachable from any other in a few hops. In indexing terms, it means you restrict a search to a small, well-connected **subset** of the embeddings rather than scanning everything — the same "work with only a subset of documents" goal that all indexing shares. You compress the search into a small world so the number of comparisons collapses.

**Navigable.** To *navigate* is to follow a route. HNSW represents the data as a graph and then *walks* it: from a **starting node**, it hops edge by edge toward the query's neighbourhood, following the **shortest path** — the fewest hops — to reach the destination node. A search isn't a scan; it's a guided walk through the graph, node to neighbouring node, each step landing closer to the answer.

**Hierarchical.** This is the twist HNSW adds on top of a plain navigable graph: it doesn't build *one* graph, it builds **several stacked layers** of graph, one on top of another — a hierarchy. The top layers are sparse (few nodes, long-range links) and the bottom layer is dense (every node, every connection). We'll see exactly why that hierarchy makes the search fast.

---

## Building the index — a worked example

Concreteness cuts through the fog here, so take a tiny store. We initialise a vector store with HNSW and feed in **5 chunks**, each about a different topic:

- **C1 — Python** (a programming language)
- **C2 — JavaScript** (also a programming language)
- **C3 — photosynthesis**
- **C4 — oxygen** (a byproduct of photosynthesis)
- **C5 — a fifth, unrelated topic** (sitting far from the rest)

Each chunk goes through an embedding model to become a vector. Normally, with `text-embedding-3-small`, each is 1536 numbers, so the batch is a matrix of shape **5 × 1536** — five vectors, each 1536-dimensional. But for *teaching*, we use a pretend embedding model that returns a **single scalar** per chunk instead — shape **5 × 1** — so each embedding is just one number on a line, and "distance" is simply the gap between two numbers. That makes the whole thing drawable.

![[AI-Engineering/RAG/04-Vector-Stores/Images/10-Layer0-Base-And-Promotion.png]]

Place the five on a number line and their values fall out sensibly: **Python 1.0**, **JavaScript 1.5** (the two programming chunks sit close together), **photosynthesis 5.0**, **oxygen 5.3** (the two biology chunks cluster around 5), and the **fifth chunk at 9.0**, off on its own. Similar meanings, similar numbers — exactly the semantic-clustering property, now in 1-D.

This bottom level is **Layer 0**, the **base layer**, and its defining feature is that it holds **all** the embeddings with **all** their connections visible. Nothing is hidden here; the full graph lives at the bottom.

### Promotion — how the higher layers get built

The hierarchy is built by **promotion**, and the rule is delightfully simple: there's no clever formula. You **randomly** pick some embeddings from Layer 0 and *promote* them up to Layer 1, then rebuild a fresh graph among just those promoted nodes. Repeat to build Layer 2 from Layer 1, and so on. Each layer up keeps only a random subset of the layer below, so the stack narrows into a pyramid — many nodes at the bottom, very few at the top.

![[AI-Engineering/RAG/04-Vector-Stores/Images/11-Hierarchical-Layers.png]]

In our example, Layer 0 has all five. Suppose the promotion randomly lifts JavaScript, photosynthesis, and the fifth chunk into **Layer 1**, and then lifts photosynthesis and the fifth chunk again into **Layer 2**. The result is the stacked structure above: a sparse top layer with long-range links, a middle layer, and the dense full-graph base. The sparse top exists to let a search take giant leaps across the space; the dense bottom exists to pin down the exact nearest neighbour. That division of labour is the entire point of making it hierarchical.

---

## Searching the index — the greedy top-down walk

Now the query. A user asks something like *"how do we reduce CO₂ in the atmosphere?"* We embed it with the same scalar model and get a **query value of 5.2**.

![[AI-Engineering/RAG/04-Vector-Stores/Images/12-Query-Descending-Layers.png]]

The search **enters at the top layer** and works **downward**, layer by layer — Layer 2, then Layer 1, then Layer 0. Within each layer it does a **greedy walk**:

```
at the current node:
  1. compute the distance from the query to each neighbour
  2. move to the neighbour closest to the query
  3. repeat until no neighbour is closer than where you are
  → that node is this layer's best match
then: descend one layer, using this layer's best node as the ENTRY point below
```

That "greedy" step is worth watching in isolation. At the top, the walk stands on a node, looks only at that node's neighbours, compares each one's distance to the query, and jumps to whichever is closest — never scanning the whole layer, only the local neighbours.

![[AI-Engineering/RAG/04-Vector-Stores/Images/14-HNSW-Greedy-Move-Step.png]]

In the animation above, the walker is at node A in the top layer. A's only neighbour there is B. It compares: B is at distance 236.2 from the query, A is at 413.5 — B is closer, so it **greedily moves to B**. No unvisited neighbours remain, so this layer is done and B becomes the entry point for the layer below.

Two efficiencies make this cheap. First, the query only ever compares against a handful of *neighbours*, never the whole layer. Second, distances already computed in an upper layer are **cached** — when the walk meets the same node again lower down, it doesn't recompute; it reuses the number. So descending costs less than it looks.

The walk keeps dropping: the best node of Layer 2 is the entry to Layer 1, where it greedily hops again to find Layer 1's best, which becomes the entry to Layer 0. And Layer 0 — the dense full graph — is where the *precise* nearest neighbour is finally nailed down, because that's the only layer holding every node and every connection.

![[AI-Engineering/RAG/04-Vector-Stores/Images/15-HNSW-Nearest-Found.png]]

The payoff, shown at the end of the walk: the search declares its nearest neighbour having **visited only a handful of nodes across the three layers — far fewer than checking all of them**. For our number-line store, the query at 5.2 lands right next to **oxygen at 5.3** (distance ~0.1), so oxygen is retrieved as the top match — the CO₂/atmosphere question correctly pulled the oxygen-and-photosynthesis chunk, after only a few distance computations instead of scanning the entire store.

---

## The catch: approximate, not exact

HNSW is an *Approximate* Nearest Neighbour method, and the graph makes the approximation vivid.

![[AI-Engineering/RAG/04-Vector-Stores/Images/13-Greedy-Search-Suboptimal.png]]

Because the walk is **greedy** and only ever looks at the **local neighbourhood** of the node it's standing on, it can settle on a **sub-optimal solution**. Picture the true best match as a node that your path never reaches — its only edges connect it to nodes you didn't walk through. The greedy walk, hopping from local best to local best, can glide right past it and terminate at a node that's *very good* but not *the* best. If, by luck, some node on your path happened to have an edge to that true best, you'd find it — *but that's only by chance*, a consequence of how the random promotion wired the graph, not a guarantee.

This is the deal every ANN method strikes, and HNSW is explicit about it: it typically claims **95–99% accuracy**, not 100%. You give up the certainty of the exact nearest neighbour in exchange for not having to compare against every vector.

---

## Why it's worth it: O(log N) instead of O(N)

The reason to accept that 1–5% accuracy risk is the payoff in speed, and it's enormous.

![[AI-Engineering/RAG/04-Vector-Stores/Images/16-Brute-Force-Vs-HNSW.png]]

Brute-force exact search compares the query against **every** vector, so its cost is **O(N)** — linear in the number of vectors. At a million vectors that's a million comparisons per query; at ten crore, a hundred million. HNSW's hierarchical graph lets a search skip across the sparse top layers and only densely inspect a tiny region at the bottom, giving it a time complexity of **O(log N)** — logarithmic. The difference between linear and logarithmic at scale is the difference between unusable and instant: doubling the corpus adds one more comparison-ish worth of work to an HNSW query, versus doubling the work of a brute-force one.

The mental image from the summary says it best: brute force is *reading every book in the library* to find one; HNSW is *walking straight to the right shelf*. You trade a sliver of accuracy for a walk instead of a full read — and that trade is why real vector databases (ChromaDB among them) run HNSW by default.

---

## What it guarantees — and what it doesn't

**What HNSW gives you:**

- **Logarithmic search — O(log N)** instead of brute force's O(N), by taking long jumps across sparse upper layers and only inspecting a small dense region at the bottom.
- **A guided walk, not a scan** — each step only compares against a node's local neighbours, and previously-computed distances are cached across layers.
- **High accuracy in practice** — typically 95–99%, close enough for retrieval where you want a few good chunks, fast.
- **A build-once structure** — the layered graph is constructed at initialisation and reused by every query.

**What it does not give you:**

- **Exactness** — it's *approximate*; the greedy, local walk can miss the true nearest neighbour if that vector isn't reachable along the path taken. Finding it can come down to how the random promotion happened to wire the edges.
- **A free build** — constructing the hierarchy (promoting nodes, wiring neighbourhoods across layers) is real work done up front; it's just not repeated per query.
- **Zero tuning** — how many neighbours each node keeps, how many layers, how greedily to search: these are knobs trading accuracy against speed and memory.

> [!tip] Interview framing: "HNSW — Hierarchical Navigable Small World — is the graph-based ANN index most production vector databases use. It builds a multi-layer graph of the embeddings at insert time: 
> The bottom layer holds every node and connection, and each higher layer is a random sparse subset. 
> 
> A query enters at the sparse top and greedily walks toward its nearest neighbour, hopping to the closest local neighbour at each step and descending layer by layer, so it takes big jumps up top and pins the exact match only in the dense base. That gives **O(log N)** search versus brute force's O(N), at the cost of being *approximate* — roughly 95–99% accurate, 
> 
> Since the greedy local walk can miss a true nearest neighbour that isn't on its path. It's the six-degrees-of-separation idea applied to vectors: a few hops through a well-connected graph reach any neighbourhood."


