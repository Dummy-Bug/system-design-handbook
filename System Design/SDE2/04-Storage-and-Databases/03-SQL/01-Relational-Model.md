# The Relational Model

---

## The Problem With One Big Table

You're building Twitter. A beginner's first instinct is to put everything in one table:

```
| user_id | username | email           | tweet_text      | tweet_date |
|---------|----------|-----------------|-----------------|------------|
| 1       | alice    | alice@gmail.com | "Hello world"   | 2024-01-01 |
| 1       | alice    | alice@gmail.com | "Second tweet"  | 2024-01-02 |
| 1       | alice    | alice@gmail.com | "Third tweet"   | 2024-01-03 |
```

Alice's username and email are repeated on every single row. She has 1000 tweets? Her email is stored 1000 times.

**What happens when Alice changes her email?**

You have to update every single row. Miss even one — now you have two different emails for the same user in your database. Inconsistent data. This problem is called **data duplication**.

---

## The Fix — Split Into Separate Tables

Move user data to a users table. Move tweet data to a tweets table. Link them with a reference.

```
Users table:
| user_id | username | email           |
|---------|----------|-----------------|
| 1       | alice    | alice@gmail.com |
| 2       | bob      | bob@gmail.com   |

Tweets table:
| tweet_id | user_id | tweet_text      | tweet_date |
|----------|---------|-----------------|------------|
| 1        | 1       | "Hello world"   | 2024-01-01 |
| 2        | 1       | "Second tweet"  | 2024-01-02 |
| 3        | 2       | "Bob's tweet"   | 2024-01-03 |
```

Alice's email is stored exactly once. She changes it — one update, done. All her tweets automatically reflect it because they just point to `user_id = 1`.

This is the **relational model** — data split into tables, linked by references.

---

## Foreign Keys

The `user_id` column in the tweets table is a **foreign key** — a reference to the primary key of another table. It's how tables talk to each other.

```
tweets.user_id → REFERENCES users(user_id)
```

The database enforces this — you can't insert a tweet with `user_id = 99` if user 99 doesn't exist. This is **referential integrity**.

> [!info] Foreign key = a column in one table that points to the primary key of another table. The database enforces that the reference always points to something real.

> [!important] Foreign key constraints are the C (Consistency) from ACID in action. The database rejects any write that would violate the reference — no orphan tweets, no broken links.

---

## Primary Keys

Every table needs a way to uniquely identify each row. That's the **primary key**.

```
users.user_id   → unique identifier for each user
tweets.tweet_id → unique identifier for each tweet
```

Primary keys are:
- Unique — no two rows have the same value
- Never null — every row must have one
- Immutable — should never change after creation

> [!tip] Always use a system-generated ID (auto-increment integer or UUID) as your primary key — never use something like `email` or `username`. Those can change. An ID never should.

---

## Summary

```
One big table      → data duplication → inconsistency on updates
Relational model   → split into tables → each piece of data stored once
Foreign key        → links tables together, enforced by the database
Primary key        → uniquely identifies each row in a table
Referential integrity → FK constraint ensures references always point to real rows
```
