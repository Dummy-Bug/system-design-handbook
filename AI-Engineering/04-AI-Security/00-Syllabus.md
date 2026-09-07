#ai-engineering #security #guardrails #owasp #prompt-injection #authorization #block-4 #syllabus

# Block 4 · AI Security and Guardrails — Syllabus

**20 notes, 201 rungs.** Generic — the attack surface and the defences that hold, not Xarvis's implementation, which is mapped at the bottom.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — the guard model scores 91% on the benchmark, therefore it looks like a solution, therefore you test a phrasing it has not seen, therefore it scores 34%, therefore the number was measuring memorisation. Rungs are not topics and not section headings. Seven to fourteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about AI security teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

**Why generic first.** Several concepts here — indirect injection, inter-agent communication, rogue agents — are things a single-agent system structurally cannot exercise. That is exactly why the syllabus must not be derived from the codebase: those are the ones an interviewer asks about, and skipping them because they are inapplicable is how you arrive unable to discuss the field.

**Three modes, trained differently.** Notes 1 to 9 and 12, 16, 17 are **mechanism** — how the attacks work and what the standards name — and respond to retrieval. Notes 10, 11, 13, 14, 15 and 18 are **design decisions**, defended against changed constraints rather than recalled. Notes 19 and 20 are **practice**: a threat model and a red-team suite are produced against a real system, and reading about them transfers nothing.

**Currency check (2026-09-06) — this remains the block that moves most.**

**Two OWASP lists, not one.** The **OWASP Top 10 for LLM Applications v2.0 (2025)** still covers LLM apps generally. The **OWASP Top 10 for Agentic Applications** was announced **9 December 2025** for 2026 by the OWASP GenAI Security Project, and it is drawn from real incident data rather than research projections. Naming its ten items is worth doing, because most candidates know only that it exists: **ASI01 Agent Goal Hijack · ASI02 Tool Misuse and Exploitation · ASI03 Identity and Privilege Abuse · ASI04 Agentic Supply Chain Vulnerabilities · ASI05 Unexpected Code Execution · ASI06 Memory and Context Poisoning · ASI07 Insecure Inter-Agent Communication · ASI08 Cascading Failures · ASI09 Human-Agent Trust Exploitation · ASI10 Rogue Agents.** Lead with this list when the system in front of you is an agent.

**Prompt injection is still architecturally unsolved**, and the field has now converged on what the answer is not. Detection-based defences fail on distribution shift, with hard numbers: a leading guard model drops from **91.0% to 33.8%** accuracy on novel attacks, established classifiers catch only **7 to 37%** of indirect injections against agents, and open-weight safety training can be removed with about **ten fine-tuning examples and under five dollars of compute**.

What replaced that instinct between 2024 and 2026 is a single idea worth stating precisely: **enforce security outside the model, with a deterministic policy that mediates the agent's actions, rather than training the model to refuse.** The named systems are **CaMeL, FIDES, Progent, RTBAS and FORGE**, built from capabilities, information-flow labels and reference monitors, and several report near-elimination of attacks on the **AgentDojo** benchmark. CaMeL is the one to be able to describe: a privileged model plans from the trusted user query, a quarantined model processes untrusted data with **no tool access**, and a custom interpreter tracks data provenance and checks policy before every tool call.

Re-verify before relying on: the ASI item names and ordering, any specific guard-model number, and whether the LLM v2.0 list has been superseded.

---

## How to teach from this

**One note per session, rungs in order, never skipping.**

**Where a rung says break, it is run, not read.** Watching your own agent follow an instruction embedded in a record it fetched produces a problem the fix attaches to. Reading that indirect injection exists produces a fact that decays.

**Recall is per note, from memory, file closed.**

**Notes 19 and 20 cannot be faked and are the two that produce something.** A threat model and a written attack suite are artifacts; the rest of the block is what makes them any good.

**Do not build a guard model.** Note 13 explains why, with numbers. If the instinct survives that note, the note failed.

**Three rabbit holes are marked and binding** — gradient-based adversarial ML in note 2, cryptographic supply-chain machinery in note 17, and container-escape internals in note 18.

