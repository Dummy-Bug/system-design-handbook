The twenty **Tier 1** questions from `01-Spring-Core-And-Boot-Questions.md`, each with the answer to give in the room. **Every claim is taken from Spring's own documentation, and every claim that could be run was run** against Spring Boot **4.1.1** on Java **25** — the measured output is quoted where it settles something.

---

# Q1 — Spring vs Spring Boot

> **Interviewer** — What is the difference between **Spring** and **Spring Boot** ?

> [!important] **Spring** is the framework. At its core it is **dependency injection** and the **IoC container**, and on top of that core sit the modules — **Spring MVC**, **Spring Data**, **Spring Security**, **Spring AOP**.

> [!important] **Spring Boot** is a separate **project** that sits above all of these modules as an **automation layer**. What it removed is the **setup**.
> Before Boot, starting a Spring MVC project meant three things by hand
> 1. **writing the configuration** — XML or a config class — to tell the container what to build.
> 2. **choosing every dependency and checking the versions were mutually compatible**.
> 3. **building a WAR to deploy into a Tomcat you had installed and configured yourself**.

Spring Boot replaces those with three mechanisms.

> 1. **Auto-configuration** — it configures your application based on the **JAR dependencies on the classpath**, so adding the web dependency gives you a working MVC stack with no configuration class.
> 2. **Starter dependencies** — one entry like `spring-boot-starter-webmvc` pulls in a **curated set of managed transitive dependencies**, and because each Boot release curates the whole list, **you do not give a version for any of them**.
> 3. **An embedded server** — **Tomcat or Jetty is a library inside your JAR**, started by your own `main` method, listening on **port 8080** by default, so you ship a runnable JAR instead of deploying a WAR into a server someone else installed.

> [!important] And it is **opinionated, not restrictive**. Spring's own word for this is **non-invasive** — at any point you can define your own configuration to replace part of the auto-configuration, and the default **backs away**. Add your own `DataSource` bean and the embedded database support is simply never created.

> [!question]- **Follow-ups.** Four probes this answer attracts.
> **So has Spring Boot replaced Spring?** No. You are still writing Spring — same beans, same IoC container, same annotations. Boot removed the configuration around them and nothing else.
> **Then can I learn only Spring Boot?** Not usefully. You can only change a default you understand, and understanding it means knowing the module being configured.
> **Does Boot make the application start faster?** No — it makes **you** start faster. Startup is if anything slower, because there is a classpath scan and a conditions evaluation on every boot.
> **Name something Boot did not change.** The programming model. A bean, an injection point and a lifecycle callback behave identically with and without Boot.

---

# Q2 — What `@SpringBootApplication` does

> **Interviewer** — What does `@SpringBootApplication` do internally, and which three annotations does it combine?

> [!important] It is a **meta-annotation** — a convenience for three annotations you would otherwise write yourself. Measured, by reading them off the annotation at runtime:
> ```
> @SpringBootApplication
>    SpringBootConfiguration   (org.springframework.boot)
>    EnableAutoConfiguration   (org.springframework.boot.autoconfigure)
>    ComponentScan             (org.springframework.context.annotation)
> ```

> 1. **`@SpringBootConfiguration`** — marks the class as a **source of bean definitions**. It is Spring's `@Configuration` with one extra property: Boot's test support can locate it automatically, and **there should be exactly one per application**.
> 2. **`@EnableAutoConfiguration`** — turns on the auto-configuration mechanism, which configures the application **from the JAR dependencies on the classpath**.
> 3. **`@ComponentScan`** — scans for components **in the package of the annotated class and every package below it**.

> [!important] **None of the three is mandatory.** Delete `@SpringBootApplication`, write the three annotations by hand, and the application behaves identically — which is the cleanest way to say that it adds no behaviour of its own. It also exposes **aliases** so you can set `@EnableAutoConfiguration` and `@ComponentScan` attributes through it, most commonly `exclude` and `scanBasePackages`.

> [!question]- **Follow-ups.** Five probes, including the one about having two of them.
> **What happens if you delete it and write the three annotations by hand?** Nothing changes. It is a convenience meta-annotation with no behaviour of its own.
> **Difference between `@SpringBootApplication` and `@EnableAutoConfiguration`?** The first is the second **plus** `@SpringBootConfiguration` and `@ComponentScan`. Using `@EnableAutoConfiguration` alone gives you auto-configuration with no component scanning.
> **Why does `@SpringBootConfiguration` exist when `@Configuration` already does?** So that Boot's test support can find **the one primary configuration class** automatically. There should be exactly one per application.
> **Can you have two `@SpringBootApplication` classes?** Not in the same context — the test support expects a single `@SpringBootConfiguration` and will not know which to bootstrap.
> **How do you exclude an auto-configuration through it?** `@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)`, or `excludeName` when the class is not on the classpath — both are aliases onto `@EnableAutoConfiguration`.

---

# Q3 — How auto-configuration works

> **Interviewer** — How does Spring Boot auto-configuration work under the hood?

> [!important] **It configures your application from the JAR dependencies on the classpath.** If HSQLDB is on the classpath and you have not configured a database connection yourself, Boot auto-configures an in-memory database. The classpath is the signal.

