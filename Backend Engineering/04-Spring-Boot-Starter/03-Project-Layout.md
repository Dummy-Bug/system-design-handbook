A freshly generated project contains a lot of files, and the volume is the first thing that feels overwhelming. It is worth going through them, because each one has a job and none of it is arbitrary.

# Why there are so many

> [!info] **Think of a base-model car.** It arrives with everything a car needs to run — engine, seats, the basic structure — and nothing more. From there you add what you want: a better sound system, different interiors, third-party extras. A generated Spring Boot project is the base model. Everything necessary to run is already wired up, and additions go on top.

The volume is a direct consequence of Spring Boot being opinionated. It made the sensible choices already, and those choices are files.

# The layout

```
SpringDemoTodo/
├── .gitignore              ← paths version control should skip
├── .gradle/                ← local cache (generated)
├── build/                  ← compiled output (generated)
├── build.gradle            ← project configuration
├── settings.gradle
├── gradle/wrapper/
├── gradlew                 ← wrapper script, Unix
├── gradlew.bat             ← wrapper script, Windows
└── src/
    ├── main/
    │   ├── java/com/example/demo/
    │   │   └── TodoAppApplication.java
    │   └── resources/
    │       └── application.properties
    └── test/
```

# `.gitignore`

**A list of paths that version control should ignore**, so they are never pushed to a **hosting platform**. Generated output and local caches belong here — they can always be rebuilt, and they would only bloat the repository.

# `build.gradle`

The main configuration file, and the one you will edit most.

```groovy
1  // build.gradle
2  plugins {
3  	id 'java'
4  	id 'org.springframework.boot' version '4.0.2'
5  	id 'io.spring.dependency-management' version '1.1.7'
6  }
7
8  group = 'com.example'
9  version = '0.0.1-SNAPSHOT'
10 description = 'TodoApp'
11
12 java {
13 	toolchain {
14 		languageVersion = JavaLanguageVersion.of(21)
15 	}
16 }
17
18 repositories {
19 	mavenCentral()
20 }
21
22 dependencies {
23 	implementation 'org.springframework.boot:spring-boot-starter-web'
24 	compileOnly 'org.projectlombok:lombok'
25 	developmentOnly 'org.springframework.boot:spring-boot-devtools'
26 	annotationProcessor 'org.springframework.boot:spring-boot-configuration-processor'
27 	annotationProcessor 'org.projectlombok:lombok'
28 	testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
29 }
30
31 tasks.named('test') {
32 	useJUnitPlatform()
33 }
```

What is in it:

- **`dependencies`** — the block you touch most. Every third-party or Spring library your project uses is declared here. The choices made in the generator appear as lines in this block, and adding one later means adding a line.
- **`repositories`** — where to download those dependencies from. `mavenCentral()` is the usual public repository.
- **`java { toolchain }`** — which Java version to build against.
- **`group`, `version`, `description`** — project metadata. **The version matters if you ever publish this as a library, and it is what you increment on release.**

> [!important] In short, `build.gradle` is your **project configuration**: what dependencies it uses, what Java version, where to fetch things from. It is the Gradle equivalent of Maven's `pom.xml`, with the added ability to hold real logic.

## Every ecosystem has one of these

The idea is not Java-specific, which makes it easier to recognise:

| Ecosystem | File | Holds |
|---|---|---|
| Gradle / Java | `build.gradle` | Dependencies, versions, repositories, metadata |
| Node.js | `package.json` | Dependencies, scripts, metadata |
| Ruby | `Gemfile` | Dependencies |

Some ecosystems split configuration across several files; some keep it in one. The job is the same everywhere.

# `.gradle/`

A generated folder — the **local cache** for the project. **Downloaded dependencies and compiled classes live here.**

Change your dependencies and Gradle needs to fetch the new ones; that is what this folder holds. It is safe to delete: rebuild and it comes back.

> [!info] Inside it you may notice a folder for parallel workers. Gradle can run work concurrently in the background, and the properties and configuration for those workers are kept there.

# `gradlew` and `gradlew.bat`

Two scripts that let you drive the build from a terminal.

**`gradlew`** is a shell script, identifiable from its first line:

```bash
1  #!/bin/sh
```

That shebang is the giveaway. It is for Unix-based systems — Linux and macOS.

**`gradlew.bat`** is its Windows counterpart, a batch file. If you have used Windows you have probably seen a `.bat` before: a script of commands to be executed.

Together they mean the build can be run the same way on any operating system, from the command line.

# `build/`

The other generated folder — the **compiled output** of your project.

```
build/
├── classes/java/     ← compiled classes
├── generated/sources/
├── resources/main/
├── libs/             ← the packaged jars
└── tmp/
```

The path structure under `classes` mirrors your source tree, which makes sense — it is the same code, compiled.

The interesting part is `libs`, which holds what the build actually produced:

```text
1  demo-0.0.1-SNAPSHOT.jar          19,705,563 bytes
2  demo-0.0.1-SNAPSHOT-plain.jar         8,073 bytes
```

> [!important] **Two jars, and the size difference is the point.** The plain jar is 8 KB — just your compiled code. The other is nearly 20 MB, because it packages your code **together with every dependency and an embedded web server**, so it can run on its own. That self-contained one is what gets deployed.

Like `.gradle/`, this folder is disposable. Delete it, rebuild, and it returns.

# `src/`

Where you actually spend your time. Two halves:

- **`src/test/`** — unit tests and integration tests.
- **`src/main/`** — the application itself, split again into `java/` for code and `resources/` for configuration and static files.

## The main class

Every Java application needs a `main` method somewhere to start it. In a generated project that is the application class:

```java
1  // src/main/java/com/example/demo/TodoAppApplication.java
2  package com.example.demo;
3
4  import org.springframework.boot.SpringApplication;
5  import org.springframework.boot.autoconfigure.SpringBootApplication;
6
7  @SpringBootApplication
8  public class TodoAppApplication {
9
10 	public static void main(String[] args) {
11 		SpringApplication.run(TodoAppApplication.class, args);
12 	}
13
14 }
```

Line 11 is what starts the Spring Boot application. Everything Spring does begins from that call, which makes it the natural place to put anything that must happen **before** the framework comes up.

## `resources/`

Holds `application.properties` — where application-specific values are configured. That file is substantial enough to be worth its own treatment.
