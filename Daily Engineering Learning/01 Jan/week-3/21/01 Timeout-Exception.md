Think of an HTTP call as:

```
1. Get connection from pool
2. Open TCP connection
3. Establish TLS (HTTPS)
4. Send request bytes
5. Wait for response
6. Read response bytes
```

Failures map to these steps.

---

# TIMEOUT FAMILY (took too long)

These mean the operation did not fail logically. It just **exceeded time limit**.

---

## 1. PoolTimeout

### What it means

No free connection available in the client connection pool.

---

### When it happens

- You set max connections = 10
    
- 10 requests are already in progress
    
- New request waits
    
- Pool wait exceeds timeout
    

---

### Visualization

```
Client wants connection
↓
Pool is full
↓
Waits
↓
Timeout
```

---

### Real scenario

High concurrency onboarding runs.

Too many parallel API calls.

---

### Retry?

Yes. Temporary resource exhaustion.

---

# 2. ConnectTimeout

### What it means

Could not establish TCP connection to server in time.

---

### When it happens

- Server is overloaded
    
- Network routing problem
    
- Firewall blocking
    
- Load balancer not responding
    

---

### Visualization

```
Dial server IP
↓
No handshake
↓
Timeout
```

---

### Retry?

Yes.

---

# 3. WriteTimeout

### What it means

Client could not send request data fast enough.

---

### When it happens

- Slow network upload
    
- Large payload
    
- Congested network
    

---

### Visualization

```
Sending request body
↓
Network stalls
↓
Timeout
```

---

### Retry?

Yes.

---

# 4. ReadTimeout

### What it means

Server accepted request but did not send response fast enough.

---

### When it happens

- Backend processing slow
    
- Database query slow
    
- External dependency slow
    

---

### Visualization

```
Request sent
↓
Server thinking...
↓
Timeout
```

---

### Retry?

Yes.