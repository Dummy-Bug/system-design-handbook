Mocking and arrange-act-assert are the shape of a unit test. This is that shape in a real Spring project, on the layer where most of your tests will live.

# Where tests go

```text
  src/
  ├── main/java/com/example/FakeCommerce/services/CategoryService.java
  └── test/java/com/example/FakeCommerce/services/CategoryServiceTest.java
```

> [!important] **`src/test/java` mirrors `src/main/java`, package for package.** Gradle treats it as a separate source set compiled and run only for tests. Mirroring the structure is convention, and it is what makes a test findable from the class it covers.

> [!important] **The service layer is where most of your testing time goes**, because that is where the business logic is. Controllers mostly delegate and repositories mostly generate queries; the service is the part with branches worth checking.

# The two dependencies you already have

```groovy
  testImplementation 'org.springframework.boot:spring-boot-starter-data-jpa-test'
  testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
```

Between them these bring JUnit 5, Mockito, AssertJ and the Spring test slices. Nothing else is needed for a service test.

# The setup

```java
1  // src/test/java/com/example/FakeCommerce/services/CategoryServiceTest.java
2  @ExtendWith(MockitoExtension.class)
3  public class CategoryServiceTest {
4
5      @Mock
6      private CategoryRepository categoryRepository;
7
8      @InjectMocks
9      private CategoryService categoryService;
10 }
```

Three annotations, and each answers a question raised in `02-Unit-Tests`.

> [!important] **`@Mock` creates the stand-in.** 
> A fake `CategoryRepository` with every method present and every method doing nothing until told otherwise. **No database connection is opened**, so running the test cannot touch or pollute real data.

> [!important] **`@InjectMocks` creates the real thing.** 
> An actual `CategoryService`, constructed by calling its real constructor — and Mockito supplies the mocks as the arguments. The class under test is genuine, only its dependencies are not.

> [!important] **`@ExtendWith(MockitoExtension.class)` keeps Spring out of it.** 
> It wires the two annotations above and nothing else. **No component scan, no context, no connection pool** — just a Java object constructed with fakes.

That last one is the performance decision. Starting a Spring context takes seconds, constructing one object takes microseconds, and a suite of hundreds runs in the time one context load would take.

# Stubbing

A mock returns null for everything until told what to do.

```java
  when(categoryRepository.save(any(Category.class))).thenReturn(testCategory);
```

> [!important] Read as: **when anyone calls `save` with any `Category`, return this object.** `when(...).thenReturn(...)` is the whole stubbing vocabulary for most tests.

> [!info] **`any(Category.class)`** is an argument matcher — it says the argument's value is not what this test is about. Where the value does matter, pass it literally: `findById(1L)` stubs only that call.

# A complete test

```java
1  @Test
2  void createCategory_savesAndReturnsCategory() {
3      // arrange
4      CreateCategoryRequestDto dto = CreateCategoryRequestDto.builder().name("Test Category").build();
5      Category testCategory = Category.builder().name("Test Category").build();
6      testCategory.setId(1L);
7      when(categoryRepository.save(any(Category.class))).thenReturn(testCategory);
8
9      // act
10     Category result = categoryService.createCategory(dto);
11
12     // assert
13     assertEquals("Test Category", result.getName());
14     assertEquals(1L, result.getId());
15 }
```

**Lines 4 to 7 arrange** — the input, the object the mock will hand back, and the stub connecting them. **Line 10 acts**, calling the real service. **Lines 13 and 14 assert.**

> [!info] Line 6 sets the id separately rather than in the builder because `id` comes from `BaseEntity` and the class uses `@Builder` rather than `@SuperBuilder` — so the builder does not expose inherited fields. A small detail that decides how the arrange step is written.

## The naming convention

```text
  method _ [condition _] expected result
```

Two parts are always present — **what was called** and **what should happen**. The condition sits between them and is **optional**, appearing only when the method has more than one path:

```text
  createCategory_savesAndReturnsCategory
  getCategoryById_whenFound_returnsCategory
  getCategoryById_whenNotFound_throwsResourceNotFoundException
```

| name | underscores | why |
|---|---|---|
| `createCategory_savesAndReturnsCategory` | 1 | one path, so there is no case to distinguish |
| `getCategoryById_whenFound_returnsCategory` | 2 | one of two paths |
| `getCategoryById_whenNotFound_throwsResourceNotFoundException` | 2 | the other path |

