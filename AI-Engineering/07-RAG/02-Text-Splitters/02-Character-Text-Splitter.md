The simplest possible answer to **where do I cut a large text?** is: **count characters and cut when you hit a number.** No understanding of the text, no analysis of its structure — just a ruler. That strategy is called **length-based splitting**, and LangChain implements it as `CharacterTextSplitter`.

It's worth learning first for two reasons: it introduces every parameter (`chunk_size`, `separator`, `chunk_overlap`) that all the smarter splitters also use, and its **failures** are exactly what motivate those smarter splitters.

---

## The idea — a ruler, not a reader

Length-based splitting measures the text and cuts at a fixed length. The length itself can be counted two ways:

- **Characters** — count letters one by one; cut every N characters.
- **Tokens** — count the way the LLM itself counts (more on this below); cut every N tokens.

Take character counting with a limit of 100. The splitter starts at the first character, counts to 100, and cuts. Then it starts from character 101, counts another 100, cuts again. And so on to the end of the text. That's the entire algorithm — which is precisely why it's fast, and precisely why it's crude.

Two parameters control the behaviour:

**`chunk_size`** — the maximum size of each chunk. It's a **ceiling**, not an exact size: chunks are allowed to come out smaller, but should not exceed it.

**`separator`** — **where** cuts are allowed to happen. This is the interesting one:

- `separator=""` (empty) — cut anywhere, even mid-word. Pure character counting.
- `separator=" "` (space) — only cut at word boundaries.
- `separator="\n"` — only cut at line breaks.
- `separator="\n\n"` — only cut between paragraphs.

When a separator is set, the splitter won't blindly cut at character 100. If the chunk is approaching its limit and a separator appears **before** the limit, the cut happens there — early — so the chunk stays within `chunk_size` without breaking a word or line in half. A chunk with limit 100 might come out at 92 or 95 characters because that's where the last clean boundary was.

---

## Setup

