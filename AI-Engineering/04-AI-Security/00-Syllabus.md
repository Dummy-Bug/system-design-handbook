#ai-engineering #security #guardrails #owasp #prompt-injection #block-4 #syllabus

# Block 4 · AI Security & Guardrails — Syllabus

20 concepts. **Generic** — the field, not Xarvis. Map afterwards.

> Learn the full surface first, *then* decide what Xarvis can demonstrate. Several concepts here (indirect injection, inter-agent communication, rogue agents) are things Xarvis structurally cannot exercise — which is exactly why the syllabus must not be derived from it.

**Currency check (2026-07-30) — this is the block that moved most.** There are now **two OWASP lists**, not one:

- **OWASP Top 10 for LLM Applications v2.0 (2025)** — still current for LLM apps generally
- **OWASP Top 10 for Agentic Applications (2026)** — brand new, `ASI01`–`ASI10`, aimed specifically at autonomous tool-using systems

The agentic list is the more relevant one for a tool-calling agent, and it is new enough that most candidates won't know it exists. Learn both; lead with the agentic one when the system in front of you is an agent.

---

## A · The core problem

**1. Why prompt injection is architecturally unsolved**
The context window has no privilege separation between instructions and data. It's all tokens. Why this is a design property rather than a bug to be patched, and why no filter closes it.

**2. Direct injection vs jailbreak**
Different attacker, different target, different owner. A jailbreak attacks the model's trained behaviour; an injection attacks *your application*. Why conflating them leads to fixing the wrong layer.

**3. Indirect injection**
The attack arrives inside content the system ingests — a retrieved document, an email, a web page, a tool result, an image. Why it's more dangerous than direct injection: the victim never sees the attack. The channels it can arrive through.

**4. The lethal trifecta**
Private data access + exposure to untrusted content + an exfiltration channel. Remove any one leg and the system stops being exploitable *by construction* rather than by hoping the model refuses. How to use it as a design-review instrument.

**5. Assume the system prompt leaks**
Why extraction always eventually succeeds, and what follows: no secrets and no unenforced authorization logic in the prompt. The prompt is documentation, not a boundary.

## B · The two OWASP lists

**6. OWASP LLM Top 10 v2.0 (2025) — walk it**
Prompt injection · sensitive information disclosure · supply chain · data and model poisoning · improper output handling · **excessive agency** · system prompt leakage · vector and embedding weaknesses · misinformation · unbounded consumption. Not recitation — knowing which two or three dominate for a given system.

**7. Excessive agency in depth (LLM06)**
Its sub-types: excessive functionality, excessive permissions, excessive autonomy. Mapping every tool to blast radius. The distinguishing question: what is the *reversibility* of this action?

**8. OWASP Top 10 for Agentic Applications (2026) — walk it**
`ASI01` Agent Goal Hijack · `ASI02` Tool Misuse & Exploitation · `ASI03` Agent Identity & Privilege Abuse · `ASI04` Agentic Supply Chain Compromise · `ASI05` Unexpected Code Execution · `ASI06` Memory & Context Poisoning · `ASI07` Insecure Inter-Agent Communication · `ASI08` Cascading Agent Failures · `ASI09` Human-Agent Trust Exploitation · `ASI10` Rogue Agents.

**9. What the agentic list adds that the LLM list missed**
Persistence (memory poisoning survives the turn), identity (an agent acting *as* a user), composition (failures cascading across agents), and the human factor (approval fatigue as an attack surface). These are the genuinely new ideas.

## C · Defences that hold

**10. Defence in depth — the four layers**
Input filtering · prompt hardening · output validation · **architectural isolation**. Why the first three reduce the attack surface and only the fourth limits blast radius. The reframe: not "is this secure" but "what's the damage if it fails."

**11. Least-privilege tool design**
Scoping each tool to the minimum capability. Why an access check living *inside* a tool body is structurally fragile — a new tool that forgets it silently has none. Enforcing at registration instead.

