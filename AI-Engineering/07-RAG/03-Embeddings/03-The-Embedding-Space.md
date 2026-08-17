An embedding model turns each chunk into a dense, context-aware vector — say **512** numbers long. A vector of 512 numbers is a **point in 512-dimensional space.** Do this for every chunk in your knowledge base and you get a cloud of points living in that space. That space has a name — the **embedding space** (or **hyperspace**) — and understanding its geometry is what makes retrieval make sense.

Before we go in, here is where embeddings sit in the pipeline as a whole:

```mermaid
flowchart LR
    KS["Knowledge source<br/>(files, pages)"] --> DL["Document loaders"]
    DL --> DO["Document objects"]
    DO --> CH["Chunking"]
    CH --> EM["Embedding model"]
    EM --> VDB["Vector database<br/>(the embedding space)"]
    Q["User query"] --> EMQ["Embedding model"]
    EMQ --> QV["Query vector (512-dim)"]
    QV --> VDB
    VDB --> R["Nearest chunks retrieved"]
```

Both paths — the chunks going in, and the query coming later — pass through the **same** embedding model, so the query and the chunks land in the **same** space and can be compared. Now the geometry.

> [!info] The embedding space is the n-dimensional space (here we fix n = 512 to picture it) where every embedding vector lives as a point. Its defining property: **text with similar meaning lands on nearby points.** That single fact is the engine of retrieval.

We obviously cannot draw 512 dimensions, so every picture below is a 2-D stand-in. The intuition carries up to 512 unchanged.

---

## Property 1 — semantic clustering

Embed a batch of sentences and the points do not scatter randomly. Text about the same topic **clusters together**:

![[AI-Engineering/07-RAG/03-Embeddings/Images/03-Embedding-Space-Clusters.png]]

Points about **Python** form one tight cluster (green). Points about **JavaScript** form another (blue). And notice they sit **close to each other** — because Python and JavaScript are both programming languages, their clusters are neighbours, near enough to be circled together as one bigger **programming** region. Now look at the red cluster off on its own: that is **farming** — agriculture, a completely different topic — and its cluster sits far away from the programming clusters. Related concepts are naturally grouped; unrelated concepts drift apart. Nobody programmed those groupings; they fall out of the embeddings.

This gives you **similarity at multiple scales at once.** Zoom out and you see broad similarity — the whole programming region is one big neighbourhood, distinct from farming. Zoom in and you see narrow similarity — within Python, different sub-topics form their own little sub-clusters. A useful rule of thumb rides along with the picture:

> [!important] Cluster size tracks the breadth of the similarity. A **large** cluster covers a **broad** area of the space and therefore a **broad** similarity — **all of programming.** A **small** cluster covers a **narrow** area and a **narrow** similarity — **OOP concepts inside Python.** The distance **between** two clusters tells you how related their topics are: horticulture sits right next to farming (small gap, closely related), while farming sits far from programming (large gap, unrelated).

---

## Property 2 — direction carries meaning too

Distance is not the only thing the space encodes. **Direction** does as well — the **way** a vector points, measured from the origin, captures relationships between points.

![[AI-Engineering/07-RAG/03-Embeddings/Images/04-Directional-Meaning.png]]

Inside the Python cluster, take two points that are both about the **same kind** of thing — say two object-oriented-programming (OOP) concepts. Draw an arrow from the origin to each. The **angle between those two arrows is small** — they point in nearly the same direction, because they are closely related. Now take a point about something else in Python, like `functions`. The arrow to it points off at a noticeably **wider angle** — different direction, because it is a different sub-topic. So even **within** a single cluster, the direction a point sits in has meaning: similar things point similar ways.

Hold on to that idea — **similarity as a small angle between directions** — because it is exactly what one of the distance metrics in the next note is built on.

---

## What this buys us at query time

Now the retrieval story writes itself. A query arrives; it goes through the same embedding model and becomes a **dense, context-aware query vector** — 512 numbers, one more point dropped into the same space. Because that point lands wherever its **meaning** belongs, it falls right into the middle of the chunks that mean the same thing. Around that point sits a small **neighbourhood** — a localized region — and the chunk-points inside that neighbourhood are the ones we pull out and hand to the model.

```
query text
   │  same embedding model as the chunks
   ▼
query vector (512-dim)  ──►  placed into the embedding space
                                   │
                                   ▼
                        forms a local neighbourhood
                                   │
                                   ▼
                    nearest chunk-points = retrieved chunks
```

> [!tip] Interview framing: **Embeddings put every chunk into a high-dimensional space where meaning becomes geometry — similar text clusters together, and even direction encodes relationships. Retrieval is then just: embed the query into the same space and grab its nearest neighbours. That's why the whole approach hinges on a good embedding model — if meaning doesn't map to proximity, nearest-neighbour search returns nonsense.**

The one thing we've hand-waved is **nearest** — **how** do you actually measure how close the query point is to a chunk point? That is a choice of **distance metric**, and it's the next note.
