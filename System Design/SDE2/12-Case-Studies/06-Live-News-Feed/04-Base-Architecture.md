**Client** A client can either post some content or they could request a feed.

**Load Balancer** Redirect the traffic to the Api Gateway/Web Server

**API Gateway** Intermediate layer between the user and backend services . So it act as the encapsulator that encapsulate all the backend services and provides the one front.Responsible for Rate limiting , Authentications and to redirect the traffic to appropriate service etc etc


![[System Design/SDE2/12-Case-Studies/06-Live-News-Feed/Images/01-Base-Architecture.png]]


**News Feed Generation** Whatever relevant posts from Followers or Friends of the User should be shown to the user , get all it's metadata all of it's references and store it inside in-memory.

**News Feed Publishing** While publishing we have to get that meta data and references(from news feed cache) and hit the blob storage and show it to the user.

**Notification Service** It notifies News Feed Generation service whenever a new post is available from one of the following by sending the push notification.

**Post Service** Whenever there's a request to create a post then this service is called and the created post is stored inside the Post database and also with corresponding cache and the actual Media content is stored inside the Blob storage.like data about the post would be present inside the db but actual video or image would be present inside the Blob storage.


### Storage Schema

**User** This table contains data about the User.
```Json

id,
mobile,
name,
email
```

**Entity** Stores data related to any data such as pages , groups etc.
```Json

id,
name,
created_at
```

**Feed Item** Data about the post posted by a User.
```Json

id,
likes,
media_id,
```

**Media** Information about the Media type
```Json

id,
type
```

User and Feed Item tables have structured data so SQL db makes sense here but what about storing the relationships between user , friend and followers ? **Graph DB** is the natural choice for the relationships among the User.

We can think of Graph DB consisting of two relational tables
1. Vertices -> Users
2. Edges -> Relations
so we follow a relational schema only for the Graph DB.

so in Graph DB we would have the following

**USER**
```Json

user_id :int 
properties : Json
```

**RELATIONSHIP**
```Json

relation_id :int 

relation_from : int (reference user_id)

relation_towards :int (reference user_id)

label:

proprties: Json
```

say we have two Users U1 (user_id 123) and U2 (user_id 321). now say U1 has started following U2.

so RELATIONSHIP table would contain the following things

```Json

relation_id : 1000
relation_from : 123
relation_towards : 321
label : following
```