> [!important] A test name is almost never read in the file it lives in. **It is read in a failure report by someone who did not write it**, with no surrounding context — and `CategoryServiceTest > getCategoryById_whenNotFound_throwsResourceNotFoundException FAILED` names the class, the method, the scenario and the expectation in one line, without anybody opening anything.

Which is what the alternatives lose:

| name | what the failure report gives you |
|---|---|
| `test1` | nothing |
| `testCreate` | something about creating |
| `testCreateCategory` | the method, but not the scenario or the expectation |
| `shouldCreateCategory` | reads well, still no scenario |

> [!info] The mix of underscores and camelCase looks wrong for Java, and is deliberate. **Underscores separate the parts, camelCase runs inside each part.** This is the one place the convention is bent, because legibility in a failure report matters more here than consistency with the rest of the codebase.

> [!warning] No `test` prefix. `testCreateCategory` is JUnit 3 residue, from when the framework located tests by looking for methods whose names began with `test`. `@Test` states it now, so the prefix is noise repeated in every report.

> [!info] `@DisplayName("returns the category when it exists")` puts a real sentence in the report, but only in the report — grep, IDE navigation, stack traces and build logs all still show the method name. It is an addition to a good name, never a replacement for one.

A side effect worth noticing: a test class where every name carries a single underscore is saying the service has no branches. Which is either true, or a sign the failure paths were never tested.

## One test per branch

Those last two names are the same method twice.

```java
1  @Test
2  void getCategoryById_whenNotFound_throwsResourceNotFoundException() {
3      // arrange
4      when(categoryRepository.findById(2L)).thenReturn(Optional.empty());
5
6      // act and assert
7      assertThrows(ResourceNotFoundException.class, () -> categoryService.getCategoryById(2L));
8  }
```

> [!important] **Every conditional creates a branch, and every branch needs a test.** `getCategoryById` either returns a category or throws — two paths, two tests. A method with a null check and a default has more.

> [!info] **`assertThrows` merges act and assert**, because the call has to happen inside the assertion for the exception to be caught. It is the one place the three steps become two.

# Prove the test can fail

A test that has only ever passed has not been shown to work.

> [!important] **Break the implementation deliberately and watch the test go red.** Make `createCategory` return `null` and the assertion fails, reporting expected the object, got null. Restore it and the test passes again.

That takes ten seconds and rules out the most embarrassing possibility: **a test that passes regardless of what the code does** — the assertion that compares nothing, the stub that was never called.

# Test-driven development

The obvious objection: you wrote the code, then wrote a test arranged so the code passes. What did that prove?

> [!important] **TDD writes the tests first.** Define inputs and expected outputs for the good and bad cases before implementing anything. Every test fails at the start, and the implementation progresses by making them pass one at a time.

> [!warning] **It is much less common in practice than in writing about practice.** 
> The usual order is implementation first, tests after — and the reason is visible in the test above. **You cannot write the stubs until you know what the method calls**, so a test-first attempt on non-trivial code becomes a cycle of writing a test, discovering a dependency, mocking it, returning to the logic, and discovering another.

> [!important] Which does not make the test worthless. **Tests are reviewed** — a test that does not genuinely exercise the branch it names should not get through review. And its value was never in proving the code correct today; it is in **failing tomorrow, when someone changes something and does not realise what it touched.**

# On generating tests

Test code is repetitive enough that generating it is tempting, and it mostly works — the arrange-act-assert skeleton is nearly identical across a service layer, and a tool given one example will find the branches you missed, including the null-quantity default and the empty-list case.

> [!warning] **Review it as carefully as you would review a stranger's.** The failure mode is not broken tests, it is **tests that pass while testing nothing.**

> [!warning] The clearest example is from a front-end review: the generated test **mocked the component it was supposed to be testing**, mounted the mock, and asserted against it. Everything passed. Nothing was verified — the real component was never involved.

> [!important] That is the rule from `02-Unit-Tests` violated exactly. **The thing under test must be real; only its dependencies are mocked.** A mock of the subject tests the mock. It is easy to write by accident, easy to generate by accident, and it looks identical to a working test in the report.
