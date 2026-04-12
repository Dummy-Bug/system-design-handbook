## What It Is

A **Schema Registry** is a central store for message schemas. It acts as a gatekeeper — producers must register and validate their schema before publishing. Consumers fetch the schema to deserialize messages.

Incompatible schema changes are **rejected at registration time** — before they ever reach Kafka.

---

## How It Works

Instead of embedding the full schema in every message (expensive), the message carries only a tiny **schema ID**:

```
Message format:
[schema_id=101] [field1_value] [field2_value] ...
```

Consumer receives the message, looks up schema 101 from the registry, and deserializes.

---

## Full Flow: v1 → v2 Schema Change

**Setup:**
```
Producer: Order Service
Consumer: Billing Service
Topic: orders
```

**Step 1 — Producer registers schema v1:**
```protobuf
message Order {
  int32 order_id = 1;
  float amount   = 2;
}
```
Registry assigns **schema ID = 101**.

**Step 2 — Producer publishes:**
```
[schema_id=101] [order_id=123] [amount=50.0]
```

**Step 3 — Consumer receives:**
```
Fetches schema 101 from registry
Deserializes → order_id=123, amount=50.0 ✅
```

---

**Producer adds `currency` field — schema v2:**

**Step 4 — Producer registers schema v2:**
```protobuf
message Order {
  int32 order_id  = 1;
  float amount    = 2;
  string currency = 3;
}
```

Registry checks compatibility:
- Old consumer reads new message → field 3 missing → uses default ✅
- New consumer reads old message → field 3 unknown → ignores ✅

**Compatible → schema ID = 102 assigned.**

**Step 5 — Producer publishes:**
```
[schema_id=102] [order_id=124] [amount=75.0] [currency=USD]
```

**Step 6 — Old consumer (not yet updated) receives:**
```
Fetches schema 102 from registry
Reads field 1 → order_id=124 ✅
Reads field 2 → amount=75.0  ✅
Field 3 unknown → ignores    ✅
No crash
```

---

## Registry Rejects Incompatible Changes

Producer tries to change field 2 type from `float` to `int32`:

```
Registry checks: int32 ≠ float on field 2 → type change breaks old consumers
→ REJECTED
```

Producer cannot publish until they fix the schema. Bad changes never reach Kafka.

---

## Key Properties

| Property | Detail |
|----------|--------|
| Schema storage | Central registry, not in messages |
| Message overhead | Only schema ID (4 bytes) per message |
| Compatibility check | Enforced at registration, not at runtime |
| Consumer lookup | Fetch schema by ID, cache locally |
| Popular implementations | Confluent Schema Registry (for Kafka + Avro/Protobuf) |