> [!warning] **Auto-configuration classes are not found by component scanning.** They are **listed by name** in a file inside each JAR:
> ```
> META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
> ```
> A class annotated `@AutoConfiguration` that is not in that file is never considered. This is the single most commonly given wrong answer to this question. Spring Boot **2.x** used `META-INF/spring.factories` for the same job.

Each candidate is then **guarded by conditions**, and only registers its beans if they all pass.

> 1. **`@ConditionalOnClass`** — only if a given type is on the classpath. It is evaluated by reading bytecode, so the class is checked by name without being loaded, which is why an auto-configuration can safely reference a type that may be absent.
> 2. **`@ConditionalOnMissingBean`** — only if you have not defined that bean yourself.
> 3. **`@ConditionalOnProperty`** — only if a property is set to a given value.

> [!important] **Ordering is what makes it non-invasive.** Auto-configuration is applied **after your own beans are registered**, so `@ConditionalOnMissingBean` sees yours and the default is never created. You are not overriding Boot's bean — Boot's bean does not exist.
> To see the decisions, run with **`--debug`** and read the **CONDITIONS EVALUATION REPORT**, which lists every positive and negative match with the condition that decided it. To switch one off, `@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)` or the `spring.autoconfigure.exclude` property.

> [!question]- **Follow-ups.** Five probes. The first two are where this question is actually won.
> **How are the candidate classes found?** By name, from `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` inside each JAR — **not** by component scanning. Boot 2.x used `META-INF/spring.factories`.
> **How can `@ConditionalOnClass` reference a class that might not exist?** The condition is evaluated by **reading bytecode**, so the class is checked by name and never loaded. Referencing an absent type is therefore safe.
> **What controls the order auto-configurations run in?** The `before`, `after`, `beforeName` and `afterName` attributes of `@AutoConfiguration`, plus `@AutoConfigureOrder`. It is a declared ordering, not alphabetical and not classpath order.
> **A bean you expected is not there — how do you find out why?** Run with **`--debug`** and read the **CONDITIONS EVALUATION REPORT**. The negative-match list names the condition that failed and, for `@ConditionalOnMissingBean`, the bean that displaced it.
> **How would you write your own?** An `@AutoConfiguration` class with the conditions on it, listed in the `AutoConfiguration.imports` file. By convention it goes in two modules, `acme-spring-boot-autoconfigure` and `acme-spring-boot-starter` — and **never with a `spring-boot` prefix**, which is reserved for official artefacts. Give your properties a namespace you own, not `spring` or `server`.

---

# Q4 — Dependency injection and its types

> **Interviewer** — What is dependency injection, and what are its types?

> [!important] **Dependency injection is a specialised form of Inversion of Control.** An object declares the other objects it needs — through constructor arguments, factory-method arguments, or properties set after construction — and **the container supplies them**. The object never looks its dependencies up and never constructs them.

> 1. **Constructor injection** — dependencies arrive as constructor arguments. **This is the one Spring recommends.**
> 2. **Setter injection** — the container calls a setter after constructing the object.
> 3. **Field injection** — Spring writes the field directly through reflection. It is not one of the two variants the documentation describes; it works, and it is the one to argue against.

> [!important] **Spring's stated reason for preferring constructor injection:** it lets you implement components as **immutable** objects, it **guarantees required dependencies are not null**, and the object is **always handed to the caller fully initialised**. Setter injection is for **optional** dependencies that have a sensible default.
> A large number of constructor arguments is called out in the documentation as **a bad code smell** — a sign the class has too many responsibilities. That is a feature: constructor injection makes the problem visible.

> [!question]- **Follow-ups.** Four probes, and the first one catches people who recited the list.
> **How many types does Spring's documentation actually describe?** **Two** — constructor and setter. Field injection is not presented as a variant; the documentation discusses its problems instead. Saying three without that caveat is a tell.
> **What is wrong with field injection?** The dependency is invisible from outside the class, the field cannot be `final`, and a class with twelve injected fields looks the same as one with two — so the design pressure disappears. It also cannot be constructed in a test without reflection or a container.
> **Is `@Autowired` required on a constructor?** Not if the class has only one. Spring uses the single constructor regardless.
> **What if there are several constructors?** Annotate the one to use. Only one constructor may declare `@Autowired` with `required = true`.

---

# Q5 — IoC and the IoC container

> **Interviewer** — What is Inversion of Control, and what is the IoC container?

> [!important] **Inversion of Control is the inversion of who creates what.** Normally an object constructs or looks up its own collaborators. Under IoC it only **declares** them, and something else creates them and hands them over. Dependency injection is how Spring implements it.

> [!important] **The IoC container is the thing doing the creating.** In Spring it is the `org.springframework.beans` and `org.springframework.context` packages, exposed through two interfaces:
> 1. **`BeanFactory`** — the basic container. Configuration and instantiation.
> 2. **`ApplicationContext`** — a **sub-interface** of `BeanFactory` that adds AOP integration, message resources for internationalisation, event publication, and web-aware contexts.

**What you get from it:** the container reads the configuration metadata, builds the objects, injects the dependencies, and manages the whole lifecycle. **Your classes stop containing the wiring**, so a dependency can be swapped without editing the class that uses it — which is the point of the exercise.

