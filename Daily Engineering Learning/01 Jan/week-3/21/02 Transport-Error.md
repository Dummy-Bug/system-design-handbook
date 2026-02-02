# TRANSPORT ERROR FAMILY (connection broke)

These mean **connection failed abruptly**, not just slow.


## 1. ConnectError

### What it means

TCP connection attempt failed immediately.

---

### When it happens

- Server actively refused connection
- Port closed
- Wrong IP/port

---

### Visualization

```
Dial server
↓
Server says "connection refused"
```

---

### Retry?

Yes.

---

# 2. RemoteProtocolError

### What it means

Server sent invalid HTTP protocol data.

---

### When it happens

- Proxy bug
- Corrupt response 
- Server crash mid-response

---

### Visualization

```
Client reads response
↓
Header malformed
↓
Protocol error
```

---

### Retry?

Yes.

---

# 3. NetworkError

### What it means

Generic network failure.

---

### When it happens

- WiFi drops
- VPN disconnect 
- Packet loss

---

### Visualization

```
Request in progress
↓
Network cable unplugged
```

---

### Retry?

Yes.

---

# 4. SSLError

### What it means

TLS handshake failed.

---

### When it happens

- Certificate expired
- Invalid cert chain
- Clock skew

---

### Visualization

```
Secure handshake
↓
Certificate rejected
```

---

### Retry?

Usually NO if config issue.  
YES if transient handshake failure.

Production systems often retry once.

---

# Big picture summary

|Stage|Error type|
|---|---|
|Connection pool|PoolTimeout|
|TCP connect|ConnectTimeout / ConnectError|
|TLS handshake|SSLError|
|Sending request|WriteTimeout|
|Waiting response|ReadTimeout|
|Protocol parse|RemoteProtocolError|
|Network drop|NetworkError|
