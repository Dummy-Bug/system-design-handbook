Every loader so far assumed the same thing: the knowledge source is a **local file** — something sitting on your disk. But that's not always true. Plenty of real knowledge lives as **web pages**: documentation sites, product pages, wikis. No file to point a path at — just a URL. LangChain covers this with two loaders, and along the way we'll meet a distinction that applies to **every** loader: `load()` versus `lazy_load()`.

---

## WebBaseLoader — one page (or a few) by URL

A web page is HTML — and from the theory note you already know what that means: text buried inside a structure of tags, waiting for a **specialized parser** that understands that structure. For HTML, the parser is **BeautifulSoup** (installed as the `bs4` package — it's in the project's requirements for exactly this reason). The `WebBaseLoader` wraps it: give it a URL, it fetches the page, hands the HTML to BeautifulSoup, and out comes the extracted text content as a Document.

```python
from langchain_community.document_loaders import WebBaseLoader
from pprint import pp

loader = WebBaseLoader(web_paths=["https://docs.langchain.com/..."])
documents = loader.load()
```

One URL in → one document out: `page_content` is the page's text, and the metadata tells you where it came from:

```python
pp(documents[0].metadata)
# source   → the URL of the document
# title    → the page title
# language → the language of the page
```

And because `web_paths` is a list, several pages load in one shot. Here, three pages from LangChain's own documentation — the doc pages for three different PDF loaders:

```python
url_1 = "https://docs.langchain.com/oss/python/integrations/document_loaders/pypdfloader"
url_2 = "https://docs.langchain.com/oss/python/integrations/document_loaders/pdfminer"
url_3 = "https://docs.langchain.com/oss/python/integrations/document_loaders/pdfplumber"

loader = WebBaseLoader(web_paths=[url_1, url_2, url_3])
documents = loader.load()
len(documents)   # 3 — one Document per URL, each with its own source/title/language
```

Notice the URL pattern, because it sets up the next idea: all three are **children of the same page** — the base `document_loaders` documentation page, followed by the loader's name. Which raises the obvious question...

---

## RecursiveUrlLoader — a page and everything it links to

What if you want that entire documentation section? The base page, plus every child page it links to? With `WebBaseLoader` you'd have to collect every child URL yourself and pass the whole list — you can't do it independently. For this, LangChain has a specialized loader: the **`RecursiveUrlLoader`**.

Its job: scrape the URL you give it — and then **recursively scrape the child links** found on that page, loading each page as its own Document.

```python
from langchain_community.document_loaders import RecursiveUrlLoader

base_url = "https://docs.langchain.com/oss/python/integrations/document_loaders"

loader = RecursiveUrlLoader(url=base_url,
                            max_depth=2)   # base page + one level of children

documents = loader.load()
len(documents)   # 222
```

**222 documents from one URL.** Loop over the first few and print their metadata and the crawl becomes visible:

```python
for i in range(10):
    doc = documents[i]
    pp(doc.metadata)
    print()
```

The first document is the base page itself — the document-loaders index — with `content_type: text/html`, `charset: utf-8`, the page title, and the language. Then come the child links it found: the source-code page, Azure AI Data, Ollama, LakeFS, Markdown, even a `sitemap.xml` and the site's Twitter link — every page reachable one hop from the base, each as a Document with `page_content` (the full HTML text content) and its own metadata.

> [!info] `max_depth` is the recursion leash. Depth 2 means **the base page plus pages it links to.** Raise it and the crawler follows links-of-links — the document count (and load time) grows fast.

---

## The catch — and the `load()` vs `lazy_load()` distinction

Loading those 222 documents surfaced two problems worth taking seriously:

1. **It took ~6 minutes.** And `load()` is all-or-nothing — you stare at a blocked cell for six minutes before you can touch even the **first** document.
2. **Everything landed in memory at once.** `load()` returns a **list** of Documents — all 222 page contents plus metadata, held in memory simultaneously, whether you need them all right now or not.

For 222 documents that's tolerable. Scale the same pattern to thousands of pages and it's neither fast to start nor kind to memory.

That's why every LangChain loader offers a second method: **`lazy_load()`**.

```python
documents_lazy_load = loader.lazy_load()
documents_lazy_load
# <generator object ...>
```

No list — a **generator object**. (A generator is a function that uses `yield` instead of `return`: rather than computing everything and handing it back at once, it produces values **one at a time**, each time the loop asks for the next one.) Nothing has been fetched yet; each document is loaded into memory **only when the iteration reaches it**:

```python
counter = 0

for document in documents_lazy_load:
    # stop condition
    if counter == 20:
        break

    # increment the counter
    counter += 1

    # print metadata and page content
    print(document.page_content[0:300])
    pp(document.metadata)
```

This runs **immediately** — no six-minute wait, because nothing is loaded up front. Documents arrive one by one, get processed one at a time, and only ever one sits in memory. The stop condition even means pages 21–222 are **never fetched at all**.

```
load()      →  [doc1, doc2, ... doc222]     all at once: 6-min wait, all in memory
lazy_load() →  generator                    one at a time: starts instantly, one in memory
```

> [!important] The difference in one line: **`load()` loads every document object into memory at once and returns a list; `lazy_load()` returns a generator, and you loop through it, loading documents into memory one by one.** Same documents either way — the difference is **when** they're materialised. For a handful of files, `load()` is fine. For big crawls or bulk ingestion, `lazy_load()` saves memory and lets processing start on document 1 while document 222 hasn't even been fetched.

---

## Web loading in one breath

When the knowledge source is a URL instead of a file: **`WebBaseLoader`** fetches one or more pages (`web_paths` list) and extracts their text through BeautifulSoup — metadata carries the source URL, title, and language. **`RecursiveUrlLoader`** takes a base URL and recursively loads its child links too — one URL became 222 Documents here, with `max_depth` controlling how far it follows. And when a load is that big, **`lazy_load()`** replaces the all-at-once list with a generator that yields Documents one at a time — instant start, minimal memory.

---

