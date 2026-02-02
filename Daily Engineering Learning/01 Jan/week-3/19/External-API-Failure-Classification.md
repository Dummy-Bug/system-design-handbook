#backend #reliability #error-handling #distributed-systems

---

## Why Failure Classification Matters

Not all failures are equal.

Treating all errors the same causes:

- Wrong retry behavior
    
- Wasted resources
    
- Cascading failures
    
- Poor observability
    

Correct classification lets you apply the right response.

---

## The Four Failure Categories

Every external API failure fits into one of these layers:

`Network Layer Transport Layer Protocol Layer Data Contract Layer`

Mapped as:

- NETWORK ERROR
    
- TIMEOUT ERROR
    
- HTTP ERROR
    
- SCHEMA ERROR
    

---

## TIMEOUT Errors

### What It Means

Request reached the server, but no response arrived within time limit.

---

### Common Causes

- Slow database queries
    
- Server overload
    
- Cold starts
    
- Network latency spikes
    

---

### Correct Action

- Retry
    
- Tune timeout budgets
    
- Monitor latency metrics
    

Timeouts are usually transient.

---

## NETWORK Errors

### What It Means

Connection failed before request completed.

Examples:

- DNS resolution failure
    
- TLS handshake failure
    
- Connection reset by peer
    

---

### Correct Action

- Retry
    
- Investigate network or infrastructure issues
    

Network failures are external and unpredictable.

---

## HTTP Errors

### What It Means

Server responded with an explicit error status code.

Examples:

- 401 → authentication failure
    
- 403 → permission or CSRF issue
    
- 404 → incorrect endpoint
    
- 500 → server crash
    

---

### Correct Action

#### 4xx Errors

- Do NOT retry
    
- Fix request, credentials, or configuration
    

#### 5xx Errors

- Retry
    
- Treat as server instability
    

---

## SCHEMA Errors

### What It Means

Response body does not match expected data structure.

Causes:

- API contract change
    
- Backend bug
    
- Version mismatch
    

---

### Correct Action

- Do NOT retry
    
- Fix integration or schema
    
- Update contract assumptions
    

Retrying invalid data does nothing.

---

## Summary Table

|Failure Type|Retry?|Root Cause|
|---|---|---|
|TIMEOUT|Yes|Server slow|
|NETWORK|Yes|Infrastructure|
|HTTP 4xx|No|Client mistake|
|HTTP 5xx|Yes|Server failure|
|SCHEMA|No|Contract mismatch|

---

## Mental Model To Remember

`Retry Transient Failures Fix Deterministic Failures`

---

## Common Mistakes To Avoid

- Retrying authentication failures
    
- Retrying schema mismatches
    
- Treating all errors as network issues
    

---

## Transferable Principle

> Correctly classifying failures is required to build reliable distributed systems.

This knowledge applies to:

- APIs
    
- Databases
    
- Message brokers
    
- Microservices