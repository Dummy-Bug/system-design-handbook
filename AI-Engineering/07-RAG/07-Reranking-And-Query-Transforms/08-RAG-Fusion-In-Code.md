There is no `RAGFusionRetriever` in LangChain to import. RAG Fusion is a pattern, not a class, so the implementation here is a hand-written `RAGFusion` class in a plain Python file — which is the right way to meet it, because every piece is visible.

The class is built to fuse in **two different ways**.

![[AI-Engineering/07-RAG/07-Reranking-And-Query-Transforms/Images/20-Two-Ways-To-Fuse.png]]

- **① Query → rephrased sub-queries.** One retriever, several queries. This is RAG Fusion as described so far.
- **② Ensemble retriever.** Several *retrievers*, one query. LangChain's `EnsembleRetriever` runs them in parallel and merges — and **it already fuses with RRF internally**.

Same fusion idea, two different things being fused: several *queries* against one retriever, or one *query* against several retrievers.

---

## Setup

```python
import logging, os
from langchain_core.documents import Document
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables.base import Runnable
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_fusion.log")

logger = logging.getLogger("rag_fusion_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    _file_handler = logging.FileHandler(_log_path)
    _file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_file_handler)
```

> [!info] The logging is not decoration. RAG Fusion is a multi-stage process whose output is several steps removed from its input — when three documents come back you cannot tell by looking whether the sub-queries were sensible, which run retrieved what, or how the scores accumulated. The log records the generated sub-queries, the documents retrieved per sub-query, and the final RRF scores, which makes *"why did I get these three?"* an answerable question.

Sub-queries are requested as structured output, so a list comes back rather than prose to parse:

```python
class SubQuerySchema(BaseModel):
    sub_queries: list[str] = Field(..., description="List of sub-queries to be generated from the main query.")
```

---

## The two constructors

```python
class RAGFusion:
    def __init__(self, retriever, llm_chain=None, num_subqueries: int = 3, k: int = 5):
        self.retriever = retriever
        self.llm_chain = llm_chain
        self.num_subqueries = num_subqueries
        self.k = k
```

### `from_llm` — fuse across sub-queries

```python
@classmethod
def from_llm(cls, llm, retriever: BaseRetriever, num_subqueries: int = 3, k: int = 5):
    prompt = ChatPromptTemplate(
        messages=[
            ("system", "You are a helpful assistant that generates sub-queries from a main query to enhance retrieval."),
            ("user", "Given the main query: '{main_query}', generate {num_subqueries} sub-queries that can be used to retrieve relevant documents.")
        ],
        input_variables=["main_query", "num_subqueries"]
    )
    structured_llm = llm.with_structured_output(SubQuerySchema)
    llm_chain = prompt | structured_llm
    return cls(retriever=retriever, llm_chain=llm_chain, num_subqueries=num_subqueries, k=k)
```

### `from_retrievers` — fuse across retrievers

```python
@classmethod
def from_retrievers(cls, base_retrievers: list[BaseRetriever], weights=None, k: int = 5):
    if not base_retrievers:
        raise ValueError("At least one retriever must be provided.")
    ensemble = EnsembleRetriever(retrievers=base_retrievers, weights=weights)
    return cls(retriever=ensemble, k=k)
```

Note what this one does **not** set: `llm_chain` stays `None`. That turns out to matter enormously.

---

## `invoke` — and the branch that decides everything

```python
def invoke(self, query: str) -> list[Document]:
    if self.llm_chain:
        sub_queries = self._generate_subqueries(query)
        all_retrieved_docs = [self._retrieve_documents(sub_query) for sub_query in sub_queries]
        fused_docs = self._reciprocal_rank_fusion(all_retrieved_docs)
        return fused_docs[:self.k]
    else:
        return self._retrieve_documents(query)[:self.k]
```

> [!warning] **The hand-written RRF only runs on the `from_llm` path.** Build the object with `from_retrievers` and `llm_chain` is `None`, so `invoke` takes the `else` branch — it calls the `EnsembleRetriever` once and slices. `_reciprocal_rank_fusion` is never reached.
>
> This is not a bug. `EnsembleRetriever` performs RRF itself, so fusion still happens — just inside LangChain rather than in this file. But it means **one class contains two different RRF implementations**, and which one executes depends on the constructor you called. Reading `_reciprocal_rank_fusion` and assuming it governs both paths is the easy mistake here.

---

## The RRF implementation

