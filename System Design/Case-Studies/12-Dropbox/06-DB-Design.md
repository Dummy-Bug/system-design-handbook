## DB Design and Permission Handling

- In home page of client we might need to show the users a list of all the documents they have access to. Like a few they created or maybe shared to them.
- Users might also filter the documents on the home page based on the access control.
- We can easily store it in a RDBMS like MySql , document store like MongoDB or a key value store like Redis.Mainly we have to store mapping of user_id and file_id along with the access viz :visitor , editor or creator
![[Excalidraw/Drawing 2026-03-29 19.17.53.excalidraw]]
- To decide the final DB we can think about the replication strategy required for the DB to scale.A single leader replication should be fine here , as this table won't be a big bottleneck for the overall system. As we won't update file permissions very frequently,hence writes will be less, so a single leader is good.Hence MySql is a good choice for this permission DB.


## Versoning in chunks metadata

- Instead of storing one list of chunks , we can store multiple lists of chunks where each list will denote version , and the set of chunks will be the file hashes for that version.S3 supports chunk version etc etc
- A lot of chunjs might be common across versions so the S3 link will be same also.

## What DB to chose from DB

- Now we know that system might lead to race conditions where two clients are trying to change chunk of same file.
- We might need some locking mechanism in this case and keeping a single leader replication will make it easy to apply ACID here.so again using RDBMS like MySql should work for us.If race conditions are not in place then a document store like MongoDB is also good.
- For a better throuput we can partition the DB based on fileId as it is the primary key in identifying the file.

**What if we use multi leader replication ?**
- In multi leader replication it can happen that multiple clients do a write of metadata to different leader for the same file , which will lead to conflict.
- In that case we might need to do a manual conflict resolution by the user,which will be complex for users.