
## How to support recent chats ?

Inside Inbox we can maintain OrderedSet of 
user:[{chatId,lastMessageTimestamp,lastMessageId}]

Now any client is going to communicate with App-Server and this App-Server will communicate with OrderedSet part inside the Redis Inbox.This orderset we can maintain for a particular user.Now App-Server would fetch this orderset for the client using userId and now app-server has the last 10 chats of the user with messageId etc and now it can go to DB and make a batch query to get the data of all of these chats and sends it back to the client.

![[Excalidraw/Drawing 2026-03-24 14.20.09.excalidraw]]


Only thing left is how the DB should look like,

since we need write heavy DB so Cassandra is one of the option 

But how can we partition the data.

**When is a partition strategy is not good ?** When queries needs to go to multiple partitions.

> UserId - u1 is chatting to u2,Now if U1 send a message to U2 then M1 would get sent to both the partitions, so this would introduce **Double Write Problem** again.


- ChatId - u1 is chatting to u2 . Now if u1 send a message then we only need to write to one partition.

Chat Table
```Http
chatId
senderId
receiverId
createdAt
updatedAt
```

Message Table
```Http
messageId
chatId(FK)
text
medias:[]
createdAt
updatedAt 
```


so chatId would work great for all the Functional Requirements except for recent messages , let's say we have to fetch recent 20 chats then we have to go to 20 partitions to get the last 10 messages of each chat and this involves multi-partition query.

user:[{chatId,lastMessageTimestamp,lastMessageId}].

If we look at whatsapp's functionality clearly in recent chats instead of showing whole text it only show the truncated text.

![[Excalidraw/Drawing 2026-03-24 15.15.00.excalidraw]]

so we need just some text or information to show or we can also keep the complete message payload of the latest message but if you think this is too much to store in the Redis cache then we can store the truncated text. so intsead of storing just the MessageId in orderedSet we can save lastMessage's Truncated Text. 
user:[{chatId,lastMessageTimestamp,lastMessageTruncated}].


Now if reciever comes up and open one of the recent chat then our normal history API would get called using cursor pagincation and all.

so one of the WebSocket server serving 10 users got crashed then what happen ? **Consistent Hashing** comes into play.