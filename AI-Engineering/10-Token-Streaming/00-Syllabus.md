#tokens #streaming #llm #agents #langchain #syllabus

# 10 · Token Streaming — Syllabus

**10 notes, 112 rungs.** Generic — what is inside the stream and why it behaves as it does, not any one implementation, which is mapped at the bottom.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — the sampler picks one token, therefore it must be appended and rerun, therefore generation is serial, therefore decode sets a second latency number. Rungs are not topics and not section headings. Eight to fifteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about tokens teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

> [!important] Three folders, one subject, and this is the last one
> | Folder | What it owns | Shelf life |
> |---|---|---|
> | [[../08-Streaming-And-SSE/00-Syllabus\|08 · Streaming and SSE]] | the **pipe** — framing, heartbeats, proxies, reconnection | portable, decades old |
> | [[../09-LangGraph-Streaming/00-Syllabus\|09 · LangGraph Streaming]] | the **framework** — modes, writers, chunk shapes, interrupts | perishable, moves every minor release |
> | **10 · Token Streaming** (this) | the **payload** — what a token is, and what streaming costs you | portable, survives a framework swap |
>
> Read in that order. This folder is the **payload** — why a token arrives when it does, why the same answer can arrive three times, and why nothing can be un-sent. Every problem in it survives replacing SSE with WebSocket, or LangGraph with anything else.
>
> It meets folder 08 in exactly one place: an error after the first byte cannot be a status code. That rung appears in both, on purpose, from the two directions.

**Two halves, trained differently.** Notes 1 through 7 are mechanism — what the model and the framework actually do — and respond to retrieval practice, so the rungs are the recall unit. Notes 8 through 10 are design judgement, and the evidence says retrieval drills do **not** transfer to problem-solving, so they are worked as positions defended against changed constraints rather than recalled.

**Currency check (2026-09-08):** provider chunking is undocumented and changes without notice — the measurements in note 3 are from `gemini-3.6-flash` on 2026-09-08 and must be re-taken rather than trusted. Re-verify before relying on: whether requesting the streaming mode is enough to make your provider's finished-answer call stream, which it was on 2026-09-10 (note 4), whether reasoning summaries are enabled by default (note 7), and what your framework's accumulated chunk type is called (note 5).

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**Where a rung says break, it is run, not read.** Counting chunks against tokens on a real endpoint produces a problem the rest of the note attaches to. Reading that providers batch produces a fact that decays.

**Recall is per note, from memory, file closed.** Recognising an answer does not count.

**Two rabbit holes are marked and binding** — transformer attention internals in note 2, and tokenizer training in note 1. Both are deep, genuinely interesting, and pay back nothing here.

**Spacing:** re-test notes 1 to 4 after finishing note 7, and all ten after any streaming implementation is done. Same-day re-testing is close to wasted, because retrieval works when forgetting has started.

---

## Note 1 · A Token Is Not A Word

10 rungs. No break — this is the vocabulary everything else counts in.

1. Text has to become integers before a model can touch it, so something must cut it into pieces.
2. The obvious piece is the word. **Break it** — a vocabulary of every word is unbounded, and any word missing from it cannot be represented at all.
3. The obvious fix is the character. **Break that too** — sequences become several times longer, and the model has to learn spelling before it can learn grammar.
4. Byte-pair encoding sits between them: start from characters, repeatedly merge the most frequent adjacent pair, stop at a fixed vocabulary size.
5. So a token is simply whatever was frequent enough during training to earn a merge — a whole word, a word-piece, a prefix, a space, a punctuation mark.
6. Common words are one token, rare words are several, and the same word with a leading space is a **different token** from the word without one.
7. Which is why token counts cannot be derived from word counts, and why the ratio differs sharply between languages.
8. It is also why a model can spell a word it has never seen — it is assembling pieces it does know.
9. The tokenizer is fixed when the model is trained, so it is a property of the model rather than a setting you choose.
10. Therefore every number you bill on, cache on, truncate to, or set a limit in is counted in this vocabulary — not in words, and not in characters.

