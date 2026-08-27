The layering material describes what each layer is for. This note walks a single request through all of them in real code — a POST that creates a todo — and picks up the annotations, the JSON conversion, and one judgement call about where logic belongs.

# CRUD

Four operations turn up on essentially every resource, and they have a collective name:

| Letter | Operation | Method |
|---|---|---|
| **C** | Create | `POST` |
| **R** | Read | `GET` |
| **U** | Update | `PUT` |
| **D** | Delete | `DELETE` |

> [!info] **CRUD is the backbone of a resource API.** If you can create a thing, read it, update it and delete it, you have covered what most callers need. The REST conventions covered earlier are what map each operation onto a method and a URL.

For todos:

```text
1  POST    /api/v1/todos           create a todo, with a body
2  GET     /api/v1/todos           read them all, no body
3  PUT     /api/v1/todos/:todoId   update one, with a body
4  DELETE  /api/v1/todos/:todoId   delete one, no body
```

# A tool for calling them

A browser can issue a `GET` by visiting a URL. It cannot easily send a `POST` with a JSON body.

**Postman** is a client for exactly this — a form where you pick the method, type the address, and compose a request body. Available on every platform.

For the create endpoint you would select `POST`, enter `http://localhost:3001/api/v1/todos`, choose a raw JSON body, and type:

```json
1  {
2    "content": "Another todo"
3  }
```

Send that before the endpoint exists and you get a method-not-supported error — the routing layer received a `POST` for a route that only handles `GET`, and correctly refused it.

# Declaring the endpoint

`@GetMapping` declares a `GET`. `@PostMapping` declares a `POST`:

```java
1  // src/main/java/com/example/demo/controllers/TodoController.java
2  @RestController
3  @RequestMapping("/api/v1/todos")
4  @AllArgsConstructor
5  public class TodoController {
6
7      private TodoService todoService;
8
9      @GetMapping
10     public List<Todo> getAllTodos() {
11         return todoService.getAllTodos();
12     }
13
14     @PostMapping
15     public Todo createTodo(@RequestBody CreateTodoDTO createTodoDTO) {
16         return todoService.createNewTodo(createTodoDTO);
17     }
18 }
```

`@RequestMapping` on line 3 sets the **base route for the whole class**. The method annotations then say which HTTP method each function handles.

# Why the parameter is a DTO

Line 15 takes a `CreateTodoDTO`. It could not take the JSON directly, and the reason is the same one behind the schema layer.

> [!important] **Java has no JSON type.** JSON arrives as text over the network; Java understands Java objects. So the body has to be converted into an object — and creating an object requires a class. That class is the DTO.

```java
1  // src/main/java/com/example/demo/dtos/CreateTodoDTO.java
2  package com.example.demo.dtos;
3
4  import lombok.AllArgsConstructor;
5  import lombok.Getter;
6  import lombok.Setter;
7
8  @Getter
9  @Setter
10 @AllArgsConstructor
11 public class CreateTodoDTO {
12     private String content;
13 }
```

One field, because `content` is the only thing the client supplies. The id is generated server-side.

> [!info] Lombok's `@Getter` and `@Setter` generate the accessors the conversion needs. `@Data` is a shorthand that brings both together along with a few other things — either is fine.

## `@RequestBody`

The annotation on line 15 of the controller is what connects the two:

> [!important] **`@RequestBody` tells Spring to bind the incoming request body to that parameter.** Without it, Spring has no reason to think the parameter should come from the body at all.

## Serialisation, and who does it

The conversion itself has a name.

> [!info] **Serialisation** is turning an object into a transferable form. **Deserialisation** is turning it back. A JSON body arriving and becoming a `CreateTodoDTO` is deserialisation; your response object becoming JSON on the way out is serialisation.

Spring Boot does this using **Jackson**, which it wires up automatically — which is why none of this appears in your code.

> [!tip] If the idea feels abstract, it is the same problem as the classic exercise of serialising a binary tree. You cannot send a tree across a network, so you turn it into a string, send that, and rebuild the tree at the other end. That exercise is not a puzzle for its own sake — it is this, in miniature.

# Down through the layers

The controller hands off, doing nothing else:

```java
1  // src/main/java/com/example/demo/services/TodoService.java
2  public Todo createNewTodo(CreateTodoDTO createTodoDTO) {
3
4      Integer newTodoId = 1;
5
6      List<Todo> todos = todoRepository.findAll();
7
8      if(!todos.isEmpty()) {
9          Todo lastTodo = todos.get(todos.size() - 1);
10         newTodoId = lastTodo.getId() + 1;
11     }
12
13     Todo newTodo = todoRepository.save(newTodoId, createTodoDTO.getContent());
14     return newTodo;
15 }
```

And the repository only stores:

```java
1  // src/main/java/com/example/demo/repositories/InMemoryTodoRepository.java
2  public Todo save(Integer newTodoId, String todoContent) {
3
4     Todo newTodo = new Todo(newTodoId, todoContent);
5
6      todos.add(newTodo);
7      return newTodo;
8  }
```

```mermaid
flowchart LR
    P["POST with JSON body"] --> C["Controller<br/>@RequestBody → DTO"]
    C --> S["Service<br/>works out the new id"]
    S --> R["Repository<br/>stores it"]
    R -. "saved todo" .-> S
    S -. "saved todo" .-> C
    C -. "JSON response" .-> P
```

# The judgement call worth copying

The id-generation logic on lines 4 to 11 was first written **inside the repository** — fetch the last todo, add one, build the object, store it. It worked.

Then it got moved, and the reasoning is the thing to take away:

> [!important] **Deciding what the next id should be is a rule about how the application behaves. Storing a record is not.** Fetching the last todo and incrementing is business logic, so it belongs in the service. The repository should receive a finished id and a finished piece of content and do nothing but save them.

Look at the signature that resulted — `save(Integer newTodoId, String todoContent)`. The repository is told exactly what to store. It makes no decisions.

> [!info] On an application this small the distinction changes nothing that runs. It is still worth making, because the boundary is easier to hold when the code is simple than to recover once it is not.

# It works

```text
1  POST /api/v1/todos   {"content": "Another todo"}→ the created todo, with an id
2  GET  /api/v1/todos                     → four todos, including the new one
3  POST /api/v1/todos   {"content": "Fifth todo"} → the created todo
4  GET  /api/v1/todos                        → five todos
```

Each layer did its own job: the controller took the request and returned the response, the service decided the id, the repository stored the record. That is the layering from the previous folder, running.

# Path variables

Update and delete both need to identify **which** todo, which the create endpoint never had to:

```text
1  PUT     /api/v1/todos/:todoId
2  DELETE  /api/v1/todos/:todoId
```

That `:todoId` is a **path variable** — a part of the route that changes per request. `/api/v1/todos/2` addresses the todo with id 2.

Consuming one requires an annotation not used above, and wiring the two endpoints through the same three layers.

> [!info] `PUT` also carries a body, since updating means supplying new content. `DELETE` does not — the id in the path is the entire request.
