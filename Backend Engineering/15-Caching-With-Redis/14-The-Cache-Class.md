The connection is configured. What travels over it is the next problem, because Redis stores strings and an application deals in objects — and bridging that gap is most of what a cache class does.

# Redis returns strings

> [!important] Every value read back from Redis arrives as **a string**. A `GetProductResponseDto` cannot be handed to Redis and cannot be received from it. Something has to convert in both directions.

> [!important] **Serialisation** is turning an object into a form another system can hold — here, JSON text. **Deserialisation** is the reverse. It is the same problem as sending JSON over HTTP, appearing again at a different boundary.

```mermaid
flowchart LR
    O["GetProductResponseDto"] -- "serialise" --> S["JSON string"]
    S --> R[("Redis")]
    R --> S2["JSON string"]
    S2 -- "deserialise" --> O2["GetProductResponseDto"]
```

# RedisTemplate

> [!important] **`RedisTemplate` is Spring Data Redis's main entry point.** Instead of raw commands it exposes typed operations, grouped by the structure they act on — `opsForValue()` for strings, `opsForHash()`, `opsForList()`, `opsForSet()`, `opsForZSet()`.

The grouping maps directly onto the structures from earlier notes, so `opsForZSet().add(...)` is `ZADD` under a Java name.

## StringRedisTemplate

> [!important] **`StringRedisTemplate` is `RedisTemplate` with both key and value fixed as `String`.** Nothing more — a subclass with its serialisers preset to the string serialiser.

That is the right choice here precisely because the values are JSON text. **Redis stores a string; the application converts it.** Handing the conversion to the template as well would mean two serialisation mechanisms doing the same job.

## When you want something else

A custom template is a bean with different serialisers:

```java
1  @Bean
2  public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
3      RedisTemplate<String, Object> template = new RedisTemplate<>();
4      template.setConnectionFactory(factory);
5      template.setKeySerializer(RedisSerializer.string());
6      template.setValueSerializer(RedisSerializer.json());
7      return template;
8  }
```

> [!info] `RedisSerializer` offers several — `string()`, `json()`, `byteArray()`, and Java serialisation. A JSON value serialiser moves the conversion into the template, so application code passes objects directly. **Unverified** — this pattern is from the Spring Data Redis documentation and was not run.

> [!warning] Keys should stay string-serialised whatever the values do. A key serialised any other way is unreadable from `redis-cli`, which makes diagnosing a cache problem far harder than it needs to be.

# ObjectMapper

> [!important] **`ObjectMapper` is Jackson's converter between Java objects and JSON.** `writeValueAsString` serialises; `readValue` deserialises given the target class. Spring Boot already configures one, so it is injected rather than constructed.

# The class

```java
1  // src/main/java/com/example/FakeCommerce/services/cache/ProductRedisCache.java
2  package com.example.FakeCommerce.services.cache;
3
4  import java.time.Duration;
5  import java.util.Optional;
6
7  import org.springframework.data.redis.core.StringRedisTemplate;
8  import org.springframework.stereotype.Service;
9
10 import com.example.FakeCommerce.dtos.GetProductResponseDto;
11
12 import lombok.RequiredArgsConstructor;
13 import lombok.extern.slf4j.Slf4j;
14 import tools.jackson.databind.ObjectMapper;
15
16 @Service
17 @RequiredArgsConstructor
18 @Slf4j
19 public class ProductRedisCache {
20
21     private static final String KEY_SUMMARY = "product:summary:";
22     private static final Duration CACHE_TTL = Duration.ofMinutes(1);
23
24     private final StringRedisTemplate stringRedisTemplate;
25     private final ObjectMapper objectMapper;
26
27     public Optional<GetProductResponseDto> getSummary(Long id) {
28         String responseJson = stringRedisTemplate.opsForValue().get(KEY_SUMMARY + id);
29
30         if (responseJson == null) {
31             log.info("Cache miss for product summary: {}", id);
32             return Optional.empty();
33         }
34         log.info("Cache hit for product summary: {}", id);
35         try {
36             GetProductResponseDto response = objectMapper.readValue(responseJson, GetProductResponseDto.class);
37             return Optional.of(response);
38         } catch (Exception e) {
39             log.error("Error parsing product summary from cache: {}", e.getMessage());
40             stringRedisTemplate.delete(KEY_SUMMARY + id);
41             return Optional.empty();
42         }
43     }
44
45     public void putSummary(Long id, GetProductResponseDto response) {
46         try {
47             stringRedisTemplate.opsForValue().set(
48                 KEY_SUMMARY + id,
49                 objectMapper.writeValueAsString(response),
50                 CACHE_TTL);
51         } catch (Exception e) {
52             throw new RuntimeException("Error serializing product summary to cache: " + e.getMessage());
53         }
54     }
55 }
```

Six decisions in it are worth drawing out.

## The key is built from a constant prefix

**Line 21** gives every entry a key of the form `product:summary:47` — the `object:id` convention from `04-Strings-And-Hashes`, with `summary` recording that this holds a summary rather than a full product.

> [!important] **The prefix is a constant in one place.** A key assembled inline at each call site is a typo away from a permanent miss that no test will catch, because a wrong key is not an error — it is a cache that quietly never hits.

## A miss returns `Optional`, not null

**Line 32.** The alternative is returning `null` and requiring every caller to check for it.

> [!important] **`Optional` puts the miss in the type.** The compiler forces the caller to acknowledge the empty case, where a `null` return depends on the caller remembering. A cache miss is not an error and not an exception — it is an ordinary, expected outcome, and `Optional` is the type for exactly that.

## Both outcomes are logged

**Lines 31 and 34.** Without them there is no way to know whether the cache is doing anything.

> [!important] **The hit rate is the only measure of whether a cache is working**, and these two log lines are what makes it visible.

## A corrupted entry is deleted, not just reported

**Line 40** is the subtle one.

> [!warning] If a stored value cannot be parsed — written by an older version of the DTO, or stored under a key another piece of code also uses — then **every future read of that key fails the same way**. The entry is poison, and it stays until its TTL expires.

> [!important] Deleting it converts a permanently failing key into **one miss**. The next request refetches from the database and stores a correct value. The failure repairs itself instead of repeating.

The failure is still logged, because silently discarding data is how a mismatch stays invisible for months.

## Serialisation failure throws

**Line 52**, and it is deliberately unlike the read path.

> [!important] **A read failure is recoverable and a write failure is a bug.** Failing to parse means bad data is already in the cache; failing to serialise means the object cannot be represented as JSON at all, which is a defect in the code that no retry fixes. Swallowing it would hide a broken DTO forever.

> [!info] Note also what is not converted with `toString()`. On a Lombok `@Data` class that produces a readable line, but it is not JSON and `readValue` cannot parse it back. `writeValueAsString` is the only thing that round-trips.

## The TTL is on the write

**Line 50** passes `CACHE_TTL` as a third argument to `set`, which is `SET key value EX seconds` from `05-Expiry-And-Locks`.

> [!important] **Every entry expires after one minute.** Nothing invalidates this cache when a product changes, so that minute is the agreed maximum staleness — the write-around behaviour of `11-Write-Patterns`, with the TTL as its only bound.

> [!info] A minute is short enough to demonstrate expiry and short enough that the cache does little for genuinely hot data. A real value belongs in configuration, chosen per kind of data, rather than compiled in as a constant.