> **Recall:** What breaks word-level tokenization, and what breaks character-level? · Why is a leading space part of the token? · Why can you not convert a word budget into a token budget?
>
> **Stop:** No training a tokenizer, no merge-table construction, no comparison of BPE against WordPiece or SentencePiece.

---

## Note 2 · One Token At A Time

12 rungs. **Break:** time the first token and the last token of a long answer separately, and watch the gap.

1. A model does not compute an answer and then send it.
2. One forward pass produces a probability distribution over the entire vocabulary for **the next token only**.
3. A sampler picks one from that distribution, and temperature and top-p shape how adventurous the pick is.
4. The chosen token is appended to the input, and the whole thing runs again.
5. That loop is autoregressive decoding, and it is the reason output is inherently sequential rather than available at once.
6. **Break the naive reading** — if every step reprocessed the entire prompt, a 500-token answer would cost 500 full passes over a growing input.
7. The KV cache prevents that: attention keys and values for tokens already processed are kept, so each step only processes the one new token.
8. So generation splits into two phases with completely different cost profiles — **prefill**, which processes the prompt once, and **decode**, which runs once per output token.
9. Prefill is compute-bound and parallel across the prompt; decode is memory-bound and strictly serial.
10. That produces two independent latency numbers: **time to first token**, set by prefill, and **inter-token latency**, set by decode.
11. Streaming improves neither of them. It exposes tokens that decode was producing at that rate anyway.
12. Therefore the whole benefit of streaming is that the user gets to see prefill finish, instead of waiting for decode to finish as well.

> **Recall:** Which phase sets time to first token, and which sets the gap between tokens? · Why is decode serial when prefill is not? · What exactly does streaming improve, given it changes no total?
>
> **Stop:** No attention mathematics, no positional encodings, no speculative decoding — that belongs with inference optimisation, not here.

---

## Note 3 · The Chunk Is Not The Token

11 rungs. **Break:** instrument a real endpoint, log chunks per response and characters per chunk across twenty answers of different lengths.

1. The natural assumption is one token, one network write.
2. **Break it** — count chunks against the reported output-token count on a real stream and they do not match, usually by a large factor.
3. A token is a few characters, so one write per token means a tiny payload carrying full framing overhead.
4. Providers therefore batch: several tokens are gathered and delivered as one chunk.
5. How many is not a documented constant — it varies by provider, by model, and by fleet load at that moment.
6. Measured on 2026-09-08: a 675-character answer arrived in **8 chunks**, and a 59-character answer arrived in **1**.
7. So a short answer does not stream at all in any sense a user perceives — it arrives as one write, exactly like a non-streamed response.
8. The threshold is perceptual rather than numerical: below roughly a sentence, the first chunk is the whole answer.
9. Which makes the decision to stream a question about **your** distribution of answer lengths, not about the technology.
10. Batching also interacts with server-side scheduling — continuous batching and chunked prefill change when your tokens are produced relative to everyone else's.
11. Therefore inter-token latency is partly a property of the fleet you are sharing, which is why it moves without your code changing.

> **Recall:** Why do providers batch tokens rather than write each one? · What answer length makes streaming invisible, and how would you find yours? · Why can inter-token latency change with no deploy on your side?
>
> **Stop:** No vLLM or TensorRT internals, no scheduler tuning. Knowing the two names is enough to explain a moving number.

---

## Note 4 · The Model Is Not The Stream

12 rungs. **Break:** run the probe, see a single item, conclude that token streaming does not work, then find out the call had been streaming the whole time.

