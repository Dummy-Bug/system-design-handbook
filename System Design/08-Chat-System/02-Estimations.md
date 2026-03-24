- DAU - 50M, per user assume 100 messages per day , so we can see 500M writes per day. 
- Assuming peak load to be 20x , so (500M * 20) = 10B writes,
  so write QPS -> 10 * 10^9 / 10^5 -> 1M writes per second.


# Major APIs

1. Send message(from,to,text,media:[s3links]) // no need of group_id as we are focusing only on 1:1 chat.
2. Recent chats (user_id) : `List<Chats>` 
3. Open chat thread (current_user,other_user)

 We need Realtime communication here that can be faciliiated via 
 Short polling, Long-polling,SSE or Websockets.

- No need of short polling as we do not want to bombard our servers since there might not be any message for the user.
- No need of long polling because if there was a message present but because of long poll delay you did not get the message immediatley.
- No need of SSE as well because messages are client to server as well as server to client.

so only option left is bidirectional Websockets

communication protocol -> Websockets