**Spacing:** re-test notes 1 to 9 after finishing note 15, and the defences after the red-team suite has actually been run.

**The syllabus governs the numbering — never the source material.** Gaps are concepts not yet reached, not missing files.

---

# A · The Core Problem

## Note 1 · Why Prompt Injection Is Architecturally Unsolved

11 rungs. No break — this is the framing the rest of the block depends on.

1. A classical injection attack works because data reaches an interpreter that treats it as code.
2. SQL injection was solved by **separating the channels**: the query is parsed, then parameters are bound, and no parameter can become syntax.
3. So the fix was never better escaping, it was a structural boundary between instruction and data.
4. **Break the analogy** — a language model has **one channel**. The system prompt, the user message, and the contents of a fetched document all arrive as the same undifferentiated token stream.
5. There is no parameterised equivalent, because the model's whole function is to interpret whatever it reads as meaningful.
6. Which means injection here is not a bug in an implementation, it is a property of the architecture, and no amount of prompt engineering removes it.
7. Delimiters, all-caps warnings and instructions to ignore later instructions all reduce success rates and none establishes a boundary.
8. So the honest statement is that the model cannot be made to reliably distinguish its operator's instructions from an attacker's.
9. Which forces the conclusion the field reached between 2024 and 2026: **enforce the boundary outside the model**, in a deterministic layer that mediates what the agent may do.
10. That reframes every defence in this block — the question is never can the model resist, it is what can the model cause if it does not.
11. And it makes the blast radius, not the refusal rate, the thing you engineer.

> **Recall:** Why did parameterisation solve SQL injection, and why does the analogy fail here? · What is the honest one-sentence statement of the problem? · What replaces can the model resist as the design question?

## Note 2 · Direct Injection Versus Jailbreak

9 rungs. **Break:** send your own agent an instruction telling it to ignore its instructions, and record exactly what it does.

1. Two attacks are constantly conflated and have different targets.
2. A **jailbreak** targets the model's safety training — it tries to make the model produce content the provider trained it to refuse.
3. **Direct injection** targets the application — it tries to make the model ignore the developer's instructions and follow the user's instead.
4. Which means a jailbreak is the provider's problem and an injection is yours, and the mitigations sit in different places.
5. **Break the assumption that your system prompt is authoritative** — it is text in the same stream as the attack, and it has no special standing beyond position and phrasing.
6. Position helps slightly, because instructions earlier in context carry somewhat more weight, and that is a tendency rather than a rule.
7. So a direct injection succeeds or fails probabilistically, which means it succeeds eventually across enough attempts.
8. Which is why measuring a defence's success rate on a fixed attack set flatters it — the attacker retries and you do not.
9. And why the useful question is what the agent could do on the attempt that works.

> **Recall:** State the target of each attack and whose problem it is. · Why does position help without solving anything? · Why does a success-rate measurement flatter a defence?
>
> **Stop:** No gradient-based or optimisation-based adversarial ML. Rabbit hole, marked, binding.

## Note 3 · Indirect Injection

11 rungs. **Break:** put an instruction inside a record or document your agent reads, and watch it be followed.

1. Direct injection requires the attacker to talk to the agent.
2. **Break that requirement** — the agent reads things: documents, web pages, database rows, tool outputs, emails, calendar entries.
3. Anything it reads enters the same single channel from note 1, so an instruction planted in a document is an instruction.
4. Which means the attacker never needs access to your application at all; they need only to influence something it will later read.
5. That is indirect injection, and it is the attack that makes retrieval and tool use dangerous rather than merely useful.
6. It also breaks the mental model of the user as the threat: here the user is the **victim**, and the payload arrives through content they asked about.
7. The delivery is asynchronous, so the plant and the trigger are separated in time, and logs at the moment of compromise show a normal request.
8. Detection is measurably poor — established classifiers catch between 7 and 37% of indirect injections against agents.
9. Which is a rate low enough that treating detection as the control is a decision to be compromised.
10. So the structural answer is **provenance**: track which content is trusted and which is not, and forbid untrusted content from causing actions.
11. That is exactly what the CaMeL line of systems implements, and why note 10's layering exists.