**12. The confused deputy problem**
Why an LLM agent is close to a worst case for it. Agent authentication to downstream systems: shared service account vs acting on behalf of the user, and what each leaks.

**13. Guardrail layers in practice**
Input guards, output guards, action guards. Fail-closed on actions, fail-open with logging on style. The latency and false-positive budget. Tooling: NeMo Guardrails, Llama Guard, ShieldGemma, provider moderation APIs.

**14. Human-in-the-loop as a control**
Where gates go. The distinction that matters: a *selection* prompt is not an *approval* gate. And the failure mode the agentic list names explicitly — approval fatigue turning gates into rubber stamps.

**15. Kill switches, circuit breakers, and denial-of-wallet**
Two different mechanisms for two different problems, and why you need both. Unbounded consumption as an economic attack. Spend caps and blast-radius caps.

## D · Data, supply chain, and sandboxing

**16. PII and data governance end to end**
Detection, redaction, tokenisation. Where PII enters (prompt, retrieved context, tool result, trace) and where it leaks (completion, log, eval set). Right-to-erasure when data is in fine-tuning weights or a vector index.

**17. Model and tool supply chain**
Safetensors vs pickle and why deserialisation is code execution. Weights provenance. Third-party MCP servers as an unvetted trust boundary — what to check before approving one.

**18. Sandboxing code execution**
Isolating a code-executing agent. Filesystem, network, process, and resource limits. Why "unexpected code execution" earned its own entry on the agentic list.

## E · Verification

**19. Threat modelling an agent before it ships**
The walkthrough: trust boundaries, data flows, capability inventory, blast radius, abuse cases. Producing a document a security reviewer will accept.

**20. Red teaming**
Manual vs automated, pre-launch vs continuous. Building an attack suite. How red-teaming differs from a penetration test. Turning findings into durable regression tests rather than a one-off report.

---

## Notes to write

```
04-AI-Security/
├── 00-Syllabus.md      ← this file
├── 00-Resources.md
├── 01-Why-Injection-Is-Unsolved.md
│   … through …
└── 20-Red-Teaming.md
```

## Deferred

| Topic | Goes to |
|---|---|
| Judge-based safety scoring, calibration | Block 3 |
| Cost caps as a cost lever rather than a control | Block 5 |
| Cascading failure math (`p^n`) | Block 6 |
| ACL-aware retrieval, vector store isolation | Blocks 7-8 |

## Xarvis mapping

*Filled after learning.* **applicable** / **theory-only** / **parked**.

Going in — this block has the widest expected split:

- **Applicable:** direct injection (2), excessive agency (7), least-privilege (11), HITL as a control (14), threat modelling (19), attack suite (20)
- **Theory-only:** indirect injection (3) and the lethal trifecta (4) — Xarvis has leg one only, it never ingests untrusted content. Also `ASI07` inter-agent communication and `ASI10` rogue agents, since its three agents never talk to each other. Sandboxing (18) — no code execution.
- **Parked for the retrieval product:** indirect injection via retrieved documents, vector/embedding weaknesses, memory poisoning through an index.

That split is the correct outcome, not a gap. The rule stands: learn it, discuss it, never claim to have built it.

## Sources to verify against

- [OWASP Top 10 for Agentic Applications 2026 — ASI01-ASI10](https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications)
- [OWASP LLM Top 10 2026, annotated](https://www.wraith.sh/learn/owasp-top-10-llm-annotated)
- [OWASP LLM Top 10 v2.0 explained](https://repello.ai/blog/owasp-llm-top-10-2026)
- [Security testing & mitigation guide](https://www.siemba.io/owasp-top-10-llm-security-testing)
- Simon Willison — [prompt injection tag](https://simonwillison.net/tags/prompt-injection/), the reference for this whole area
- Corpus: `09-safety-security-and-responsible-ai/` Q1-Q20, Q26-Q33, Q36-Q42 · `06-agents-and-tool-use/` Q26, Q39-Q41
