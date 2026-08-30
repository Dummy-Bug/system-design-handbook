Two entities now, and both need an id declared exactly the same way. Three entities and it will be three copies. The obvious fix is a parent class — and the obvious fix does not work, for reasons worth understanding.

# The duplication

Both classes carry this:

```java
1  @Id
2  @GeneratedValue(strategy = GenerationType.IDENTITY)
3  private Long id;
```

Identical, and it will be identical in every entity you ever add. In ordinary Java the answer is inheritance: put it in a parent, extend it.

```java
1  public class BaseEntity {
2
3      @Id
4      @GeneratedValue(strategy = GenerationType.IDENTITY)
5      private Long id;
6  }
```

```java
1  @Entity
2  @Table(name = "categories")
3  public class Category extends BaseEntity {
4
5      private String name;
6  }
```

Run it and it fails.

# Failure one

```text
1  entity Category has no identifier
```

Category extends a class that plainly declares `@Id`, and Hibernate cannot see it.

> [!important] **The annotations only mean something on a class Hibernate is looking at.** `BaseEntity` is an ordinary Java class as far as the framework is concerned — not part of the mapping at all — so the `@Id` inside it is just an annotation on a field nobody is reading.

# Failure two

The natural next thought: mark the parent as an entity too, so the framework does look at it.

```java
1  @Entity
2  public class BaseEntity { ... }
```

Which fails differently:

```text
1  Category is a subclass in a single table hierarchy and cannot be annotated with @Table
```

> [!important] **`@Entity` means table.** Marking `BaseEntity` as one told Hibernate you want it stored — and then it had to decide how a parent table and two child tables relate, chose a strategy, and that strategy conflicts with `Category` naming its own table.

That is a real feature, and sometimes what you want.

> [!info] **Inheritance has a genuine meaning in the database, not only in Java.** Consider a `user` who may be a `customer` or a `seller` — shared properties, plus properties specific to each, and both still users. Expressing that faithfully is what the inheritance strategies are for, and JPA offers several: everything in one table, or a table per subclass joined to the parent. Which to use is a design decision with real trade-offs.

But that is not the situation here. **There is no base entity in the business domain.** Nothing is a BaseEntity. It exists only to avoid typing the same three lines repeatedly.

# `@MappedSuperclass`

Which is exactly what the annotation is for.

```java
1  // src/main/java/com/example/FakeCommerce/schema/BaseEntity.java
2  package com.example.FakeCommerce.schema;
3
4  import jakarta.persistence.GeneratedValue;
5  import jakarta.persistence.GenerationType;
6  import jakarta.persistence.Id;
7  import jakarta.persistence.MappedSuperclass;
8  import lombok.Data;
9
10 @Data
11 @MappedSuperclass
12 public class BaseEntity {
13
14     @Id
15     @GeneratedValue(strategy = GenerationType.IDENTITY) 
16     private Long id;
17 }
```

> [!important] **`@MappedSuperclass` declares a class that is not itself an entity, but whose mappings are inherited by the entities extending it.**
>
> Not an entity means **no table**. Mappings inherited means the `@Id` and `@GeneratedValue` are picked up by every subclass as though written there.

```mermaid
flowchart TB
    B["BaseEntity<br/>MappedSuperclass<br/>declares id"]
    B -- extends --> C["Category<br/>Entity"]
    B -- extends --> P["Product<br/>Entity"]
    C -- creates --> TC[("categories<br/>id, name")]
    P -- creates --> TP[("products<br/>id, title, price, category_id")]
```

Both child tables carry an `id` that neither child class declares. The parent has no box of its own on the database side, because it was never meant to be stored.

Exactly the distinction the two failures were groping at. `@Entity` says store this. `@MappedSuperclass` says do not store this, **but do read the annotations inside it.**

# Proof

Running it against MySQL produces:

```text
1  Tables_in_fakecommerce_scratch
2  categories
3  products
```

**Two tables. No `base_entity`.** And each carries the inherited id:

```text
1  Hibernate: create table categories (id bigint not null auto_increment, name varchar(255),
2             primary key (id)) engine=InnoDB
3  Hibernate: create table products (price decimal(38,2) not null, category_id bigint not null,
4             id bigint not null auto_increment, description TEXT, image varchar(255),
5             rating varchar(255), title varchar(255) not null, primary key (id)) engine=InnoDB
```

> [!info] **Verified.** The `id bigint not null auto_increment, primary key (id)` on both tables comes from a field neither class declares. That is the mapping being inherited without the parent existing as a table.

# The resulting classes

```java
1  // src/main/java/com/example/FakeCommerce/schema/Category.java
2  @Data
3  @AllArgsConstructor
4  @NoArgsConstructor
5  @Builder
6  @Entity
7  @Table(name = "categories")
8  public class Category extends BaseEntity {
9
10     private String name;
11 }
```

