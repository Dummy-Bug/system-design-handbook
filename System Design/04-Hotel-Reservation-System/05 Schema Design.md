
## Hotel Service Schema

### Hotel Table

`hotel ------ id (PK) name address city country latitude longitude rating created_at`

---

### Room Table

Rooms represent physical units.

`room ------ id (PK) hotel_id (FK) room_type_id (FK) floor room_number status created_at`

Important:

- Do NOT store is_available boolean.
    
- Availability is date-based and derived.
    

---

### Room Type Table

Shared configuration.

`room_type --------- id (PK) hotel_id (FK) name capacity bed_type amenities base_price`

Examples:

- DELUXE
    
- SUITE
    
- STANDARD

---

# Rate Service Schema (Dynamic Pricing)

Price changes by date.

---

### Room Rate Table

`room_rate --------- id (PK) hotel_id (FK) room_type_id (FK) date price currency`

Indexed by:

- (hotel_id, date)
    
- (room_type_id, date)
    

---

# Reservation Service Schema

---

### Reservation Table

`reservation ----------- id (PK) hotel_id (FK) room_id (FK) guest_id (FK) start_date end_date status total_price created_at`

Status examples:

- PENDING
    
- CONFIRMED
    
- CANCELLED
    
- EXPIRED
    

---

### Inventory Calendar Table (Critical)

Tracks availability per room per date.

`room_inventory -------------- room_id (FK) date is_booked reservation_id PRIMARY KEY (room_id, date)`

This is the table used for locking.

---

# Guest Schema

---

### Guest Table

`guest ----- id (PK) first_name last_name email phone created_at`

Index:

- Unique(email)


# Inventory Schema
# Room Type Inventory

This table is the **source of truth** for availability.
```json
room_type_inventory
-------------------
hotel_id (FK)
room_type_id (FK)
date
total_rooms
booked_rooms
overbooking_limit
version
PRIMARY KEY (hotel_id, room_type_id, date)

```
---