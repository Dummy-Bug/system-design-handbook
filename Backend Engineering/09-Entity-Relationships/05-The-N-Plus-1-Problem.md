Returning a DTO without the category stopped the extra queries. But that only worked because the category was not wanted. This note is what happens when you genuinely need it — and the named problem you are looking at.

# Naming it

Three products across two categories produced one product query plus two category queries. Generalise it.

Fetch **N** products, each in a distinct category:

```text
1  SELECT * FROM products                         ← 1 query
2  SELECT * FROM categories WHERE id = ?          ← for product 1
3  SELECT * FROM categories WHERE id = ?          ← for product 2
4  ...                                            ← N of these
```

> [!important] **This is the N+1 query problem.** One query to fetch the parent rows, then one further query per row to fetch its association. **N+1 database round trips** to assemble data that a single query could have returned.

# Why it matters

The results are correct either way, so the objection is fair: what is actually wrong?

**Load.** Each query is a round trip your database has to accept, parse, plan and answer. You have replaced one unit of work with N+1.

> [!important] Scale it. A service taking a thousand requests a second, each listing fifty products, is issuing **fifty thousand extra queries per second** — for data one join would have returned. That is not inefficiency at the margin; it is a database brought down by a design detail.

It is common enough that hunting for N+1 patterns is a routine activity on real teams, and finding one is usually a large, cheap win.

# The DTO was an escape, not a solution

Worth being honest about what happened in the previous note.

> [!important] Removing the category from the response did not solve N+1. **It avoided it**, by not needing the data. The queries stopped because the association was never touched.

Which is the right answer when you do not want the category. It is no answer at all when you do — an endpoint returning a product **with** its category details cannot dodge the problem.

# The actual solution is a join

Step outside the framework for a second. Asked in plain SQL for products with their categories, nobody would write N+1 queries:

```sql
1  SELECT p.*, c.*
2  FROM products p
3  JOIN categories c ON p.category_id = c.id
4  WHERE p.id = ?
```

One query. The database does the matching, which is what a relational database is for.

> [!important] **N+1 is not a problem the database has. It is a problem the ORM creates** by treating an association as something to resolve separately. The fix is to express what you actually want as one query.

# Attempt one: a native join

```java
1  @Query(nativeQuery = true, value =
2      "SELECT p.*, c.* FROM products p JOIN categories c ON p.category_id = c.id WHERE p.id = :id")
3  List<Product> findProductWithDetailsById(Long id);
```

Which fails:

```text
1  Duplicated SQL alias id
```

Both tables have a column called `id`, and `p.*, c.*` returns two of them. Nothing can tell which is which.

Selecting only the column actually needed fixes that:

```sql
1  SELECT p.*, c.name AS category FROM products p JOIN categories c ON p.category_id = c.id WHERE p.id = :id
```

**And a category query still fires.**

## Why

The join worked. The data came back. But the method returns `List<Product>`, and Hibernate has to build `Product` objects from the result — and it has no idea what to do with a column called `category`.

> [!important] With a **native** query, Hibernate is handed rows it did not plan. It maps what matches the entity and discards the rest. So `c.name AS category` lands nowhere, the `Product` object's `category` field stays empty — and the moment the service calls `getCategory()`, **lazy loading does its job and fetches it.**

The join was performed and then thrown away.

# Attempt two: `JOIN FETCH`

The answer is to write the join in **JPQL**, so Hibernate is generating the query and knows what the result means:

```java
1  // src/main/java/com/example/FakeCommerce/repositories/ProductRepository.java
2  @Query("SELECT p FROM Product p JOIN FETCH p.category WHERE p.id = :id")
3  List<Product> findProductWithDetailsById(Long id);
```

Note what it names: `Product`, the **entity**. `p.category`, the **field**. No tables, no columns, no join condition — the mapping already knows how they relate.

> [!important] **`JOIN FETCH` is two instructions.**
>
> **`JOIN`** — join with the table behind `p.category`, which the mapping identifies as `categories`.
>
> **`FETCH`** — take the joined result and **populate it into the object immediately**, rather than leaving the association unresolved.
>
> That second word is the whole difference. A plain `JOIN` would filter correctly and still leave the category to be lazily loaded later.

## What it produces

```text
1  Hibernate: select p1_0.id,p1_0.category_id,c1_0.id,c1_0.name,p1_0.description,p1_0.image,
2             p1_0.price,p1_0.rating,p1_0.title
3             from products p1_0 join categories c1_0 on c1_0.id=p1_0.category_id
4             where p1_0.id=?
```

> [!info] **Verified.** **One query.** A real `join` on line 3, and both entities' columns selected on line 1 — `p1_0` for the product, `c1_0` for the category. No follow-up category query, because the object came back complete.

The service was not changed at all. It still calls `getCategory()` — and now the category is already there.

# The progression

| Approach | Queries | Gets the category |
|---|---|---|
| Eager association, return the entity | **N+1** | Yes |
| Lazy association, return a DTO without it | 1 | **No** |
| Native join returning an entity | **N+1** | Yes, but only via lazy loading |
| **JPQL `JOIN FETCH`** | **1** | **Yes** |

Only the last row is both correct and efficient. And the third is the interesting one — it **looks** solved, the join is right there in the code, and the query count is unchanged.

> [!important] Which is why reading the SQL log matters more than reading your own code. A join in your repository does not prove a join happened; the log does.

# What this cost to learn

Worth noticing what the chain of failures actually taught, because each one was necessary:

- Eager loading is the default, and defaults have consequences at scale
- Lazy loading is defeated by anything that touches the field, including a serialiser
- Returning entities gives that away silently
- A native query gives up Hibernate's ability to map the result back
- `JOIN FETCH` exists precisely because a join alone is not enough

None of that is visible from a working endpoint. It came from making it fail and reading why.
