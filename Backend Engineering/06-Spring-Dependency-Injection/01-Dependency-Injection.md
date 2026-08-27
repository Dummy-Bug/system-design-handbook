Layering a project puts the service in one folder and the repository in another, and has the service call the repository. That leaves a question nobody asked yet: when the service runs, where does its repository actually come from? Answering it properly means starting with no framework at all.

# Two ordinary classes

Strip everything back. No Spring, no framework — a plain Java project with two classes.

```java
1  // TodoService.java
2  public class TodoService {
3
4      private TodoRepository todoRepository;
5
6      public List<Todo> getAllTodos() {
7          return todoRepository.findAll();
8      }
9  }
```

```java
1  // TodoRepository.java
2  public class TodoRepository {
3
4      private List<Todo> todos = new ArrayList<>();
5
6      public List<Todo> findAll() {
7          return todos;
8      }
9  }
```

Nothing unusual. The service holds a repository and calls `findAll()` on it.

# Running it fails

Now a main method that uses the service:

```java
1  // Main.java
2  public class Main {
3      public static void main(String[] args) {
4          TodoService ts = new TodoService();
5          ts.getAllTodos();
6      }
7  }
```

Line 4 calls the **default constructor** — the one Java provides because no constructor was written. Line 5 then fails at runtime.

Trace why, because the reasoning is the whole point.

`getAllTodos()` calls `todoRepository.findAll()`. So what is `todoRepository`?

> [!important] **Nothing ever created it.** `new TodoRepository()` appears nowhere — not in `main`, not in `TodoService`, nowhere at all. Its constructor was never called, so no object exists. The field is a reference with nothing to refer to, so Java leaves it **null**, and calling a method on null fails.

The class compiles perfectly. It fails the moment it runs.

# Creating the object is not enough

The obvious fix is to make one. `TodoService` depends on `TodoRepository`, so the repository has to exist first:

```java
1  // Main.java
2  public static void main(String[] args) {
3      TodoRepository r = new TodoRepository();
4      TodoService ts = new TodoService();
5      ts.getAllTodos();
6  }
```

This still fails, for a reason worth being precise about.

> [!warning] An object now exists, but it exists **as a local variable in `main`**. Nothing connected it to the service's field. `TodoService.todoRepository` is still null — the object over in `main` has no relationship to it.

Creating a dependency and supplying a dependency are two different steps.

# Supplying it

The missing step is getting `r` into the service's field, and a constructor is the natural way:

```java
1  // TodoService.java
2  public class TodoService {
3
4      private TodoRepository todoRepository;
5
6      public TodoService(TodoRepository r) {
7          this.todoRepository = r;
8      }
9
10     public List<Todo> getAllTodos() {
11         return todoRepository.findAll();
12     }
13 }
```

```java
1  // Main.java
2  public static void main(String[] args) {
3      TodoRepository r = new TodoRepository();
4      TodoService ts = new TodoService(r);
5      ts.getAllTodos();
6  }
```

Line 4 passes the object in. Line 7 of the service stores it. Now it runs.

# What that was

```mermaid
flowchart LR
    A["TodoRepository object<br/>created first"] -- "passed to the constructor" --> B["TodoService"]
    B --> C["stored in its field<br/>and usable"]
```

> [!important] **Dependency injection is supplying an object its dependencies from outside, rather than having it create them itself.**
>
> `TodoService` depends on `TodoRepository`. Rather than the service constructing its own, the object is built elsewhere and handed in. That handing-in is the injection.

And because it arrived through a constructor, this is specifically **constructor-based injection**.

Note what has not happened: the service never calls `new TodoRepository()`. It states what it needs and receives it. That separation is the whole idea, and it is what makes swapping the implementation possible later.

# The observation that motivates everything else

Now go back and look at a Spring Boot project doing the same job.

```java
1  // src/main/java/com/example/demo/services/TodoService.java
2  @Service
3  public class TodoService {
4
5      private ITodoRepository todoRepository;
6
7      public TodoService(ITodoRepository _todoRepository) {
8          this.todoRepository = _todoRepository;
9      }
10     // ...
11 }
```

There is a constructor, so injection is clearly happening. But search the entire project and:

- Nobody writes `new TodoService()`
- Nobody writes `new TodoRepository()`
- Nobody writes `new TodoController()`

> [!important] **`new` does not appear anywhere.** Yet the application runs, so the objects plainly exist and are plainly being wired together.

Something is creating them and supplying their dependencies without being asked. What that something is, and how it knows what to build, is the next thing to work out.
