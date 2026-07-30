The text loader was one class, because plain text has one way to be read. PDFs are different — and the difference shows up immediately in LangChain's catalogue: **there isn't *a* PDF loader, there's a whole family of them.** The reason is the parser underneath. PDF is a notoriously messy format — text, images, tables, fonts, layouts all packed together — and different parsers attack it with **different unique advantages**: some are fast, some can parse the images, some give you far more detailed metadata. So the real skill isn't "the PDF loader API"; it's knowing **which PDF loader to reach for**.

This note works through three of them — **PyPDF**, **PDFMiner**, and **PDFPlumber** — on a document chosen to stress-test all three:

```python
from langchain_community.document_loaders.pdf import PyPDFLoader
from pathlib import Path
from pprint import pp

# create the path for pdf file
file_path = Path("../knowledge-source/attention_is_all_you_need.pdf")
file_path.exists()   # True
```

*Attention Is All You Need* — the Transformer paper itself: 15 pages, and crucially it contains **figures** (the famous architecture diagram) and **tables** (results tables). Plain text, image text, tabular data — one file, all three challenges.

---

## PyPDFLoader — the straightforward one

```python
# create a loader
pypdf_loader = PyPDFLoader(file_path=file_path.as_posix(),
                           mode='page')

documents = pypdf_loader.load()
len(documents)   # 15
```

Two things to unpack.

**The `mode` parameter.** This tells the loader *how* to load the document: `'page'` loads it **page by page** — every page becomes its own Document object — while `'single'` loads the entire PDF as **one** Document. Page mode is what we want (and it's PyPDF's default): 15 pages in, 15 documents out, and the page instantly becomes the natural unit of retrieval.

**The metadata got serious.** Compare this to the text loader's lonely `source` key:

```python
pp(documents[0].metadata)
# {'producer': ..., 'creator': ..., 'creationdate': ...,
#  'source': '../knowledge-source/attention_is_all_you_need.pdf',
#  'total_pages': 15, 'page': 0, 'page_label': '1'}
```

Producer, creator, creation date, the source path, the total page count, and *this document's* position in the file. A PDF simply knows more about itself than a text file does, and the loader passes all of it through — this is the metadata that later powers source attribution ("that answer came from page 3 of the Attention paper").

> [!important] Note the off-by-one hiding in plain sight: **`page` is a 0-based index, `page_label` is the human-readable page number** — so the document with `page: 1` carries `page_label: '2'`. When you filter by page later, be sure which one you're using.

Printing `documents[1].page_content` dumps the full text of page 2 — the extraction itself just works.

---

## The image problem — where PyPDF hits its ceiling

Look closely at the paper, though: page 3 contains the architecture **figure** — and the words inside that figure (*Softmax*, *Feed Forward*, *Add & Norm*...) live in an *image*, not in the PDF's text layer. A plain text extraction never sees them.

Reading text out of an image is **OCR** — optical character recognition — and LangChain wires it in through an **images parser**:

```python
from langchain_community.document_loaders.parsers import TesseractBlobParser, RapidOCRBlobParser

# create pypdf instance which can extract images
pypdf_image_loader = PyPDFLoader(file_path=file_path.as_posix(),
                                 mode="page",
                                 extract_images=True,
                                 images_parser=RapidOCRBlobParser(),
                                 images_inner_format="html-img")

documents_with_images = pypdf_image_loader.load()
```

