This is the record of the questions from `01-Spring-Core-And-Boot-Questions.md` being asked cold, and it holds three things the notes deliberately do not: **what I actually answered**, **what was missing from it**, and **the answer as it should be spoken in the room**. The notes teach the concept in prose; a prose explanation is not an interview answer. This file is where the concept gets compressed into something that can be said out loud in under a minute.

**Reread this file, not the notes, the night before an interview.** It is the only surface in this vault that is specific to what I get wrong.

---

# Scoreboard

| Q | Question | Verdict | Status |
|---|---|---|---|
| **Q1** | Difference between Spring and Spring Boot | **Partially correct** — one factual error, fresher-level depth | rung 1 worked through · to re-ask |

---

# Q1 — What is the difference between Spring and Spring Boot?

**Tier 1 ▲** · asked 2026-08-28 · notes `01`, `09` · **worked answer with diagrams and measurements: [[03-Question-Answers]]**

## What I said

> Spring is a framework while Spring Boot is one of the modules inside Spring that helps the developers with fast booting up with the application creation with minimal setup required as it's very less boilerplate and makes it very easy to getting started with the ecosystem by default configurations out of the box with the flexibility to later change these configurations if required.

## Verdict

**Partially correct.** The placement is wrong, the closing idea is the strongest part of the answer, and the depth overall is a fresher's — every claim is a benefit, none is a mechanism.

## What was wrong

**Spring Boot is not a module inside Spring.** The modules are Spring MVC, Spring Data, Spring AOP, Spring Security, and they sit on Spring Core. **Spring Boot is an automation layer above all of them** — a separate project, its own release train, its own `groupId` (`org.springframework.boot`, not `org.springframework`). An interviewer who hears module inside Spring stops trusting that the rest of the ecosystem map is in your head.

**No mechanism anywhere.** Minimal setup, less boilerplate, easy to get started — all true, all things a six-month developer would say. At 3–5 years the interviewer already assumes Boot is convenient; the question is whether you know what it is doing to be convenient. The answer has to name **auto-configuration, starter dependencies and the embedded server**, and say what each one replaced.

**Fast booting up is a phrasing risk.** It is heard as fast startup time, which Boot does not improve and arguably worsens. Say fast to get started.

**What was right, and worth keeping:** defaults out of the box with the freedom to change them later. That is the opinionated-not-restrictive point and it belongs at the end of the answer, where it landed.

## The answer to give

> Spring is the framework. At its core it is dependency injection and the IoC container, and on top of that core sit the modules — Spring MVC, Spring Data, Spring Security, Spring AOP. **Spring Boot is not one of those modules.** It is a separate project that sits above all of them as an automation layer.
>
> What it removed is the setup. Before Boot, starting a Spring MVC project meant three things by hand: **writing the configuration** — XML or a config class — to tell the container what to build; **choosing every dependency and checking the versions were mutually compatible**; and **building a WAR to deploy into a Tomcat you had installed and configured yourself**.
>
> Boot replaces those with three mechanisms. **Auto-configuration** — it reads what is on the classpath and configures the beans for it, so adding the web dependency gives you a working MVC stack with no configuration class. **Starter dependencies** — one entry like `spring-boot-starter-webmvc` pulls in the whole coherent set, and `spring-boot-starter-parent` pins their versions so they cannot clash. **An embedded server** — Tomcat is a library inside your JAR, started by your own `main` method, so you ship a runnable JAR instead of deploying a WAR into a server someone else installed.
>
> And it is **opinionated, not restrictive**. Every one of those is a default. The moment you define your own bean, the auto-configuration backs off and yours is the one that is used.

## If they probe

| Follow-up | The line that answers it |
|---|---|
| So has Spring Boot replaced Spring? | No — you are still writing Spring. Same beans, same IoC container, same annotations. Boot removed the configuration around them, nothing else. |
| Then can I learn only Spring Boot? | Not usefully. You can only change a default you understand, and understanding it means knowing the module underneath — which is why the core matters more than Boot does. |
| How does auto-configuration back off? | `@ConditionalOnMissingBean`. Auto-configuration is applied **after** your beans are registered, so the condition sees yours and the default is never created. |
| Does Boot make the application start faster? | No. It makes you start faster. Startup time is if anything slightly worse, because there is a classpath scan and a conditions evaluation on every boot. |

## Verdict on delivery

The answer above is **four beats: placement, the problem, the three mechanisms, the closing line.** Practise it as four beats rather than as a paragraph — under pressure the mechanisms are what get dropped, and they are the only part that separates this from a fresher's answer.
