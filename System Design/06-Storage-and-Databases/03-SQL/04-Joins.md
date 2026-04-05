# SQL Joins

---

## Why Joins Exist

When you normalise your database — splitting data into separate tables to eliminate duplication — you need a way to pull that data back together when querying. That's what a JOIN does: combine rows from two tables based on a matching column.

```
Users:                    Tweets:
| user_id | username |    | tweet_id | user_id | text         |
|---------|----------|    |----------|---------|--------------|
| 1       | alice    |    | 1        | 1       | "Hello"      |
| 2       | bob      |    | 2        | 1       | "World"      |
| 3       | charlie  |    | 3        | 2       | "Bob tweet"  |
```

Charlie has never tweeted. Bob has one tweet. Alice has two. Each join type answers a different question about how to handle the gaps.

---

## INNER JOIN

Returns only rows where there's a match in **both** tables. Non-matching rows are dropped entirely.

```sql
SELECT users.username, tweets.text
FROM users
INNER JOIN tweets ON users.user_id = tweets.user_id
```

```
Result:
| username | text        |
|----------|-------------|
| alice    | "Hello"     |
| alice    | "World"     |
| bob      | "Bob tweet" |
```

Charlie is gone — he has no tweets, so there's no match. INNER JOIN drops him.

Think of it as the **intersection** — only rows that exist on both sides.

**Use when:** you only want records that have related data on both sides.
```
"Show me all tweets with their author's username"
→ every tweet must have an author → INNER JOIN
```

---

## LEFT JOIN

Returns **everything from the left table**, and matching rows from the right. If there's no match on the right, columns from the right table come back as NULL.

```sql
SELECT users.username, tweets.text
FROM users
LEFT JOIN tweets ON users.user_id = tweets.user_id
```

```
Result:
| username | text        |
|----------|-------------|
| alice    | "Hello"     |
| alice    | "World"     |
| bob      | "Bob tweet" |
| charlie  | NULL        |
```

Charlie is included — with NULL for tweet text because he has no tweets. Every user appears regardless of whether they have tweets.

**Use when:** you want all records from the left table, whether or not they have related data.
```
"Show me all users and how many tweets they've posted, including users with zero tweets"
→ LEFT JOIN users → tweets
```

---

## RIGHT JOIN

Exact opposite of LEFT JOIN. Returns **everything from the right table**, matching rows from the left. If no match on the left, you get NULL.

```sql
SELECT users.username, tweets.text
FROM users
RIGHT JOIN tweets ON users.user_id = tweets.user_id
```

```
Result:
| username | text        |
|----------|-------------|
| alice    | "Hello"     |
| alice    | "World"     |
| bob      | "Bob tweet" |
```

In a well-designed schema with foreign key constraints, RIGHT JOIN looks the same as INNER JOIN — every tweet must have a valid user, so there are no orphans. But if FK constraints aren't enforced, orphan tweets with no owner would appear with NULL for username.

> [!tip] RIGHT JOIN is rarely used in practice. Most engineers just flip the table order and use LEFT JOIN instead — same result, more readable. If you find yourself writing RIGHT JOIN, ask whether swapping the tables makes it a LEFT JOIN.

---

## FULL OUTER JOIN

Returns **everything from both tables**. Matches where they exist, NULL where they don't. Nobody gets dropped from either side.

```sql
SELECT users.username, tweets.text
FROM users
FULL OUTER JOIN tweets ON users.user_id = tweets.user_id
```

```
Result:
| username | text        |
|----------|-------------|
| alice    | "Hello"     |
| alice    | "World"     |
| bob      | "Bob tweet" |
| charlie  | NULL        |    ← user with no tweets
| NULL     | "orphan"    |    ← tweet with no user (if FK not enforced)
```

Think of it as LEFT JOIN + RIGHT JOIN combined.

**Use when:** auditing — "show me everything from both sides, flag anything that doesn't have a match."

---

## Summary

```
INNER JOIN       → only matched rows — both sides must exist
LEFT JOIN        → all from left, NULL if no match on right
RIGHT JOIN       → all from right, NULL if no match on left
FULL OUTER JOIN  → everything from both, NULL where no match
```

> [!important] Foreign key constraints prevent orphan rows — a tweet can't exist without a valid user_id. This is the C (Consistency) from ACID — the database enforces your rules on every write. If FK constraints are in place, RIGHT JOIN and FULL OUTER JOIN rarely surface orphan rows in practice.
