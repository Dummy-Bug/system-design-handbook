#sse #streaming #proxies #buffering #debugging

**Turning off buffering in one place is not turning off buffering.** A deployed request passes through several machines, each of which decides independently whether to hold your bytes — and fixing one of them looks exactly like fixing none of them.

# A frame does not go from your code to the browser

It goes through a chain:

```mermaid
flowchart LR
    A["your app"] --> B["nginx"] --> C["load balancer"] --> D["CDN"] --> E["browser"]
    linkStyle default stroke:#7d8590,stroke-width:2px
```

Each of those is a **separate program, usually on a separate machine, often owned by a different person.** Each receives bytes from the thing before it, decides when to pass them on, and may hold them in a buffer while deciding.

So a frame written by your code has to survive four hand-offs, and **any one of them can hold it.**

# What the header actually covers

`X-Accel-Buffering: no` is a convention that **nginx** looks for. Your app sets it in the response, nginx reads it, and nginx disables its own buffering.

That is the entire scope of it.

```text
1  your app  →  nginx  →  load balancer  →  CDN  →  browser
2                 ▲
3                 └── the header fixed this one, and only this one
```

The CDN has never heard of that header. Neither has the load balancer. Each has its own configuration, in its own place, controlled by whoever owns that box.

So the sequence is: your app writes a frame, nginx forwards it immediately because you fixed nginx, and **the CDN holds it anyway.** Nothing reaches the browser, the symptom is completely unchanged, and it looks as though the fix did nothing at all.

> One fix at one hop is not a fix. **Streaming has to be enabled at every hop**, and nothing anywhere tells you when one was missed.

# Finding which hop is doing it

The header did not help, and there is no error to read. So the question becomes which of four machines is holding the bytes — and the way to answer it is to **remove hops one at a time.**

Test progressively closer to the application:

| test | what it goes through | result |
|---|---|---|
| `curl` the app directly, on the box | nothing | streams fine |
| `curl` through nginx | nginx | streams fine |
| `curl` through the load balancer | nginx, LB | streams fine |
| `curl` the public URL | nginx, LB, CDN | **arrives in one lump** |

**The first step that breaks is the hop that is buffering.** Working at step three and failing at step four means the CDN is holding your frames, and no amount of nginx configuration will ever change that.

```mermaid
flowchart LR
    T1["direct ✓"] --> T2["+ nginx ✓"] --> T3["+ load balancer ✓"] --> T4["+ CDN ✗"]
    style T4 fill:#da3633,color:#fff
    linkStyle default stroke:#7d8590,stroke-width:2px
```

> [!important] The technique is more general than the bug
> Any failure that appears only in production and not locally is a failure introduced by something between the two. **Bisecting the path** — testing at each hop, from the application outwards — finds it without needing to understand what each box does internally.
>
> It works for buffering, for stripped headers, for altered timeouts, and for anything else the middle of a network does silently.

# Why this bug comes back

Nothing about the fix is durable, because the fix lives in configuration on machines your code does not own.

Somebody adds a CDN six months later, for reasons that have nothing to do with streaming. No code changes. No deployment of your service. **And streaming silently stops working**, with the same symptom as the first time — everything arriving at once at the end, no errors anywhere, healthy logs.

> [!warning] The path is not stable, and changes to it are invisible to your service
> A hop added by another team, a load balancer swapped for a different product, a proxy inserted for compliance — none of these appear in your repository, your logs, or your deploys.
>
> Which makes this worth writing down somewhere the next person will find: **the list of hops, and the buffering setting each one needs.** It is the only thing that survives the person who worked it out.
