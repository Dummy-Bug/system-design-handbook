## What if Receiver is offline? 

> PubSub server would push the data or message to server's websocket server and sender will get the ACK.because receiver is not connected to any websocket server .So now again we would need Cache so that PubSub can check if there's websocket connection present for the user or not.If user is offline then websocket connection won't be present for that user.This Cache can be re-populated again and again similar to heartbeat mechanism, such that any user who is going to communicate or setup a connection with any websocket server they have to send constantly heartbeat to our Redis Cache Server and inside this Cache we can setup a TTL so after 10 second let's say we delete the entry of userId:WebsocketServerId and if we do not get any heartbeat then there won't be any entry inside the Cache.

- Whenever receiver comes back online , it make a query to application server that give me all the pending messages and for this we can use **cursor based pagination** that would tell I know what was the last message that was on my device so only provide messages after that last message.So it is a sync request to app-server based on cursor where cursor can be a timestamp.

Problem with this mechanism is that if we have to implement the double tick then we have to send back the ACK to sender also signifying that message has been received by the receiver.


we can use similar thing to what mails do . In mails we have option of outbox and sent.Mails that are in outbox are not yet received by the receiver or not yet atleast acknowledged to be sent they are about to be delivered.While sent are successfully sent.

![[Excalidraw/Drawing 2026-03-24 12.35.38.excalidraw]]
- We can maintain an Inbox of receivers, if it's offline then we can send the message to the Redis Inbox of that receiver and it will stay in the Inbox till the time receiver has not received it.The moment receiver receives it , we will delete that message or those messages.Now when sender receives the ACK it can also check the Redis Inbox that are these messages present inside the Redis Inbox or not if present then it means receiver has not received it yet . so it will still show `Single Tick`, if messages are not present then show `Double Tick`.And once receiver comes back online it can make a websocket connection and websocket server can go to Inbox and fetch all the messages for the corresponding chatId and deliver them back to receiver. We can use separate notification system FCM(firebase Cloud Messaging) that would take all the pending messages from Inbox and notify receiver when he comes back.Like FCM can give us the signal when a receiver is connected to the internet or not. so when receiver turns on thr internet it gets connected to FCM which will signal the notification system that receiver is online and it can proceed to get the data from Inbox and deliver the pending messages.


**what if when receiver comes back online sender send the new message ?** 
In this case how can we make sure that new message should be received only after the pending messsages have been delivered ?

- One way to maintain the ordering of messages is to re-order them according to timstamp.Linkedin sometimes have been seen doing the re-ordering of messages showing jittery behaviour.

- Other and more correct way could be once app server has published the message inside PubSub , the pubSub would check if there are any other messages present for the receiver or not if yes then append the current latest messages in the inbox as well.for example message m1 was sent but receiver was offline so PubSub would keep it inside inbox then m2 was sent again same flow but now say receiver has came back and at the same time sender sent the m3 now pubsub could send the m3 directly to receiver but it won't first it will check if receiver has received old messages or not , if inbox contains chatId and is non empty then it would append this latest message to inbox as well and it would reach the receiver via FCM path. and if inbox had not contained the chatId then it would mean that m3 is the latest message because by the time m3 was sent m1 and m2 were already delivered by FCM and now PubSub can directly send the m3 via websocket server path.and even if after applying all of this still some messages have arrived not in order then we can apply re-ordering based on timestamp on top of it.


Now both sender and receiver **closed** the whatsapp and now they both have opened the same chat then how will they see all the messages ?

- We have to communicate to the app-server that give me the last 100 messages of this chat.

In this case it would not matter if sender was sending some message or not because we are directly fetching the messages from the DB.So in this case we are not fetching anything from Inbox or Websockets.It's just previous history of messages from DB.
