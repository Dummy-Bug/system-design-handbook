Every loader so far could decide things for itself: the text loader took the whole file as one document, the PDF loaders took a page, the CSV loader took a row. Now the loader that can't decide anything on its own — the genuinely tricky one: **JSON**.

Why tricky? A text file has one obvious answer to "what's the text?" — the whole file. JSON doesn't. JSON is nested structure: objects inside arrays inside objects, and *you* have to tell the loader which part is the content, which parts are metadata, and what counts as "one document." That's three decisions the other loaders never ask you to make.

---

## The data — a product catalog

The knowledge source here is `apparels.json`, a Zara-style product catalog. Its shape is the thing to stare at:

```json
{
  "products": [
    {
      "productID": "0000001",
      "manufacturer": "Zara",
      "img": "https://static.zara.net/photos/...",
      "Url": "https://www.zara.com/in/en/man-outerwear...",
      "productName": "PINSTRIPE COAT",
      "Description": "Oversize-fit coat made of a viscose blend fabric. Notch lapel collar and long sleeves with buttoned cuffs.",
      "price": 4900,
      "category": "Men Cloths"
    },
    { "...product 2..." },
    { "...product 3..." },
    { "...product 4..." },
    { "...product 5..." }
  ]
}
```

The outer JSON has **one key, `products`, and that key is an array** holding 5 JSON elements — element 1 through 5, one per product.

Now the goal: we want to go *into* that array and load each element as a **separate document** — 5 document objects. Think of the array elements like individual rows inside a CSV file: row 1, row 2, ... row 5, except here the "rows" are listed inside the `products` array. One product = one unit of retrieval — so that a query about coats can match *a product*, not the whole catalog.

---

## Setting up

```python
from langchain_community.document_loaders.json_loader import JSONLoader
from pathlib import Path
from pprint import pp

# create the path for the json file
file_path = Path("../knowledge-source/apparels.json")
file_path.exists()   # True — always worth checking before blaming the loader
```

One dependency worth knowing about before the first run: **`JSONLoader` internally uses the `jq` parser.** The documentation's installation section lists the `jq` package — a small library whose whole purpose is navigating JSON structures with path expressions. That's why the loader's key parameter is called `jq_schema`: it's the instruction telling jq *where inside the JSON to walk*.

---

## Finding the right `jq_schema` — by breaking it twice

The honest way to learn `jq_schema` is the way it happens live: try the obvious thing, read the error, fix, repeat.

**Attempt 1 — point at the array.** A `.` enters the JSON root, so `.products` reaches our array:

```python
loader = JSONLoader(file_path=file_path.as_posix(),   # as_posix() — just to be safe with paths
                    jq_schema=".products")
documents = loader.load()
```

```
Error: Expected page content to be a string, but got a list instead.
```

Of course — `products` *is* an array. The loader tried to stuff the entire list into `page_content`, and `page_content` must be a **string**. The error is the design talking back: one Document holds one text.

**Attempt 2 — iterate the array.** jq's `[]` operator means "each element of":

```python
jq_schema=".products[]"
```

Closer — now the loader visits each of the 5 elements as its own document-to-be. But each element is a JSON **object** — a dictionary with 8 keys — and a dictionary still isn't a string. Which of those keys is *the text*?

**The fix — pick the content key.** For a product, the natural retrieval text is its description. The `content_key` parameter names which field becomes `page_content`:

```python
loader = JSONLoader(file_path=file_path.as_posix(),
                    jq_schema=".products[]",
                    content_key="Description")
documents = loader.load()
```

And now it works — 5 documents, and printing their `page_content` gives exactly the five descriptions:

```
Oversize-fit coat made of a viscose blend fabric...
Trench coat made of technical fabric...
...
```

> [!important] The division of labour: **`jq_schema` decides what counts as one document** (each element of `.products[]`), and **`content_key` decides which field inside it is the text** (`Description`). Get the first wrong and your retrieval granularity is wrong; get the second wrong and you're embedding IDs and URLs instead of meaning.

---

## The metadata problem — and `metadata_func`

Check what a loaded document's metadata looks like by default:

```python
documents[0].metadata
# {'source': '/.../apparels.json', 'seq_num': 1}
```

Just the source file and a sequence number. But look back at the JSON — each product carries far more that we'd want riding along: the product ID, the manufacturer, the image, the URL, the product name, the price, the category. If a retrieved chunk is going to *cite* a product or be *filtered* by category or price, that information has to be in the metadata — and right now the loader is throwing it away.

The fix is the **metadata function**. You define a function with **two inputs** — the `record` (the raw JSON object for this document, all 8 keys of it) and the default `metadata` dict — and it returns the metadata you actually want:

```python
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["product_name"] = record["productName"]
    metadata["category"]     = record["category"]
    metadata["price"]        = record["price"]
    # delete seq num
    del metadata["seq_num"]
    return metadata
```

Two things it demonstrates:

1. **Adding** — pull any field out of the original record and put it into metadata (`product_name`, `category`, `price`).
2. **Deleting** — existing default keys can be removed too. `seq_num` isn't useful here, so `del metadata["seq_num"]` drops it.

Wire it into the loader and the final, complete version reads:

```python
loader = JSONLoader(file_path=file_path.as_posix(),
                    jq_schema=".products[]",
                    content_key="Description",
                    metadata_func=metadata_func)

documents = loader.load()
documents[0].metadata
# {'source': '/.../apparels.json',
#  'product_name': 'PINSTRIPE COAT',
#  'category': 'Men Cloths',
#  'price': 4900}
```

Same 5 documents, same descriptions as `page_content` — but now each one carries curated provenance: its name, category, and price, with the noise removed.

---

## JSON loading in one breath

The JSON loader is tricky because JSON is structure, not text — so you make three calls the loader can't make for you. **`jq_schema`** (powered by the internal jq parser) walks the structure and defines the unit of document — here `.products[]`, each element of the products array, like rows of a CSV. **`content_key`** names the field that becomes the searchable text — the `Description`. **`metadata_func(record, metadata)`** curates what rides along — adding the product name, category, and price from the record, deleting what's useless. Out come 5 clean Document objects from one nested file.

---