> [!question]- **Follow-ups.** Four probes on the distinction people blur.
> **Are IoC and DI the same thing?** No. **IoC is the principle** — something other than the object decides what it gets. **DI is one implementation** of that principle, and the one Spring uses.
> **Which packages are the container?** `org.springframework.beans` and `org.springframework.context`, exposed as `BeanFactory` and `ApplicationContext`.
> **What does the container hold?** **Bean definitions first** — name, class, scope, laziness, dependencies — and only then the objects. Definitions all exist before any object is built, because scope and laziness decide what gets built.
> **Could you have IoC without Spring?** Yes. It is a design principle; you could hand-wire everything in `main` and have IoC with no container. The container is what makes it manageable at scale.

---

# Q6 — Bean scopes

> **Interviewer** — What are the bean scopes in Spring, and which is the default?

> [!important] **Six scopes. `singleton` is the default.** Four of the six only exist in a web-aware context.
>
> | Scope | One instance per |
> |---|---|
> | **`singleton`** — the default | **container, per bean definition** |
> | **`prototype`** | **every request for the bean** |
> | `request` | HTTP request |
> | `session` | HTTP session |
> | `application` | `ServletContext` |
> | `websocket` | WebSocket lifecycle |

> [!important] **Singleton here does not mean the Gang of Four singleton.** It is **per container and per bean definition**, not one instance per class loader. Two bean definitions of the same class give you two objects, and two containers in the same JVM give you two more.

> [!warning] **Prototype beans never get their destruction callbacks.** Initialization callbacks run for every scope, but for a prototype the container hands the object over and forgets it — **`@PreDestroy` never runs**, and releasing anything expensive is the caller's job. Measured: `getBean` twice on a prototype returns two different objects, and both are unknown to the container afterwards.

> [!question]- **Follow-ups.** Four probes. The first is the most-asked follow-up in the entire Spring interview.
> **Is a singleton bean thread-safe?** **No.** The container guarantees one instance; it guarantees nothing about concurrent access. Tomcat serves requests on a pool of around 200 threads, all sharing that one object, so any mutable instance field is a race. **Stateless beans are safe by construction** — which is why nearly every service and repository is stateless. And the fix is not `synchronized` on the bean; the fix is to remove the state, or hold it in a local variable, or move it to a `request`-scoped bean.
> **How is Spring's singleton different from the Gang of Four singleton?** It is **per container and per bean definition**, not one per class loader. Two definitions of the same class give two objects.
> **What does a prototype not get?** **Destruction callbacks.** The container builds it, injects it, hands it over and forgets it — `@PreDestroy` never runs, so releasing resources is the caller's job.
> **When would you actually use prototype?** For **stateful** beans. Stateless ones have no reason not to be singletons.

---

# Q7 — The bean lifecycle

> **Interviewer** — Describe the Spring bean lifecycle.

> [!important] The container reads the configuration into **bean definitions** first, and only then starts building objects — because scope and laziness decide what gets built at all.
> 1. **Instantiate** — the constructor runs.
> 2. **Populate** — dependencies are injected. Constructor injection merges this with step 1.
> 3. **Aware callbacks** — `BeanNameAware`, `BeanFactoryAware`, `ApplicationContextAware`.
> 4. **Initialization callbacks** — see the order below.
> 5. **The bean is in use.**
> 6. **Destruction callbacks**, on container shutdown.

> [!important] **There are three ways to hook initialization, and they run in a fixed order** — measured end to end on one bean carrying all of them:
> ```
> 1 constructor -> 2 BeanNameAware(lifecycleBean) -> 3 @PostConstruct
>   -> 4 afterPropertiesSet -> 5 initMethod
>   -> 6 @PreDestroy -> 7 DisposableBean.destroy -> 8 destroyMethod
> ```
> So: **`@PostConstruct`, then `InitializingBean.afterPropertiesSet()`, then the custom `init` method** — and destruction mirrors it exactly with `@PreDestroy`, `DisposableBean.destroy()`, the custom destroy method. **`@PostConstruct` and `@PreDestroy` are the recommended ones**, because they do not tie your class to a Spring interface.

**Why not just use the constructor?** Because at constructor time the dependencies are not injected yet. `@PostConstruct` is the first point where the object is complete.

> [!question]- **Follow-ups.** Five probes, and the proxy one is where senior interviewers go.
> **What is a `BeanPostProcessor`?** A hook that gets every bean instance twice — `postProcessBeforeInitialization` and `postProcessAfterInitialization`, around the initialization callbacks.
> **How is that different from a `BeanFactoryPostProcessor`?** The factory one runs **earlier and on metadata** — it modifies **bean definitions before any instance exists**. The bean one works on **instances after they are created**. Touching instances from a `BeanFactoryPostProcessor` forces premature instantiation and is a bug.
> **When are AOP proxies created?** In **`postProcessAfterInitialization`** — the post-processor returns a proxy in place of your object. This is why the bean that gets injected elsewhere may not be the instance your constructor built, and why a self-invocation inside the class bypasses the proxy.
> **Why not do the initialization work in the constructor?** At constructor time the dependencies are not injected yet. `@PostConstruct` is the first point where the object is complete.
> **Do prototype beans reach the destruction steps?** No — initialization callbacks run for every scope, destruction callbacks do not run for prototypes.

