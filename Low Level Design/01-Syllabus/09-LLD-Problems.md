## Phase 9 — LLD Case Studies (Problems)

> This is the destination. Everything in Phases 1–8 feeds directly into these problems.
> Practice them in order — Tier 1 builds intuition, Tier 2 adds complexity, Tier 3 tests mastery.

---

### Structure for Every LLD Problem
1. **Requirements** — What are the core use cases? (3-5 max)
2. **Entities** — Nouns from requirements → candidate classes
3. **Class Diagram** — Relationships, key fields, key methods
4. **Design Patterns Used** — Which patterns and why
5. **Core Logic** — The non-obvious algorithm or data structure choice
6. **Concurrency** — What shared state exists? How is it protected?
7. **Extensibility** — What's the likely "add a new requirement" question? Is your design ready?

---

### Tier 1 — Beginner (Do These First)

> These teach you to identify classes, apply basic patterns, and write clean OOP code.
> If you can't do these in 60 minutes, you're not ready for Tier 2.

**1. Parking Lot System**
- Core use cases: Park vehicle, unpark vehicle, calculate fee, check availability
- Key classes: `ParkingLot`, `ParkingFloor`, `ParkingSpot`, `Vehicle` (Car/Truck/Motorcycle), `Ticket`, `PricingStrategy`
- Patterns: Factory (vehicle/spot creation), Strategy (pricing), Singleton (lot), Observer (notify when full)
- Core logic: Finding the nearest available spot of the right type — `HashMap<SpotType, Queue<ParkingSpot>>`
- Concurrency: Two users claim last compact spot — `synchronized` on spot or CAS
- Extension test: "Add motorcycle support" → new VehicleType enum + new SpotType + new PricingStrategy
- **Companies**: Flipkart, Amazon, Rippling, Microsoft — the most common LLD question

**2. Tic-Tac-Toe**
- Core use cases: Place a mark, check for winner, handle draw
- Key classes: `Board`, `Cell`, `Player`, `Game`, `WinChecker`
- Patterns: Strategy (win-checking algorithm — can swap brute force for O(1) row/col/diagonal tracking)
- Core logic: O(1) win check — maintain row sum, col sum, diagonal sums. Player X = +1, Player O = -1. If any sum reaches +N or -N, that player wins.
- Extension test: "Make it N×N instead of 3×3" → your win-checker should work with any board size
- **Companies**: Google, Amazon, Microsoft

**3. Library Management System**
- Core use cases: Add book, search book, borrow book, return book, manage members
- Key classes: `Library`, `Book`, `BookCopy`, `Member`, `BorrowRecord`, `SearchService`
- Patterns: Strategy (search by title/author/ISBN), Observer (notify when overdue)
- Core logic: Distinguish `Book` (title, author, ISBN) from `BookCopy` (physical copy with barcode, availability) — multiple copies of same book
- Concurrency: Two members borrow the last copy — lock on `BookCopy`
- Extension test: "Add fine calculation for late returns" → new PricingStrategy
- **Companies**: Amazon, Microsoft, Flipkart

**4. Vending Machine**
- Core use cases: Insert coin, select product, dispense, return change
- Key classes: `VendingMachine`, `Product`, `Coin`, `Inventory`, State classes (`IdleState`, `CoinInsertedState`, `DispensingState`)
- Patterns: **State** (machine states — this is THE state pattern problem), Chain of Responsibility (coin/change processing)
- Core logic: State transitions — Idle → (insert coin) → HasMoney → (select product) → Dispensing → (dispense) → Idle
- Extension test: "Add support for notes (bills) alongside coins" → new `CurrencyType` enum, same State logic
- **Companies**: Flipkart, Rippling, Amazon

**5. Snake and Ladder Game**
- Core use cases: Roll dice, move player, handle snakes/ladders, determine winner
- Key classes: `Board`, `Player`, `Dice`, `Snake`, `Ladder`, `Game`, `Cell`
- Patterns: Strategy (dice rolling — normal vs loaded), Template Method (game loop)
- Core logic: Board as array. Each cell optionally has a jump (snake or ladder). After dice roll, check if landing cell has a jump → move to jump destination.
- Extension test: "Add a crocodile that reverses 5 moves" → new `SpecialCell` type, no Board logic change
- **Companies**: Flipkart (very common), Rippling

