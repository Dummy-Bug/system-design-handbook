# Normalisation

> [!question] You know data should be split into separate tables. But how do you know *exactly* what goes where?
> That's what Normal Forms define — a systematic set of rules for splitting tables correctly.

---

## Why "Just Split It" Isn't Enough

From the relational model, you know that storing Alice's email in every tweet row is wrong — split users and tweets into separate tables. That's the intuition.

But splitting tables the wrong way still leaves problems. You need formal rules for *how* to split — that's what 1NF, 2NF, and 3NF give you. Each one catches a different type of duplication that the previous form missed.

Let's work through them with an employee dataset:

```
| emp_id | emp_name | dept_id | dept_name   | phone_numbers  |
|--------|----------|---------|-------------|----------------|
| 1      | Alice    | 10      | Engineering | "9999, 8888"   |
| 2      | Bob      | 10      | Engineering | "7777"         |
```

Three things are wrong here — and each one is fixed by a different Normal Form.

---

## 1NF — Fix Multi-Value Cells

Look at Alice's `phone_numbers` — two values crammed into one cell: `"9999, 8888"`.

Now try to write a query: *"find all employees with phone number 9999."*

You can't do a clean lookup. You'd have to fetch every row, split the string on commas, and pattern-match — on every single row in the table. At millions of rows, that's a full table scan with string parsing on each row. Fragile and slow.

The fix is simple — one value per cell, one row per phone number:

```
| emp_id | emp_name | phone_number |
|--------|----------|--------------|
| 1      | Alice    | 9999         |
| 1      | Alice    | 8888         |
| 2      | Bob      | 7777         |
```

Now `emp_id` alone is no longer unique — Alice appears twice. `phone_number` alone isn't unique either — the same number could belong to different employees. So the primary key becomes `(emp_id, phone_number)` together. Neither column alone, but the pair is always unique.

> [!info] **1NF — First Normal Form**
> Every cell must contain a single atomic value. No lists, no comma-separated values, no arrays. Each row must be uniquely identifiable.

---

## 2NF — Fix Partial Dependencies

After fixing 1NF, look at what we have:

```
| emp_id | phone_number | emp_name |
|--------|--------------|----------|
| 1      | 9999         | Alice    |
| 1      | 8888         | Alice    |
| 2      | 7777         | Bob      |
```

`emp_name` repeats for Alice — once for each phone number. The PK is `(emp_id, phone_number)`. But does `emp_name` have anything to do with the phone number? No. Alice is always Alice regardless of which number you're looking at. It only depends on `emp_id` — half the primary key.

This is called a **partial dependency** — a non-key column depending on only part of a composite PK.

The fix — move `emp_name` out to its own table where `emp_id` is the full PK:

```
Employees table:          Emp_Phones table:
| emp_id | emp_name |     | emp_id | phone_number |
|--------|----------|     |--------|--------------|
| 1      | Alice    |     | 1      | 9999         |
| 2      | Bob      |     | 1      | 8888         |
                          | 2      | 7777         |
```

`emp_name` is now stored exactly once per employee. No duplication.

> [!info] **2NF — Second Normal Form**
> Must be in 1NF first. Every non-key column must depend on the **whole** primary key, not just part of it. If a column only depends on part of a composite PK, move it to its own table.

---

## 3NF — Fix Transitive Dependencies

Now add department data back:

```
| emp_id | emp_name | dept_id | dept_name   |
|--------|----------|---------|-------------|
| 1      | Alice    | 10      | Engineering |
| 2      | Bob      | 10      | Engineering |
| 3      | Charlie  | 20      | Marketing   |
```

PK is `emp_id`. Alice and Bob both have `dept_name = Engineering` — it repeats for every employee in the same department.

Does `dept_name` depend on `emp_id`? No. It depends on `dept_id`. Engineering is always Engineering regardless of which employee you're looking at. If you rename "Engineering" to "Tech" — you update every employee row in that department. Miss one row — inconsistent data.

This is a **transitive dependency** — `dept_name` depends on `dept_id`, which depends on `emp_id`. It's connected to the PK, but indirectly through another non-key column.

The fix — move department data to its own table:

```
Employees table:                    Departments table:
| emp_id | emp_name | dept_id |     | dept_id | dept_name   |
|--------|----------|---------|     |---------|-------------|
| 1      | Alice    | 10      |     | 10      | Engineering |
| 2      | Bob      | 10      |     | 20      | Marketing   |
| 3      | Charlie  | 20      |
```

`dept_name` stored once per department. Rename "Engineering" to "Tech" — one update, done, all employees see it immediately.

> [!info] **3NF — Third Normal Form**
> Must be in 2NF first. Every non-key column must depend on the PK **directly** — not on another non-key column. If column A depends on column B and B depends on the PK, move A and B to their own table.

---

## Summary

```
1NF → no multi-value cells — one atomic value per cell, one row per fact
2NF → no partial dependency — every column depends on the whole PK
3NF → no transitive dependency — every column depends on PK directly, not via another column
```

Each normal form builds on the previous. You can't be in 2NF without first being in 1NF. You can't be in 3NF without first being in 2NF.
