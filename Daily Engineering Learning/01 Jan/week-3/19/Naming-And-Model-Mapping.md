
#backend #data-modeling #api-integration #python

---

## Problem This Solves

External APIs use naming styles and field structures that do not match Python conventions.

If you mix styles directly:

- Code becomes inconsistent
    
- Refactoring becomes risky
    
- Business logic becomes tied to API contracts
    

This file documents the correct way to separate **external representation** from **internal domain model**.

---

## Snake Case Internally, Camel Case Externally

### What This Means

Python follows PEP8:

`snake_case`

Most APIs return:

`camelCase`

These two styles must not be mixed.

---

### Correct Pattern

- Internal Python models use snake_case
    
- External API fields remain untouched
    
- Mapping is handled at the adapter layer
    

Example:

External API:

`isWorkflowEnabled`

Internal Python:

`is_workflow_enabled`

---

### Why This Matters

If you allow camelCase inside Python:

- Codebase becomes stylistically inconsistent
    
- Linters and formatters lose effectiveness
    
- Developers get confused
    

Maintaining idiomatic style improves:

- Readability
    
- Maintainability
    
- Long-term scalability
    

---

## Mapping Using Pydantic Aliases

### What Aliases Do

Pydantic allows mapping external fields using:

`Field(alias="externalFieldName")`

This creates a clear boundary between:

`External contract ↓ Internal domain model`

---

### Example Pattern

Instead of accessing raw JSON:

`data["isWorkflowEnabled"]`

Use:

`model.is_workflow_enabled`

This provides:

- Type safety
    
- IDE autocomplete
    
- Refactor support
    
- Validation
    

---

### Why Aliases Are Better Than Manual Mapping

Manual mapping:

- Is repetitive
    
- Is error-prone
    
- Breaks easily when API changes
    

Schema-based mapping:

- Centralizes contract definition
    
- Makes API assumptions explicit
    
- Fails fast on mismatch
    

---

## populate_by_name = True

### What It Does

Allows Pydantic models to be created using:

- External alias names
    
- Internal Python field names
    

---

### Why This Is Important

Models are used in two places:

1. Parsing API responses
    
2. Creating objects manually in application code
    

Without this flag:

- You are forced to use API naming style inside Python
    
- Internal code becomes polluted with camelCase
    

With this flag:

- API parsing works normally
    
- Internal code remains Pythonic
    

---

## Mental Model To Remember

`External API Format         ↓ Adapter Layer (Aliases + Validation)         ↓ Internal Domain Model`

Never let external formats leak into business logic.

---

## Common Mistakes To Avoid

- Renaming internal fields to match API naming
    
- Accessing raw JSON dictionaries inside business code
    
- Skipping schema mapping and trusting API structure
    

---

## Transferable Principle

> Internal domain models must remain clean and idiomatic, even when external APIs are messy.

This applies across:

- Languages
    
- Frameworks
    
- Companies