**Unicode** is:

> A universal character identity standard that assigns every character a unique numeric ID.

It does NOT define:

- How characters are stored in memory
- How bytes are transmitted over network
- How files are encoded

Unicode only defines:

> What characters exist and what their identities are.

---

## What Problem Unicode Solves

Before Unicode:

- Different countries used different character encodings
- Same byte values meant different characters
- Data corrupted when crossing systems

Unicode solved this by:

- Creating a single global character identity space
- Ensuring consistent meaning across platforms

---

## Unicode Uses Code Points

Unicode identifies characters using **code points**.

A code point is:

> A unique number assigned to a character.

Examples:

| Character | Code Point |
-----------|------------
A          | U+0041
₹          | U+20B9
你         | U+4F60
😂          | U+1F602

These values are global and platform-independent.

---

## Unicode Is Language-Agnostic

Unicode does not care about:

- English
- Hindi
- Arabic
- Emoji
- Symbols

Everything is treated as:

> Character → Unique ID

This enables:

- Global APIs
- International databases
- Multi-language search systems

---

## Unicode Is Infrastructure, Not Feature

Unicode is similar to:

- TCP/IP for networking
- UTF-8 for web text
- Timezones for timestamps

You don’t “add Unicode support”.

You either design correctly with it — or your system breaks internationally.

---

