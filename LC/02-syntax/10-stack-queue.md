# 10 — Stack & Queue

## Declaration

```java
// stack
Deque<Integer> stack = new ArrayDeque<>();

// queue
Deque<Integer> queue = new ArrayDeque<>();
```

Both use `ArrayDeque` — never use the legacy `Stack` class (slow, synchronized).

## Stack Operations (LIFO — last in, first out)

```java
stack.push(5);    // add to top
stack.pop();      // remove from top
stack.peek();     // look at top without removing
stack.isEmpty();  // true if empty
stack.size();
```

## Queue Operations (FIFO — first in, first out)

```java
queue.offer(5);   // add to back
queue.poll();     // remove from front
queue.peek();     // look at front without removing
queue.isEmpty();  // true if empty
queue.size();
```

## Deque as Double-Ended Queue (sliding window)

```java
Deque<Integer> dq = new ArrayDeque<>();

dq.offerFirst(5);   // add to front
dq.offerLast(5);    // add to back
dq.pollFirst();     // remove from front
dq.pollLast();      // remove from back
dq.peekFirst();     // look at front
dq.peekLast();      // look at back
```

## Gotchas

- `Deque` is an interface — `new Deque<>()` won't compile. Always instantiate as `new ArrayDeque<>()`
- Never use `Stack` class — use `ArrayDeque` always
- `pop()` / `poll()` return `null` (queue) or throw exception (stack) if empty — check `isEmpty()` first
- Stack uses `push/pop/peek`, Queue uses `offer/poll/peek` — same `peek` for both
- `addFirst`/`addLast` exist but prefer `offerFirst`/`offerLast` — offer returns false on failure, add throws exception
