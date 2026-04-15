
> [!info] Why API Gateway can't rate limit WebSocket messages
> API Gateway works at the HTTP layer. Once a connection upgrades to WebSocket, the gateway is out of the picture — and so is any rate limiting it provides.

---

## The naive approach

The first instinct for rate limiting is to put it at the API Gateway. Every request passes through the gateway, so it's a natural chokepoint. For REST APIs this works perfectly — the gateway sees every HTTP request and can count them per user.

For WhatsApp, this only works up to the WebSocket upgrade.

```
Client → HTTP GET /connect (upgrade request) → API Gateway → Connection Server
                                                ↑
                               Gateway sees this, can rate limit here

Client ←→ [WebSocket connection established] ←→ Connection Server
                                                ↑
                       Gateway is now invisible — all messages bypass it entirely
```

After the upgrade, the connection is a persistent TCP stream between the client and the connection server. Every message the user sends flows directly over this stream. The API Gateway never sees them.

> [!danger] A common interview mistake
> "I'll rate limit at the API Gateway" only works for the connection setup, not for messages. At the message level, the gateway is completely bypassed. Rate limiting must live inside the connection server.
