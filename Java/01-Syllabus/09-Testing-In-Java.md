## Phase 9 — Testing in Java

> Interview relevance: "How would you test this?" is a standard follow-up in both LLD and system design
> rounds. Google and Amazon expect SDE-2 candidates to write testable code and know the basics of JUnit
> and Mockito. Flipkart/Rippling machine coding rounds give bonus points for including tests.

> **Note**: LLD Phase 10 covers clean code and testability principles. This phase covers the actual
> tools — JUnit 5 and Mockito — and Java-specific testing patterns.

---

### 9.1 JUnit 5 — The Testing Framework
- **Annotations**:
  - `@Test` — marks a test method
  - `@BeforeEach` — runs before each test (setup). Replaces JUnit 4's `@Before`.
  - `@AfterEach` — runs after each test (cleanup)
  - `@BeforeAll` / `@AfterAll` — runs once before/after all tests in the class (must be static)
  - `@DisplayName("descriptive name")` — human-readable test name
  - `@Disabled` — skip this test
  - `@Nested` — group related tests in inner classes
  - `@Tag("integration")` — categorize tests for selective execution
- **Assertions**:
  - `assertEquals(expected, actual)` — equality check
  - `assertTrue(condition)` / `assertFalse(condition)`
  - `assertNull(value)` / `assertNotNull(value)`
  - `assertThrows(Exception.class, () -> code())` — verify exception is thrown
  - `assertAll("group", () -> assertEquals(...), () -> assertTrue(...))` — run all assertions, report all failures
  - `assertTimeout(Duration.ofSeconds(2), () -> code())` — fail if too slow
- **Parameterized tests** — run the same test with different inputs:
  ```
  @ParameterizedTest
  @ValueSource(ints = {1, 2, 3, 5, 8})
  void testIsPrime(int number) { assertTrue(isPrime(number)); }

  @ParameterizedTest
  @CsvSource({"1, 1, 2", "2, 3, 5", "10, 20, 30"})
  void testAdd(int a, int b, int expected) { assertEquals(expected, add(a, b)); }
  ```
- **Test lifecycle**: new instance of the test class is created for each `@Test` method. Tests are isolated — no shared state between tests by default.

### 9.2 Mockito — Mocking Dependencies
- **Why mock**: unit tests should test one class in isolation. If `OrderService` depends on `PaymentGateway`, you mock `PaymentGateway` so you're testing `OrderService`'s logic — not the payment gateway.
- **Creating mocks**:
  ```
  PaymentGateway gateway = mock(PaymentGateway.class);
  // or with annotations:
  @Mock PaymentGateway gateway;
  @InjectMocks OrderService orderService; // injects mocks into constructor
  ```
- **Stubbing** — define what the mock returns:
  ```
  when(gateway.charge(any(), any())).thenReturn(PaymentResult.SUCCESS);
  when(gateway.charge(any(), eq(BigDecimal.ZERO))).thenThrow(new InvalidAmountException());
  ```
- **Verification** — assert that a method was called:
  ```
  verify(gateway).charge(userId, amount);          // was called exactly once
  verify(gateway, times(2)).charge(any(), any());  // called exactly 2 times
  verify(gateway, never()).refund(any());           // never called
  ```
- **Argument captors** — capture what was passed to a mock:
  ```
  ArgumentCaptor<PaymentRequest> captor = ArgumentCaptor.forClass(PaymentRequest.class);
  verify(gateway).charge(captor.capture());
  assertEquals(500, captor.getValue().getAmount());
  ```
- **`spy()`** — partial mock. Uses the real implementation but lets you stub specific methods. Use sparingly — if you need a spy, your design might need refactoring.
- **Matchers**: `any()`, `eq(value)`, `anyString()`, `anyInt()`, `argThat(predicate)` — flexible argument matching.

### 9.3 Test Patterns
- **Arrange-Act-Assert (AAA)** — the structure of every test:
  ```
  // Arrange — set up the test data and mocks
  var user = new User("alice", "alice@test.com");
  when(userRepo.findById("alice")).thenReturn(Optional.of(user));

  // Act — call the method under test
  var result = userService.getProfile("alice");

  // Assert — verify the result
  assertEquals("alice@test.com", result.getEmail());
  verify(userRepo).findById("alice");
  ```
- **One behavior per test** — each test verifies one thing. Don't test happy path and error case in the same test.
- **Test naming**: `methodName_scenario_expectedResult` — `charge_validAmount_returnsSuccess`, `charge_zeroAmount_throwsException`. The test name should tell you what broke without reading the test body.
- **Test independence** — no test should depend on another test's execution or state. Each test sets up its own data.

### 9.4 What to Test vs What Not to Test
- **Test**:
  - Business logic — calculations, validations, state transitions
  - Edge cases — null inputs, empty collections, boundary values
  - Error paths — what happens when things fail
  - Conditional logic — every branch of an if-else
- **Don't test**:
  - Getters/setters — no logic, no value in testing
  - Framework behavior — don't test that Spring wires beans correctly
  - Private methods — test through the public interface
  - Implementation details — test behavior, not which internal method was called
- **The rule**: if the test would break when you refactor the implementation (but not the behavior), the test is testing the wrong thing.

### 9.5 Integration Testing Basics
- **What**: test the interaction between real components — service + actual database, service + actual API.
- **When**: after unit tests prove individual classes work, integration tests prove they work together.
- **Spring Boot**: `@SpringBootTest` — starts the full application context. `@DataJpaTest` — starts only the JPA layer with an in-memory database.
- **Testcontainers** — spin up real Docker containers (PostgreSQL, Redis, Kafka) in tests. Integration tests with real infrastructure, no mocks.
- **Test pyramid**: many unit tests (fast, cheap) → fewer integration tests (slower, test boundaries) → very few end-to-end tests (slowest, most brittle). Most of your tests should be unit tests.
