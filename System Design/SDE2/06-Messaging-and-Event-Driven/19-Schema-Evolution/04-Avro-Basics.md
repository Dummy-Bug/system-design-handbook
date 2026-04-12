## What Is Avro

Avro is a schema format developed by Apache, commonly used with Kafka. Unlike Protobuf which uses field numbers, Avro uses **field names** — same as JSON.

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

No field numbers. Fields are identified by name.

---

## The Problem With Field Names

If identity is based on name, renaming a field is a **breaking change**:

```json
{ "name": "amount" }   →   { "name": "price" }
```

Old messages have `amount`. New consumer looks for `price`. No match — field is lost.

This is the fundamental tradeoff vs Protobuf:

| | Protobuf | Avro |
|---|---|---|
| Field identity | Number | Name |
| Rename field | Safe | Breaking change |
| Human readable schema | Yes | Yes (JSON) |

---

## Writer Schema vs Reader Schema

Avro solves compatibility differently from Protobuf. Instead of field numbers, it uses **schema resolution** — comparing the schema the producer used (writer schema) against the schema the consumer has (reader schema).

```
Writer schema (producer):   { order_id, amount }
Reader schema (consumer):   { order_id, amount, currency }
```

Avro compares them field by field and resolves differences:

- Field in reader but not in writer → use the **default value** defined in reader schema
- Field in writer but not in reader → **ignore it**
- Field in both → deserialize normally

---

## Default Values Are Mandatory for New Fields

Since Avro relies on defaults for missing fields, every new field **must** have a default value:

```json
{
  "name": "currency",
  "type": "string",
  "default": "USD"    ← required for backward compatibility
}
```

If you add a field without a default, old messages (which don't have this field) cannot be read by the new consumer. Schema Registry will reject it.

---

## Why Schema Registry Is Critical for Avro

Protobuf embeds field numbers in the binary — the consumer can partially decode even without the exact writer schema.

Avro binary is **just values, no field names or numbers**:

```
Binary: [123] [50.0]   ← just raw values, no labels
```

Without the writer schema, the consumer has no idea what these bytes mean. It cannot deserialize at all.

This is why Schema Registry is not optional for Avro — the consumer **must** fetch the exact writer schema to make sense of the binary data.
