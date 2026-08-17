The theory note made a promise: whatever format goes into a document loader, the same unified thing comes out — a Document object. Time to watch that promise being kept in code. The knowledge source for this whole module is one directory containing files in different formats — a PDF, a CSV, a JSON, and a text file — and the plan is to load every one of them, starting with the simplest possible case: **the plain text file** 

The text loader is deliberately the first one, because with no structure to parse, nothing distracts from the core API — and that API is **identical** for every loader that follows.

---

## Project setup — one aside before the code

Two practical notes from the course project, so the imports below make sense:

- Everything needed to run the project is listed in **`requirements.txt`**, and the virtual environment is built with **UV** — a (very fast) Python package manager; if you haven't met it, it plays the role pip + venv normally play.
- All the loaders in this module live in the **`langchain_community`** package — community-maintained integrations. Every loader import in this module starts from there.

```python
from pprint import pp
from langchain_community.document_loaders import TextLoader
from pathlib import Path
```

(`pp` is pretty-print — it just formats dictionaries readably, which we'll want for metadata.)

---

## Load a text file

The file is `transformers.txt` — a plain-text explainer about the Transformer architecture, sitting in the knowledge-source folder. First, the habit worth copying: **build the path, then prove it exists** before blaming the loader for anything:

```python
# define the path for the text file
file_path = Path("../knowledge-source/transformers.txt")

print(file_path)
print(file_path.exists())   # True
```

Then the loader. `TextLoader` takes three parameters worth knowing: **`file_path`** (you can pass it as a string **or** as a Path object — both work), **`encoding`**, and **`autodetect_encoding`** for when you don't know the file's encoding:

```python
# define the loader
loader = TextLoader(file_path=file_path)

# load the documents
documents = loader.load()
```

`load()` takes **no input** — and what it returns is the whole theory note come true:

```python
print(type(documents))      # <class 'list'>
print(type(documents[0]))   # <class 'langchain_core.documents.base.Document'>
```

A **list of Document objects** — the unified output format, exactly as promised. Every loader in this module, no matter how different its input, will hand back this same shape.

---

## What came back

For a plain text file, the whole file becomes **one document**:

```python
len(documents)   # 1
```

And the two attributes from the theory note are sitting right there:

```python
extracted_doc = documents[0]

print(extracted_doc.page_content)
# "Transformer models in large language models... the big picture...
#  core building blocks... feed-forward..."   ← the entire file's text

pp(extracted_doc.metadata)
# {'source': '../knowledge-source/transformers.txt'}
```

`page_content` holds the full extracted text. The metadata is minimal — just the source path — and that's honest: a bare text file simply doesn't **have** pages, authors, or creation dates to report. (Keep this in mind for contrast — the PDF loader's metadata will be a different story.)

> [!info] The ritual you just saw is the ritual for **every** loader: **build the path → create the loader → call `.load()` → get a list of Documents.** From here on, only the loader class and its parameters change; the shape of what comes back never does.

Two more things every loader carries, mentioned here once so they're known: alongside `load()` there's **`lazy_load()`** (returns documents one at a time — covered properly in the web-loaders note, where it matters), and **async variants** of both for concurrent code.

---

## And when your format isn't covered here?

This module walks through the five types you'll generally use — **text, PDF, CSV, JSON, and web pages**. But LangChain ships far more loaders than that. Need to load a Microsoft Excel sheet? There's a loader — visit the documentation page, check its parameters, and the pattern is the same: create the loader, call `.load()`, receive Documents. Once you've internalised the ritual above, every loader in the catalogue is the same loader with different knobs.

---