> **Recall:** Why does the attacker not need access to your application? · Who is the user in this attack? · What is the measured detection rate, and what does it imply about strategy? · Name the structural answer.

## Note 4 · The Lethal Trifecta

9 rungs. No break — this is the diagnostic you apply to every system.

1. Indirect injection is dangerous only in combination, and the combination has three parts.
2. **Access to private data** — the agent can read something worth stealing.
3. **Exposure to untrusted content** — the agent reads something an attacker can influence.
4. **An ability to communicate externally** — the agent can send data somewhere the attacker can observe.
5. All three present means an attacker can plant an instruction, have it read private data, and have it exfiltrate the result.
6. **Any one absent breaks the chain**, and that is what makes this a design tool rather than a taxonomy.
7. Which gives the cheapest real mitigation in the block: remove the third leg. An agent with no outbound channel cannot exfiltrate, whatever it is told.
8. Outbound is broader than it looks — a URL rendered in a reply, an image loaded from a link, a tool that posts anywhere, an email draft.
9. So the diagnostic is three questions asked of any agent design, and answering yes three times means the system is exploitable regardless of its prompt.

> **Recall:** Name the three legs. · Which is usually cheapest to remove, and what counts as that leg? · What does the trifecta let you say about a design before it is built?

## Note 5 · Assume The System Prompt Leaks

8 rungs. **Break:** ask your own agent to repeat its instructions, in three different phrasings.

1. System prompts are extracted routinely, by asking directly, by asking obliquely, and by asking the model to translate or summarise its context.
2. **Break the defence** — instructing the model never to reveal its prompt is itself part of the prompt, and is subject to the same override as everything else.
3. So a leaked prompt is not a possibility to defend against, it is a default state to design around.
4. Which makes the actual question what the prompt contains that matters if published.
5. Credentials, internal endpoints, and customer names in examples are the obvious ones and are outright bugs.
6. The subtler one is **security logic** — a prompt that lists which users may do what has published your access-control policy.
7. And a policy that lives only in a prompt was never enforced in the first place, which is note 12's problem arriving early.
8. So the rule is that the prompt may contain instructions and must not contain secrets or controls.

> **Recall:** Why can a prompt not protect itself? · What are the three categories of thing that must not be in one? · Why is security logic in a prompt worse than merely leaked?

---

# B · The Two OWASP Lists

## Note 6 · OWASP LLM Top 10 v2.0 — Walk It

10 rungs. No break — orientation, but the walk is done out loud from memory.

1. A shared vocabulary matters in interviews and in incident reports, and this is the one people cite.
2. The v2.0 list from 2025 is still current for LLM applications generally, and covers **LLM01 Prompt Injection** at the top for the reason note 1 gives.
3. **LLM02 Sensitive Information Disclosure** — the model reveals what it was given or trained on.
4. **LLM03 Supply Chain** — the model, its weights, and its dependencies are software you did not write.
5. **LLM04 Data and Model Poisoning** — corrupting training or fine-tuning data.
6. **LLM05 Improper Output Handling** — treating model output as trusted input to something else, which is injection pointed downstream.
7. **LLM06 Excessive Agency** — the model can do more than it needs to; note 7 takes this apart.
8. **LLM07 System Prompt Leakage** — note 5.
9. **LLM08 Vector and Embedding Weaknesses**, **LLM09 Misinformation**, **LLM10 Unbounded Consumption** complete it.
10. The point of the walk is that most items are ordinary application security wearing new names, and the genuinely new ones are 01, 06 and 08.

> **Recall:** Name all ten from memory. · Which three are genuinely new rather than renamed application security? · Why is improper output handling an injection problem?

## Note 7 · Excessive Agency In Depth

10 rungs. **Break:** list every tool your agent has and mark which ones could cause harm if invoked with attacker-chosen arguments.