---

# Q8 — Constructor, setter or field injection

> **Interviewer** — Which type of dependency injection do you use, and why?

> [!important] **Constructor injection, and Spring's documentation says the same.** Three reasons, in the order that convinces:
> 1. **Immutability** — the field can be `final`, so it cannot be reassigned and it is safely published to other threads.
> 2. **No half-built object** — a required dependency cannot be null, and the object is handed to the caller fully initialised.
> 3. **Testable without Spring** — `new OrderService(mockRepo)` works. Field injection forces reflection or a container in every unit test.

> [!important] **Setter injection is for optional dependencies** that have a reasonable default, or where the object genuinely needs to be reconfigured later.
> **Field injection is the one to argue against**: the dependency is invisible from outside the class, the field cannot be `final`, and a class with twelve injected fields looks exactly like a class with two — so the design pressure that constructor injection creates is gone.

**One practical detail worth stating:** `@Autowired` is **not needed on a single constructor**. If the class has exactly one constructor, Spring uses it. You only need the annotation to pick between several.

> [!question]- **Follow-ups.** Four probes that separate a memorised list from an opinion.
> **Why does `final` matter?** It makes the object immutable after construction, so the reference cannot be reassigned and is safely published to other threads. Field injection cannot give you a `final` field.
> **How do you unit-test a constructor-injected class?** `new OrderService(mockRepo)`. No container, no reflection, no Spring on the test classpath.
> **When would you deliberately use setter injection?** For an **optional** dependency with a reasonable default, or an object that genuinely has to be reconfigured after construction.
> **What does a constructor with ten arguments tell you?** Spring's own documentation calls it **a bad code smell** — the class has too many responsibilities. That is constructor injection working: it makes the problem visible instead of hiding it behind ten annotated fields.

---

# Q9 — What a Spring bean is

> **Interviewer** — What is a Spring bean?

> [!important] **A bean is an object that is instantiated, assembled and managed by the Spring IoC container.** That is the whole definition — it is not a special kind of class and it needs no interface, no annotation on the type, and no base class. An object the container did not create is just an object.

> [!important] **Every bean has a name, and the defaults are worth knowing** — measured on a running context:
> ```
> @Component class EmailNotifier   ->  emailNotifier
> @Component class SmsNotifier     ->  smsNotifier
> @Configuration class Cfg         ->  cfg
> @Bean Proto proto()              ->  proto
> ```
> A scanned component is named by the **uncapitalised simple class name**; a `@Bean` method is named by the **method name**. Both can be overridden by giving the annotation a value.

> [!question]- **Follow-ups.** Four probes, including the duplicate-name one.
> **How do you list every bean in the application?** `ctx.getBeanDefinitionNames()`, or the Actuator `/actuator/beans` endpoint on a running application.
> **What name does a bean get by default?** The **uncapitalised simple class name** for a scanned component, the **method name** for a `@Bean` method.
> **What if two beans end up with the same name?** In Spring Boot, startup fails. Measured on 4.1.1 with two `@Bean` methods both named `svc`:
> ```
> APPLICATION FAILED TO START
> BeanDefinitionOverrideException: Invalid bean definition with name 'svc' defined in
> class path resource [CfgB.class] ... since there is already [ ... CfgA.class] bound.
> ```
> Boot **disables bean overriding by default** so that an accidental clash is loud rather than silent. `spring.main.allow-bean-definition-overriding=true` permits it, but which definition wins then depends on creation order, so the honest answer is to rename one.
> **Is every object in your application a bean?** No — only the ones the container created. An object you make with `new` is just an object, and gets no injection and no lifecycle callbacks.

---

# Q10 — Starter dependencies

> **Interviewer** — What are Spring Boot starters, and what does a starter actually contain?

> [!important] **A starter is a dependency descriptor, not a library.** The JAR contains essentially no code — what it has is a `pom.xml` naming the dependencies that belong together for one job, so ordinary transitive resolution brings the rest. Spring's phrase for it is a **one-stop shop** for the technologies you need, with a **consistent, supported set of managed transitive dependencies**.

> [!important] **The second half is version management, and it is the half people forget.** Each Boot release publishes a **curated list of dependencies**, so you **give no version at all** for anything on that list — `spring-boot-starter-parent` inherits it from `spring-boot-dependencies`, which pins **686 artifacts** driven by 195 version properties. Upgrade Boot and all of them move together.

**Naming:** official starters are `spring-boot-starter-*`; that prefix is reserved, so a third-party one is named the other way round, `<project>-spring-boot-starter`.

> [!important] **The versions are chosen by testing, not by recency.** Boot 4.1.1 pins `<tomcat.version>11.0.24</tomcat.version>` while 11.0.25 is already on Maven Central — deliberately one behind, because 11.0.24 is what the release was tested against.

