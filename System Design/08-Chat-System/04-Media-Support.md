## Sending Images instead of Text

We know we need Blob storage to store media as they are heavy in size.

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

so now we do not need any cache at all everything is facilitiated by Redis PubSub.


