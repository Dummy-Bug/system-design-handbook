Returning a DTO without the category stopped the extra queries. But that only worked because the category was not wanted. This note is what happens when you genuinely need it — and the named problem you are looking at.

# Where the extra queries come from

Start with the actual rows.

```text
1  products                             categories
2  id | title         | category_id     id | name
3  ---+---------------+-------------    ---+-------------
4  1  | iPhone 17     | 1               1  | electronics
5  2  | iPhone 17 Pro | 1               2  | kitchenware
6  3  | Plates        | 2
```

The first query fetches the products:

```sql
1  SELECT * FROM products
```

Three rows come back. Now look at what each row actually holds for its category: the number `1`, `1`, `2`.

> [!important] **The word `electronics` is nowhere in the products table.** All the product row has is a foreign key. To show the category, Hibernate has to go and fetch it from the other table.

So it works through the products one at a time, and for each one asks whether that category has already been loaded:

| | Product | Category needed | Already loaded? | What happens |
|---|---|---|---|---|
| **Query 2** | iPhone 17 | `1` | No | `SELECT * FROM categories WHERE id = 1` |
| — | iPhone 17 Pro | `1` | **Yes** | Reused. No query |
| **Query 3** | Plates | `2` | No | `SELECT * FROM categories WHERE id = 2` |

**Three queries in total**, and the middle row explains the count. The second iPhone needed category `1`, which had just been loaded, so nothing was fetched.

That is why three products produced **two** category queries rather than three — the number follows the **distinct** categories.

# Now the bad case

That was lucky. Suppose every product is in a different category:

```text
1  products
2  id | title    | category_id
3  ---+----------+-------------
4  1  | iPhone   | 1
5  2  | Plates   | 2
6  3  | T-shirt  | 3
```

Now nothing can be reused. Every product needs a category that has not been loaded yet:

```sql
1  SELECT * FROM products                  -- query 1
2  SELECT * FROM categories WHERE id = 1   -- query 2
3  SELECT * FROM categories WHERE id = 2   -- query 3
4  SELECT * FROM categories WHERE id = 3   -- query 4
```

**Three products, four queries.** Generalise it: **N products, 1 + N queries.**

> [!important] **This is the N+1 query problem.** **One** query to fetch the parent rows, then **N** more — one per row — to fetch each row's association. N+1 round trips to assemble data a single join could have returned in one.

# Why it matters

The results are correct either way, so the objection is fair: what is actually wrong?

**Every query is a round trip.** Your application sends it, the database accepts, parses, plans and answers it, and the result travels back. That cost is paid per query, not per row of data.

> [!important] Scale it. Fifty products on a page, all in different categories, is **51 round trips** where one would do. At a thousand requests a second that is **fifty thousand wasted queries a second** — for data a single join would have returned.
>
> That is not inefficiency at the margin. It is a database brought down by a detail nobody wrote.

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

Reading it a line at a time, because every part matters later.

**Line 2 — `products p`.** The `p` is an **alias**, a nickname for the table, so you can write `p.id` instead of `products.id`. Line 3 gives `categories` the alias `c` the same way. The letters are arbitrary.

**Line 3 — `ON p.category_id = c.id`.** The **join condition**: it tells the database how rows from the two tables pair up. A product matches a category when the product's `category_id` equals that category's `id` — the foreign key relationship, stated as a rule.

**Line 1 — `p.*, c.*`.** A bare `*` means **all columns**. Qualifying it scopes it to one table: `p.*` is every column of products, `c.*` every column of categories. Together they ask for both tables' columns side by side.

**Line 4 — `WHERE p.id = ?`.** Narrow it to one product. The `?` is a placeholder for a value supplied separately rather than pasted into the string.

What comes back is one row holding both:

```text
 p.id | p.title   | p.price | p.category_id | c.id | c.name
 1    | iPhone 17 | 80000   | 1             | 1    | electronics
   └────────── from products ───────────┘ └── from categories ──┘
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

Look back at the result above: there are **two columns called `id`** — `p.id` and `c.id` — because `p.*` brought one and `c.*` brought the other. Nothing can tell which is which.

Selecting only the column actually needed fixes that:

```sql
 SELECT p.*, c.name AS category 
 FROM products p JOIN categories c 
 ON p.category_id  = c.id 
 WHERE p.id = :id
