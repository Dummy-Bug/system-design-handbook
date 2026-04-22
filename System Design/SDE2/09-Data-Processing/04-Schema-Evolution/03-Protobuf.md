
## What Is Protobuf

Protocol Buffers (Protobuf) is a schema format developed by Google. It defines message structures using **field numbers** instead of field names.

```protobuf
message Order {
  int32 order_id  = 1;
  float amount    = 2;
  string currency = 3;
}
```

The wire format sends `field 1: 123`, `field 2: 50.0` — not `order_id: 123`, `amount: 50.0`.

---

## Why Field Numbers Beat Field Names

### Renaming is safe
```protobuf
float amount = 2;   ← rename to "price" in code
```
Wire still sends `field 2: 50.0`. Old consumer reads field 2, calls it `amount`. New consumer reads field 2, calls it `price`. Both work — the number is the identity, not the name.

### Reordering is safe
```protobuf
float amount    = 2;   ← always field 2, regardless of position
int32 order_id  = 1;   ← always field 1
```
Position in the file doesn't matter. The number determines what the field is.

---

## Adding Fields Safely

Add new fields with a new number:

```protobuf
message Order {
  int32 order_id  = 1;
  float amount    = 2;
  string currency = 3;  ← new field, new number
}
```

- Old consumer sees field 3 — unknown, **ignores it** → forward compatible ✅
- New consumer reads old message — field 3 missing, uses **default value** → backward compatible ✅

---

## Deleting Fields — Retire the Number Forever

```protobuf
message Order {
  int32 order_id  = 1;
  // float amount = 2;  ← deleted
  string currency = 3;
}
```

Number 2 is **retired forever**. Never reuse it for a new field.

Why? Old messages in Kafka still have `field 2: 50.0` (a float). If you reuse number 2 for a new `int32 discount` field:

```
Old consumer reads field 2 → expects float → gets int → crash
```

The old data doesn't know field 2 was deleted. Reusing its number corrupts deserialization.

---

## Type Changes — Widening Safe, Narrowing Not

| Change | Safe? | Why |
|--------|-------|-----|
| `int32` → `int64` | ✅ | Wider type, old values still fit |
| `float` → `double` | ✅ | Wider type, old values still fit |
| `int32` → `string` | ❌ | Completely different wire format |
| `float` → `int32` | ❌ | Loses precision, old data corrupted |
| `int64` → `int32` | ❌ | Narrowing — large values overflow |

Rule: **widening is safe, narrowing and cross-type changes are not.**

Schema Registry enforces this automatically.

---

## Protobuf vs JSON

| | JSON | Protobuf |
|---|---|---|
| Format | Human readable text | Binary |
| Size | Large | 3-10x smaller |
| Speed | Slow to parse | Fast |
| Schema | Optional | Required |
| Evolution | Manual, error-prone | Built-in via field numbers |
| Use case | REST APIs, debugging | Kafka, gRPC, high-throughput systems |

---

## One-Line Summary

> Protobuf uses field numbers as permanent identities — rename, reorder, add, or remove fields freely, as long as you never reuse a retired number or change types incompatibly.
