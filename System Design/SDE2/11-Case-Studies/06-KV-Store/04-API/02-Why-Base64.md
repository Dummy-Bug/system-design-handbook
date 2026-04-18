## The Problem — How Do You Send Raw Bytes in JSON?

Our KV store accepts **opaque bytes** as values. The client might store a string, a number, a serialized protobuf, or a tiny image thumbnail. The store doesn't care — it just holds the bytes and gives them back.

But the API uses JSON, and JSON is **text-only**. You can't put raw bytes in a JSON string. Some byte values are invalid UTF-8, some are control characters that break parsers, some are the `"` character itself which terminates the string.

```json
{
  "key": "user:123:avatar",
  "value": ???  ← raw image bytes can't go here
}
```

So how do you get arbitrary bytes into a JSON body?

---

## Option 1 — Just stringify the bytes directly?

Your first instinct might be: just put the bytes inside quotes. Like `"value": "\xFF\xD8\xFF"`.

This breaks because JSON strings are UTF-8 text, and not all byte sequences are valid UTF-8:

```
Byte 0xFF → not a valid UTF-8 character → parser rejects it
Byte 0x00 → null byte → terminates strings in many languages
Byte 0x0A → newline → breaks JSON structure
Byte 0x22 → the " character → JSON thinks the string ended
```

Imagine your image has the byte `0x22` somewhere in it. The JSON parser sees a closing quote mid-string:

```json
{
  "key": "user:123:avatar",
  "value": "some bytes then " oops JSON is broken here"
}
```

The JSON is malformed. The parser crashes or returns garbage. So raw bytes in JSON strings is not an option.

---


## Option 2 — Base64 (the winner)

Base64 converts any sequence of bytes into **text characters that are safe everywhere** — in JSON, in URLs, in HTTP headers, in emails. It uses exactly 64 characters:

```
A-Z  (26 characters)
a-z  (26 characters)
0-9  (10 characters)
+ /  (2 characters)
─────────────────────
= 64 characters total, all printable, all safe
```

### How it works

Take the string `"Hi"` as a simple example. In bytes:

```
H = 72  → binary: 01001000
i = 105 → binary: 01101001
```

That's 16 bits total: `01001000 01101001`

Base64 regroups these bits into **6-bit chunks** instead of the original 8-bit bytes:

```
Original (8-bit groups):   01001000  01101001
Base64 (6-bit groups):     010010    000110    100100

(the last group is padded with zeros to fill 6 bits)
```

Each 6-bit number (0-63) maps to one of the 64 safe characters:

```
010010 = 18 → S
000110 =  6 → G
100100 = 36 → k
(padding)   → =
```

Result: `"Hi"` (2 bytes) becomes `"SGk="` (4 characters)

### Why 33% overhead?

Every 3 bytes of input become 4 base64 characters:

```
3 bytes in → 24 bits → split into 4 groups of 6 bits → 4 characters out

4 / 3 = 1.33× the original size = 33% overhead
```

The reason: raw bytes use 8 bits per character (256 possible values), but base64 uses only 6 bits per character (64 possible values). Fewer possibilities per character means you need more characters to carry the same information. Like a currency exchange — if each base64 "dollar" is worth less than a byte "dollar," you need more of them.

### Why not base128 or base256?

Because the whole point is safety. Base256 would use all 256 byte values — but many of those are control characters (null, newline, tab) or characters that break JSON (`"`, `\`). Base128 has the same problem with ASCII 0-31. Base64 is the sweet spot: maximum alphabet size where **every character is guaranteed safe** in any text-based format.

### At our scale

```
Base64 overhead:  1 KB → 1.33 KB per value → 330 GB/day extra
Hex overhead:     1 KB → 2 KB per value    → 1 TB/day extra
```

Base64 adds 330 GB/day. Hex adds 1 TB/day. Over 10 years, base64 saves ~2.4 PB of storage and network traffic compared to hex. That's why it's the industry standard for encoding binary data in text formats.

---

## How it looks in our KV store API

The client base64-encodes the value before sending, and base64-decodes after receiving:

```
PUT request:
{
  "key": "user:123:avatar",
  "value": "/9j/4AAQSkZJRg..."    ← base64-encoded image bytes
}

GET response:
{
  "key": "user:123:avatar",
  "value": "/9j/4AAQSkZJRg..."    ← same base64 string
}

Client decodes "/9j/4AAQ..." back to the original image bytes
```

The server receives the base64 string, decodes it back to raw bytes, and stores the raw bytes on disk. It doesn't store the base64 version — that would waste 33% disk space. Base64 is only used for **transport** over JSON, not for storage.

---

> [!tip] Interview framing
> "Values are opaque bytes, but our API uses JSON which is text-only. We base64-encode the value for transport — it's the standard way to carry binary data in JSON. 33% overhead on the wire, but we store the decoded raw bytes on disk so there's no storage penalty. We chose base64 over hex encoding because hex has 100% overhead — doubles the payload size, which at a billion writes per day adds up to an extra TB of daily network traffic."