> [!question]- **Follow-ups.** Five probes. The Maven one is asked by anyone who has thought about it.
> **What is actually inside a starter JAR?** Almost nothing — a `pom.xml` naming the dependencies that belong together. The code lives in what it pulls in.
> **Is this a Spring Boot feature or a Maven feature?** The **machinery is Maven's** — transitive resolution, `dependencyManagement`, parent POMs, all of which predate Boot. The **content is Boot's**: knowing which artifacts and versions work together. The proof is that the same starters work in **Gradle**.
> **What does a starter add over writing `dependencyManagement` yourself?** Mechanically nothing; you could reproduce it. What you cannot reproduce is the knowledge that these versions were integration-tested together.
> **How do you override a managed version?** Set the version property Boot uses, or declare the dependency with an explicit `<version>`. Both are supported, and both mean you now own that compatibility decision.
> **How would you write your own starter?** Name it `acme-spring-boot-starter` — **never** a `spring-boot` prefix, which is reserved. Optionally split the auto-configuration into `acme-spring-boot-autoconfigure`. Use your own property namespace, not `spring` or `server`.

---

# Q11 — `@Autowired`

> **Interviewer** — What does `@Autowired` do, and how does Spring decide what to inject?

> [!important] **It marks an injection point, and Spring resolves it by type.** It works on constructors, setters, arbitrary methods and fields. On a class with a **single constructor it is not needed at all** — Spring uses that constructor anyway.

> [!important] **Resolution is by type first, then by name as the tie-break.** Three outcomes:
> 1. **Exactly one bean of the type** — injected.
> 2. **No bean of the type** — startup fails with **`NoSuchBeanDefinitionException`**: `No qualifying bean of type '…' available`. Make it optional with `@Autowired(required = false)`, `Optional<T>` or `@Nullable`.
> 3. **Several beans of the type** — **`NoUniqueBeanDefinitionException`**: `expected single matching bean but found 2: cardOne,cardTwo`. Resolve it with `@Primary` or `@Qualifier`.

> [!question]- **Follow-ups.** Four probes, and the collection one comes up constantly in plugin-style designs.
> **What happens when there is no bean of that type?** Startup fails with `NoSuchBeanDefinitionException`. Make it optional with `@Autowired(required = false)`, `Optional<T>` or `@Nullable`.
> **And when there are several?** `NoUniqueBeanDefinitionException`, naming every candidate. Resolve with `@Primary` or `@Qualifier`.
> **What if you inject `List<Rule>` instead of `Rule`?** You get **every implementation**, which is the idiomatic way to build a plugin or rule chain. `@Order` controls the sequence — measured, `@Order(1)` on `RuleA` and `@Order(2)` on `RuleB` gives `[RuleA, RuleB]`. Inject `Map<String, Rule>` and the **keys are the bean names**.
> **Does `@Autowired` ever match by name?** Type first. The field or parameter name is used only as a tie-break among several same-typed candidates.

---

# Q12 — Circular dependencies

> **Interviewer** — What is a circular dependency, and how do you fix it?

> [!important] **Two beans that need each other to be created.** A needs B in its constructor, B needs A in its constructor, so neither can be built first. Spring detects it at container load time and fails with **`BeanCurrentlyInCreationException`** — `Requested bean is currently in creation: Is there an unresolvable circular reference?`

> [!important] **Field and setter injection can survive a cycle where constructor injection cannot**, because the object exists before its dependencies are set, so Spring can hand out an **early reference** to a not-yet-finished bean. A constructor has not returned yet, so there is no object to hand out. Measured on a plain Spring container: the same X and Y cycle **starts successfully with field injection** and **fails with constructor injection**.

> [!warning] **Spring Boot prohibits it anyway.** Since Boot 2.6 the same field-injection cycle that plain Spring allows fails at startup. Measured on 4.1.1:
> ```
> APPLICATION FAILED TO START
> Relying upon circular references is discouraged and they are prohibited by
> default. Update your application to remove the dependency cycle between beans.
> As a last resort, it may be possible to break the cycle automatically by
> setting spring.main.allow-circular-references to true.
> ```
> **Naming that property is not the answer to give** — it is the thing you say you would not do. The fix is to **extract the shared behaviour into a third bean** that both depend on, which is what the cycle was telling you. `@Lazy` on one injection point works, by injecting a proxy and building the real bean on first use, but it hides a design problem rather than solving it.

> [!question]- **Follow-ups.** Five probes. The Boot-default one is the currency check.
> **Which exception, exactly?** `BeanCurrentlyInCreationException` — Requested bean is currently in creation: Is there an unresolvable circular reference?
> **Why does field injection survive where constructor injection does not?** With field or setter injection the object **exists** before its dependencies are set, so Spring can expose an early reference to the half-built bean from its singleton cache. A constructor has not returned yet, so there is no object to expose.
> **Does Spring Boot allow it?** No — **prohibited by default since Boot 2.6**. The same field-injection cycle that a plain Spring container starts fine fails under Boot with `APPLICATION FAILED TO START` and a message naming `spring.main.allow-circular-references`.
> **So is that property the fix?** No, and saying so is the trap. It postpones the redesign. **The fix is to extract the shared behaviour into a third bean** that both depend on — the cycle was telling you the responsibility was in the wrong place.
> **Is `@Lazy` on the bean the same as `@Lazy` on the injection point?** No. On the bean it delays creation. **On the injection point it injects a proxy** and builds the real bean on first method call, which is what actually breaks the cycle.