1. Excessive agency is the item that most often turns an injection into an incident, so it earns its own note.
2. It decomposes into three distinct excesses, and conflating them hides the fix.
3. **Excessive functionality** — the agent has tools it does not need for its purpose, often because a library exposed them by default.
4. **Excessive permissions** — the tools it has run with more privilege than the task requires, typically a shared service account.
5. **Excessive autonomy** — the agent acts without confirmation on operations whose consequences are irreversible.
6. Which maps onto three different fixes: remove the tool, scope the credential, insert a human.
7. **Break the framing that this is about the model** — every one of these is decided by the developer at registration time, and none is affected by how good the model is.
8. Which is why this is the highest-leverage item on the list: it is entirely within your control and it bounds the damage of every attack in section A.
9. The test is a sentence: if this agent were fully controlled by an attacker, what is the worst it could do with the tools it has.
10. If the answer is unacceptable, the fix is fewer tools or narrower ones, not a better prompt.

> **Recall:** Name the three excesses and the fix for each. · Why is none of them affected by model quality? · State the test in one sentence.

## Note 8 · OWASP Top 10 For Agentic Applications — Walk It

12 rungs. No break — orientation, walked out loud.

1. The LLM list treats the model as a component that answers; an agent plans, remembers, calls tools and acts with delegated authority.
2. Which produces risks the earlier list has no entry for, and the 2026 agentic list exists to name them.
3. It was announced on 9 December 2025 and is built from real incident data rather than projections, which is worth saying when citing it.
4. **ASI01 Agent Goal Hijack** — the objective itself is redirected, not just one response.
5. **ASI02 Tool Misuse and Exploitation** — legitimate tools driven to illegitimate ends.
6. **ASI03 Identity and Privilege Abuse** — the agent acting with authority it should not have, or on behalf of the wrong principal.
7. **ASI04 Agentic Supply Chain Vulnerabilities** — tools, plugins and servers the agent trusts by configuration.
8. **ASI05 Unexpected Code Execution** — the agent reaching a code path that runs arbitrary code.
9. **ASI06 Memory and Context Poisoning** — persistent state corrupted so the attack survives the conversation.
10. **ASI07 Insecure Inter-Agent Communication**, **ASI08 Cascading Failures** — one agent's bad output becoming another's trusted input, and failures compounding across a chain.
11. **ASI09 Human-Agent Trust Exploitation** — the user believing the agent because it is confident and fluent, which is a social attack the system enables.
12. **ASI10 Rogue Agents** — an agent operating outside its intended scope or oversight entirely.

> **Recall:** Name all ten with their numbers. · Which one covers an attack that survives the conversation? · Which one is a social rather than technical failure?

## Note 9 · What The Agentic List Adds That The LLM List Missed

9 rungs. No break — this is synthesis.

1. Reading two lists is less useful than knowing what the second one saw that the first did not.
2. **Persistence** — ASI06. The LLM list assumes a stateless call; memory makes an attack outlive the request that planted it.
3. **Identity** — ASI03. The LLM list has no notion of on whose behalf, and an agent acts for a principal whose authority it can exceed or confuse.
4. **Composition** — ASI07 and ASI08. Two agents in sequence create a boundary where one's untrusted output becomes another's trusted input.
5. Which is note 3's provenance problem occurring inside your own system rather than at its edge.
6. **The human as attack surface** — ASI09. Fluency is a vulnerability when the user's approval is the control.
7. Which quietly undermines note 14: human-in-the-loop is a real control and it degrades when the human trusts the agent.
8. **Scope** — ASI10. An agent that can spawn work, schedule itself, or act unattended has no equivalent in a request-response list.
9. So the addition is not ten new attacks, it is four properties — persistence, delegated identity, composition, and autonomy — each of which generates attacks.

> **Recall:** Name the four properties the agentic list adds. · Which two ASI items are the same problem at different boundaries? · Which item undermines a defence from a later note?

---

# C · Defences That Hold

## Note 10 · Defence In Depth — The Four Layers

10 rungs. Decision note.

