#rag #embeddings #vector-search #semantic-search #similarity

---

# How Do You Search for Meaning, Not Just Keywords?

You want to find documents about "employee time off." Your document says "staff are entitled to 18 days of annual leave." Not a single word overlaps. A keyword search returns nothing. So how do you find it?

---

## Why Keyword Search Fails for Meaning

ElasticSearch, SQL `LIKE`, grep — all of these look for matching characters. They work on bags of words, TF-IDF scores, term frequency. They are asking: *does this word appear here?*

They are not asking: *does this sentence mean the same thing?*

"the student has a book" and "a book has the student" — a keyword engine treats these as nearly identical (same words). But "absent from class" and "missed school session" — it treats these as completely different (no shared words).

> [!danger] Keyword search matches characters. It cannot match concepts. Two sentences can mean the same thing with zero overlapping words.

---

## What If You Could Represent Meaning as Numbers?

Think of describing a person with numbers:

- Height: 6ft → 1.82
- Age: 25
- Experience: 8 years

That's just data about something, expressed as a list of numbers. Now what if you could describe the *meaning* of a sentence the same way — as a list of numbers where similar meanings produce similar numbers?

That's an **embedding**.

---

## What Is an Embedding?

An embedding model takes a sentence and outputs a fixed-length list of numbers — a **vector**. The model is trained so that sentences with similar meanings produce vectors with similar numbers.

```
"I love dogs"        → [0.21, 0.79, 0.11, 0.88, ...]
"I adore puppies"    → [0.20, 0.81, 0.10, 0.87, ...]   ← very close

"Stock market crash" → [0.91, 0.12, 0.73, 0.20, ...]   ← very different
```

One vector per sentence — not one per word. The model reads the whole sentence and outputs a single list capturing its overall meaning.

> [!info] You don't produce embeddings manually. A pre-trained embedding model does it. You pass text in, a vector comes out. Models like `text-embedding-ada-002` (OpenAI) or `sentence-transformers` (open source) are trained specifically for this.

---

## What Comes Next?

You now have vectors that represent meaning. The next question is: how do you store them so they can be searched efficiently at scale? That's covered in the next file — building a vector index.

---

## Mental Model To Remember

> [!info] Embeddings are meaning compressed into numbers. A vector DB is a library where books are shelved by meaning, not title. Ask a question, get back the shelf closest to what you meant — regardless of which exact words you used.
