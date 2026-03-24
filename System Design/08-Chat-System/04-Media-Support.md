
Let's add Media Support as well.

so we know we need Blob storage to store media as they are heavy in size.

Whenever sender sends a message then sender is going to connect to the app server to get  the presigned url from app server because to load something to s3 directly sender needs presigned url from server which server would get from connecting to s3.Then presigned url can be used to upload the images to s3 directly.Then get the link of the files that are uploaded and sender can send.

![[Excalidraw/Drawing 2026-03-24 10.56.33.excalidraw]]

> Most of the times we can notice in our chat app as well that e.g in ChatGpt when we try to upload an image till the time that image has not uploaded it does not sends the message.

- It might also happen that upload is succesfull but then user never clicked the send messsage so in this case image would still be stored inside the s3 and a cronJob would be needed to remove such files periodic files that were never sent.



**Double Write Problem**

App server has to send two requests to websocket server , what if one of the request fails and other succeed ? like with the current diagram receiver can receive the message but sender might not get the ACK.

> 2 Phase Commit but problem with it is , it's hard to implement and can take lot of time

> use Saga using orchestration , e.g we use the application server as orchestrator and you have retry mechanisms and one of the requests fails we retry and even after retry it does not work then we can have fallback mechanism to bring the message back. but if receiver has already received the message we cannot delete it so even SAGA won't work here.


> How about placing a Kafka Cluter between websocket and App Server but Kafka does not push the data so we have to write consumers as well . Kafka is a pull mechanism but we need push mechanism. What would be the Topic in Kakfa if we use it ? say chatid :sender_id+client_id , then can chatId can be a topic ? if yes then there would be billions of topics.One idea for topic could be all the messages that are expected to be read by one websocket server goes to one topic .So if we have 10 websocket servers then we have 10 topics , all the messages goes through one topic but then these websockets servers has to do extra work of pulling the things from Kafka which includes extra overhead.
> All in all Kafka is needed we need the payload to be read multiple time but here we need atmost one kinda delivery.


So better solution here is to use **Redis PubSub**.SO what we gonna do is, after message is persisted in DB and we get the ACK back we will send the message to realtime PubSub which is a push based mechanism.Now PubSub will directly push it to the corresponding set of websocket servers provides websocketr servers are consumer of this PubSub, the difference here is that in Kafka consumers have to pull the data from the Message Stream but here consumers would get the data directly from [PubSub](https://redis.io/docs/latest/develop/pubsub/). In our case App-Server are the publisher of the message and Websockets are the subscriber of the message and neither publisher knows who are consumer and vice versa.

![[Excalidraw/Drawing 2026-03-24 11.58.34.excalidraw]]

so now we do not need any cache at all everything is facilitiated by Redis PubSub


**what if receiver is offline** 

> PubSub server would push the data or message to server's websocket server and sender will get the ACK.because receiver is not connected to any websocket server .So now again we would need Cache so that PubSub can check if there's websocket connection present for the user or not.If user is offline then websocket connection won't be present for that user.This Cache can be re-populated again and again similar to heartbeat mechanism, such that any user who is going to communicate or setup a connection with any websocket server they have to send constantly heartbeat to our Redis Cache Server and inside this Cache we can setup a TTL so after 10 second let's say we delete the entry of userId:WebsocketServerId and if we do not get any heartbeat then there won't be any entry inside the Cache.

- Whenever receiver comes back online , it make a query to application server that give me all the pending messages and for this we can use **cursor based pagination** that would tell I know what was the last message that was on my device so only provide messages after that last message.So it is a sync request to app-server based on cursor where cursor can be a timestamp.

Problem with this mechanism is that if we have to implement the double tick then we have to send back the ACK to sender also signifying that message has been received by the receiver.


we can use similar thing to what mails do . In mails we have option of outbox and sent.Mails that are in outbox are not yet received by the receiver or not yet atleast acknowledged to be sent they are about to be delivered.While sent are successfully sent.

![[Excalidraw/Drawing 2026-03-24 12.35.38.excalidraw]]
- We can maintain an Inbox of receivers, if it's offline then we can send the message to the Redis Inbox of that receiver and it will stay in the Inbox till the time receiver has not received it.The moment receiver receives it , we will delete that message or those messages.Now when sender receives the ACK it can also check the Redis Inbox that are these messages present inside the Redis Inbox or not if present then it means receiver has not received it yet . so it will still show `Single Tick`, if messages are not present then show `Double Tick`.And once receiver comes back online it can make a websocket connection and websocket server can go to Inbox and fetch all the messages for the corresponding chatId and deliver them back to receiver. We can use separate notification system FCM(firebase Cloud Messaging) that would take all the pending messages from Inbox and notify receiver when he comes back.Like FCM can give us the signal when a receiver is connected to the internet or not. so when receiver turns on thr internet it gets connected to FCM which will signal the notification system that receiver is online and it can proceed to get the data from Inbox and deliver the pending messages.


what if when receiver comes back online sender send the new message ?  in this case how can we make sure that new message should be received only after the pending messsages have been delivered ?

- One way to maintain the ordering of messages is to re-order them according to timstamp.Linkedin sometimes have been seen doing the re-ordering of messages showing jittery behaviour.

- Other and more correct way could be once app server has published the message inside PubSub , the pubSub would check if there are any other messages present for the receiver or not if yes then append the current latest messages in the inbox as well.for example message m1 was sent but receiver was offline so PubSub would keep it inside inbox then m2 was sent again same flow but now say receiver has came back and at the same time sender sent the m3 now pubsub could send the m3 directly to receiver but it won't first it will check if receiver has received old messages or not , if inbox contains chatId and is non empty then it would append this latest message to inbox as well and it would reach the receiver via FCM path. and if inbox had not contained the chatId then it would mean that m3 is the latest message because by the time m3 was sent m1 and m2 were already delivered by FCM and now PubSub can directly send the m3 via websocket server path.and even if after applying all of this still some messages have arrived not in order then we can apply re-ordering based on timestamp on top of it.


Now both sender and receiver **closed** the whatsapp and now they both have opened the same chat then how will they see all the messages ?

- We have to communicate to the app-server that give me the last 100 messages of this chat.

In this case it would not matter if sender was sending some message or not because we are directly fetching the messages from the DB.So in this case we are not fetching anything from Inbox or Websockets.It's just previous history of messages from DB.


**How can we support recent chats ?**
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

Chat 
```Http
chatId
senderId
receiverId
createdAt
updatedAt
```
Message
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