1. No single control stops injection, so the design question is what the layers are and what each is for.
2. **Input layer** — what reaches the model: source validation, provenance labelling, structural separation of untrusted content.
3. **Model layer** — instructions, formatting, and whatever the provider's own training gives you. It reduces frequency and establishes nothing.
4. **Tool layer** — what the model may invoke and with what arguments and authority. This is where enforcement is real, because it is deterministic code.
5. **Output layer** — what leaves: egress control, rendering rules, and never treating model output as trusted input downstream.
6. **Break the instinct to weight them evenly** — the model layer is the one people invest in and the only one that cannot be made reliable.
7. So the weighting is inverted from intuition: most of the engineering belongs in the tool and output layers, because those are ordinary deterministic software.
8. Which is the whole content of the 2024-2026 convergence — capabilities, information-flow labels, and reference monitors are all tool-layer mechanisms.
9. CaMeL is the reference design: a privileged model plans from the trusted query, a quarantined model reads untrusted data with **no tool access**, and an interpreter tracks provenance and checks policy before each call.
10. Which is the dual-model pattern, and being able to describe it is a strong answer, because it is the shape of the only defences that measure well on AgentDojo.

> **Position to defend:** Name the four layers and what each can and cannot guarantee. · Why is the intuitive weighting wrong? · Describe CaMeL's separation in two sentences.

## Note 11 · Least-Privilege Tool Design

11 rungs. **Break:** take one tool and count how many records it can reach for a caller who should see one.

1. Note 7 said fewer and narrower tools; this is what narrower means concretely.
2. **Scope by data, not by action** — a tool that fetches an employee record should fetch the caller's record by default, not any record by id.
3. Which turns an authorisation question into an argument the attacker cannot supply, and that is the strongest form available.
4. Where an id argument is genuinely needed, the tool authorises the caller against that specific id **inside the tool**, not at the route.
5. **Break the route-level guard** — a check at the entry point decides which agent runs and cannot decide which record is touched, so a caller with legitimate access to the system gets illegitimate access to a record.
6. Which means the two checks answer different questions and neither substitutes for the other.
7. Tools should be **audience-segregated** at registration, so an agent is never handed a tool outside its role.
8. Read and write should be separate tools with separate authority, because the blast radius differs by orders of magnitude.
9. Arguments should be **schema-validated** before execution, since a schema is a deterministic control and a prompt instruction is not.
10. Destructive operations should be **irreversible-by-exception**: soft delete, confirmation, or a reversal path.
11. And every guard needs a test, because a guard that is never exercised is a guard that can become vacuous without anyone noticing.

> **Position to defend:** Why is scoping by data stronger than scoping by action? · What question does a route-level check answer, and what can it not answer? · Why does a guard need a test specifically?

## Note 12 · The Confused Deputy Problem

10 rungs. No break — this is the mechanism behind note 11's rung 5.

1. A confused deputy is a program with more authority than its caller, tricked into using that authority on the caller's behalf.
2. It is a 1988 idea and it describes an agent exactly, which is worth knowing because it means the analysis is settled.
3. The agent holds a service credential that can read every record; the user may read one.
4. **The gap between those two is the vulnerability**, and it exists whether or not anyone attacks it.
5. Injection is only the mechanism for reaching it — the same gap is reachable by an ordinary user asking an ordinary question the guard fails to catch.
6. Which is why this is not filed as a prompt-injection problem: it is an authorisation problem that injection makes easier to exploit.
7. The correct fix is that the deputy acts with the **caller's** authority, not its own — ephemeral, scoped credentials rather than a shared service account.
8. Where that is impossible, the deputy must check the caller's authority itself, on every access, against the specific resource.
9. **Every access** is the operative phrase: a check performed once at the start of a conversation does not cover the fifth tool call in it.
10. And the check must be in exactly one place, because a rule duplicated across call sites drifts, and the copy that drifts is the one nobody tests.

> **Recall:** Define the confused deputy in one sentence. · Why is this an authorisation problem rather than an injection problem? · What are the two acceptable fixes, in order of preference? · Why must the rule live in one place?

## Note 13 · Guardrail Layers In Practice

12 rungs. **Break:** take a guard model, test it on a phrasing it has not seen, and record the drop.