```

**And an extra category query runs anyway.**

You wrote one query. Two are executed:

```text
Hibernate: SELECT p.*, c.name AS category FROM products p
            JOIN categories c ON p.category_id = c.id WHERE p.id = ?
            
Hibernate: select c1_0.id,c1_0.name from categories c1_0 where c1_0.id=?
```

Line 1 is your join, working correctly. **Line 3 is a second query nobody asked for** — the same category, fetched again on its own.

## Why

The join worked. The data came back. The obvious objection is that everything needed is right there — so why go back for it?

Look at the row the query returns:

```text
1  id | title     | price | category_id | category
2  1  | iPhone 17 | 80000 | 1           | electronics
```

`electronics` is present, in the last column. Now look at the field it would have to go into:

```java
1  private Category category;
```

That field holds a **`Category` object** — something with an `id` and a `name`. What arrived is the **string** `electronics`: one of a category's column values, with no identity attached.

> [!important] **A string cannot be put into a field that holds an entity.** There is no conversion between them, so that column is ignored. The data is present; it is in the wrong shape for the field.

Column by column, here is what becomes of the result:

| Column returned | What happens to it |
|---|---|
| `id`, `title`, `price` | Copied into the matching fields |
| `category_id` = `1` | Hibernate now knows **which** category this is, so it puts a placeholder in the field — id `1`, contents not loaded |
| `category` = `electronics` | **Ignored.** Wrong type for the only field it could belong to |

So the `Product` comes back holding a placeholder that knows its category is number 1, and knows nothing else about it.

Then the service calls `getCategory()`. Touching the placeholder makes it load itself:

```text
1  select c1_0.id,c1_0.name from categories c1_0 where c1_0.id=?
```

> [!important] Read the `where c1_0.id=?` on line 1. **It already knew the id was 1** — it took that from `category_id`. What it never had was the name, because the column carrying the name was discarded.

Which is the whole absurdity of this attempt: **the join fetched `electronics`, Hibernate discarded it because it did not fit, and then went back to the database to fetch `electronics` again** — this time in a shape it could use.

The join was performed and thrown away.

# Attempt two: `JOIN FETCH`

The failure above came from Hibernate being handed a result set it did not design. The answer is to let it design one — write the join in **JPQL**, and Hibernate generates the SQL itself:

```java
1  // src/main/java/com/example/FakeCommerce/repositories/ProductRepository.java
2  @Query("SELECT p FROM Product p JOIN FETCH p.category WHERE p.id = :id")
3  List<Product> findProductWithDetailsById(Long id);
```

Note what it names: `Product`, the **entity**. `p.category`, the **field**. No tables, no columns, no join condition — the mapping already knows how they relate.

That is the difference that matters. **Because Hibernate wrote the query, it knows what every column in the result is for** — those category columns are the category belonging to the product in that row, so it builds a real `Category` object and puts it in the field. Nothing is discarded, and nothing needs fetching twice.

> [!important] **`JOIN FETCH` is two instructions.**
>
> **`JOIN`** — join with the table behind `p.category`, which the mapping identifies as `categories`.
>
> **`FETCH`** — take the joined result and **populate it into the object immediately**, rather than leaving the association unresolved.
>
> That second word is the whole difference. A plain `JOIN` would filter correctly and still leave the category to be lazily loaded later.

## What it produces

```text
Hibernate: select p1_0.id , p1_0.category_id , c1_0.id , c1_0.name , p1_0.description , p1_0.image , p1_0.price , p1_0.rating , p1_0.title from products p1_0 join categories c1_0 on c1_0.id = p1_0.category_id where p1_0.id=?
```


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

- Eager loading is the default, and **defaults have consequences at scale**
- Lazy loading is defeated by **anything that touches the field**, including a serialiser
- Returning entities gives that away silently
- **A native query gives up Hibernate's ability to map the result back**
- `JOIN FETCH` exists precisely because a **join alone is not enough**

None of that is visible from a working endpoint. It came from making it fail and reading why.
