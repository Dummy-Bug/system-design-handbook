# Layer 4 — How It Actually Works

> [!question] A packet arrives. The LB picks a server. But mechanically — how does it forward the packet, track the connection, and hide the server from the client?
> NAT, connection tables, and the difference between TCP and UDP — all of it here.

---

## The Backend Pool — How the LB Knows Its Servers

The L4 LB doesn't discover servers on its own. You configure it with a **backend pool** — a list of servers it can forward to, the port they listen on, and which algorithm to use.

```
Backend Pool — Valorant Game Servers:
  Server A: 10.0.0.3:7777  ✓ healthy
  Server B: 10.0.0.5:7777  ✓ healthy
  Server C: 10.0.0.7:7777  ✓ healthy

Protocol:  UDP
Algorithm: Least Connections
Listen on: port 7777
```

When a new server spins up, it registers itself into the pool. When a server fails health checks, it's removed. The pool is dynamic — the LB's view of available servers updates continuously.

---

## NAT — How the LB Hides Backend Servers

The client connects to the LB's IP. It has no idea backend servers exist. The LB uses **NAT (Network Address Translation)** to make this work — it rewrites IP addresses on every packet.

**On the way in (client → server):**
```
Packet arrives at LB:
  Source IP:   192.168.1.50:54321  (Valorant client)
  Dest IP:     10.0.0.1:7777       (load balancer)

LB rewrites destination:
  Source IP:   192.168.1.50:54321  (unchanged)
  Dest IP:     10.0.0.5:7777       (Server B — swapped!)

LB forwards to Server B
```

**On the way back (server → client):**
```
Server B responds:
  Source IP:   10.0.0.5:7777       (Server B)
  Dest IP:     192.168.1.50:54321  (client)

LB rewrites source:
  Source IP:   10.0.0.1:7777       (load balancer — swapped back!)
  Dest IP:     192.168.1.50:54321  (client)

Client receives response from LB's IP — never saw Server B
```

---

## TCP Full Walkthrough — PgBouncer (PostgreSQL Connection Pooling)

PostgreSQL speaks its own binary wire protocol over TCP — not HTTP. An app server connecting to PostgreSQL through PgBouncer is a perfect L4 TCP example — one service, custom protocol, port 5432.

```mermaid
sequenceDiagram
    participant App as App Server (192.168.1.50)
    participant PB as PgBouncer L4 LB (10.0.0.1:5432)
    participant DB as Postgres B (10.0.0.5:5432)

    App->>PB: TCP SYN (dst: 10.0.0.1:5432)
    Note over PB: Port 5432 → PostgreSQL pool<br/>Least Connections → picks DB B<br/>Rewrites dst: 10.0.0.5<br/>Records: 192.168.1.50:54321 → 10.0.0.5
    PB->>DB: TCP SYN (dst: 10.0.0.5:5432)
    DB->>PB: TCP SYN-ACK
    Note over PB: Rewrites src: 10.0.0.5 → 10.0.0.1
    PB->>App: TCP SYN-ACK (src: 10.0.0.1)
    Note over App: TCP handshake complete ✓
    App->>PB: PostgreSQL wire protocol — SELECT * FROM users WHERE id=7
    Note over PB: Looks up connection table<br/>192.168.1.50:54321 → DB B<br/>Forwards to 10.0.0.5
    PB->>DB: PostgreSQL wire protocol — SELECT * FROM users WHERE id=7
    DB->>PB: Result rows (binary PostgreSQL format)
    Note over PB: Rewrites src to 10.0.0.1
    PB->>App: Result rows
    Note over App: Got query results. Never knew DB B existed.
```

> [!warning] Why not use L4 for HTTPS (port 443) routing to multiple services?
> If Valorant had `/login`, `/store`, `/skins`, `/matchhistory` all arriving on port 443, L4 cannot tell them apart — they all look identical. It would blindly send all of them to the same server pool, which may be completely wrong for most requests. That's exactly L7's job — read the URL and route to the right service.

> [!info] How the connection table tracks every packet across the connection's lifetime — see `05-Layer4-Connection-Tables.md`

---

## TCP vs UDP — The Core Difference

Before the UDP walkthrough, you need to understand why UDP exists.

**TCP — connection first, data second**

```
Client → SYN          → Server   (want to talk?)
Client ← SYN-ACK      ← Server   (yes, ready)
Client → ACK          → Server   (connected)
Client → data         → Server   (actual request)
Client ← data         ← Server   (actual response)
Client → FIN          → Server   (done, closing)
```

TCP guarantees delivery — lost packets are resent. This adds latency. Fine for login, not fine for real-time gameplay.

**UDP — just fire the packet**

```
Client → packet → Server   (data sent, no waiting)
```

No handshake. No acknowledgment. No guarantee. If the packet is lost — it's gone. The game client doesn't wait for confirmation. It fires the next packet 8ms later anyway.

| | TCP | UDP |
|---|---|---|
| Handshake | Yes — 3 steps before any data | No |
| Delivery guarantee | Yes — resends lost packets | No |
| Speed | Slower | Much faster |
| Use when | Correctness matters (DB queries, file transfers) | Speed matters, loss is ok (positions, game state) |

---

## UDP Full Walkthrough — Valorant Position Update

Valorant runs at **128 tick rate** — 128 position updates per second, every 8ms.

```mermaid
sequenceDiagram
    participant Client as Valorant Client (192.168.1.50)
    participant LB as L4 Load Balancer (10.0.0.1)
    participant ServerB as Game Server B (10.0.0.5)

    Note over Client: Player moved. Pack position into 14 bytes.
    Client->>LB: UDP packet (dst: 10.0.0.1:7777, data: playerID=7 x=44 y=01 z=89)
    Note over LB: Port 7777 → Game server pool<br/>IP Hash → always picks same server per player<br/>NAT: rewrites dst to 10.0.0.5<br/>UDP session table tracks this mapping
    LB->>ServerB: UDP packet (dst: 10.0.0.5:7777, data: playerID=7 x=44 y=01 z=89)
    Note over ServerB: Updates game state for player 7
    ServerB->>LB: UDP packet (updated world state)
    Note over LB: NAT: rewrites src to 10.0.0.1
    LB->>Client: UDP packet (updated world state)
    Note over Client: 8ms later — fires next position update
```

**What the Valorant client actually sends — raw binary, not HTTP:**

```python
# Inside Valorant client — simplified
import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket

# Pack position as binary — 14 bytes total
# No HTTP headers. No JSON. Just raw numbers.
position_data = struct.pack('!HfffB',
    player_id,   # 2 bytes
    x,           # 4 bytes
    y,           # 4 bytes
    z,           # 4 bytes
)  # = 14 bytes

# No connect() — UDP has no connection
# Just fire the packet
sock.sendto(position_data, ("10.0.0.1", 7777))
```

Compare to what an HTTP request looks like:

```
POST /api/v1/location HTTP/1.1
Host: game-server.valorant.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...
Content-Length: 28

{"x": 44, "y": 01, "z": 89}
```

~300 bytes with headers vs 14 bytes binary. 20x smaller. No TCP handshake. 128 times per second across 10 players — the difference is enormous.

> [!info] How UDP session tables differ from TCP connection tables — and when UDP needs one at all — see `05-Layer4-Connection-Tables.md`