---

# Q13 — `@Component` versus `@Bean`

> **Interviewer** — What is the difference between `@Component` and `@Bean`?

> [!important] **`@Component` goes on a class and is found by scanning. `@Bean` goes on a method and hands the container an object you built yourself.**
>
> | | `@Component` | `@Bean` |
> |---|---|---|
> | Applied to | a **class** | a **method** in a `@Configuration` class |
> | Found by | **component scanning** | the configuration class being read |
> | Who constructs the object | **Spring** | **you**, in the method body |
> | Default bean name | uncapitalised class name | the **method name** |

> [!important] **The deciding question is whether you own the class.** `@Component` requires editing the source to add the annotation, so it is only available for **your own classes**. For a class from a third-party JAR — a `DataSource`, an `ObjectMapper`, a client from someone else's library — you cannot annotate it, so you write a `@Bean` method. That is also the case where you need constructor arguments or setup logic before the object is usable.

> [!question]- **Follow-ups.** Four probes, and the second is the best trick question in this whole set.
> **Which one for a class from a third-party library?** `@Bean`. You cannot add an annotation to source you do not own, so a `DataSource`, an `ObjectMapper` or someone else's client is always a `@Bean` method.
> **What happens if one `@Bean` method calls another `@Bean` method directly?** With the default `@Configuration`, Spring generates a **CGLIB subclass** that intercepts the call and returns the existing singleton. Measured — a method calling `thing()` twice produced **1** instance. Set `@Configuration(proxyBeanMethods = false)` and the same code produced **3**, because the calls are now plain Java method calls.
> **Why would anyone set `proxyBeanMethods = false`?** Faster startup and no CGLIB subclass, which also matters for native images. It is safe exactly when your `@Bean` methods do not call each other.
> **Can `@Bean` go on a method in a plain `@Component`?** Yes — that is lite mode. No CGLIB proxy, so inter-bean calls create new objects, which is the same trap as above.

---

# Q14 — Two beans of the same type

> **Interviewer** — Two classes implement the same interface. What happens when you inject that interface, and how do you resolve it?

> [!important] **Startup fails**, because resolution is by type and the type matches twice. Measured message:
> ```
> NoUniqueBeanDefinitionException: No qualifying bean of type 'in.strikes.Pay'
> available: expected single matching bean but found 2: cardOne,cardTwo
> ```

> 1. **`@Primary`** on one of the beans — it becomes the default candidate, and every injection point that gives no further hint gets it. One decision, made at the bean.
> 2. **`@Qualifier("cardOne")`** at the injection point — that site names the bean it wants. One decision per injection point.

> [!important] **When both are present, `@Qualifier` wins** — the specific request beats the general default. Measured: with `@Primary` on `Upi` and `@Qualifier("card")` at the injection point, the injected bean is **card**.

**Which to use:** `@Primary` when there is a genuine default and one odd case; `@Qualifier` when the choice is a real decision at each site. Reaching for `@Qualifier` everywhere usually means the two beans should have had different types.

> [!question]- **Follow-ups.** Four probes. The precedence one is not answered in the documentation, so knowing it marks you out.
> **If both `@Primary` and `@Qualifier` are present, which wins?** **`@Qualifier`.** Measured — with `@Primary` on `Upi` and `@Qualifier("card")` at the injection point, the injected bean is `card`. The specific request beats the general default.
> **And if neither is used?** `NoUniqueBeanDefinitionException`, listing every candidate by name: expected single matching bean but found 2.
> **Any way to resolve it without either annotation?** Yes — name the field or parameter after the bean you want, since the name is the tie-break. It works, and it is fragile, because a rename silently changes which bean you get.
> **When is `@Primary` the wrong tool?** When there is no genuine default and every call site really is making a choice. Then `@Qualifier` at each point is honest, and needing it everywhere usually means the two beans should have had different types.

---

# Q15 — `BeanFactory` versus `ApplicationContext`

> **Interviewer** — What is the difference between `BeanFactory` and `ApplicationContext`?

> [!important] **`ApplicationContext` is a sub-interface of `BeanFactory`** — verified at runtime, `BeanFactory.isAssignableFrom(ApplicationContext)` is `true`. So it is not an alternative, it is a **superset**. `BeanFactory` is the container contract: hold bean definitions, create beans, inject dependencies.

> [!important] **`ApplicationContext` adds the things an application needs**
> 1. **AOP integration.**
> 2. **Message resources** for internationalisation.
> 3. **Event publication.**
> 4. **Web-aware contexts** such as `WebApplicationContext`.
> 5. **Eager instantiation of singletons at startup**, rather than on first request — which is why a misconfigured bean fails when you start the application rather than when the first user hits it.

**Which you actually use:** `ApplicationContext`, always. Spring's own documentation uses it exclusively in describing the container, and a Spring Boot application gets a `ConfigurableApplicationContext` back from `SpringApplication.run`.

