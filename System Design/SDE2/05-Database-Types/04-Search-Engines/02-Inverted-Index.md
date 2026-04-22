## The Key Insight — Flip the Question

A normal database index answers: "Does this document contain this word?"

An inverted index flips the question: "Which documents contain this word?"

This sounds like a small change. The performance difference is enormous.

With a normal approach, to answer "which products mention wireless?" you scan every product. With an inverted index, you look up "wireless" and instantly get the list of documents — like looking up a word in a book's index at the back, instead of reading the entire book.

---

## Building the Index

Say you have 3 product descriptions:

```
Doc 1: "wireless headphones bluetooth"
Doc 2: "noise cancelling headphones"
Doc 3: "wireless earbuds noise"
```

You build a lookup table mapping each word to the list of documents containing it:

```
wireless    → [Doc 1, Doc 3]
headphones  → [Doc 1, Doc 2]
bluetooth   → [Doc 1]
noise       → [Doc 2, Doc 3]
cancelling  → [Doc 2]
earbuds     → [Doc 3]
```

This is the inverted index. Each word is a key. The value is the list of document IDs that contain it.

---

## Answering a Query

User searches **"wireless headphones"**. You look up both words:

```
wireless    → [Doc 1, Doc 3]
headphones  → [Doc 1, Doc 2]
```

Then take the **intersection** — documents that appear in both lists:

```
Doc 1 appears in both → return Doc 1
```

That's the entire lookup. No document scanning. No string comparison across 50 million rows. Just a hash map lookup followed by a set intersection.

> [!info] Why this is fast
> The lookup is O(1) — you go directly to the word in the index. The intersection is proportional to the size of the result lists, not the total document count. Even with 1 billion documents, the lookup time doesn't grow.

Compare this to SQL: O(n) full table scan every time, where n = total rows. The inverted index reduces this to effectively O(1) for the lookup phase.

---

## The "Inverted" Part

The name comes from the direction of the mapping:

```
Normal index:   Document → Words it contains
Inverted index: Word → Documents that contain it
```

It's "inverted" because you've flipped the natural direction. Instead of starting with a document and listing its words, you start with a word and list its documents.

---

## What Gets Stored Per Entry

In practice, each entry in the inverted index stores more than just document IDs. It also stores:

```
wireless → [(Doc1, position: 0), (Doc3, position: 0)]
```

Positions matter for phrase queries — if a user searches "noise cancelling" as a phrase (not just both words anywhere), the index can verify that "noise" appears immediately before "cancelling" in the same document.

This is the core data structure that every search engine — Elasticsearch, Solr, Lucene, Google — is built on.
