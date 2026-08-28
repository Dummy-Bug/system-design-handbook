Every question below is one that gets asked in a real Java backend interview at the 3–5 year mark, and every one of them is answerable from parts `01` to `09` of this folder. Nothing here needs a topic we have not covered yet — no JPA, no Security, no Actuator, no microservices. That filter is the whole point of the list: it is the slice of the interview you can already walk into and win.

The ordering is by **how often the question actually comes up**, not by difficulty and not by the order we studied it. A question that appears in almost every list and in first-person interview reports outranks one that appears in a single senior-level blog post, however interesting the second one is.

---

# How to read this list

**Three tiers, by frequency.**

| Tier | What it means | How many |
|---|---|---|
| **Tier 1** | Turns up in nearly every source, at every experience level. If you can only prepare twenty questions, prepare these. | 20 |
| **Tier 2** | Common. Expect several of these in a typical two-round loop, especially from an interviewer who probes past the first answer. | 28 |
| **Tier 3** | Occasional, and the mark of an interviewer who actually knows the framework. High reward when it lands. | 25 |

**The ▲ marker.** Public interview-question lists are mostly curated by content sites, not transcribed from real interviews, so cross-source frequency alone is a weak signal. **A ▲ means the question is corroborated by a first-person interview report or a company-tagged question log**, not only by question banks. Those are the ones with hard evidence behind them.

**The last column** points at the note that answers it, so a question you fumble turns straight into a section to reread.

> [!important] **Recency was weighted deliberately.** Sources dated 2026 were preferred, and where a 2026 source and an older one disagreed on what gets asked, the newer won. Two shifts show up clearly in the recent material: interviewers now push past the definition into mechanism — not what is auto-configuration but how does it decide — and **scenario questions have partly displaced annotation trivia**. Prepare the follow-up, not just the answer.

---

# Tier 1 — asked in almost every interview

| # | Question | | Answered in |
|---|---|---|---|
| **Q1** | What is the difference between Spring and Spring Boot? | ▲ | `01`, `09` |
| **Q2** | What does `@SpringBootApplication` do internally, and which three annotations does it combine? | ▲ | `09` |
| **Q3** | How does Spring Boot auto-configuration work under the hood? | ▲ | `09` |
| **Q4** | What is dependency injection, and what are its types? | ▲ | `04` |
| **Q5** | What is Inversion of Control, and what is the IoC container? | ▲ | `04`, `05` |
| **Q6** | What are the bean scopes in Spring, and which is the default? | ▲ | `06` |
| **Q7** | Describe the Spring bean lifecycle. | ▲ | `07` |
| **Q8** | Constructor, setter or field injection — which is preferred, and why? | ▲ | `04`, `05` |
| **Q9** | What is a Spring bean? | ▲ | `05` |
| **Q10** | What are Spring Boot starters, and what does a starter dependency actually contain? | ▲ | `03`, `09` |
| **Q11** | What does `@Autowired` do, and how does Spring decide what to inject? | ▲ | `05` |
| **Q12** | What is a circular dependency, and how do you fix it? | ▲ | `06` |
| **Q13** | What is the difference between `@Component` and `@Bean`? | | `05` |
| **Q14** | Two beans implement the same interface — what happens, and how do `@Primary` and `@Qualifier` differ? | | `05` |
| **Q15** | What is the difference between `BeanFactory` and `ApplicationContext`? | ▲ | `05` |
| **Q16** | What does `@ComponentScan` do, and which packages does it scan by default? | ▲ | `05`, `09` |
| **Q17** | What is the difference between singleton and prototype scope? | ▲ | `06` |
| **Q18** | Spring Boot runs an embedded Tomcat — what port does it use, and how do you change it? | ▲ | `02` |
| **Q19** | What is the difference between `@Component`, `@Service`, `@Repository` and `@Controller`? | ▲ | `05` |
| **Q20** | How does a Spring Boot application actually start — what happens inside `SpringApplication.run()`? | ▲ | `02`, `09` |