**6. Stack Overflow (Q&A Platform)**
- Core use cases: Post question, post answer, upvote/downvote, comment, search, accept answer
- Key classes: `User`, `Question`, `Answer`, `Comment`, `Vote`, `Tag`, `SearchService`
- Patterns: Observer (notify question author on new answer), Strategy (search/sort), Composite (Comment can have replies)
- Core logic: Voting system — `Map<PostId, AtomicInteger>` for vote counts. User can only vote once per post — `Set<UserId>` per post.
- Extension test: "Add reputation system (upvotes give +10 rep)" → new `ReputationService`, Observer listens to votes
- **Companies**: Rippling, Microsoft

---

### Tier 2 — Intermediate

> These add state machines, complex scheduling, real-world business logic, and concurrency requirements.

**7. Elevator System**
- Core use cases: Request elevator from floor, select destination floor, move elevator, open/close doors
- Key classes: `Elevator`, `ElevatorController`, `Floor`, `Request`, `Direction`, State classes (`IdleState`, `MovingUpState`, `MovingDownState`, `DoorOpenState`)
- Patterns: **State** (elevator states), **Strategy** (scheduling algorithm — SCAN, LOOK, SSTF), Observer (display updates), Command (button press)
- Core logic: **SCAN (elevator) algorithm** — move in one direction, serve all requests in that direction, then reverse. Like a disk arm.
  - Alternative: LOOK (only go as far as the farthest request, don't go to the end)
  - Alternative: SSTF (Shortest Seek Time First — nearest floor, can cause starvation)
- Concurrency: Multiple people pressing buttons on different floors simultaneously → `PriorityBlockingQueue<Request>`
- Extension test: "Add VIP elevator that serves only certain floors" → new ElevatorType, same controller
- **Companies**: Flipkart, Rippling, Google, Amazon — second most common LLD question

**8. Chess**
- Core use cases: Move piece, validate move, check for check/checkmate, handle special moves (castling, en passant, pawn promotion)
- Key classes: `Board`, `Cell`, `Piece` (abstract), `King/Queen/Rook/Bishop/Knight/Pawn`, `Player`, `Game`, `Move`, `MoveValidator`
- Patterns: Factory (piece creation), Strategy (each piece has its own `getValidMoves()`), Command (move as undoable command), Observer (check detection)
- Core logic: `Piece.getValidMoves(Board board, Position current)` — each piece computes its valid positions based on board state. Polymorphism handles the rest — no switch on piece type.
- Extension test: "Add undo/redo" → Command pattern is already there, just add a move stack
- **Companies**: Flipkart, Amazon, Rippling

**9. BookMyShow / Movie Ticket Booking**
- Core use cases: Browse movies, select showtime, select seats, book with payment, cancel booking
- Key classes: `Movie`, `Theatre`, `Screen`, `Show`, `Seat`, `Booking`, `Payment`, `User`
- Patterns: Facade (BookingFacade coordinates selection → lock → payment → confirm), Strategy (pricing by seat type), Observer (notify on booking confirmation)
- Core logic: **Seat locking** — when user selects seats, temporarily lock for 10 minutes (TTL). If payment completes → confirm. If timeout → release. Use State pattern on `Seat`: AVAILABLE → LOCKED → BOOKED.
- Concurrency: Two users select the same seat simultaneously → optimistic lock (version check) or `synchronized` on seat
- Extension test: "Add discount coupons" → new `DiscountStrategy`, applied during pricing
- **Companies**: Flipkart, Rippling, Amazon

**10. Splitwise / Expense Sharing**
- Core use cases: Add expense, split (equal/exact/percentage), view balances, simplify debts
- Key classes: `User`, `Group`, `Expense`, `Split` (abstract), `EqualSplit`, `ExactSplit`, `PercentSplit`, `BalanceSheet`
- Patterns: Strategy (split type), Factory (create correct split type), Observer (notify users of new expense)
- Core logic: **Balance simplification** — minimize number of transactions. This is a graph problem: build net balance per user, then greedily match largest creditor with largest debtor.
  - Simplified: `Map<UserId, Map<UserId, Double>>` — who owes whom. On each expense, update pairwise balances.
- Validation: Splits must sum to total expense amount — fail fast if not.
- Extension test: "Add percentage-based split" → new `PercentSplit implements Split`
- **Companies**: Flipkart (VERY common), Rippling, Google

**11. Hotel Management System**
- Core use cases: Search rooms, book room, check-in, check-out, generate invoice
- Key classes: `Hotel`, `Room`, `RoomType`, `Reservation`, `Guest`, `Invoice`, `PaymentService`
- Patterns: State (room lifecycle: AVAILABLE → RESERVED → OCCUPIED → MAINTENANCE), Strategy (pricing by room type + season), Builder (Reservation with many optional fields)
- Core logic: Room availability for date range — for each room, check if any existing reservation overlaps with requested dates. `TreeMap<Date, Reservation>` per room enables efficient overlap detection.
- Extension test: "Add conference room booking with hourly slots" → new RoomType + HourlyPricingStrategy
- **Companies**: Amazon, Microsoft, Flipkart

**12. ATM Machine**
- Core use cases: Authenticate user, check balance, withdraw cash, deposit, transfer
- Key classes: `ATM`, `Account`, `Card`, `Transaction`, `CashDispenser`, `CashDenomination`
- Patterns: **State** (ATM states: IDLE → CARD_INSERTED → AUTHENTICATED → TRANSACTION → CASH_DISPENSING), **Chain of Responsibility** (denomination dispenser: try ₹2000 notes → ₹500 → ₹100 → ₹50)
- Core logic: Cash dispensing algorithm — greedy, largest denominations first. Track available notes per denomination. If a denomination runs out, skip to next.
- Concurrency: Two ATMs accessing same account — DB-level locking (in code, `synchronized` on account)
- **Companies**: Amazon, Microsoft

**13. LRU / LFU Cache**
- Core use cases: `get(key)`, `put(key, value)`, eviction on capacity overflow
- Key classes: `Cache<K,V>` (interface), `LRUCache`, `LFUCache`, `Node`, `DoublyLinkedList`
- Patterns: Strategy (eviction policy — LRU, LFU, FIFO all implement `EvictionPolicy`)
- Core logic: See Phase 7 (7.2 and 7.3) for full implementation details
- Concurrency: Concurrent reads and writes → `ReentrantReadWriteLock`
- Extension test: "Add TTL-based expiry" → background thread + `TreeMap<ExpiryTime, Key>` for efficient expiry
- **Companies**: Google, Amazon, Flipkart, Rippling

**14. Pub-Sub / In-Memory Message Broker**
- Core use cases: Create topic, subscribe, publish message, unsubscribe
- Key classes: `Broker`, `Topic`, `Message`, `Publisher`, `Subscriber` (interface), `Subscription`
- Patterns: Observer (core of the system), Strategy (delivery — async vs sync, at-most-once vs at-least-once)
- Core logic: `Map<TopicId, List<Subscriber>>`. On publish → iterate subscribers, deliver message. Async delivery → `ExecutorService` with thread pool.
- Concurrency: Concurrent publish and subscribe → `ConcurrentHashMap` for topic-subscriber map, `CopyOnWriteArrayList` for subscriber lists
- Extension test: "Add message filtering — subscriber only gets messages matching a predicate" → `FilteredSubscriber` decorator
- **Companies**: Rippling, Flipkart

---

### Tier 3 — Advanced

> These combine multiple patterns, require non-trivial algorithms, and test system thinking.
> Flipkart and Rippling L5+ / SDE-3 territory, but knowing them makes SDE-2 a strong hire.

**15. Cron Job / Task Scheduler**
- Core use cases: Schedule task (one-time or recurring), cancel task, execute tasks at the right time, handle failures
- Key classes: `Scheduler`, `Task`, `CronExpression`, `TaskExecutor`, `TaskRegistry`
- Patterns: Command (Task as command), Strategy (scheduling policy), Observer (task completion notification)
- Core logic: **Min-heap sorted by next execution time**. Scheduler thread sleeps until `heap.peek().nextRunTime`. On wake → execute task, if recurring → compute next run time → re-insert.
  - Cron expression parsing: parse "0 */5 * * *" into next execution time
  - Missed task detection: if scheduler was down, check for tasks with `nextRunTime < now` on startup
- Concurrency: Thread pool for task execution — don't block the scheduler thread on a slow task
- Extension test: "Add task dependencies — task B runs only after task A completes" → DAG of tasks + topological execution
- **Companies**: Flipkart, Rippling, Google

**16. Ride-Sharing (Uber/Ola LLD)**
- Core use cases: Request ride, match with nearby driver, track ride, calculate fare, rate driver
- Key classes: `Rider`, `Driver`, `Ride`, `Location`, `RideRequest`, `MatchingService`, `FareCalculator`, `RatingService`
- Patterns: Strategy (matching algorithm, fare calculation), Observer (ride status updates), State (ride lifecycle: REQUESTED → MATCHED → IN_PROGRESS → COMPLETED)
- Core logic: **Matching** — find nearest available driver. Simple: iterate all available drivers, compute distance, pick closest. Better: spatial index (HashMap of geohash bucket → list of drivers).
- Extension test: "Add ride pooling / shared rides" → new RideType, modified MatchingStrategy
- **Companies**: Flipkart, Rippling, Google

**17. Spreadsheet (Excel)**
- Core use cases: Set cell value, set cell formula (=A1+B2), get cell value (evaluates formula), detect circular dependency
- Key classes: `Spreadsheet`, `Cell`, `CellValue` (literal vs formula), `FormulaEvaluator`, `DependencyGraph`
- Patterns: Observer (when A1 changes, all cells depending on A1 recompute), Composite (formula is a tree of expressions), Command (undo cell edit)
- Core logic:
  - **Dependency graph** — `Map<CellId, Set<CellId>>` of which cells depend on which. When cell changes, DFS/BFS through dependents to recompute.
  - **Circular dependency detection** — DFS cycle detection on the dependency graph before accepting a formula.
  - **Formula evaluation** — parse "=A1+B2*3" into expression tree, evaluate recursively.
- Concurrency: Concurrent cell edits — lock at cell level, not spreadsheet level
- Extension test: "Support functions like SUM(A1:A10)" → new `FunctionExpression` node in the expression tree
- **Companies**: Rippling (VERY common), Google, Flipkart

**18. Rule Engine / Workflow Engine**
- Core use cases: Define rules (IF condition THEN action), evaluate rules against data, priority ordering, chaining
- Key classes: `Rule`, `Condition`, `Action`, `RuleEngine`, `Fact`, `RuleSet`
- Patterns: **Chain of Responsibility** (rule evaluation chain), Strategy (different condition evaluators), Composite (AND/OR conditions as tree), Command (actions)
- Core logic:
  - `Condition` is a tree: `AND(age > 18, OR(country == "IN", country == "US"))` → Composite pattern
  - Rules evaluated in priority order — `PriorityQueue<Rule>`
  - First-match vs all-match — configurable
- Extension test: "Add a new condition type (regex match)" → new `RegexCondition implements Condition`
- **Companies**: Rippling (very common — their product IS a rule engine), Flipkart

**19. Multi-Player Card Game (e.g., Blackjack / UNO)**
- Core use cases: Deal cards, play turn, validate move, determine winner, handle special cards
- Key classes: `Game`, `Player`, `Card`, `Deck`, `Hand`, `GameRules`, `TurnManager`
- Patterns: Template Method (game loop: deal → play turns → determine winner), Strategy (game rules vary by game type), State (game phases), Observer (notify players of moves)
- Core logic: `Deck` with `shuffle()` and `draw()`. `TurnManager` tracks whose turn it is (circular iteration). `GameRules.isValidMove(card, topCard)` encapsulates game-specific logic.
- Extension test: "Support a new special card" → add to Card enum + update rules (if Strategy pattern, just add to the strategy)
- **Companies**: Flipkart, Rippling

**20. Rate Limiter (LLD)**
- Core use cases: Allow/deny request based on rate limit, support multiple algorithms, per-user limits
- Key classes: `RateLimiter` (interface), `TokenBucketLimiter`, `SlidingWindowLimiter`, `FixedWindowLimiter`, `RateLimitConfig`
- Patterns: Strategy (algorithm selection), Factory (create limiter from config)
- Core logic: Each algorithm from the System Design syllabus, implemented as a class
  - Token Bucket: `tokens` field, refilled by `rate * elapsed_time`, decrement on request
  - Sliding Window: `TreeMap<Timestamp, Count>` — remove entries older than window
- Concurrency: Thread-safe — `AtomicInteger` for token count or `synchronized` for window updates
- **Companies**: Google, Rippling, Flipkart

---

### Tier 4 — Rippling / Flipkart SDE-3 Specials

> These are the hardest problems. If you can do these clean in 90 minutes, you're SDE-3 material.

**21. Calendar / Meeting Scheduler**
- Core use cases: Create event, check availability, find common free slot for N users, recurring events
- Key classes: `Calendar`, `Event`, `User`, `TimeSlot`, `RecurrenceRule`, `AvailabilityService`
- Core logic: Per-user `TreeMap<StartTime, Event>`. Free slot = gap between events. Common free slot for N users = interval intersection across N TreeMaps.
- **Companies**: Google (very common), Rippling

**22. Multi-Tenant RBAC (Role-Based Access Control)**
- Core use cases: Create org/tenant, define roles with permissions, assign roles to users, check access
- Key classes: `Tenant`, `User`, `Role`, `Permission`, `AccessControlService`, `Resource`
- Core logic: `Role` has `Set<Permission>`. User has `Set<Role>`. Access check: `user.getRoles().stream().anyMatch(r -> r.hasPermission(resource, action))`. Hierarchy: roles can inherit from other roles.
- **Companies**: Rippling (their core product), Google

**23. In-Memory File System**
- Core use cases: Create file/directory, delete, move, ls, find, read/write content
- Key classes: `FileSystem`, `FileSystemItem` (abstract), `File`, `Directory`, `Path`
- Patterns: **Composite** (Directory contains FileSystemItems — files or other directories), Iterator (traverse tree)
- Core logic: Tree structure. `Directory` has `Map<String, FileSystemItem>` children. Path resolution = split by "/" and traverse.
- **Companies**: Google, Amazon, Flipkart

**24. Logging Framework (Log4j-style)**
- Core use cases: Log message with level, route to multiple outputs (console, file, DB), filter by level, format output
- Key classes: `Logger`, `LogLevel`, `LogMessage`, `Appender` (interface), `ConsoleAppender`, `FileAppender`, `Formatter`
- Patterns: **Singleton** (Logger), **Chain of Responsibility** (log level filtering), **Observer** (multiple appenders), **Strategy** (formatting), **Decorator** (add timestamp/thread-name decoration)
- Core logic: `Logger` has `LogLevel threshold` and `List<Appender>`. On `log(level, message)` → if level >= threshold → format → dispatch to all appenders.
- **Companies**: Rippling, Flipkart

---

### Problem → Pattern Quick Reference

| Problem | Must-Use Patterns | Key Data Structure |
|---------|------------------|-------------------|
| Parking Lot | Factory, Strategy, Singleton | HashMap, Queue |
| Tic-Tac-Toe | Strategy | 2D Array |
| Vending Machine | State, Chain of Responsibility | Enum, State classes |
| Elevator | State, Strategy, Observer | PriorityQueue |
| Chess | Factory, Strategy, Command | 2D Array, List |
| BookMyShow | Facade, Strategy, State | HashMap, TreeMap |
| Splitwise | Strategy, Factory, Observer | HashMap of HashMaps |
| Spreadsheet | Observer, Composite, Command | Graph (adjacency list) |
| Rule Engine | Chain of Resp, Composite, Strategy | PriorityQueue, Tree |
| Cron Scheduler | Command, Strategy | Min-Heap (PriorityQueue) |
| LRU Cache | Strategy | HashMap + DoublyLinkedList |
| Pub-Sub | Observer | ConcurrentHashMap |
| Rate Limiter | Strategy, Factory | TreeMap, AtomicInteger |
| Calendar | Strategy | TreeMap |
| File System | Composite, Iterator | Tree (Map children) |
| Logger | Singleton, Chain of Resp, Observer | List of Appenders |

---

### How to Practice

1. **Read the problem** — understand all use cases
2. **Sketch class diagram on paper** (5 min) — identify entities, relationships, patterns
3. **Code it** (60-90 min) — get happy path working first, then edge cases
4. **Review against checklist**:
   - [ ] No if-else on type — polymorphism instead
   - [ ] Strategy pattern for varying behavior
   - [ ] Factory for object creation
   - [ ] State pattern for entities with lifecycle
   - [ ] Each class has one responsibility
   - [ ] Dependencies injected, not hardcoded
   - [ ] Working main/driver demonstrating use cases
5. **Test the "new requirement" scenario** — add one feature, see how many files you touch
6. **Repeat in 3 days without notes** — draw the class diagram from memory