Three new parameters: **`extract_images=True`** switches the behaviour on; **`images_parser`** picks the OCR engine (two are imported here — Tesseract-based and RapidOCR; RapidOCR needs zero configuration, so that's the one used); and **`images_inner_format`** — hold that thought for a moment.

Now the test — the figure is on page 3, so check the tail of that document's content:

```python
page_with_image = documents_with_images[2]
print(page_with_image.page_content[-700:])
```

...and the image text **isn't there**. The PDF's ordinary text is all present, but nothing from the figure. This is the honest lesson of the section:

> [!danger] PyPDF *documents* the image-extraction functionality, but in practice it doesn't work properly — the figures' text never made it into the output. If you need data out of images inside a PDF, you need a more advanced loader. That's not a bug in your code; it's the parser's ceiling — and the reason the PDF loader family exists at all.

---

## PDFMinerLoader — the advanced one: images and tables

PDFMiner's feature list is exactly what we're missing: it supports lazy loading, and it can extract **images** *and* **tables**. Same construction, same parameters:

```python
from langchain_community.document_loaders import PDFMinerLoader

# create the miner loader
pdfminer_loader = PDFMinerLoader(file_path=file_path.as_posix(),
                                 mode="page",
                                 extract_images=True,
                                 images_parser=RapidOCRBlobParser(),
                                 images_inner_format="html-img")

documents_with_images = pdfminer_loader.load()
```

One trap in there: **PDFMiner's default `mode` is `'single'`** — the opposite of PyPDF's default. Forget to set `mode="page"` and you'll silently get one giant document instead of fifteen. (Also: this load takes noticeably longer — OCR is real compute, and it runs on every image in the file.)

The verdict, again on the figure page:

```python
# image text in pdf
print(documents_with_images[2].page_content[-450:])
```

And this time it's all there — the architecture diagram's labels, extracted from the image by OCR:

```
<img alt="Output Probabilities  Softmax  Linear  Add & Norm
Feed Forward  ..." />
```

The figure's text — *Output Probabilities, Softmax, Linear, Add & Norm, Feed Forward* — is now part of `page_content`, which means it's embeddable and retrievable like any other text. A query about "softmax layers in the Transformer architecture" can now actually reach this page.

### Why `images_inner_format="html-img"`?

Notice the OCR text arrived wrapped in an HTML `<img>` tag. That's the `images_inner_format` parameter: it controls the wrapper that marks image-extracted text inside the output. The alternative is `"markdown-img"`, which wraps the same text in Markdown image syntax instead — run it and the output looks different only in the wrapping.

The lecture's recommendation: **prefer HTML.** The reasoning is sharp: a PDF's ordinary text can easily contain characters that *look like* Markdown syntax (asterisks, brackets, dashes — they occur naturally in prose), but ordinary PDF text never contains HTML tags. So an HTML wrapper lets you **unambiguously tell image-extracted text apart** from the surrounding real text; a Markdown wrapper can blur into the document.

### Tables too

The paper's **Table 1** sits on page 6. Check that document:

```python
# text from table
print(documents_with_images[5].page_content)
```

The table's data is extracted as text — and it appears **in place**, exactly where the table sits within the page's content, not dumped somewhere separate. Structured results data, now retrievable.

### Metadata as a search key

With page-wise documents and rich metadata, finding a specific page becomes a filter:

```python
for doc in documents_with_images:
    if doc.metadata["page"] == 7:
        print(doc.page_content)
        break
```

Loop the documents, match on a metadata field, stop at the hit. Trivial code — but it's the first taste of a big later idea: **metadata isn't decoration, it's a query surface.**

---

## PDFPlumberLoader — the metadata specialist

The third member of the family, and the simplest to construct:

```python
from langchain_community.document_loaders import PDFPlumberLoader

# create the loader
plumber_loader = PDFPlumberLoader(file_path=file_path.as_posix())

documents_with_metadata = plumber_loader.load()
len(documents_with_metadata)          # 15 — page-wise again
print(documents_with_metadata[1].page_content)
pp(documents_with_metadata[0].metadata)
```

Its text extraction is solid, but its distinguishing edge is in that last line: PDFPlumber returns **notably more detailed metadata** than the other two — the fullest picture of the document's properties. When your downstream logic leans on metadata (filtering, attribution, auditing what you ingested), this is the specialist.

---

## Choosing between them

| | **PyPDF** | **PDFMiner** | **PDFPlumber** |
|---|---|---|---|
| Text extraction | ✅ fast, reliable | ✅ | ✅ |
| Images (OCR) | documented but doesn't work properly | ✅ works | — |
| Tables | — | ✅ extracted in place | — |
| Metadata | standard PDF fields | standard | **most detailed** |
| Default `mode` | `page` | `single` — set `page` yourself | per-page |

> [!tip] The interview-ready framing: "PDF loading isn't one problem, it's three — text, images, tables — and LangChain's PDF loaders are parsers with different specialties. PyPDF for plain text page-by-page; PDFMiner when figures and tables must become retrievable text via OCR; PDFPlumber when I want the richest metadata. Load page-wise, and mind that `page` is 0-indexed while `page_label` is the printed number."

---
