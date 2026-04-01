
> [!abstract] Think of a hotel booking form with 10 fields sitting in a filing cabinet.
> Every HTTP method does something different to that form.

---

> [!example]- `GET` — Read something (no changes made)
> Fetch a hotel, a reservation, a list of rooms. The server reads and returns data. Nothing is created or modified.
> ```http
> GET /hotels/H1001
> ```
> **Analogy:** Walking to the filing cabinet and reading the form. You don't touch it.
> **ID needed?** Yes (or filter via query params like `?city=New+York`)

---

> [!example]- `POST` — Create something new
> The resource doesn't exist yet. The server creates it and generates a new ID.
> ```http
> POST /hotels
>
> { "name": "Marriott Downtown", "city": "San Francisco" }
> ```
> **Analogy:** Handing in a blank new form to be filed. The clerk stamps a new ID on it.
> **ID needed?** No — server generates it. Every call creates a new record.

---

> [!example]- `PUT` — Replace an existing resource completely
> The resource exists. You send the entire object. The server overwrites it wholesale — fields you omit get wiped.
> ```http
> PUT /hotels/H1001
>
> {
>   "name": "Marriott Downtown",
>   "city": "San Francisco",
>   "rating": 4.5,
>   "amenities": ["wifi"]
> }
> ```
> **Analogy:** Taking the form out, whiting out every field, rewriting all 10 from scratch.
> **ID needed?** Yes — you are replacing a specific existing record.

---

> [!example]- `PATCH` — Update specific fields only
> The resource exists. You send only the fields you want to change. Everything else stays untouched.
> ```http
> PATCH /hotels/H1001
>
> { "rating": 4.8 }
> ```
> **Analogy:** Taking out the form and crossing out just field 3. The other 9 fields are untouched.
> **ID needed?** Yes — you are partially updating a specific existing record.

---

> [!example]- `DELETE` — Remove a resource
> The resource exists. The server deletes it entirely.
> ```http
> DELETE /hotels/H1001
> ```
> **Analogy:** Pulling the form out of the filing cabinet and shredding it.
> **ID needed?** Yes — you are deleting a specific record.

---

> [!tip] One-line summary
> `GET` → read &nbsp;|&nbsp; `POST` → create &nbsp;|&nbsp; `PUT` → full replace &nbsp;|&nbsp; `PATCH` → partial update &nbsp;|&nbsp; `DELETE` → remove

---
