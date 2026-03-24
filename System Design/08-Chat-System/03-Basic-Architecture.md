

- We have to persist the messages inside the DB as we do not want to lose the messages.
- Once the ACK is received from the DB , App Server would broadcast message to the reciever and also broadcast to the sender that the message has been successfully sent.

> **Single Tick** in whatsapp only come when we have the ACK that message has been persisted in the DB.

![[Excalidraw/Drawing 2026-03-24 07.32.11.excalidraw]]
**Problems**
we have horizontally scaled App-Servers maintaining websocket connections.It might happen that Sender is connected to s1 and receiver is connected to s2.So if a message comes to s1 then it has communicate with s2 to somehow broadcast the message to receiver.


So we have to introduce have to maintained by separate websocket service.

Now when sender is going to send a message then that message is going to be received by one of the websocket server say ws1 then this server would send the request to application server say s1 and after persisting data inside DB s1 has the following information sender_id and receiver_id. So we can maintain a cache which would store the mapping of user_id:socket_server_id
to know which user is connected to which socket server.

![[Excalidraw/Drawing 2026-03-24 10.27.06.excalidraw]]

Now s1 knows which user is connected to which websocket server so it will make requests to both those websocket servers ws1 and ws2 to broadcast the message to both of them.

So this basic flow only take care of 1:1 chat for only text messages.