1. A client library usually offers two calls — one that returns the finished answer, one that yields it in pieces.
2. The obvious assumption is that these are the same request with a flag, so either can be adapted into the other.
3. **Break it** — they are two different requests, and for some providers two different endpoints, and only one of them produces anything before the answer is complete.
4. So a framework that streams by intercepting token callbacks receives nothing at all when the underlying request was the non-streaming one.
5. And **nothing fails**. The stream yields a single item carrying the whole answer, which is indistinguishable from a working stream with very coarse chunking.
6. **Break the assumption that your code chose which request was made** — it usually did not. The framework chooses, at call time, and the finished-answer method routes itself to the streaming request whenever anything is listening for tokens.
7. Which means asking the framework for its streaming mode is itself what makes the model stream, and the call inside your node may not need to change at all.
8. **Break the provider investigation** — reading whether the provider's finished-answer method delegates to its streaming one answers a question nobody asked. That dispatch lives one layer above the provider, and the provider supplies only two yes-or-no facts: does a streaming method exist on this class, and has streaming been disabled on this instance.
9. So the whole check collapses to one predicate, which can be asked directly with no API call and no key.
10. **Break the test harness** — a fake model produces tokens under the finished-answer call for exactly the same reason a real one does, something being attached to listen. A green fake test is not the trap it looks like; the trap is concluding anything about the provider from either result.
11. Therefore verify in the order the dispatch actually runs — is streaming disabled on this instance, does a streaming method exist, is anything listening — because it is decided in that order and stops at the first no.
12. And **a single-item stream is not evidence of a non-streaming call**, because a framework that also republishes whole messages returned by nodes produces exactly one item with no tokens involved anywhere. One item is what both explanations predict.

> **Recall:** Why can a call that returns one finished answer still emit tokens along the way? · What question does reading the provider's adapter fail to answer, and where does the answer actually live? · Why is a stream of exactly one item evidence of nothing?
>
> **Stop:** No provider SDK archaeology beyond the one method. You are answering a yes-or-no question, not learning the library.

---

## Note 5 · Putting The Answer Back Together

11 rungs. **Break:** accumulate a stream, then compare the reconstructed object field by field against a non-streamed one.

1. A stream yields fragments, and almost everything downstream — history, logging, the next model call — wants a whole message.
2. Frameworks give fragment objects that support addition, so folding the stream reconstructs the message.
3. **Break the assumption that the result is the same type as a normal message** — it is a fragment type, not a message type, even after the fold.
4. The two differ in the field that identifies the message kind, which is exactly what routing and filtering code switches on.
5. So returning the accumulated fragment where a message is expected gets **silently skipped** rather than rejected, and the answer disappears with no exception anywhere.
6. Rebuilding a real message from the fragment fixes it, and that means enumerating the fields to carry across.
7. **Break the enumeration** — anything not named is silently lost, and token usage is the field people forget.
8. Losing usage does not fail either. It reports zero, and zero looks like a measurement rather than a missing one.
9. Therefore reconstruct explicitly, and assert on the reconstructed object rather than on the fragments that fed it.
10. Fold order matters: fragments must be added in arrival order, and folding them out of order corrupts the text without raising anything.
11. Therefore accumulation is the second place a stream can be wrong while looking entirely healthy.

> **Recall:** Why can an accumulated fragment be dropped by code that accepts a normal message? · Which carried-across field fails silently by reporting a plausible number? · What are the two failures in this note that raise no exception?
>
> **Stop:** No framework-specific class hierarchy diagrams. The lesson is that the type changes, not what it is called this month.

---

## Note 6 · The Same Answer, More Than Once

10 rungs. **Break:** enable two views at once, sum the fragment lengths, and compare against the final answer length.

1. An orchestration layer usually exposes more than one view of the same run — a token view and a step view.
2. Turn two on together and the same answer can arrive through both.
3. **Break the naive consumer** — emitting a delta for every item on the token channel renders the answer twice.
4. Worse, the duplicate is not another fragment: it is the **complete message**, arriving after all the fragments, on the same channel.
5. And a third copy arrives on the step channel, because a node's output is also a message.
6. So the filter cannot be on the producing node alone — it has to be on the kind of object as well.
7. The fragment type is a subclass of the message type rather than the reverse, so an isinstance test against the fragment type excludes the complete copy.
8. The same single test also excludes tool output, which otherwise reaches the user as raw internal data.
9. Therefore the correct filter is a conjunction: the right producer **and** the right object kind.
10. Verify by arithmetic, not by eye — sum the fragment lengths and compare to the final length. Equal is one copy, double is two.