Two lines of substance. The id, its generation strategy and its primary-key status all arrive from the parent.

> [!info] `@MappedSuperclass` is the right tool when the parent is a **convenience for developers** rather than a concept in the domain. When the parent is a real thing — a user that is sometimes a customer and sometimes a seller — you want one of the actual inheritance strategies instead, and a table to go with it.

This also scales in a way that matters later. Fields almost every table wants — created and updated timestamps, a soft-delete flag — go on `BaseEntity` once and appear everywhere.

# What inheriting does to equality

Extending a parent class has one consequence that is easy to miss, and the compiler says so out loud:

```text
1  warning: Generating equals/hashCode implementation but without a call to superclass,
2  even though this class does not extend java.lang.Object. If this is intentional,
3  add '@EqualsAndHashCode(callSuper=false)' to your type.
4  @Data
```

**`@Data` generates `equals` and `hashCode` from the fields declared in the class itself, and only those.** Java's default is that two objects are equal when they are the same object in memory; Lombok replaces that with a field-by-field comparison. Inherited fields are not part of it.

```mermaid
flowchart TB
    subgraph CAT["Category"]
        N["name"]
    end
    subgraph BASE["BaseEntity"]
        I["id"]
        C["createdAt"]
        U["updatedAt"]
    end
    CAT --> IN["compared by equals"]
    BASE --> OUT["ignored by equals"]
```

Which means **`id` is excluded** — the one field that says which row this is.

# The two ways that bites

**Different rows compare as equal.** Nothing stops two categories sharing a name unless a unique constraint says so:

```text
1  id = 2   name = Books
2  id = 7   name = Books
```

Two rows, two distinct categories. Comparing only `name` reports them as the same object, so `List.contains` matches the wrong one, a `Set` silently keeps one and drops the other, and a `Map` overwrites.

**The hash changes as the object changes.** This one is worse, because entities are mutable by design:

```java
1  Set<Product> selected = new HashSet<>();
2  selected.add(product);        // hashed on the current title and price
3  product.setPrice(newPrice);   // the hash is now a different number
4  selected.contains(product);   // false
```

The object is in the set, and the set cannot find it — it was filed under the old hash and is being looked for under the new one. Saving a new entity does the same damage in reverse: `id` goes from null to a real value, and anything already keyed on that object is stranded.

# Identity belongs to the id

A row is identified by its primary key. Basing equality on anything else is guessing, so the parent should decide it once for everyone:

```java
1  // src/main/java/com/example/FakeCommerce/schema/BaseEntity.java
2  @Getter
3  @Setter
4  @MappedSuperclass
5  public class BaseEntity {
6
7      @Id
8      @GeneratedValue(strategy = GenerationType.IDENTITY)
9      private Long id;
10
11     @Override
12     public boolean equals(Object o) {
13         if (this == o) return true;
14         if (o == null || Hibernate.getClass(this) != Hibernate.getClass(o)) return false;
15         BaseEntity other = (BaseEntity) o;
16         return id != null && id.equals(other.id);
17     }
18
19     @Override
20     public int hashCode() {
21         return Hibernate.getClass(this).hashCode();
22     }
23 }
```

**Line 14 uses `Hibernate.getClass` rather than `getClass`.** A lazily-loaded association is a proxy — a generated subclass standing in for the real entity until something touches it. Plain `getClass()` on a proxy returns that generated class, so a proxy and a loaded instance of the very same row would compare as different. `Hibernate.getClass` unwraps the proxy and reports the real entity class. It also keeps a `Product` with id 1 from equalling a `Category` with id 1.

**Line 16 requires a non-null id.** An entity not yet saved has no identity to compare, so it is equal only to itself — which line 13 already handles.

**Line 21 returns the same hash for every instance of a type.** That is deliberate: a constant cannot change when a field is edited or when an id is assigned on save, which is exactly the instability being fixed. Every entity of a type landing in one bucket costs nothing at the sizes entity collections actually reach.

For this to take effect the subclasses must stop generating their own. `@Data` bundles `@Getter`, `@Setter`, `@ToString`, `@EqualsAndHashCode` and a constructor together, so replacing it with the three that are wanted leaves the inherited implementation in place:

```java
1  // src/main/java/com/example/FakeCommerce/schema/Category.java
2  @Getter
3  @Setter
4  @ToString
5  @AllArgsConstructor
6  @NoArgsConstructor
7  @Builder
8  @Entity
9  @Table(name = "categories")
10 public class Category extends BaseEntity {
11
12     @Column(nullable = false)
13     private String name;
14 }
```

> [!warning] `@EqualsAndHashCode(callSuper = false)` is what the warning text suggests, and it only silences the message — the behaviour above is unchanged. `callSuper = true` does bring `id` into the comparison, but keeps every mutable field in it too, so the unstable hash survives. Neither is a fix. **Added beyond what was covered.**
