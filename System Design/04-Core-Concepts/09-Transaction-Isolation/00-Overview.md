# Transaction Isolation Levels — Overview

> The database is optimistic. Two transactions run concurrently. Things go wrong in four specific ways. Isolation levels are the database's promise about which ones it prevents.

> [!abstract] Isolation levels are the formal specification of how much one transaction can see of another's in-progress work. Too little isolation — race conditions and dirty reads. Too much — performance collapses. This folder covers the four problems, the four levels, and how to choose the right combination for any system.

---

## Files in this folder

| File | Topic |
|---|---|
| 00-ACID.md | ACID properties — the why behind isolation levels, ACID vs BASE |
| 01-Isolation-Problems.md | The four problems — dirty read, non-repeatable read, phantom read, lost update |
| 02-Isolation-Levels.md | READ COMMITTED, REPEATABLE READ, SERIALIZABLE, snapshot isolation |
| 03-Choosing-Isolation.md | Decision framework — view counter vs hotel booking vs payments |
| 04-Interview-Cheatsheet.md | What to say, isolation + locking combinations, full checklist |
