## Phase 7 — Exception Handling & I/O

> Interview relevance: "Checked vs unchecked — when do you use which?" is a standard SDE-2 question.
> Resource management (try-with-resources) and serialization pitfalls come up in both coding rounds
> and system design discussions. I/O internals matter when you're reasoning about file processing,
> network programming, or explaining NIO in a system design context.

---

### 7.1 Exception Hierarchy
```
Throwable
├── Error (don't catch these — JVM-level, unrecoverable)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── NoClassDefFoundError
└── Exception
    ├── Checked Exceptions (must handle — compiler enforces)
    │   ├── IOException
    │   ├── SQLException
    │   ├── ClassNotFoundException
    │   └── InterruptedException
    └── RuntimeException (unchecked — compiler doesn't enforce)
        ├── NullPointerException
        ├── IllegalArgumentException
        ├── IllegalStateException
        ├── IndexOutOfBoundsException
        ├── ClassCastException
        ├── UnsupportedOperationException
        └── ConcurrentModificationException
```

### 7.2 Checked vs Unchecked — The Great Debate
- **Checked exceptions**: compiler forces you to handle them (try-catch or declare throws). Represent recoverable conditions — file not found, network timeout, invalid SQL.
- **Unchecked exceptions (RuntimeException)**: compiler doesn't enforce handling. Represent programming bugs — null dereference, array out of bounds, invalid argument.
- **The debate**:
  - **Pro-checked**: force the caller to think about failure. Can't accidentally ignore an IOException.
  - **Anti-checked** (modern consensus): clutters code with try-catch blocks, forces exception wrapping up the call chain, lambdas can't throw checked exceptions (major pain with Streams API).
- **Modern practice**: most frameworks (Spring, Hibernate) use unchecked exceptions exclusively. Custom business exceptions should generally be unchecked (`extends RuntimeException`).
- **Interview answer**: "I use checked exceptions only when the caller can meaningfully recover — like retrying a connection. For everything else — validation errors, business logic violations, not-found cases — I use unchecked exceptions."

### 7.3 Custom Exceptions
- **Extend `RuntimeException`** for business logic exceptions (unchecked):
  ```
  class UserNotFoundException extends RuntimeException {
      private final String userId;
      UserNotFoundException(String userId) {
          super("User not found: " + userId);
          this.userId = userId;
      }
  }
  ```
- Include context — not just a message, but the relevant data (userId, orderId) so the handler can take action.
- **Use specific exceptions** — `SpotNotAvailableException`, `InsufficientBalanceException` — not generic `RuntimeException("error")`.
- **Exception hierarchy for your domain**: consider a base exception (`AppException`) with specific subtypes. Handlers can catch the base or the specific.

### 7.4 Try-With-Resources
- **The problem**: resources (files, connections, streams) must be closed after use. Manual try-finally is verbose and error-prone:
  ```
  InputStream is = null;
  try {
      is = new FileInputStream("file.txt");
      // use it
  } finally {
      if (is != null) is.close(); // what if close() throws?
  }
  ```
- **The fix** (Java 7+): `try (Resource r = new Resource()) { ... }` — resource is automatically closed when the block exits, even on exception.
  ```
  try (InputStream is = new FileInputStream("file.txt");
       BufferedReader br = new BufferedReader(new InputStreamReader(is))) {
      String line = br.readLine();
  }
  // both br and is automatically closed, in reverse order
  ```
- **`AutoCloseable`** — any class implementing `AutoCloseable` (with a `close()` method) can be used in try-with-resources. All Java I/O classes, JDBC Connection, Statement, ResultSet implement it.
- **Suppressed exceptions**: if both the try block and close() throw, the close() exception is **suppressed** (attached to the primary exception, accessible via `getSuppressed()`). The primary exception is thrown.
- **Interview rule**: if you see a resource opened without try-with-resources, that's a bug. Always use it.

### 7.5 Byte Streams vs Character Streams
- **Byte streams** — `InputStream` / `OutputStream` — handle raw bytes. Use for binary data (images, PDFs, network packets).
  - `FileInputStream`, `ByteArrayInputStream`, `BufferedInputStream`
