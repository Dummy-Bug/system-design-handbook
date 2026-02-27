[[04 Base Encodings.pdf]]

## 1. How URLs are actually parsed

A URL is **not a free-form string**. It has structure.

Example:

`https://s.io/a+b/c`

This is parsed as:

|Part|Meaning|
|---|---|
|`https://`|scheme|
|`s.io`|host|
|`/a+b/c`|**path**|

Now here is the key rule:

> In a URL path, the **slash `/` is a separator between path segments**.

So:

`/a+b/c`

means:

- Segment 1: `a+b`
    
- Segment 2: `c`
    

NOT a single identifier.

---

## 2. Why `/` breaks identifiers

Suppose your short code is Base64:

`a+b/c`

And you build a redirect endpoint:

`GET /{shortCode}`

Now the router sees:

`GET /a+b/c`

Routing systems (Spring, Express, Nginx, etc.) interpret this as:

`/{segment1}/{segment2}`

Not:

`/{shortCode}`

So:

- Router fails
    
- Or matches the wrong endpoint
    
- Or requires complex wildcard routing
    

That’s what **“breaks clean path segments”** means.

---

## 3. What about `+` ?

`+` is also problematic, but in a **different way**.

In URLs:

- In query strings, `+` often means **space**
    
- Some frameworks auto-decode it
    

Example:

`/a+b`

May get decoded as:

`"a b"`

Depending on:

- Framework
    
- Middleware
    
- Reverse proxy
    

This causes:

- Inconsistent behavior
    
- Hard-to-debug bugs
    

---

## 4. “But URL encoding fixes it, right?”

Yes, technically.

Base64:

`a+b/c`

URL-encoded:

`a%2Bb%2Fc`

Final URL:

`https://s.io/a%2Bb%2Fc`

Now it works.

But now you’ve created **new problems**:

- URLs are ugly
    
- Users copy/paste encoded strings
    
- QR codes become longer
    
- Verbal sharing becomes impossible
    
- You must encode/decode everywhere correctly
    

You’ve defeated the entire point of a **short URL**.

---

## 5. Why this matters in real systems

URL shorteners rely on:

`GET /{shortCode}`

That only works if `{shortCode}`:

- Is URL-safe
    
- Does not include `/`
    
- Does not require encoding
    

That’s why production systems **never use raw Base64 in paths**.

## 1. The core problem URL encoding solves

URLs were designed to be:

- ASCII
    
- Structured
    
- Safe to transmit over networks
    

But **not every character is allowed everywhere** in a URL.

So the question is:

> What if my data contains characters that the URL syntax already uses?

Answer:

> **Encode them.**

That’s all URL encoding is.

---

## 2. The rule (this is the whole thing)

> **URL encoding replaces unsafe or reserved characters with a safe representation.**

Format:

`%HH`

Where:

- `HH` = hexadecimal ASCII value of the character
    

---

## 3. Concrete examples

### Example 1: Space

Space is not allowed in URLs.

`"hello world"`

Encoded:

`hello%20world`

Because:

- Space ASCII = 32
    
- 32 in hex = `20`
    

---

### Example 2: Slash `/`

Slash has **structural meaning** in URLs.

`/`

Encoded:

`%2F`

Because:

- `/` ASCII = 47
    
- 47 in hex = `2F`
    

---

### Example 3: Plus `+`

Plus is ambiguous.

`+`

Encoded:

`%2B`

## 4. Why this matters for our Base64 example

Base64 short code:

`a+b/c`

If used directly:

`https://s.io/a+b/c`

Parsed as:

`segment: a+b segment: c`

Wrong.

So you **must encode** it:

`a%2Bb%2Fc`

Final URL:

`https://s.io/a%2Bb%2Fc`

Now it is treated as **one string**.

---

## 5. Why this is bad for short URLs

Look at this:

`Original intent: a+b/c Actual URL:      a%2Bb%2Fc`

Problems:

- Longer
    
- Ugly
    
- Non-human
    
- Error-prone
    
- Completely defeats “short URL”