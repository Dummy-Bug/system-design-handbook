Geoffrey Litt, design engineer at Notion, at the AI Engineer conference — [thread](https://x.com/geoffreylitt/status/2072522251300409556). The claim: it is still important to understand the code your agents write, and the interesting part is **why**, because the obvious reason turns out to be the wrong one.

Worth reading even though it is not a backend topic. The failure mode it names — quietly losing the ability to participate in your own project — is the one that shows up in an interview as being unable to defend work you shipped.

---

## The problem it starts from

Agents write a lot of code now, and keeping up is genuinely hard. A pull request can carry hundreds of changed files.

Reading a diff line by line is one way to understand what happened. It is also, at this scale, the **only** way most people have, which is why it stops working.

---

## Why understand at all — the wrong answer first

Most people, asked why humans still need to read agent output, say: **to verify.** The agent does something, you check it, thumbs up or thumbs down.

![[AI-Engineering/essential/Images/understand-to-verify-loop.png]]

Correctness can mean many things — matches the spec, is well architected, will not take down production — but they are all the same shape of question, and it is a question **agents are steadily getting better at answering themselves**. Given a decent verification loop, the human's share of correctness checking shrinks over time.

The talk's position on that is not defensive: that is fine, and even good. Nobody wants to be handed a broken thing so they can catch it.

But if verification were the only reason to understand, then better agents would eventually remove the need entirely. Which is where the argument turns.

---

## The right answer: understand to participate

![[AI-Engineering/essential/Images/understand-to-participate-loop.png]]

It is never one loop. A project is many loops with the agent, and **what you carry from one loop into the next is your understanding.** Reviewing changes you — you come away knowing something, and that knowledge is the raw material for the next idea.

> [!important] The difference is between two kinds of participation. Checking output is a **yes or no** contribution. Having the next idea requires a rich set of concepts already in your head, ones you can recombine quickly without stopping to ask anyone how the system works. That fluency is what lets you take a creative leap, and it only exists if you understood the previous loops.
>
> Better agents do not remove this need, because it was never about catching their mistakes.

### Cognitive debt

The talk borrows a term popularised by Margaret-Anne Storey and written about by Simon Willison: **cognitive debt**, by analogy with technical debt.

You get away with it for a while. Things are going well, code is landing, and then at some point you notice you no longer know what is going on and can no longer meaningfully steer. The debt came due.

The analogy is exact in the way that matters: the cost is not paid when you incur it, so nothing stops you incurring it.

---

## The three techniques

![[AI-Engineering/essential/Images/three-techniques.png]]

All three are borrowed from education rather than from software, which is the talk's actual move — this is not the first time humans have thought about how to make understanding happen.

---

## 1 · Explanations

When an agent finishes work, that is an opportunity for an explanation. The most naive one is the diff itself — the raw material of what changed.

The generative question the talk asks: **what would the best possible explanation be?** If you sent a team away for a year to build a personalised curriculum for this one code change, what would come back?

Litt's answer is a skill called `/explain-diff` that produces a structured explainer document. Four principles in how it is built:

**Background first.** Not what changed — how the system works. Skippable if you already know it, and personalisable to what you already know.

**Intuition before details.** State the goal of the change in plain language before any code appears. For his example, the whole commit reduces to: make the garden feel three-dimensional using only 2D drawing tricks.

![[AI-Engineering/essential/Images/explainer-intuition-before-details.png]]

**Interactive figures, used sparingly.** Where it helps, something to fiddle with — dragging objects around and watching coordinates change. The talk is explicitly cautious here: interactivity can be a crutch and can be slop. Used tastefully it conveys things a static picture cannot.

**Literate code diffs.** Then the code, but not a list of files in alphabetical order. Prose, in a sensible order, explaining what each part does before showing it.

![[AI-Engineering/essential/Images/explainer-literate-code-diff.png]]

> [!note] A detail worth noticing: he prints these and reads them at a coffee shop. AI took a process that required sitting at an IDE and turned it into something closer to reading a textbook about your own pull request.

### The quiz, and why it is the sharpest idea here

Reading is easy to fake — including to yourself. Litt describes sending a colleague a PR he believed he had understood, and being unable to answer her first basic question.

The inspiration is Andy Matuschak's line **books don't work**: it is far too easy to read something and not notice you did not understand it. Matuschak and Michael Nielsen's response was to embed spaced-repetition questions inside the essay itself, so you cannot get through it without demonstrating recall.

So every explainer document ends with five medium-difficulty questions.

![[AI-Engineering/essential/Images/explainer-quiz.png]]

> [!important] The rule attached to it is the whole point: **he does not send code for review until he can pass the quiz about what his agent wrote.** It sounds silly and it repeatedly catches him.
>
> He calls it a **speed regulator**. Everything about working with AI pushes toward going faster, and every incentive points that way. The quiz is a counterbalancing force that keeps the loop running at the speed of **understanding** rather than the speed of correctness.

The skill is published as a GitHub Gist, in two variants — one outputs HTML, one outputs a Notion page.

---

## 2 · Micro-worlds

From Seymour Papert's idea of **living in Mathland**: children learn French by living in France, so where do they go to learn maths? Papert had kids program a drawing robot called the turtle. The point was never the robot — the point was that the kids were changed by programming it.

Applied to code: have the agent build you a small, throwaway environment whose only purpose is to let you **inhabit** the system rather than read about it.

Two examples from the talk.

**A debugger for a language interpreter.** Litt was implementing Prolog and struggling to intuit what was happening inside it. Claude built him a purpose-made debugger — scrub a timeline through execution step by step, see the stack and which rules are being evaluated at each point, and leave notes to himself on the timeline.

![[AI-Engineering/essential/Images/microworld-prolog-debugger.png]]

He used it to fix specific bugs, but the real payoff was peripheral: while fixing them he was **getting a feel for the machine**. If an agent had simply fixed the bugs, none of that would have accumulated.

**A migration you play through.** Porting his personal website between frameworks, the agent wrote a script that seemed to work — but reading the script gave him no feel for what it did. So he had Claude build what amounts to a video game: old site on the left, new site on the right, a next button, and at each step the commands being run and the files moving in a visible tree. The result is close to doing the migration by hand, without the pain of doing it by hand.

> [!important] The generalisation: **agents can write code whose purpose is helping you understand other code.** Not software to ship — debuggers, playgrounds, simulations, built for one person and thrown away. That only became reasonable because writing code got cheap.

---

## 3 · Shared spaces

The first two techniques are about understanding alone. On a team, the harder problem is understanding **together**, because that shared understanding is what lets people communicate at all — shared names for parts of a system, for concepts, for UI elements.

![[AI-Engineering/essential/Images/shared-understanding.png]]

Two directions Notion is exploring:

**Multiplayer threads with humans and agents together.** Rather than each person talking privately to their own agent, everyone is in one space and can see each other's exchanges. The analogy given is moving from one-on-one conversations to Slack channels — you learn from traffic that was not addressed to you.

**Documents you can discuss.** When an agent produces a plan, a comment on it opens a conversation with teammates in the same place, rather than the plan living locally on one machine where nobody else can react to it.

---

## The closing argument

The talk widens at the end: it is not just important to understand how **code** works, it is important that humans understand how **everything** works — and that this is now genuinely contested rather than assumed.

It goes back to Alan Kay, one of the people who invented the modern graphical computer, and an essay he wrote in 1972 imagining a portable computer for children. The illustration shows two kids sitting on grass holding flat, tablet-sized screens.

### What that picture actually shows

Look at it today and you assume you know what they are doing: watching something. Consuming.

They are not. In Kay's description they are **playing a game and editing its code while they play**, changing the rules to learn physics. Change gravity, see what happens, change it again.

So the machine was never the achievement. **The achievement was supposed to be what happened to the kids** — they would come away thinking better, because they had been inside a system rather than in front of one.

### What Kay says went wrong

His complaint ever since is that computers drifted away from that. They became very good at delivering things to you and much less good at making you more capable. You use a phone; the phone does not leave you sharper.

The tool became the point, and the person stopped being the point.

### Why AI might reverse it

Building a custom tool used to be expensive. If you did not understand how some part of your system worked, nobody was going to spend two days building a visualiser so you could watch it — you read the code and got on with it.

**Code being nearly free changes that calculation completely.** A purpose-built debugger for one specific confusion, used once and thrown away, now costs a prompt. That is exactly what the micro-worlds section describes, and it is Kay's vision arriving in a form he could not build in 1972.

> [!important] The dominant story about AI is **take the human out of the loop** — automate the step, remove the person, done.
>
> The inversion here is to use the same capability to put yourself **further in**. Not fewer loops, but loops you can see inside, because the AI will write you the simulation that lets you inhabit the thing you were previously only reading about.
>
> Same technology, opposite direction. That is the whole argument, and it is why the talk ends on it rather than on the techniques.

## What to actually take from this

- **Separate the two reasons for reviewing.** Correctness checking is being automated and that is fine. Retaining the ability to have the next idea is not automatable, and it is the reason to stay in the loop.
- **Cognitive debt is real and silent.** You will not notice you have taken it on until you cannot steer.
- **Make the agent explain, structured** — background, then intuition, then code as prose. Not a diff.
- **Test yourself, do not re-read.** A five-question quiz you must pass before shipping is a concrete mechanism against the fluency illusion. Recognising an explanation is not the same as being able to produce it.
- **Ask for throwaway tools to inhabit a system**, not just fixes to it. The peripheral understanding is the product.
- **Understanding is a speed regulator, deliberately.** The bottleneck it imposes is the point, not a defect.