1. The obvious defence is a classifier that reads inputs and outputs and blocks the bad ones.
2. It is sold heavily, it is easy to add, and it does real work on known attacks.
3. **Break it** — a leading guard model scoring 91.0% on benchmark attacks drops to **33.8%** on novel ones.
4. And established classifiers detect only **7 to 37%** of indirect injections against agents.
5. Which is the same lesson as note 2: measuring a defence on a fixed set measures memorisation, and the attacker is not drawing from your set.
6. Open-weight safety training compounds it — it can be removed with roughly ten fine-tuning examples and under five dollars of compute, so a self-hosted safety layer is a speed bump.
7. So a guard model is a **filter**, not a boundary, and the failure is treating a probabilistic filter as a control.
8. Filters still earn a place: they cut volume, they catch the unsophisticated majority, and they generate the signal that tells you an attack is happening.
9. Which is the honest framing — guardrails are **detection and noise reduction**, and enforcement lives in the tool layer.
10. Deterministic guardrails are different in kind and should not be lumped in: schema validation, allowlists, regex over structured fields, egress rules.
11. Those hold, because they do not generalise and therefore cannot fail to generalise.
12. So the practical stack is deterministic rules for enforcement, a classifier for volume and telemetry, and neither described as the other.

> **Position to defend:** State the two numbers that break the guard-model instinct. · What is a guard model actually good for? · Why do deterministic rules hold where classifiers do not?

## Note 14 · Human-In-The-Loop As A Control

10 rungs. Decision note.

1. Some actions should not be automated, and the control is a person approving them.
2. It works because it inserts a non-model decision into the chain, which is the only thing injection cannot argue with.
3. Which makes it the strongest available control for irreversible operations, and the reason it is worth its friction.
4. **Break it — ASI09.** The human approves what the agent proposes, and the agent is fluent, confident and usually right.
5. So approval degrades into a click, and the control quietly becomes a log entry.
6. Which means the design question is not whether to add a human but **what the human is shown**.
7. An approval prompt must show the **effect**, not the intent: this record, these fields, this value, not I will update the employee's details.
8. And it must be **specific and rare** — approval fatigue is the mechanism by which this control fails, so asking for everything is equivalent to asking for nothing.
9. So the rule is that human review is reserved for the irreversible and the consequential, and is rendered as a diff rather than a sentence.
10. Interrupt-and-resume is the implementation shape, which makes this a state-management problem as much as a security one.

> **Position to defend:** Why can injection not argue with this control? · What is the named failure mode and what causes it? · State the rule for what gets shown and what gets asked.

## Note 15 · Kill Switches, Circuit Breakers, And Denial-Of-Wallet

9 rungs. Decision note.

1. Every control so far assumes you find out. This note is about the period before you do.
2. **Denial-of-wallet** is the attack with no other name: not taking the system down, but making it expensive, by driving loops and long contexts.
3. It is attractive because it needs no vulnerability — normal use at abnormal volume is sufficient.
4. Which makes the per-task token budget from Block 5 note 14 a **security control**, not only a cost lever, and framing it that way is the better interview answer.
5. A **kill switch** is the ability to stop a specific agent, tool, or tenant without a deploy.
6. Its value is entirely in being pre-built, because during an incident nobody is writing a feature flag.
7. A **circuit breaker** protects you from a failing dependency, which is a different failure from a rate limit protecting you from a caller — the distinction is Block 6 note 11 and it is a common stumble.
8. Rate limits, quotas and budgets all bound blast radius in time, which is the same job as least privilege doing it in scope.
9. So the note's claim is that availability and cost controls belong in a security block, because an agent's damage is measured in actions taken before someone noticed.

> **Position to defend:** Why is a token budget a security control? · What must be true of a kill switch before an incident? · State the difference between a breaker and a rate limit in one sentence.

---

# D · Data, Supply Chain, And Sandboxing

## Note 16 · PII And Data Governance End To End

11 rungs. No break — this is a survey of where data escapes.

