#httpx #http-client #cookies #shared-state #python #service-to-service

---

# A Shared HTTP Client Is a Browser, Not a Pipe

You create one `httpx.AsyncClient` at server startup and reuse it for every outgoing call. It feels like a pipe — you hand it a request, it sends it, done. But it is not a pipe. It is a browser. And that distinction is the source of a whole class of subtle bugs.

---

## The Pipe Mental Model

The naive assumption:

```python
client = httpx.AsyncClient()

# request goes in → response comes out → nothing persists between calls
response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
```

If this were a pipe, every call would be stateless. The client would carry nothing from one request to the next. What you pass is what gets sent, nothing more.

---

## What Actually Persists Inside a Shared Client

A shared `httpx.AsyncClient` holds state across requests whether you ask it to or not:

| State | What it is | Who updates it |
|---|---|---|
| **Cookie jar** | Domain-keyed store of cookies | Updated automatically on every `Set-Cookie` response header |
| **Connection pool** | Open TCP connections to recently used hosts | Managed automatically; reused across requests |
| **Redirect history** | Tracks followed redirects per host | Updated on 3xx responses |

The connection pool is the reason you create a shared client in the first place — reusing open TCP connections is fast, creating new ones is expensive.

But the cookie jar comes along for free whether you want it or not.

> [!important] You opted in for the connection pool. You got the cookie jar whether you wanted it or not. They come as a package.

---

## The Cookie Jar — Feature or Trap?

For **browser-like flows**, the jar is the feature:

```python
# login returns Set-Cookie: SESSION=abc
await client.post("/login", data=credentials)

# every subsequent call automatically sends SESSION=abc via the jar
await client.get("/dashboard")   # no cookie param needed
await client.get("/profile")     # no cookie param needed
```

You make one authenticated call and every call after it inherits the session. The jar does the bookkeeping for you.

For **service-to-service calls**, the jar is the trap:

```python
# you pass explicit tokens on every call
await client.get(url, cookies={"SESSION": token_A})
await client.post(url, cookies={"SESSION": token_A})
```

The assumption: token_A goes on the wire both times. But the GET response may have returned `Set-Cookie: SESSION=token_B` — a rotated token the server issues on every response. Now the jar holds token_B. The POST merges jar-first, so token_B leads on the wire. Your explicit token_A comes second. The server reads token_B, which it already rotated away. 401.

> [!danger] Every response can silently update the jar. A successful GET that returns `Set-Cookie` poisons every subsequent call on the same client.

---

## The Analogy

Think of the shared client as a traveller carrying a passport wallet.

The wallet has pockets. You put your own documents in one pocket (per-request cookies). But the wallet also has a second pocket that fills itself automatically — every country you visit stamps a new entry into it (jar cookies from `Set-Cookie`).

When you show your wallet at the next border, the guard sees both pockets. Crucially, they read the automatic pocket first. If the stamps in there are expired or wrong, you get turned away — even though your own valid documents are sitting right behind them.

---

## When the Jar Is Right and When to Disable It

> [!tip] Decision rule
> - **Session flows** (login → carry cookie forward): let the jar accumulate. Don't clear it.
> - **Service-to-service calls** (each request carries its own explicit auth): clear the jar before every request, or use `Authorization` headers instead of cookies (httpx never touches headers with the jar).

---

## Mental Model To Remember

> [!info] A shared `httpx.AsyncClient` is a browser. It carries a cookie jar, a connection pool, and redirect history across every call. The connection pool is why you share the client. The cookie jar is what bites you if you forget it is there.