> **Recall:** What are the three copies, and which channel does each arrive on? · Why does an isinstance test on the fragment type exclude the complete message? · What does the same filter accidentally protect you from?
>
> **Stop:** No exhaustive tour of every stream mode — that is [[../09-LangGraph-Streaming/00-Syllabus|09 · LangGraph Streaming]], which owns the concrete version of this note in its note 8. Two channels and the duplication rule is the whole lesson here.

---

## Note 7 · Not Everything In The Stream Is The Answer

13 rungs. No break — this is the shape four vendors converged on independently, and the point is the convergence.

1. Early streams carried exactly one kind of content: the answer.
2. Reasoning models added a second — the model's own account of what it is doing.
3. Tool calling added a third — the arguments to a function, emitted as text like everything else.
4. **Break the single-channel client** — with one undifferentiated channel, the UI has to guess what a fragment is by inspecting its content, and it will guess wrong.
5. Every major provider solved this the same way: a **typed block is opened before any of its content arrives**.
6. So a stream is a sequence of blocks, each with a start, a run of deltas, and a stop, and each block carries an index.
7. Deltas are typed by what they carry — answer text, reasoning text, argument JSON — so two deltas with identical text can belong in different parts of the UI.
8. Which means placement is decided entirely by the frame, and **never** by looking at the content.
9. Tool names arrive complete in the block-start event; only the arguments stream.
10. Arguments arrive as partial JSON, so they cannot be parsed until the block closes.
11. **Break the eager parser** — validating a half-written object fails by definition, because well-formedness is not a property a fragment can have.
12. So there are two genuinely different artifacts: a best-effort snapshot suitable for a progress UI, and a validated object that exists only once the block ends.
13. Reasoning text is generated text like any other, so it can name tools and arguments — a channel labelled internal is not thereby private, and that is a policy problem rather than a parsing one.

> **Recall:** Why must the block be typed before its content arrives? · What is complete at block start and what streams? · Why can partial arguments not be validated, and what do you show instead? · What does a reasoning channel leak that a status channel cannot?
>
> **Stop:** No per-vendor field-name tables. The convergence is the lesson; the spellings are lookup.

---

## Note 8 · Rendering Something Half-Written

10 rungs. Judgement, not recall — defend the choice against a changed constraint.

1. Chat answers are usually markdown, and markdown renderers are written for complete documents.
2. **Break it** — a fragment can end anywhere, so the accumulated string is invalid markdown most of the time it is on screen.
3. Re-rendering on every fragment therefore flashes: an unclosed emphasis marker, a half-written link, a code fence with no end.
4. The first naive fix is to render only when the stream ends, which discards the entire benefit you streamed for.
5. The second is to render on a timer, which makes the flashing less frequent without making it correct.
6. The real fix has two independent parts and needs both.
7. **Repair:** close unterminated constructs before rendering, respecting context — an unclosed backtick inside a fenced block must not be closed.
8. **Split and memoise:** break the accumulated text into blocks at blank lines and fence boundaries, and re-parse only the last one.
9. **Break the whole-string re-parse** — its cost grows with the square of the answer length, so long answers visibly stutter exactly when streaming was supposed to help most.
10. Therefore rendering a stream is a distinct engineering problem with its own solutions, and no transport or model choice makes it go away.

> **Defend:** The product wants code blocks to appear as they are written rather than at the closing fence. What changes, and what breaks? · A one-line answer never needs any of this — at what length does it start to?

---

## Note 9 · You Cannot Un-Send A Token

12 rungs. Judgement. **This is the note that changes how you design, and the one people who have only read about streaming get wrong.**

