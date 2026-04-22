## Producer Side (Avro Serializer)

The Avro serializer handles everything automatically — your code just sends an Order object.

```
1. Take Order object
2. Check if schema is registered in registry → if not, register it
3. Registry validates compatibility → rejects if breaking change
4. Embed schema_id in message header
5. Serialize Order to binary (just raw values, no labels)
6. Publish to Kafka
```

---

## Consumer Side (Avro Deserializer)

```
1. Read schema_id from message header
2. Fetch writer schema (id=101) from registry
3. Compare writer schema against consumer's own reader schema
4. Resolve differences (defaults for missing fields, ignore unknown fields)
5. Deserialize binary into Order object
```

Both steps are handled by the Avro library — your consumer code just receives a clean `Order` object.

---

## Full Example: v1 → v2

**Schema v1 (producer registers):**
```json
{
  "type": "record",
  "name": "Order",
  "fields": [
    { "name": "order_id", "type": "int" },
    { "name": "amount",   "type": "float" }
  ]
}
```
Registry assigns **schema_id = 101**.

**Producer publishes v1 message:**
```
[schema_id=101] [123] [50.0]
```

**Producer adds `currency` field — registers schema v2:**
```json
{
  "type": "record",
  "name": "Order",
  "fields": [
    { "name": "order_id", "type": "int" },
    { "name": "amount",   "type": "float" },
    { "name": "currency", "type": "string", "default": "USD" }
  ]
}
```

Registry checks: new field has a default → backward compatible ✅
Registry assigns **schema_id = 102**.

**Producer publishes v2 message:**
```
[schema_id=102] [124] [75.0] [USD]
```

**Old consumer (still on v1 reader schema) receives v2 message:**
```
Fetches writer schema 102 from registry
Compares with reader schema (v1 — no currency field)
  → currency in writer but not in reader → ignore it ✅
Deserializes → order_id=124, amount=75.0 ✅
```

**New consumer (on v2 reader schema) receives old v1 message:**
```
Fetches writer schema 101 from registry
Compares with reader schema (v2 — has currency field)
  → currency in reader but not in writer → use default "USD" ✅
Deserializes → order_id=123, amount=50.0, currency=USD ✅
```

---

## Avro vs Protobuf

| | Avro | Protobuf |
|---|---|---|
| Field identity | Name | Number |
| Schema format | JSON | .proto file |
| Wire format | Binary (no labels) | Binary (field numbers) |
| Schema Registry | Required — binary unreadable without it | Optional but recommended |
| Rename field | Breaking change | Safe (number stays) |
| Add field | Safe — must have default | Safe — old consumers ignore |
| Delete field | Safe — readers ignore missing | Safe — retire the number |
| Type change | Limited — compatible types only | Limited — widening safe |
| Common use | Kafka + Confluent Schema Registry | gRPC, Kafka, Google internal |

---

## One-Line Summary

> Avro resolves schema differences at read time by comparing writer and reader schemas — missing fields get defaults, unknown fields get ignored — but requires Schema Registry since binary data has no field labels.
