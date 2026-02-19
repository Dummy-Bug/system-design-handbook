# Query Patterns Observation

Before choosing a database, we identify dominant query patterns.

## Primary Query Types

1. **Hotel Detail Queries**
    
    - Fetch hotel metadata
        
    - Amenities
        
    - Location info
        
2. **Room Availability Queries**
    
    - List room types per hotel
        
    - Filter by capacity and price
        
    - Date-range availability
        
3. **Reservation Creation**
    
    - Atomic booking operation
        
    - Inventory update
        
    - Payment linkage
        
4. **Reservation History**
    
    - User booking history
        
    - Hotel booking dashboard
        

These queries involve **strong relationships** and **multi-table joins**.

---

# Database Choice: Relational Database

Relational database is the correct default choice.

---

## Why Relational DB Fits This System

### 1. Read Heavy With Transaction-Critical Writes

Search and availability:

- High read volume
    

Booking:

- Low QPS
    
- High correctness requirement
    

Relational DB handles this pattern efficiently with:

- Indexes
    
- Query optimizer
    
- Transaction isolation
    

---

### 2. ACID Guarantees Reduce Application Complexity

Booking requires:

- Atomic reservation creation
    
- Inventory consistency
    
- Payment state coupling
    

Relational DB provides:

- Atomicity
    
- Consistency
    
- Isolation
    
- Durability
    

Which avoids implementing custom distributed locking logic early.

---

### 3. Strongly Structured Relationships

Hotel domain is relational by nature:

- Hotel → Rooms
    
- Room → Room Types
    
- Reservation → Guest
    
- Reservation → Payment
    

Normalized schema maps naturally to relational model.

---

### 4. Mature Ecosystem

Benefits:

- Replication support
    
- Read replicas
    
- Backup tooling
    
- Query optimization
    
- Monitoring
    

Operational reliability matters more than raw performance.