1. An agent over personal data creates copies of it in places nobody designed as a data store.
2. **Prompts** carry it into the provider's infrastructure on every call.
3. **Traces** carry it into the observability backend, which is Block 2 note 8 seen from the security side.
4. **Logs** carry it wherever logs go, usually with the longest retention and the loosest access.
5. **Caches** carry it forward in time, and a semantic cache can carry it sideways to another user, which is Block 5 note 7.
6. **Checkpoints and memory** persist it into conversation state that outlives the session.
7. Which is six copies from one request, and the governance question is whether each was intended.
8. Minimisation is the primary control: do not put in the prompt what the task does not need.
9. Redaction is second, and note 8 of Block 2 gives its cost — over-redaction destroys the debuggability you kept the data for.
10. Retention is third and is the one with legal teeth, because a deletion request has to reach all six copies.
11. Which is the practical test of a data-governance story: name where a deleted record still exists an hour later.

> **Recall:** Name the six places one request copies data to. · State the three controls in order. · What is the practical test of the story?

## Note 17 · Model And Tool Supply Chain

9 rungs. No break.

1. The model, its libraries, and every tool the agent can call are software you did not write.
2. **LLM03 and ASI04** name this, and the agentic version is broader because an agent's tools are configuration rather than code.
3. Which is the important difference: adding a capability can be a config change, so it does not pass through code review.
4. **MCP servers** sharpen it — a server is a third party that supplies tool descriptions, and tool descriptions are prompt content the model obeys.
5. So a malicious or compromised server can inject by description alone, without ever being called.
6. Which makes tool descriptions a supply-chain artifact that needs pinning and review like a dependency.
7. Model weights from an open registry are a second surface, with poisoning and backdoors as the named risks.
8. And a provider-side model update is a silent supply-chain change, which is why the version attribute in Block 2 note 3 is a security control as well as an observability one.
9. So the practical position: pin what you can, review tool descriptions as code, and record model versions so a behaviour change can be attributed.

> **Recall:** Why is the agentic supply chain broader than the LLM one? · How does an MCP server attack without being called? · Which earlier attribute turns out to be a security control?
>
> **Stop:** No signing, attestation, or SBOM tooling depth. Rabbit hole, marked, binding.

## Note 18 · Sandboxing Code Execution

9 rungs. Decision note.

1. Some agents write and run code, which converts every previous attack into remote code execution — **ASI05**.
2. **Break the mitigation-by-prompt instinct immediately** — nothing in note 1 changes, so the model cannot be trusted to refuse to write harmful code.
3. So the control is entirely environmental: the code runs somewhere it cannot do damage.
4. Which means an isolated runtime, no credentials in the environment, no network egress by default, a filesystem that is ephemeral, and limits on CPU, memory and wall time.
5. **Egress is the one people forget**, and it is the trifecta's third leg from note 4 arriving in a new form.
6. Timeouts matter more than they look, because an infinite loop is a denial-of-wallet without an attacker.
7. The output of the sandbox is untrusted data, so it must not be treated as trusted input downstream — LLM05 again.
8. And the sandbox boundary is the security boundary, which means it should be a process or VM boundary rather than a language-level one.
9. If code execution is not a requirement, not having it is the strongest control available and costs nothing.

> **Position to defend:** Why is prompt-level mitigation not available here? · Name the five properties of the runtime. · Which earlier concept does egress control repeat?

---

# E · Verification

## Note 19 · Threat Modelling An Agent Before It Ships

10 rungs. **Practice — produced against a real system, not recalled.**

1. Everything above is a vocabulary; a threat model is the artifact that applies it to one system.
2. It answers four questions in order, and the order matters.
3. **What does the agent have access to** — tools, data, credentials, and what each can reach.
4. **What untrusted content does it read** — every input path, including ones nobody calls an input, like a fetched record.
5. **What can it cause** — the set of actions with external effect, and which are irreversible.
6. **Who is the principal** — on whose authority does each action run, and where does that authority come from.
7. The trifecta from note 4 is then applied to the answers, and a yes on all three names the exposure concretely.
8. **Break the ambition to be exhaustive** — a threat model that tries to enumerate attacks is never finished; one that enumerates **capabilities** is finished in an afternoon.
9. Because capabilities are finite and attacks are not, and bounding what is possible is the durable output.
10. The deliverable is a short document naming the blast radius and the controls that bound it, and it is worth more in an interview than any individual fix, because almost nobody has written one.