> [!question]- **Follow-ups.** Four probes; the eager-instantiation one is the behavioural difference that matters.
> **Which do you actually use?** `ApplicationContext`, always. `SpringApplication.run` hands you a `ConfigurableApplicationContext`.
> **What is the real behavioural difference?** **`ApplicationContext` pre-instantiates all singletons when the context refreshes**; `BeanFactory` creates a bean when you first ask for it. Measured — an eager `@Bean` constructor ran **before** anything was requested, while a `@Lazy` one ran only at `getBean`.
> **Why is eager instantiation a good thing?** Because a misconfigured bean then fails **when you start the application**, not on the first user request that touches it. Errors surface at deploy time rather than in production.
> **Can you turn it off?** `@Lazy` on a bean, or `spring.main.lazy-initialization=true` for the whole application — which speeds up startup and moves failures back to first use, so it is a development convenience rather than a production setting.

---

# Q16 — `@ComponentScan`

> **Interviewer** — What does `@ComponentScan` do, and which packages does it scan by default?

> [!important] **It finds annotated classes and registers a bean definition for each.** By default it detects `@Component` and everything meta-annotated with it — `@Service`, `@Repository`, `@Controller`, `@RestController`, `@Configuration` — plus any custom annotation you build on `@Component`.

> [!important] **The default is the package of the annotating class, and everything below it.** In a Boot application `@SpringBootApplication` carries the `@ComponentScan`, so **the scan root is the package of your main class**. This is why the convention is to put the main class in a **root package above everything else** — the package also becomes the search root for `@Entity` classes and other scans.

> [!warning] **Never put the main class in the default package.** With no `package` declaration, the scan root is everything, so **every class in every JAR on the classpath is read**. To widen the scan deliberately instead, use `@SpringBootApplication(scanBasePackages = "…")`.

> [!question]- **Follow-ups.** Four probes; the third is the one that shows up as a real bug.
> **What is the scan root by default?** The package of the class carrying the annotation, and every package below it. In Boot that is the package of your main class.
> **A bean in a different package is not being found — what do you do?** Widen the scan with `@SpringBootApplication(scanBasePackages = "…")`, or `@Import` the configuration class, or write a `@Bean` method for it. For a Spring-unaware third-party JAR, a `@Bean` method is usually the right answer.
> **Why is the root-package convention more than style?** Because that package is also the search root for other scans — `@Entity` classes for JPA, `@ConfigurationProperties` classes. Moving the main class deeper silently breaks those too, and the symptom looks unrelated.
> **What does it detect by default?** `@Component` and everything meta-annotated with it — `@Service`, `@Repository`, `@Controller`, `@RestController`, `@Configuration`, and any custom annotation you build on `@Component`.

---

# Q17 — Singleton versus prototype

> **Interviewer** — What is the difference between singleton and prototype scope?

> [!important] **Singleton: one instance, cached and shared. Prototype: a new instance every time the bean is requested.** Measured on a running container:
> ```
> singleton  — same object twice        : true
> prototype  — proto == proto           : false
> ```

> [!important] **Two differences that get asked as follow-ups.**
> 1. **The container stops managing a prototype once it hands it over.** Initialization callbacks run; **destruction callbacks do not**. Cleaning up is the caller's job.
> 2. **A prototype injected into a singleton stops being a prototype.** The singleton is built once, so its dependency is resolved once. Measured: the same instance is returned on every access. The fixes are `ObjectProvider<T>`, a `@Lookup` method, or a scoped proxy — **not** a wider scope.

**When to use which:** singleton for **stateless** beans, which is nearly everything in a normal application; prototype for **stateful** ones.

> [!question]- **Follow-ups.** Four probes; the first two are asked almost every time.
> **Is a singleton bean thread-safe?** No. One instance, shared across every request thread. **Stateless is what makes it safe**, and the fix for a stateful one is to remove the state — not to synchronise on the bean.
> **What happens to a prototype when the context shuts down?** Nothing. It has no destruction callbacks and the container has no reference to it.
> **You inject a prototype into a singleton and it stops behaving like a prototype — why, and how do you fix it?** The singleton is built once, so the dependency is resolved once. Use `ObjectProvider<T>` and call `getObject()`, or a `@Lookup` method, or a scoped proxy. **Not** a wider scope.
> **How do you decide?** Singleton for stateless beans, which is nearly everything. Prototype for genuinely stateful ones.

---

# Q18 — The embedded server and the port

> **Interviewer** — Spring Boot runs an embedded server. Which one, on which port, and how do you change it?

> [!important] **The server is a library inside your JAR, started by your own `main` method.** For servlet applications Boot supports **Tomcat and Jetty**, Tomcat being the default, and the default port is **8080**. Measured on 4.1.1:
> ```
> Tomcat initialized with port 8080 (http)
> Starting Servlet engine: [Apache Tomcat/11.0.24]
> Tomcat started on port 8080 (http) with context path '/'
> ```

> 1. **Change the port** — `server.port=9090`, or the environment variable `SERVER_PORT`, or `--server.port=9090` on the command line. Measured: `Tomcat started on port 9090 (http)`.
> 2. **Random free port** — `server.port=0`.
> 3. **No web server at all** — `spring.main.web-application-type=none`. To keep the web context but switch off the HTTP endpoints, `server.port=-1`.

**Why it matters beyond the trivia:** the inversion is what makes `java -jar` work. The server no longer contains your application; **your application contains the server**, which is what makes a Boot app deployable as one artefact.

