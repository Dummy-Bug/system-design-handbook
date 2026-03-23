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

Pacelec and PI theorem are more prevalent here as because it's **tough to chose between consistency and availability.but if you are going towars CAP theorem direction then make sure that you are able to justify why to chose one over the other.**


but how can we say that system is write heavy when every message we write is going to be read ?
- If a data is being read more number of times then it's read heavy system else it's a write heavy, so if it 1:1 then it's write heavy because Read is dependent on Write.
- One Write operation on DB is heavier than one Read operation on DB.