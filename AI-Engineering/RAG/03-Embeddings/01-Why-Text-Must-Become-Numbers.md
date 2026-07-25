We have loaded documents and split them into chunks. That covers the first two components of the RAG pipeline — data ingestion and chunking. The chunks are still **text**, though, and that is a problem, because the very next thing RAG needs to do is *compare* them. When a user asks a question, RAG has to find the chunks that are **most similar** to that question and pull them out of storage. So the real task ahead is: given a query and a pile of chunks, measure how similar they are.

And here is the wall you hit immediately — **you cannot do similarity on raw text.** Similarity is a calculation, and a machine cannot calculate on words. It can only calculate on numbers. So before any of the interesting RAG machinery can run, the text has to be turned into numbers. That conversion is component number three of the pipeline: **text embeddings and embedding models.**

> [!info] An embedding model takes a piece of text and returns a **vector** — a list of numbers — that stands in for that text. Once text is a vector, "how similar are these two pieces of text?" becomes "how close are these two vectors?", and *that* is a calculation a machine can do.

---

## This problem is older than RAG

If the idea of "you must convert text to numbers before a model can touch it" feels new, it isn't — anyone who has trained a machine learning model has already met it. Picture a dataset with a column like `Country` holding values `India`, `USA`, `Japan`. Try to feed that column straight into a machine learning model and you get an error. Models do maths; `India` is not a number. So the first thing you do is **encode** the column into numbers — one-hot encoding is the classic move, turning each category into a column of 0s and 1s.

The researchers building language systems faced the exact same wall, just larger: not one tidy column of three countries, but *all of human text*. Their answer evolved over three stages, and understanding that evolution is the whole point of this note and the next — because the weaknesses of each stage are precisely what the next stage was invented to fix. This note covers **stage one: the classical methods.**

---

## Stage 1 — count the words (classical methods)

The earliest techniques are the famous classical NLP methods — bag-of-words and its relatives. Their idea is disarmingly simple: **count the frequency of words in your text.** No understanding of meaning, just tallying.

To count, you first need a fixed list of every word you might see — the **vocabulary**, the unique set of words in your language. (For English that vocabulary is large; assuming **10,000** words, though real English is well beyond that.) Every word in the vocabulary becomes one **column**. Then, for each piece of text, you walk the vocabulary and write down how many times that word appeared.

Take two tiny documents and a vocabulary of `Cat, Sat, Mat, Rat, Wall, Ball`. Text 1 is "cat sat on the mat":

![[AI-Engineering/RAG/03-Embeddings/Images/01-Sparse-Bag-Of-Words.png]]

Text 1 becomes the vector `[1, 1, 1, 0, 0, 0]` — `Cat` once, `Sat` once, `Mat` once, and `Rat`, `Wall`, `Ball` never, so zero. A second document with different words produces a different count row (`[2, 0, 3, 2, 0, 1]` here). The text is now numbers. Mission accomplished — sort of.

---

## Why RAG threw this away — the sparsity problem

Look hard at that vector and two problems jump out, and both get worse at real scale.

**Problem one: the vectors are enormous and almost entirely empty.** The length of each vector equals the size of the vocabulary. A three-word sentence, in a 10,000-word vocabulary, is a vector of 10,000 numbers of which maybe three are non-zero and **9,997 are zero.** A vector that is mostly zeros is called a **sparse vector**, and sparsity is expensive. Similarity between two texts is computed element by element across the whole vector, so every single comparison drags through 10,000 multiplications — the overwhelming majority of them `something × 0`, pure wasted work. Scale that to a real vocabulary and a real corpus and the cost is brutal.

> [!danger] A sparse vector wastes both space and computation. In a 10,000-dimensional bag-of-words vector, a normal sentence lights up a handful of positions and leaves thousands sitting at zero — yet every similarity calculation still has to traverse all 10,000 dimensions. You are paying for 10,000 numbers to carry the information of three.

**Problem two — the deeper one: counts are not meaning.** Bag-of-words knows that `cat` appeared once. It has no idea that `cat` and `kitten` are related, or that `river bank` and `money bank` are completely different things. It captures *how often* words appear, never *what they mean*. And RAG lives and dies on meaning — a question about "login problems" must find a chunk about "password recovery" even though they share no words. Counting cannot do that.

> [!important] Classical count-based methods (bag-of-words) genuinely worked for older machine-learning tasks, and you will still see them. But for RAG they fail twice: the vectors are **sparse** (huge, mostly-zero, expensive), and they capture **word frequency, not semantic meaning**. Both flaws are exactly what the next stage — word embeddings — was built to fix.

**What classical methods guarantee:** text becomes numbers, and identical texts get identical vectors.
**What they don't guarantee:** anything about meaning, and nothing about efficiency — related-but-different wordings look unrelated, and every vector is as long as your entire vocabulary.