```python
def _reciprocal_rank_fusion(self, retrieved_docs: list[list[Document]]) -> list[Document]:
    doc_scores: dict[str, tuple[float, Document]] = {}   # {"doc_text": (rrf_score, doc_object)}

    for retrieved_set in retrieved_docs:
        for rank, doc in enumerate(retrieved_set, start=1):
            rrf_score = 1.0 / (rank + 60)
            key = doc.page_content

            if key in doc_scores:
                prev_score, prev_doc = doc_scores[key]
                doc_scores[key] = (prev_score + rrf_score, prev_doc)
            else:
                doc_scores[key] = (rrf_score, doc)

    docs_with_scores = doc_scores.values()
    sorted_docs = sorted(docs_with_scores, key=lambda x: x[0], reverse=True)
    logger.info(f"RRF Scores with documents: {docs_with_scores}")
    return [doc for _, doc in sorted_docs]
```

Fifteen lines, and it is exactly the formula from the previous note. Three details worth pausing on:

**`enumerate(..., start=1)`.** Ranks are 1-based. Starting at 0 would make the first document `1/60` instead of `1/61` — a small distortion, but it would also make rank-0 and rank-1 differ by more than any other adjacent pair.

**The dictionary is keyed on `doc.page_content`.** Same reasoning as the custom multi-query retriever: each retrieval run is a separate call, so the same chunk comes back as **distinct Python objects**. Identity comparison would never match and nothing would ever accumulate. The text is what identifies a chunk.

**The value is a tuple `(score, document)`.** The score has to accumulate across runs while the document object is kept intact — hence storing both, and on a repeat hit adding to `prev_score` while keeping `prev_doc`. Storing only scores would leave you with numbers and no documents; storing only documents would lose the running total.

The final `sorted(..., reverse=True)` is where consistency wins: documents that hit the `if` branch several times have accumulated several contributions, and they float to the top.

---

## Running it

```python
loader = PyPDFLoader("notebooklm_rag.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(pages)

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(documents=chunks, embedding=embedding_model,
                                    collection_name="notebooklm_rag")

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
```

```python
llm = ChatOpenAI(model="gpt-5-mini")

rag_fusion = RAGFusion.from_llm(llm=llm, retriever=retriever, num_subqueries=2, k=3)

query = "How does NotebookLM retrieve relevant information from uploaded documents?"
fused_docs = rag_fusion.invoke(query)
```

Two sub-queries, each retrieving 3 documents, fused down to the 3 with the highest RRF scores. Then the ordinary RAG ending:

```python
context = "\n\n".join([doc.page_content for doc in fused_docs])

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Use ONLY the context provided below to answer the question.
Be clear, concise, and accurate in your response.
If the answer is not present in the context, say "I don't know" - do not make up an answer.

Context:
{context}

Question: {question}

Answer:
""")

generation_chain = prompt | llm
response = generation_chain.invoke({"context": context, "question": query})
```

### The ensemble variant

The second notebook keeps everything above and swaps the retrieval half — two retrievers over the *same* store, differing in search strategy:

```python
similarity_retriever = vectorstore.as_retriever(
    search_type="similarity", search_kwargs={"k": 3}
)

mmr_retriever = vectorstore.as_retriever(
    search_type="mmr", search_kwargs={"k": 3, "lambda_mult": 0.5}
)

rag_fusion = RAGFusion.from_retrievers(
    base_retrievers=[similarity_retriever, mmr_retriever],
    weights=[0.5, 0.5],
    k=3
)
```

No LLM call, no rephrasing — and per the branch above, no hand-written RRF either. `EnsembleRetriever` runs both retrievers in parallel and fuses their rankings with its own RRF.

> [!note] This pairing is a sensible one rather than an arbitrary demo. Plain similarity returns the closest matches, which tend to resemble each other; **MMR** deliberately trades some closeness for diversity. Fusing them means a document must be either very close *or* usefully different to survive — and one that is both will appear in both lists and win on consistency.

---

> [!tip] Interview framing
> "There's no built-in RAG Fusion retriever, so it's a hand-rolled class. The core is about fifteen lines: for each retrieval run, enumerate the documents from rank 1, compute `1/(rank+60)`, and accumulate into a dict keyed on `page_content` holding a `(score, document)` tuple — keyed on the text because each run is a separate retrieval call, so the same chunk comes back as different Python objects and identity comparison would never match. Then sort by accumulated score descending. The class exposes two constructors and they behave differently in a way that's easy to misread: `from_llm` generates sub-queries and runs the hand-written RRF, while `from_retrievers` wraps a LangChain `EnsembleRetriever` and never touches that method, because `EnsembleRetriever` already does RRF internally. So the same class fuses across queries or across retrievers, using two different RRF implementations depending on how you constructed it. The demo also logs the generated sub-queries, per-run retrievals and final scores, which is what makes the output debuggable at all."
