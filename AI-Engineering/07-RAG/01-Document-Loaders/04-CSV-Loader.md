Text files loaded as one whole document. PDFs loaded page by page. Now tabular data — and with it, the question every loader has to answer differently: **what counts as one document here?**

The knowledge source is `organizations.csv` — a table of **1,000 rows**, one organization per row, with columns like:

```
Index, Organization Id, Name, Website, Country, Description, Founded, Industry, Number of employees
```

For the theory-note refresher: a CSV's structure is a **header row** naming the columns, then comma-separated value rows beneath it. The parser's job is to understand that structure — every value only means something **under its header**.

---

## Row = document

```python
from langchain_community.document_loaders.csv_loader import CSVLoader
from pathlib import Path
from pprint import pp

# define the path to csv file
file_path = Path("../knowledge-source/organizations.csv")
print(file_path.exists())   # True

loader = CSVLoader(file_path=file_path)
documents = loader.load()
len(documents)   # 1000
```

**The number of documents equals the number of rows.** Each Document object is one row of the CSV — 1,000 rows in the file, 1,000 documents in the list. That's the CSV loader's answer to the unit-of-document question, and it lines up with everything so far:

```
Text loader:  1 file  → 1 document      (the whole file is the unit)
PDF loader:   1 file  → 15 documents    (the page is the unit)
CSV loader:   1 file  → 1000 documents  (the row is the unit)
```

By default, a row-document's `page_content` is the entire row spelled out as `column: value` lines — every column, including the IDs and index numbers.

---

## The problem with every column — and the three tuning knobs

Think about what happens downstream. That `page_content` is headed for an **embedding model**, which captures **meaning**. What's the semantic meaning of `Index: 7` or `Organization Id: 8cC6B5992c3F5ba`? Noise. The only column with real **meaning** in this table is the **Description**. Meanwhile columns like the website or the founding year are genuinely useful — but as **facts about the row**, not as searchable text. That's precisely the text-vs-metadata split, and `CSVLoader` gives you a knob for each side:

```python
# create the csv loader
loader = CSVLoader(file_path=file_path,
                   source_column="Industry",
                   metadata_columns=["Website", "Founded", "Number of employees"],
                   content_columns=["Description"])

documents = loader.load()
```

- **`content_columns`** — which columns become the `page_content`. Here, only `Description`: the one column whose text has meaning worth embedding. (Same instinct as `content_key` in the JSON loader.)
- **`metadata_columns`** — which columns ride along in `metadata` instead: the website, the founding year, the employee count. Not searchable text — but available for attribution and filtering after retrieval.
- **`source_column`** — which column fills the `source` field of the metadata. By default source would be the file path — the same value for all 1,000 documents. Pointing it at a column (here `Industry`) gives each row-document its own, more meaningful source label.

The result, per document:

```python
print(documents[0].page_content)
# Description: <the organization's description text>

pp(documents[0].metadata)
# {'source': <its Industry value>, 'row': 0,
#  'Website': ..., 'Founded': ..., 'Number of employees': ...}
```

Clean split: meaning in the content, facts in the metadata.

> [!important] With tabular data, the loader configuration **is** the retrieval design. Dump all columns into `page_content` and your embeddings are polluted with IDs and URLs; split them deliberately — meaningful text into content, useful facts into metadata — and both retrieval and attribution get sharper. The CSV loader just makes you say the split out loud.

---