> **Practice:** Produce the four answers for a real system, apply the trifecta, and write the blast-radius paragraph.

## Note 20 · Red Teaming

11 rungs. **Practice — write and run the suite against your own agent.**

1. A threat model says what is possible; a red team finds out what actually works.
2. Which makes it the verification step, and the only one that produces evidence rather than argument.
3. Start from the threat model rather than from a list of attack strings, so the attacks target capabilities you already know are reachable.
4. Four families are enough to start. **Direct override** — instructions to ignore instructions, in several phrasings.
5. **Authorisation probing** — ask for another principal's data, directly, then obliquely, then by supplying an id.
6. This family is the one that finds real bugs most often, because it needs no injection at all — it just asks.
7. **Indirect payloads** — instructions planted in content the agent reads, if any input path allows it.
8. **Exfiltration** — having established the agent will follow an instruction, see whether the trifecta's third leg exists.
9. **Break the pass/fail framing** — a single run is a sample, exactly as in Block 1 note 17, so an attack that fails once has not failed.
10. So attacks are run repeatedly and reported as a rate, and the suite becomes a regression set that runs on every change.
11. Which is where this block joins Block 1: a security attack suite is an eval set whose expected outcome is a refusal, and it belongs in the same harness.

> **Practice:** Write ten attacks across the four families, run each five times, report rates, and keep the file as a regression suite.

---

## Deferred, deliberately

| Topic | Goes to |
|---|---|
| Judge-based safety scoring, calibration | Block 3 |
| Should-refuse cases as an eval category, harness mechanics | Block 1 notes 10 and 22 |
| Cost caps as a cost lever rather than a control | Block 5 note 14 |
| Retries, timeouts, backoff, circuit breakers | Block 6 note 11 |
| Cascading failure mathematics | Block 6 |
| ACL-aware retrieval, vector store isolation | Blocks 7-8 |

---

## Xarvis mapping

**Filled after learning, not before.** Each concept lands in **applicable**, **theory-only**, or **parked**.

Going in — this block has the widest expected split, and one item is not hypothetical:

- **Live, not theoretical:** ASI03 Identity and Privilege Abuse, which is what both known authorisation holes are. Note 12's confused deputy is the mechanism, note 11 rung 5 is why a route-level check did not cover it, and note 12 rung 10 is why a rule duplicated across two call sites drifted. The fix belongs in the same file as the story.
- **Applicable:** direct injection (2), excessive agency (7), least-privilege tool design (11), human-in-the-loop as a control (14), token budgets as a security control (15), threat modelling (19), and the attack suite (20). The attack suite is also build item 4, so it is written once and counted twice.
- **Theory-only:** indirect injection (3) and the lethal trifecta (4) — leg one only, since no untrusted content is ingested. Also ASI07 inter-agent communication and ASI10 rogue agents, since the agents never talk to each other. Sandboxing (18) — no code execution.
- **Parked for the retrieval product:** indirect injection via retrieved documents, vector and embedding weaknesses, memory poisoning through an index.

That split is the correct outcome, not a gap. The rule stands: learn it, discuss it, never claim to have built it.

---

## Sources to verify against

- [OWASP Top 10 for Agentic Applications 2026 — ASI01-ASI10](https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications)
- [The agentic list explained, with mitigations](https://neuraltrust.ai/blog/owasp-agentic-ai-top-10)
- [The state of AI guardrails — what they stop and what they miss](https://medium.com/@adnanmasood/the-state-of-ai-guardrails-what-they-stop-and-what-they-miss-ceb668f693bc)
- [Defeating prompt injections by design — CaMeL](https://css.csail.mit.edu/6.5660/2026/readings/camel.pdf)
- [Adaptive evaluation of out-of-band defences against prompt injection](https://arxiv.org/html/2606.26479v1)
- Simon Willison — [prompt injection tag](https://simonwillison.net/tags/prompt-injection/), the reference for this whole area
- Corpus: `09-safety-security-and-responsible-ai/` Q1-Q20, Q26-Q33, Q36-Q42 · `06-agents-and-tool-use/` Q26, Q39-Q41