The splitters live in their own package — `langchain-text-splitters` — installed separately alongside `langchain` and `langchain-core` (in the course project it's listed in `requirements.txt`, with the virtual environment built using UV):

```python
from langchain_text_splitters import CharacterTextSplitter
```

The demo text is a passage about AI — three paragraphs, each with three sentences, covering machine learning, NLP/computer vision, and AI's industry impact:

```python
text = """Artificial intelligence is transforming technology and shaping the future.
Machine learning algorithms are becoming more sophisticated every day.
Deep learning models can now process vast amounts of data efficiently.

Natural language processing has made significant strides in recent years.
Computer vision systems can now identify objects with remarkable accuracy.
Reinforcement learning is enabling robots to learn complex tasks autonomously.

The impact of AI extends across multiple industries including healthcare, finance, and transportation.
Ethical considerations around AI development are becoming increasingly important.
Researchers are working on making AI systems more transparent and explainable."""
```

Create the splitter and split:

```python
splitter = CharacterTextSplitter(
    chunk_size=100,        # max 100 characters per chunk
    chunk_overlap=0,       # no overlap (for now)
    length_function=len,   # how to measure length — len() = character count
    separator=""           # cut anywhere
)

chunks = splitter.split_text(text)
```

`split_text` takes a plain string and returns a **list of strings** — the chunks.

To actually **see** the chunks, the course builds a small display helper that prints each chunk in a random colour (using the `termcolor` package) so the boundaries are visible at a glance:

```python
from termcolor import COLORS, colored
from random import choice

def display_chunks(chunks):
    colors_list = list(COLORS.keys())[2:8]
    print(f"Total Number of Chunks: {len(chunks)}")
    for num, chunk in enumerate(chunks, 1):
        print(f"Chunk {num}: Length {len(chunk)} chars")
        print(colored(text=chunk, color=choice(colors_list)), end="\n\n")
```

And since we're about to re-run the splitter with many different settings, a second helper wraps creation + splitting into one call:

```python
def create_chunks(text: str, chunk_size: int,
                  separator: str, chunk_overlap: int = 0) -> list[str]:
    splitter = CharacterTextSplitter(chunk_size=chunk_size,
                                     chunk_overlap=chunk_overlap,
                                     separator=separator)
    return splitter.split_text(text=text)
```

---

## Experiment 1 — cut anywhere (`separator=""`)

```python
display_chunks(create_chunks(text, 100, ""))
```

Eight chunks, and almost every one is **exactly** 100 characters — the ruler at work. But look at where the cuts landed:

```
Chunk 1 (100 chars): "...Machine learning algorith"
Chunk 2 (100 chars): "ms are becoming more sophisticated..."
```

The word **algorithms is sliced in half** — `algorith` ends chunk 1, `ms` begins chunk 2. The splitter doesn't know what a word is; character 100 fell mid-word, so that's where the knife came down.

Increase the chunk size and the number of chunks drops proportionally — `create_chunks(text, 300, "")` produces just 3 chunks (300, 299, and 110 characters) — but the mid-word slicing remains. Size changes; behaviour doesn't.

---

## Experiment 2 — respect word boundaries (`separator=" "`)

```python
display_chunks(create_chunks(text, 100, " "))
```

Again 8 chunks — but now the lengths read 91, 95, 96, 95, 97, 100, 96, 33. No chunk exceeds 100, and no word is ever broken: when the next word wouldn't fit inside the 100-character ceiling, the splitter cut **early** at the last space. A chunk of 92 characters isn't a bug — it's the splitter refusing to breach the limit mid-word.

This is the general contract: **`chunk_size` is a ceiling the splitter tries to fill, and `separator` decides which cut points are legal.** With a fine-grained separator (space), there's always a legal cut point near the limit, so chunks stay close to — but under — the ceiling. The sizes become **predictable**.

---

## Experiment 3 — respect paragraphs (`separator="\n\n"`) — and a trap

```python
display_chunks(create_chunks(text, 100, "\n\n"))
```

Now something odd happens. Three chunks — one per paragraph — with lengths **216, 227, and 263 characters**. Every single one blows past the `chunk_size` of 100, and the library says so out loud:

```
Created a chunk of size 216, which is longer than the specified 100
```

> [!danger] `CharacterTextSplitter` can only cut at its separator — it has no fallback. If you say **only cut between paragraphs** and a paragraph is 216 characters long, there is no legal cut inside it, so you get a 216-character chunk and a warning. With a coarse separator, `chunk_size` becomes a wish, not a guarantee. Remember this failure — it is exactly the problem the **recursive** splitter (next note) is built to solve.

---

## Chunk overlap — don't let the cut erase the context

Even with word boundaries respected, every cut has a cost: the sentence that got split across two chunks loses its flow. Chunk 2 begins mid-thought — **algorithms are becoming more sophisticated…** — **whose** algorithms? That information lives at the end of chunk 1, and after embedding, the two chunks are separate entries in the knowledge base that know nothing about each other. The continuity of meaning is broken at every boundary.

**`chunk_overlap`** is the compensation: the last N characters of each chunk are **repeated** at the start of the next chunk, so every chunk carries a bit of the context it was cut away from.

```python
display_chunks(create_chunks(text, 100, "", chunk_overlap=20))
```

With `chunk_size=100, chunk_overlap=20`:

```
Chunk 1: "...shaping the future.\nMachine learning algorith"
Chunk 2: "ne learning algorith" + "ms are becoming more sophisticated..."
          └── repeated from chunk 1 ──┘
```

Chunk 2 now **starts** with the tail of chunk 1 — the broken word and its surroundings appear whole inside chunk 2. Nothing falls into the gap between chunks, because the chunks share their edges. (The course visualises this with a `display_chunks_with_overlaps` helper that prints the overlapping text in white at the end of one chunk and the start of the next — the shared region is literally visible on screen.)

The cost is honest: repeated text means more total characters stored and embedded — with overlap 20 the same text produced 9 chunks instead of 8. That's why overlap is kept small.

> [!tip] The working rule of thumb: set `chunk_overlap` to about **10–20% of `chunk_size`**. Enough shared edge to preserve continuity across cuts, not so much that you're paying to embed the same text twice.

---

## Token-based splitting — counting the way the model counts

Characters are **our** unit of text. LLMs don't read characters — they read **tokens**, the sub-word units the model's tokenizer produces (a token is roughly ¾ of an English word on average). The context window itself is defined in tokens. So if the whole point of `chunk_size` is **stay safely inside the model's limits,** counting tokens is the more truthful measurement than counting characters.

`CharacterTextSplitter` supports this — but not through the normal constructor. You create it through a **classmethod**, `from_tiktoken_encoder`, which wires in OpenAI's `tiktoken` tokenizer as the length function:

```python
token_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",   # the tokenizer to count with
    chunk_size=50,                 # now measured in TOKENS, not characters
    chunk_overlap=5
)

token_splitter.split_text(text)
```

Same class, same splitting mechanics — the only thing that changed is the ruler: length is now `50` **tokens**. On the demo text this produces 3 chunks (the default separator here is `"\n\n"`, so the cuts land between paragraphs, and each paragraph is comfortably under 50 tokens).

---

## `split_text` vs `split_documents`

Everything so far used `split_text`: **string in, list of strings out.** But the pipeline doesn't hand you strings — the document loaders from the previous module hand you **Document objects**, with `page_content` **and** `metadata`. Feed those through `split_text` and the metadata is gone.

Every splitter therefore has a second method — `split_documents`: **list of Documents in, list of Documents out**, where each output chunk is itself a Document that **keeps the metadata of the Document it was cut from**:

```python
from langchain_core.documents import Document

docs = [Document(
    page_content=text,
    metadata={"source": "Text on AI"}
)]

splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=20, separator="")
chunks = splitter.split_documents(docs)

chunks[0]
# Document(metadata={'source': 'Text on AI'},
#          page_content='Artificial intelligence is transforming...')
chunks[1]
# Document(metadata={'source': 'Text on AI'},
#          page_content='ne learning algorithms are becoming...')
```

Every chunk still knows it came from `"Text on AI"`. This matters downstream: when a retrieved chunk needs to cite its source, the metadata is how it does so.

```
split_text:       str             →  list[str]
split_documents:  list[Document]  →  list[Document]   (metadata preserved)
```

In a real pipeline — loader output going in — `split_documents` is the one you'll use.

---

## The verdict on length-based splitting

**What it does well:**

- **Simple** — the whole strategy is **count and cut.** Nothing to configure beyond a number and a separator.
- **Predictable chunk sizes** — with a fine separator, every chunk lands close to `chunk_size`. When you're budgeting context space, that predictability is genuinely useful.
- **Fast** — no analysis of the text at all. And because chunk boundaries depend only on counting, the chunks are independent of each other: chunk 2 doesn't need chunk 1 to exist first, so chunking can even run in parallel.

**Where it fails:**

- **It breaks words and sentences mid-flow.** An LLM handed the fragment `ms are becoming more sophisticated` has lost the first half of both the word and the thought. Every mid-stream cut destroys semantic continuity — overlap softens this but doesn't cure it.
- **It's blind to document structure.** Real documents have organisation: paragraphs about different topics, sections, chapters. Our demo text discusses machine learning in paragraph 1, NLP and computer vision in paragraph 2, industry impact in paragraph 3 — and the character splitter happily welds the end of one topic to the start of the next in a single chunk. Scale that up: in a school textbook, a pure character count would merge the last page of the physics chapter with the first page of the chemistry chapter into one chunk. One vector, two unrelated meanings — a bad match for any query about either.

> [!important] Length-based splitting optimises for **size** and ignores **meaning**. The chunks are the right shape and the wrong content. The fix is a splitter that respects the document's own structure — paragraphs first, sentences next, words only as a last resort — which is exactly what the recursive character text splitter does, in the next note.