1. A non-streamed answer can be inspected in full before anyone sees any of it.
2. **Break that with streaming** — the first fragment leaves the building before the last one exists.
3. So any check needing the whole answer necessarily runs after the user has already read part of it.
4. Checking each fragment instead fails differently: a fragment carries too little context for a stable judgement, and the verdict flips as more arrives.
5. The workable middle is a buffer to a semantic boundary — usually a sentence — checked before release.
6. Which costs exactly the latency of that buffer, and **that is the real price of moderating a stream**, paid on every answer.
7. The same asymmetry breaks retries: the HTTP status was committed with the first byte.
8. So a failure after that point cannot be a status code, and any retry logic keyed on status will never fire.
9. Falling back to a second provider after partial output means the user watches a truncated answer followed by a complete different one.
10. Buffering the first attempt to avoid that reintroduces precisely the latency streaming existed to remove.
11. And if the failed attempt already emitted a tool call that was executed, the retry repeats the side effect — the answer was abandoned, the write was not.
12. Therefore streaming converts several solved problems — validation, retry, failover, idempotency — back into open ones, and the honest engineering position is knowing which of them you have given up rather than believing you still have them.

> **Defend:** You are asked to add an output filter to a streaming assistant with no added latency. What do you say? · The provider fails after 200 tokens of a 400-token answer. Argue for one of: truncate and apologise, buffer everything, or never fail over. · Which of these problems does WebSocket solve? (None, and being able to say why is the point.)

---

## Note 10 · What It Costs And Whether It Paid

11 rungs. Judgement, and the note that should be read before building rather than after.

1. Streaming changes no total — same tokens, same money, same total generation time.
2. It changes exactly one number: time to first token.
3. So the case for it is entirely a perception argument, and it should be made with a measurement rather than an intuition.
4. The measurement is the **distribution** of answer lengths, not the mean, because the mean hides a bimodal reality of one-line lookups and long summaries.
5. Below roughly a sentence the answer arrives in one chunk, so streaming is invisible no matter how well it is implemented.
6. A system whose median answer is short should delete its loading animation and keep whole-message delivery — the animation is added latency dressed as responsiveness.
7. **Break the assumption that streaming is free** — usage accounting has to survive message reconstruction, and it is counted per model call, not per turn.
8. An agent loop makes several calls per turn, so accumulating usage across laps is the first honest measure of what a turn costs.
9. Which usually reveals that **input** tokens dominate: a one-line question can cost thousands, because persona, system prompt and policy are resent on every lap.
10. Measured on 2026-09-08: a four-character question cost **5,912 input tokens against 136 output**, and a three-lap tool turn cost 12,214 input.
11. That number is far larger than anything streaming wins, and it points at prompt caching and prompt versioning — so the measurement that settles the streaming question hands you the cost question for free.

> **Defend:** Median answer is 80 characters. Argue for and against streaming, then decide. · Your input-to-output ratio is 40:1. What do you do first, and why is it not streaming? · What would have to be true for streaming to be the highest-value change available?

---

## Coverage

None written yet. Note files will be numbered to match this list — note 4 becomes `04-Model-Is-Not-The-Stream.md`.

| Note | Rungs | Written |
|---|---|---|
| 1 · A Token Is Not A Word | 10 | no |
| 2 · One Token At A Time | 12 | no |
| 3 · The Chunk Is Not The Token | 11 | no |
| 4 · The Model Is Not The Stream | 12 | no |
| 5 · Putting The Answer Back Together | 11 | no |
| 6 · The Same Answer, More Than Once | 10 | no |
| 7 · Not Everything In The Stream Is The Answer | 13 | no |
| 8 · Rendering Something Half-Written | 10 | no |
| 9 · You Cannot Un-Send A Token | 12 | no |
| 10 · What It Costs And Whether It Paid | 11 | no |

---

## Deferred

