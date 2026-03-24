## Functional Requirements

- 1:1 chat support just like massenger
- User should be able to view the messages
- Support of Media sharing atleast Images
- If user is offline then messages should be delivered to him when he comes back
- Support recent K chats

## Non Functional Requirements

- High Consistency with good availability
- Order of messages should be taken care of
- High Reliability
- Writes are more frequent , so write heavy system.

Pacelec and PI theorem are more prevalent here as because it's **tough to chose between consistency and availability.But if you are going towars CAP theorem direction then make sure that you are able to justify why to chose one over the other.**
- We prioritize Consistency over Availability for message ordering — a user should never see messages out of order or miss a message. Brief unavailability (retry) is more acceptable than delivering wrong order or losing a message. → CP system."


but how can we say that system is write heavy when every message we write is going to be read ?
- **In a group chat or social feed:**
- 1 message written → read by 1000 people
- Clearly read-heavy

**In 1:1 chat:**
- 1 message written → read by exactly 1 other person
- Plus sender sees it → **2 reads per write at most**
- Read:Write ratio ≈ **2:1**
- That's why it's **write-heavy** — reads barely outnumber writes , moreover one Write operation on DB is heavier than one Read operation on DB as writes involve durability guarantees, replication, WAL logging etc. Reads are just lookups.