> [!question]- **Follow-ups.** Five probes, and the WAR one still comes up in enterprise interviews.
> **How do you switch to Jetty?** Exclude `spring-boot-starter-tomcat` from the web starter and add `spring-boot-starter-jetty`. The auto-configuration picks whichever server is on the classpath.
> **Can you still deploy a WAR to an external Tomcat?** Yes — set `<packaging>war</packaging>`, mark the Tomcat starter `provided` so it is not bundled, and have the main class extend `SpringBootServletInitializer` and override `configure`.
> **How do you get a free port for tests?** `server.port=0`, which asks the OS for an unused one.
> **How do you run with no web server at all?** `spring.main.web-application-type=none`. To keep the web context but turn off the HTTP endpoints, `server.port=-1`.
> **Why does a web application keep running after `main` returns?** The embedded server's threads are non-daemon and hold the JVM open. A non-web Boot application exits as soon as `run` finishes — which is the usual cause of it starts and immediately stops.

---

# Q19 — The stereotype annotations

> **Interviewer** — What is the difference between `@Component`, `@Service`, `@Repository` and `@Controller`?

> [!important] **`@Service`, `@Repository` and `@Controller` are specialisations of `@Component`** for the service, persistence and presentation layers. To the container they are all components and all get scanned the same way — the difference is meaning, plus one piece of real behaviour.

> 1. **`@Component`** — the generic stereotype, for anything that does not fit a layer.
> 2. **`@Service`** — business logic. Currently no extra behaviour; it is documentation the framework can read.
> 3. **`@Repository`** — persistence, and the one with teeth: it enables **exception translation**, converting vendor-specific database exceptions into Spring's `DataAccessException` hierarchy so your service layer is not coupled to the driver.
> 4. **`@Controller`** — the web layer, where handler mapping looks for request-handling methods.

> [!important] **The reason to use the specific one is that they are targets.** The documentation's own justification is that the specialisations make classes **better suited to processing by tools and to being associated with aspects** — an AOP pointcut can match every `@Service`, which it could not do if everything were `@Component`. And they may carry additional semantics in future releases.

> [!question]- **Follow-ups.** Four probes; the first is the only one with a factual answer rather than an opinion.
> **Which of them actually does something different?** `@Repository`. It triggers `PersistenceExceptionTranslationPostProcessor`, which wraps the bean in a proxy and **translates vendor-specific persistence exceptions into Spring's `DataAccessException` hierarchy** — so your service layer never catches a Hibernate or JDBC exception directly and is not coupled to the driver.
> **Does the container treat the others differently?** No. `@Service` and `@Controller` are scanned exactly like `@Component`. `@Controller` matters to Spring MVC's handler mapping rather than to the container.
> **Then why not use `@Component` everywhere?** Because the specialisations are **targets** — an AOP pointcut can match every `@Service`, tooling can reason about layers, and the documentation reserves the right to give them more semantics later.
> **`@Controller` versus `@RestController`?** `@RestController` is `@Controller` plus `@ResponseBody`, so return values are serialised into the response body instead of being resolved as a view name.

---

# Q20 — How a Spring Boot application starts

> **Interviewer** — What actually happens when you call `SpringApplication.run()`?

> [!important] **Four steps, in this order**, from the class's own documented contract.
> 1. **Create the right `ApplicationContext`** — chosen by what is on the classpath, so a servlet application gets a web context and a plain one does not.
> 2. **Register a `CommandLinePropertySource`**, exposing the command-line arguments as Spring properties — which is why `--server.port=9090` works with no code.
> 3. **Refresh the context** — read the bean definitions, then create all the singleton beans. **This is where component scanning, auto-configuration and dependency injection all happen.**
> 4. **Trigger any `CommandLineRunner` beans** — your code, running after the context is ready.

> [!important] **It returns a running `ConfigurableApplicationContext`** — the container itself, which you can keep and query.
> Two things worth adding. **The context is refreshed before your runner is called**, so a `CommandLineRunner` can rely on every bean existing. And in a web application, `main` returning does not end the process — the embedded server's threads keep the JVM alive, which is why a non-web Boot application exits immediately and a web one does not.

> [!question]- **Follow-ups.** Five probes on what happens around the four steps.
> **What does `run` return?** A running `ConfigurableApplicationContext` — the container itself, which you can hold and query.
> **Which step does auto-configuration happen in?** Step 3, the refresh. Component scanning, auto-configuration and dependency injection all happen there; steps 1 and 2 only prepare the context.
> **`CommandLineRunner` versus `ApplicationRunner`?** The same hook with a different signature — `CommandLineRunner` gets the raw `String[]`, `ApplicationRunner` gets `ApplicationArguments` with parsed option names and values. Several of either can exist; `@Order` decides the sequence, and without it the order is undefined.
> **Why does a web application not exit when `main` finishes?** The embedded server's non-daemon threads keep the JVM alive. A non-web application exits immediately after `run` returns.
> **How do you customise the bootstrap?** `SpringApplicationBuilder` — set the `WebApplicationType`, turn the banner off, add listeners, or add extra sources — instead of the static `SpringApplication.run`.
