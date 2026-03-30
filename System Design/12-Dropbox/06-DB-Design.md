## DB Design and Permission Handling

- In home page of client we might need to show the users a list of all the documents they have access to. Like a few they created or maybe shared to them.
- Users might also filter the documents on the home page based on the access control.
- We can easily store it in a RDBMS like MySql , document store like MongoDB or a key value store like Redis.Mainly we have to store mapping of user_id and file_id along with the access viz :visitor , editor or creator
![[Excalidraw/Drawing 2026-03-29 19.17.53.excalidraw]]
- To decide the final DB we can think about the replication strategy required for the DB to scale.A single leader replication should be fine here , as this table won't be a big bottleneck for the overall system. As we won't update file permissions very frequently,hence writes will be less, so a single leader is good.Hence MySql is a good choice for this permission DB.


## Versoning in chunks metadata