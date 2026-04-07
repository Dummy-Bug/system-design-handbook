# Layer 4 — Fundamentals

> [!question] A packet arrives at the load balancer. What can it actually see? What is it blind to?
> Everything depends on which layer you're operating at — and Layer 4 sees the envelope, never the letter inside.

---

## The OSI Model — Just Enough Context

The internet is built in layers. Each layer has one job and wraps the layer above it — like envelopes inside envelopes.

```
Layer 7 — Application   What the request contains    (HTTP, URL, headers, body)
Layer 4 — Transport     How data travels reliably     (TCP/UDP, port numbers)
Layer 3 — Network       Where data is going           (IP addresses)
Layer 2 — Data Link     Physical machine addressing   (MAC addresses)
Layer 1 — Physical      Actual cables and signals
```

When a Valorant game client sends a position update:
- Layer 7 doesn't exist — this isn't HTTP, it's raw binary data
- Layer 4 wraps it in UDP: adds source port, destination port
- Layer 3 wraps that in IP: adds source IP, destination IP
- Layers 1–2 handle the physical transmission

A Layer 4 load balancer sits at the Transport layer. It can open the IP envelope (Layer 3) and the TCP/UDP envelope (Layer 4). It **cannot** open anything inside — it never sees the actual data.

---

## What L4 Sees vs What It Cannot See

| L4 Can See | L4 Cannot See |
|---|---|
| Source IP address | URL path (`/recommendations`) |
| Destination IP address | HTTP headers |
| Port number (443, 7777) | Cookies |
| Protocol — TCP or UDP | Request body |
| TCP connection state | JSON payload |
| | SSL certificate content |

This is why L4 is extremely fast — it never reads the content. It looks at the outer envelope and forwards it.

---

## Port Numbers — Who Decides Them?

Every request has two ports — a destination port and a source port. They serve completely different purposes.

### Destination Port — the service address

This is the port the server is listening on. It tells the network which application on the server should receive this packet.

**Who decides it?**

**IANA (Internet Assigned Numbers Authority)** — the global body that manages internet standards — defined well-known ports for standard protocols:

```
Port 80    → HTTP
Port 443   → HTTPS
Port 53    → DNS  (UDP)
Port 22    → SSH
Port 25    → SMTP (email)
Port 3306  → MySQL
Port 5432  → PostgreSQL
```

These are called **well-known ports (0–1023)**. Every OS, every browser, every tool knows them. When you type `https://google.com`, the browser automatically connects to port 443 — it's baked in as a universal standard. Google didn't choose 443 — IANA defined it for HTTPS, Google just follows the standard.

For **custom applications** — the company picks a port themselves and hardcodes it into their software:

Riot decided their game servers listen on **port 7777**. That decision lives in Valorant's source code:

```python
# Inside Valorant client — hardcoded
GAME_SERVER_PORT = 7777
socket.sendto(position_data, ("game-server.valorant.com", GAME_SERVER_PORT))
```

When you install Valorant, port 7777 comes with it. Riot's servers listen on 7777 because Riot configured them to.

### The Three Port Ranges

| Range | Name | Who uses it |
|---|---|---|
| 0 – 1023 | Well-known ports | IANA standards — HTTP, HTTPS, DNS, SSH |
| 1024 – 49151 | Registered ports | Companies register with IANA — MySQL (3306), PostgreSQL (5432) |
| 49152 – 65535 | Dynamic/private ports | Anyone — game servers, internal services |

### Source Port — the return address

**The source port is randomly assigned by your OS for each new connection** — just so the server knows where to send the response back.

```
Valorant client sends packet:
  Source port:      54821   ← randomly assigned by OS (changes every session)
  Destination port: 7777    ← hardcoded in Valorant client (always 7777)
```

You never configure the source port. Your OS picks it automatically.

---

## Why L4 Is Fast

Because it never reads what's inside the packet. Processing a request at Layer 4 means:

1. Read source IP + destination port from the packet header
2. Look up which backend server to forward to
3. Rewrite the destination IP
4. Forward

That's it. No HTTP parsing, no SSL decryption, no URL inspection. This happens in **microseconds** — so fast it can be implemented in hardware on specialized network chips.

AWS Network Load Balancer (L4) handles **millions of requests per second** at under 100 microseconds latency. No Layer 7 load balancer comes close.

> [!tip] L4 is fast because it's blind
> It never reads what's inside the packet — just looks at the envelope and forwards it.