> [!question]- **The follow-up each Tier 1 question gets, and the answer that satisfies it.** Open this when the first answers feel solid — the follow-up is where the interview is actually decided.
> **Q1 → so is Spring Boot a framework in its own right?** No. It is Spring Core plus opinionated defaults, an embedded server and starter dependencies. You are still writing Spring; Boot removed the configuration.
> **Q2 → what if you delete `@SpringBootApplication` and add the three by hand?** Identical behaviour. It is a convenience meta-annotation, nothing more.
> **Q3 → how does it decide?** The classpath is the signal. Each auto-configuration class is guarded by `@Conditional…` checks, and it is only a candidate if it is **listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`**. It is not found by component scanning — this is the single most common wrong answer given to this question.
> **Q4 → which one does Spring itself recommend?** Constructor. It makes the field `final`, makes the object impossible to construct half-built, and makes it testable with plain `new` and no container.
> **Q6 → what does singleton actually mean here?** One instance **per bean definition per container**, not one per class and not the singleton design pattern. Two definitions of the same class give you two objects.
> **Q7 → where do `@PostConstruct` and `@PreDestroy` sit?** After dependency injection and the Aware callbacks, before the bean is handed out; and on container shutdown, before `DisposableBean.destroy`.
> **Q12 → why does constructor injection fail where field injection survives?** The three-level cache can hand out an early reference to a half-built object, but a constructor has not returned yet, so there is no object to hand out. Also worth saying: **since Boot 2.6 a cycle fails at startup by default**, and `spring.main.allow-circular-references=true` is a way to postpone the redesign, not a fix.
> **Q14 → which wins if both are present?** `@Qualifier`. The injection point naming a bean explicitly beats the container's default choice.
> **Q17 → what does the container stop doing for a prototype?** Destruction callbacks. Spring builds it, injects it, hands it over and forgets it — `@PreDestroy` never runs.
> **Q20 → name one thing that happens before your first bean is built.** The bean definitions are all read first, because scope and laziness decide what gets instantiated at all.

---

# Tier 2 — asked often

| # | Question | | Answered in |
|---|---|---|---|
| **Q21** | Is a singleton bean thread-safe? | ▲ | ⚠ gap — see below |
| **Q22** | What happens when you inject a prototype bean into a singleton? | | `06` |
| **Q23** | What is eager versus lazy initialization, and what does `@Lazy` change? | | `06` |
| **Q24** | What do `@PostConstruct` and `@PreDestroy` do, and when do they run? | ▲ | `07` |
| **Q25** | There are three ways to define an init callback — what are they, and in what order do they run? | | `07` |
| **Q26** | What are `@ConditionalOnClass` and `@ConditionalOnMissingBean`, and what do they let a starter do? | ▲ | `09` |
| **Q27** | How do you disable or exclude a specific auto-configuration class? | ▲ | `09` |
| **Q28** | What is the difference between `@SpringBootApplication` and `@EnableAutoConfiguration`? | | `09` |
| **Q29** | What is `spring-boot-starter-parent`, and what do you get from inheriting it? | | `03`, `09` |
| **Q30** | How does Spring Boot know the version of a dependency you never specified? | ▲ | `03`, `09` |
| **Q31** | What is autowiring, and what are its modes? | ▲ | `08` |
| **Q32** | What is the Maven build lifecycle, and what are its phases? | ▲ | `03` |
| **Q33** | What are Maven dependency scopes, and what is the default? | ▲ | `03` |
| **Q34** | What is a `pom.xml`, and what does it contain? | ▲ | `03` |
| **Q35** | What is the difference between `@Controller` and `@RestController`? | ▲ | `02` (partly) |
| **Q36** | What is Spring Initializr, and what are the ways to create a Spring Boot project? | ▲ | `02` |
| **Q37** | Can you build a Spring Boot application with no web server at all? | | `02`, `09` |
| **Q38** | What is `CommandLineRunner`, and when would you use it? | | `09` |
| **Q39** | What is a servlet, and what is a servlet container? | | `01` |
| **Q40** | Why should an object be a Spring bean instead of one you create with `new`? | | `04` |
| **Q41** | What name does Spring give a bean when you do not name it yourself? | | `05` |
| **Q42** | What is tight coupling, and how exactly does DI remove it? | ▲ | `04` |
| **Q43** | How do you get the list of every bean in the container? | | `05` |
| **Q44** | What is a `BeanPostProcessor`? | | `07` |
| **Q45** | What is the difference between `@ComponentScan` and `@EnableAutoConfiguration`? | | `09` |
| **Q46** | Your bean and an auto-configured bean are both candidates — which one wins? | | `09` |
| **Q47** | What happens if Spring finds no bean of the type you asked for? | | `05` |
| **Q48** | Where does Maven download JARs to, and what is the difference between the local and the central repository? | | `03` |

> [!question]- **Deep dive — the five Tier 2 answers people get wrong.** These are the ones where a confident half-answer is worse than saying you are not sure.
> **Q22 — the prototype is not re-created.** The singleton is built once, so its dependency is resolved once, so the prototype behaves like a singleton for the rest of the application's life. The honest fix is `ObjectProvider<T>` or `@Lookup`, not a bigger scope.
> **Q23 — `@Lazy` on the bean and `@Lazy` on the injection point are different things.** On the bean, it delays creation until first request. On the injection point, Spring injects a **proxy** immediately and builds the real bean when a method is first called on it — which is exactly why it breaks a circular dependency.
> **Q25 — the order is `@PostConstruct`, then `InitializingBean.afterPropertiesSet`, then the custom `init-method`.** The annotation runs first because it is applied by a `BeanPostProcessor` that runs before the interface callback. Saying they run in the order you declared them is wrong.
> **Q30 — two mechanisms, and interviewers want both.** `spring-boot-starter-parent` inherits a `<dependencyManagement>` block from `spring-boot-dependencies` that pins hundreds of versions. If you cannot inherit the parent, you import the same BOM with `<scope>import</scope>` instead.
> **Q46 — order matters, and it is not alphabetical.** Auto-configuration is applied **after** your own beans are registered, and `@ConditionalOnMissingBean` then sees yours and backs off. This is why defining a bean silently replaces Boot's default rather than colliding with it.

---

# Tier 3 — asked occasionally, and by the deeper interviewers

| # | Question | | Answered in |
|---|---|---|---|
| **Q49** | What is a `BeanDefinition`, and when is it created? | | `05`, `07` |
| **Q50** | How does Spring use reflection to create your objects? | | `05` |
| **Q51** | What is the difference between `BeanFactoryPostProcessor` and `BeanPostProcessor`? | | `07` (partly) |
| **Q52** | What are the Aware interfaces, and what would you actually use one for? | | `07` |
| **Q53** | What replaced `spring.factories` for registering auto-configurations? | | `09` |
| **Q54** | How would you write your own auto-configuration or your own starter? | | `09` (partly) |
| **Q55** | Why is a `@Configuration` class itself a bean? | | `06` |
| **Q56** | What are the limitations of autowiring? | | `08` |
| **Q57** | How do you configure a bean in XML — `constructor-arg`, `property`, `ref`? | | `08` |
| **Q58** | XML or annotations — which would you choose, and why? | | `08` |
| **Q59** | Can XML configuration and annotations coexist in one container? | | `08` |
| **Q60** | How do you inject a `List`, `Set` or `Map` into a bean? | | `08` |
| **Q61** | What is an inner bean? | | `08` |
| **Q62** | What do `@Import` and `@ImportResource` do? | | `08`, `09` |
| **Q63** | Does a JAR contain the JARs it depends on? | | `03` |
| **Q64** | What is the classpath, and who sets it? | | `03` |
| **Q65** | What is the difference between a JAR and a WAR, and when would you still build a WAR? | | `03` |
| **Q66** | What are Maven archetypes? | | `03` |
| **Q67** | What is the difference between `mvn package`, `mvn install` and `mvn deploy`? | | `03` |
| **Q68** | Which HTTP status codes do you return, and for what? | | `01` |
| **Q69** | What is the difference between `GET` and `POST` beyond where the data goes? | | `01` |
| **Q70** | What is content negotiation, and where have you seen Spring do it? | | `02` |
| **Q71** | How do you run a block of code once, at application startup? | | `09` |
| **Q72** | How do you find out why a bean you expected is not in the container? | | `09` |
| **Q73** | The container starts and immediately shuts down — why? | | `02`, `09` |

> [!example]- **The two Tier 3 answers that make an interviewer sit up.** Both are things you have measured in these notes rather than read.
> **Q72 — run the app with `--debug` and read the CONDITIONS EVALUATION REPORT.** It prints a positive and a negative list, and the negative entry names the condition that failed and the bean that displaced it, like `found beans of type '…' jsonMapper (OnBeanCondition)`. Naming that report is a much stronger answer than describing what you would guess.
> **Q73 — nothing kept the JVM alive.** A non-web application has no server thread, so `main` returns as soon as `run` finishes. Adding a web starter puts Tomcat on the classpath, auto-configuration starts it, and its threads hold the process open. This one is a favourite because it separates people who have run a Boot app without a web dependency from people who have not.

---

# Questions in scope whose answer the notes do not yet contain

**These are gaps, not out-of-scope items** — the question is about something we covered, but the specific answer is not in the note. Worth closing by hand before an interview.

| Question | Where the gap is |
|---|---|
| **Q21** — is a singleton bean thread-safe? | `06` teaches singleton scope but never addresses concurrency. The answer: **the container gives you one instance, and guarantees nothing about it.** Tomcat serves requests on a pool of around 200 threads, all sharing that one bean, so any mutable field on it is a race. Stateless beans are safe by construction. |
| **Q35** — `@Controller` vs `@RestController` | `02` only ever uses `@RestController`. The missing half: `@Controller` returns a **view name** for a template engine to render; `@RestController` is `@Controller` plus `@ResponseBody`, so the return value is serialised into the response body. |
| Full DispatcherServlet request flow | `01` covers servlets and `02` covers the endpoint, but nothing walks Tomcat thread → `DispatcherServlet` → `HandlerMapping` → `HandlerAdapter` → `HttpMessageConverter` → response. Commonly asked as describe the flow of a request. |
| Maven dependency conflict resolution | `03` covers transitive dependencies and `<scope>` but not **nearest-wins mediation**, `<exclusions>`, or `mvn dependency:tree` for diagnosing a version clash. This is the practical half of the Maven question. |
| When proxies are created in the lifecycle | `07` covers `BeanPostProcessor` but not that AOP proxies are what the post-processor returns — which is why the bean you get injected is not always the object your constructor built. Needs AOP first. |
| Writing a custom starter end to end | `09` shows the `imports` file and the conditions, which is most of it, but not the two-module starter/autoconfigure convention. |

---

# What is deliberately not in this list

So you know the list is filtered rather than thin. **Every one of these is a genuinely high-frequency Spring Boot interview topic, and none of it is covered by parts `01`–`09` yet:**

`application.properties` and `@Value` · profiles · `@ConfigurationProperties` · Spring Data JPA, repositories, `@Entity`, lazy loading and the N+1 problem · `@Transactional` and its self-invocation trap · Spring AOP · Spring Security, JWT and OAuth2 · Actuator · exception handling with `@ControllerAdvice` · request validation · `@RequestBody`, `@PathVariable` and `@RequestParam` · testing with `@SpringBootTest` and `@MockBean` · caching · `@Async` and `@Scheduled` · WebFlux · microservices and Spring Cloud.

That is roughly the second half of the interview. It arrives as the series continues.

---

# Sources

**Class A — first-person interview reports and company-tagged question logs.** These are what the ▲ marker is based on.

| Source | What it is | Recency |
|---|---|---|
| [InterviewEra — Infosys Java Developer questions](https://interviewera.com/interview-questions/companies/infosys/java-developer) | Company-tagged question log with difficulty ratings | Updated 2026-06-05 |
| [Glassdoor — Java Spring Boot Developer interview questions](https://www.glassdoor.com/Interview/java-spring-boot-developer-interview-questions-SRCH_KO0,26.htm) | Candidate-submitted questions, per company | Rolling |
| [anjitagargi/JavaSpringBoot_Interview_Questions](https://github.com/anjitagargi/JavaSpringBoot_Interview_Questions) | GitHub repo of questions its author states were asked in interviews | Rolling |
| [Medium — My Infosys interview experience, Java + Spring Boot](https://medium.com/devindepth/my-infosys-interview-experience-java-spring-boot-questions-that-got-me-selected-with-answers-68e2ed6e1fb4) | Single-candidate experience report, with the rounds | 2026 |
| [Medium — Java backend interview questions, 4–5 years experience](https://medium.com/@ajit-gupta/java-backend-interview-questions-4-5-years-experience-d043d6301186) | Experience report at exactly this YOE band | March 2026 |
| [Fishbowl — Infosys Java and Spring Boot interview thread](https://www.fishbowlapp.com/post/hi-tomorrow-i-have-interview-with-infosys-on-java-and-spring-boot-can-you-tell-me-how-will-be-the-interview-or-any-experience-you-xoqj-5) | Practitioner thread on what the round contains | Rolling |
| [YouTube — TCS technical round, 4 years experience](https://www.youtube.com/watch?v=Pfo2WffobXo) | Walkthrough of a reported TCS round, Java + Spring Boot | April 2026 |
| [javaready — Top 30 Spring Boot questions asked at TCS and Infosys](https://javaready.hashnode.dev/top-30-spring-boot-interview-questions-asked-in-tcs-and-infosys-with-answers-2025) | Company-attributed set | 2025 |

**Class B — curated question banks, used for the frequency count.** A question appearing across many of these independently is the frequency signal; none of them is evidence on its own that a question was asked.

| Source | Size and shape | Recency |
|---|---|---|
| [roadmap.sh — Spring Boot questions](https://roadmap.sh/questions/spring-boot) | 65 questions, tiered beginner / intermediate / advanced | 2026 |
| [InterviewBit — Spring Boot](https://www.interviewbit.com/spring-boot-interview-questions/) | 40+, with a separate tricky-questions section | 2026 |
| [InterviewBit — Spring](https://www.interviewbit.com/spring-interview-questions/) | 70+, strongest source for Spring Core and XML | 2026 |
| [GeeksforGeeks — Spring Boot](https://www.geeksforgeeks.org/springboot/spring-boot-interview-questions-and-answers/) | 50, split freshers / intermediate / experienced | 2025–26 |
| [Coding Shuttle — 100 questions for 2 to 5 years experience](https://www.codingshuttle.com/blogs/100-spring-boot-interview-questions-with-answers-for-2-to-5-years-experienced-java-developers/) | 100, aimed at exactly this YOE band | 2026 |
| [Hirist — Top 100+ Spring Boot](https://www.hirist.tech/blog/top-40-spring-boot-interview-questions/) | 100+, explicitly bucketed by years of experience | 2026 |
| [Hirist — Top 20 Maven](https://www.hirist.tech/blog/top-20-maven-interview-questions-and-answers/) | 20, several scenario-shaped | 2026 |
| [VamsiLabs — Spring Boot interview guide](https://vamsilabs.netlify.app/springboot/spring-boot-interview-guide/) | Mechanism-first, best on the three-level cache and conditions | 2026 |
| [VamsiLabs — Top 40 with answers](https://vamsilabs.netlify.app/interview/spring-boot/) | 40, grouped by subsystem | 2026 |
| [Toptal — Top 11 technical Spring questions](https://www.toptal.com/spring/interview-questions) | 11, all Spring Core, screening-oriented | 2026 |
| [SoftwareTestingHelp — Top 48 Spring](https://www.softwaretestinghelp.com/spring-interview-questions/) | 48, heavy on Spring Core and XML | 2026 |
| [InterviewKickstart — Spring concepts](https://interviewkickstart.com/blogs/interview-questions/spring-concepts-interview-questions) | Grouped by concept | 2026 |
| [GoLinuxCloud — 45+ for experienced developers](https://www.golinuxcloud.com/spring-boot-interview-questions-experienced/) | 45+, experienced-only framing | 2026 |
| [Medium — Ajay Rathod, experienced Spring and Spring Boot, 5–10 years](https://rathod-ajay.medium.com/experienced-spring-spring-boot-interview-questions-for-java-developers-5-10-years-updated-for-782cecd1d763) | Senior-band question set | April 2026 |
| [Edureka — Top 50 Maven](https://www.edureka.co/blog/interview-questions/maven-interview-questions/) | 50, standard Maven set | 2025 |
| [GoLinuxCloud — Maven questions](https://www.golinuxcloud.com/top-maven-interview-questions-answers-experienced/) | 50, freshers and experienced | 2026 |

**Class C — reference material, used to check that an answer is correct rather than to source a question.**

| Source | Used for |
|---|---|
| [Spring Framework docs — customizing the nature of a bean](https://docs.spring.io/spring-framework/reference/core/beans/factory-nature.html) | Lifecycle callback ordering |
| [Spring Framework docs — container extension points](https://docs.spring.io/spring-framework/reference/core/beans/factory-extension.html) | `BeanPostProcessor` and `BeanFactoryPostProcessor` |
| [Spring Boot docs — auto-configuration](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html) | How candidates are loaded and when they back off |
| [`@EnableAutoConfiguration` javadoc, Boot 4.1](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/autoconfigure/EnableAutoConfiguration.html) | The current annotation contract |
| [reflectoring.io — hooking into the Spring bean lifecycle](https://reflectoring.io/spring-bean-lifecycle/) | Ordering of Aware callbacks against post-processors |

> [!info] **A note on what these sources can and cannot prove.** Cross-source frequency is the best public signal available for what gets asked, but it is a proxy: the banks copy from each other, which inflates a question's apparent frequency without adding evidence. The ▲ marker exists to separate the questions with a first-hand report behind them from the ones that are merely widely republished. Where the two disagree, trust the ▲.

---

# What this list established

| | |
|---|---|
| **Scope** | 73 questions, every one answerable from parts `01`–`09` |
| **Tier 1** | 20 questions — auto-configuration, DI, IoC, scopes, lifecycle, starters, the container |
| **Tier 2** | 28 questions — the follow-ups, plus Maven and the servlet layer |
| **Tier 3** | 25 questions — mechanism, XML, packaging, HTTP |
| **▲** | corroborated by a first-person report or company-tagged log, not just a question bank |
| **The single most-asked** | **the three annotations inside `@SpringBootApplication`**, and how auto-configuration decides |
| **The most-failed** | **auto-configuration is discovered by scanning** — it is not; it is the `AutoConfiguration.imports` file |
| **Gaps to close by hand** | singleton thread safety · `@Controller` vs `@RestController` · the DispatcherServlet flow · Maven conflict mediation |
| **Not covered yet** | properties and profiles · JPA · transactions · AOP · Security · Actuator · testing · microservices |
