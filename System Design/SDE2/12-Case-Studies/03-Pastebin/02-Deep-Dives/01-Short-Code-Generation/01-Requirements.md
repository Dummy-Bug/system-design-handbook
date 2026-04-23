
> [!info] Before picking a generation strategy, calculate how many unique codes you actually need.
> The math tells you the minimum code length — everything else follows from that.

---

## How Many Unique Codes Do We Need?

From estimation: 1M pastes/day × 3,650 days = 3.65B pastes over 10 years. Add safety margin → call it **5 billion unique codes** needed.

---

## Why Base62?

Short codes appear in URLs — they must be URL-safe and human-readable. Base62 uses:

```
a-z  → 26 chars
A-Z  → 26 chars
0-9  → 10 chars
Total: 62 chars
```

No special characters, no encoding needed in URLs, easy to type and share. Base64 adds `+` and `/` which are not URL-safe without percent-encoding. Base62 is the clean choice.

---

## How Many Characters Do We Need?

Same logic as any number system. In base 10 with N digits you can represent 10^N combinations. In Base62 with N characters you can represent 62^N combinations.

```
1 char → 62^1 = 62
2 chars → 62^2 = 3,844
3 chars → 62^3 = 238,328
4 chars → 62^4 = 14,776,336        (~14 million)
5 chars → 62^5 = 916,132,832       (~900 million)
6 chars → 62^6 = 56,800,235,648    (~56 billion)
```

We need 5 billion unique codes.

```
5 chars → max 900 million  → NOT enough (5B > 900M)
6 chars → max 56 billion   → ENOUGH     (5B < 56B) ✓
```

**6 Base62 characters gives 56 billion combinations — 11× headroom over our 10-year requirement.**

---

## The Binary Intuition

To understand why 6 chars is enough, think in binary first.

In binary, each position has 2 choices (0 or 1). N bits = 2^N combinations.

```
32 bits → 2^32 = 4.3 billion  → not enough for 5B
33 bits → 2^33 = 8.6 billion  → enough
```

In Base62, each position has 62 choices instead of 2. So each Base62 character carries more information than a single bit — roughly log2(62) ≈ 5.95 bits per character.

```
6 Base62 chars ≈ 6 × 5.95 = 35.7 bits of information
2^35.7 ≈ 56 billion combinations ✓
```

This is why 6 chars in Base62 comfortably covers what would take 36 bits in binary.

---

## Final Answer

```
Code length:    6 characters
Alphabet:       Base62 (a-z, A-Z, 0-9)
Combinations:   56 billion
Requirement:    5 billion
Headroom:       11×
```

---

> [!tip] Interview framing
> "We need 5B unique codes over 10 years. 62^6 = 56 billion — 11x headroom. 6 Base62 characters is the minimum safe length. Base62 chosen over Base64 because it's URL-safe with no special characters."