| Topic | Goes to |
|---|---|
| SSE framing, heartbeats, proxies, reconnection, resumption | [[../08-Streaming-And-SSE/00-Syllabus\|08 · Streaming and SSE]] |
| Stream modes, `get_stream_writer`, chunk shapes, interrupt delivery, subgraphs | [[../09-LangGraph-Streaming/00-Syllabus\|09 · LangGraph Streaming]] |
| Async generators, `async for`, closing a generator early | `00-Python-Utils/04-Generators-And-Iterators` |
| Cancellation delivery, `CancelledError`, `asyncio.shield` | `00-Python-Utils/08-Async` |
| Prompt caching, quota windows, cost per tenant | `05-Cost-And-Latency` |
| Span boundaries for a streamed agent run | `02-Observability` |
| Prompt injection through a reasoning channel | `04-AI-Security` |
| KV cache, paged attention, speculative decoding, quantization | outside this vault — interview discussion material only |

---

## Where this shows up in Xarvis

Every rung in notes 4, 5 and 6 was paid for on 2026-09-08 while wiring token streaming into the admin agent, and the sequence is in `Current-Standing/TODO/05-Streaming-Build.md`.

**Note 4** did waste a day, in the other direction. The build doc concluded that the node's finished-answer call could not stream, having checked that the provider implements both methods separately and neither delegates — a true fact about the wrong layer. Measured on 2026-09-10 with no API call: the predicate that decides it returns true as soon as the framework's streaming handler is attached, so the call had been streaming from the moment the mode was requested, and the node rewrite built on that premise was never needed for tokens. It earns its keep for a different reason, which is where the timeout is measured.

**Note 5** cost two silent bugs. The accumulated fragment is a chunk type whose kind field reads differently, so the streaming service skipped it and the answer vanished with no exception. Then the rebuilt message dropped `usage_metadata`, and every streamed turn reported zero tokens — a number, not a gap.

**Note 6** is exact: the answer arrived **three times**. Nine fragments summing to 781 characters, then a complete 781-character message on the same channel, then a third copy on the step channel. The filter is the conjunction in rung 9.

**Note 3** is the finding that undercuts the whole feature: 8 chunks for 675 characters, and **1 chunk for 59 characters**. **Note 10** is therefore unresolved and blocking — the median `final_response_length` over fourteen days is already in the outcome log and has still not been read.

**Note 7** is half-built: the frame taxonomy is specified in `Current-Standing/TODO/03-Stream-Contract.md` and the reasoning channel is wired but empty, because thought summaries are off by default. Rung 13 is the reason a reasoning channel cannot be shipped raw as a privacy guarantee.

---

## Interview hooks

The three that recur: **why does streaming not make the answer faster** (note 2, and the answer is prefill against decode, not hand-waving about perception) · **how do you moderate a streamed answer** (note 9, which separates people who have shipped it from people who have read about it) · **how do you retry when the provider fails mid-answer** (note 9 again, and the correct answer includes what you give up).

The one that catches people who only read: **how many chunks is a token** (note 3). Everyone assumes one. Nobody who has measured it does, and the follow-up — so when is streaming pointless — is a design question wearing a trivia question's clothes.

---

## Sources to verify against

- [Anthropic — Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming), the clearest published block model
- [OpenAI — Responses streaming events](https://developers.openai.com/api/reference/resources/responses/streaming-events)
- [Gemini — Streaming interactions](https://ai.google.dev/gemini-api/docs/streaming) and [thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [LangGraph — Streaming](https://docs.langchain.com/oss/python/langgraph/streaming) and [LangChain standard content blocks](https://www.langchain.com/blog/standard-message-content)
- [Karpathy's tokenizer walkthrough](https://www.fast.ai/posts/2025-10-16-karpathy-tokenizers.html) for note 1
- [Continuous and chunked batching](https://handbook.modular.com/inference-optimization/static-dynamic-continuous-batching/) for note 3 rung 10
- [SentGuard — sentence-level streaming guardrails](https://arxiv.org/html/2606.02041) for note 9 rung 5
- [Streamdown](https://vercel-streamdown.mintlify.app/introduction) and [marked issue 3657](https://github.com/markedjs/marked/issues/3657) for note 8