- **Character streams** — `Reader` / `Writer` — handle characters (text) with encoding awareness. Use for text files, logs, configs.
  - `FileReader`, `BufferedReader`, `InputStreamReader` (bridge: byte stream → character stream with encoding)
- **The encoding trap**: `new FileReader("file.txt")` uses the platform's default encoding — different on different systems. Always specify: `new InputStreamReader(new FileInputStream("file.txt"), StandardCharsets.UTF_8)`.
- **Since Java 11**: `Files.readString(path)` and `Files.writeString(path, content)` — simplest way to read/write text files. Use these.

### 7.6 Buffered I/O
- **The problem**: every `read()` or `write()` call on an unbuffered stream triggers a system call to the OS. System calls are expensive — crossing the user/kernel boundary takes microseconds each.
- **The fix**: wrap in a buffer. `BufferedInputStream` / `BufferedReader` read a large chunk (8KB default) into an in-memory buffer. Subsequent reads come from the buffer — no system call until the buffer is empty.
- **Performance difference**: reading a 10MB file byte-by-byte with `FileInputStream` → millions of system calls. With `BufferedInputStream` → ~1,250 system calls (10MB / 8KB). Orders of magnitude faster.
- **Always buffer**: `new BufferedReader(new FileReader(...))`, `new BufferedOutputStream(new FileOutputStream(...))`. Or use `Files.newBufferedReader()` / `Files.newBufferedWriter()`.

### 7.7 NIO Basics — Channels, Buffers, Non-Blocking
- **Old I/O (java.io)**: stream-based, blocking, one byte/char at a time (buffered or not), one thread per connection.
- **NIO (java.nio)**: buffer-based, supports non-blocking, channel-based, can handle many connections with fewer threads.
- **Key concepts**:
  - **Buffer** — a block of memory. You write data into a buffer, flip it, then read from it. `ByteBuffer` is the most common.
  - **Channel** — a bidirectional pipe to a data source (file, socket). `FileChannel`, `SocketChannel`. Read/write through buffers.
  - **Selector** — watches multiple channels for events (readable, writable, connectable). One thread can monitor thousands of connections.
- **Non-blocking I/O**: `channel.configureBlocking(false)` — `read()` returns immediately (0 bytes if no data available) instead of blocking. Combined with Selector, enables event-driven servers.
- **When NIO matters**: high-concurrency network servers (thousands of connections). Netty, a popular Java network framework, is built on NIO. This is the foundation for understanding how web servers like Tomcat handle concurrent requests.
- **For interviews**: know that NIO exists and why (many connections, fewer threads). Don't need to write NIO code from scratch.

### 7.8 Serialization
- **What**: converting an object to bytes (serialization) and back (deserialization). Used for: saving to disk, sending over network, caching.
- **`Serializable`** — marker interface. Implement it and Java's default serialization kicks in. No methods to override.
- **`serialVersionUID`** — a version number for the class. If you don't declare it, Java auto-generates one from the class structure. If the class changes (add/remove field), the auto-generated UID changes → deserialization of old data fails with `InvalidClassException`. **Always declare it explicitly**: `private static final long serialVersionUID = 1L;`
- **`transient`** — marks a field to be excluded from serialization. Use for sensitive data (passwords), derived data (can be recomputed), or non-serializable fields (threads, connections).
- **Why default serialization is dangerous**:
  - Security — deserialization can execute arbitrary code (deserialization attacks). Never deserialize untrusted data.
  - Brittleness — any class change can break compatibility.
  - Performance — Java's default serialization is slow and produces large output.
- **Modern alternative**: use JSON serialization (Jackson `ObjectMapper`) or Protocol Buffers for structured data exchange. Default Java serialization is legacy — avoid in new code.
- **Interview answer**: "I'd use Jackson for JSON serialization over Java's built-in Serializable. It's safer (no code execution on deserialization), human-readable, language-agnostic, and gives explicit control over what's serialized."
