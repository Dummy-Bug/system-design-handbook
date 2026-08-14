
# What an exception is

> **Exception:** an **unwanted**, **unexpected** event that **disturbs the normal flow of the program**.

Every word in it is doing work — *unwanted*, *unexpected*, and above all *disturbs the normal flow*. He builds up to it through two stories rather than stating it cold.

# Why you should handle exceptions

> It is **highly recommended** to handle exceptions.

## The database connection

```
open DB connection
read the data          ← SQLException raised here
close the connection
```

The connection opens. While reading, an `SQLException` is raised. It is not handled, so **the program terminates right there** — at the read.

Which means the third line never runs. **Nobody closes the connection.** One connection is now leaked.

Let that happen ten times and ten connections are wasted. And if the database server supports only ten concurrent connections, the **eleventh person cannot connect at all**. The entire application is down — not because of the original `SQLException`, but because of what the unhandled exception skipped.

The right behaviour is obvious once stated: if an exception occurs, **close the connection first, then stop.**

> [!important] **The main objective of exception handling is graceful (normal) termination of the program.** And *graceful* has a precise meaning here: **we should not miss anything and we should not lose anything.** The program may still end — but it ends having released what it held.
>


---

# What exception handling actually means

This is the part people get wrong, and the PDF states it flatly:

> **Exception handling doesn't mean repairing an exception.** We have to define an **alternative way to continue the rest of the program normally**. This way of defining an alternative is nothing but exception handling.

## In code

Which turns the London requirement into this shape:

```java
try {
    // read data from the Remote file
} catch (FileNotFoundException e) {
    // use a local file and continue the rest of the program normally
}
```

If the Remote file is not available, you cannot make it available — **you are not responsible for placing a file one Remote server.** What you can do is keep a local file on your own machine and use that instead.

> [!important] **The two definitions to keep separate.**
> **An exception** is an unwanted, unexpected event that disturbs the normal flow of the program.
> **Exception handling** is defining an alternative way to continue the rest of the program normally — *not* repairing the exception.

---
