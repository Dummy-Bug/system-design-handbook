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

## TCP Full Walkthrough — Valorant Login

Login uses HTTPS (TCP) — correctness matters, can't lose the authentication token.

```mermaid
sequenceDiagram
    participant Client as Valorant Client (192.168.1.50)
    participant LB as L4 Load Balancer (10.0.0.1)
    participant ServerB as Auth Server B (10.0.0.5)

    Client->>LB: TCP SYN (dst: 10.0.0.1:443)
    Note over LB: Port 443 → Auth server pool<br/>Round Robin → picks Server B<br/>Rewrites dst: 10.0.0.5<br/>Records: 192.168.1.50:54321 → 10.0.0.5
    LB->>ServerB: TCP SYN (dst: 10.0.0.5:443)
    ServerB->>LB: TCP SYN-ACK
    Note over LB: Rewrites src: 10.0.0.5 → 10.0.0.1
    LB->>Client: TCP SYN-ACK (src: 10.0.0.1)
    Note over Client: TCP handshake complete ✓
    Client->>LB: POST /login {username, password}
    Note over LB: Looks up connection table<br/>192.168.1.50:54321 → Server B<br/>Forwards to 10.0.0.5
    LB->>ServerB: POST /login {username, password}
    ServerB->>LB: 200 OK {auth_token}
    Note over LB: Rewrites src to 10.0.0.1
    LB->>Client: 200 OK {auth_token}
    Note over Client: Logged in. Never knew Server B existed.
```

The connection table is what makes this work:

```
Connection Table:
192.168.1.50:54321  →  Server B (10.0.0.5)
192.168.1.51:61234  →  Server A (10.0.0.3)
192.168.1.52:49812  →  Server C (10.0.0.7)
```

Every packet that arrives gets looked up and forwarded to the right server for the duration of that TCP connection.

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
| Use when | Correctness matters (login, purchases) | Speed matters, loss is ok (positions, game state) |

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
    Note over LB: Port 7777 → Game server pool<br/>Least Connections → picks Server B<br/>NAT: rewrites dst to 10.0.0.5<br/>No connection table — UDP is stateless
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

> [!info] UDP has no connection table
> TCP needs a connection table because the LB must map ongoing connections to the right server. UDP has no connections — each packet is independent. The LB uses IP hashing (source IP → same server) to ensure all UDP packets from the same player go to the same game server.
